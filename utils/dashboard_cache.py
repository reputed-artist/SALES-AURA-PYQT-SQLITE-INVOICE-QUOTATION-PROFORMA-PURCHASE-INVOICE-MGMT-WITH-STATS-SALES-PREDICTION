"""
dashboard_cache.py

Thread-safe in-memory cache for dashboard queries.

Public API
----------
cached(key, ttl, loader, default=..., on_error=None) -> value
get(key, default=None) -> value
set(key, value, ttl=TTL_CHART) -> None
invalidate(prefix="") -> None
warm_many(tasks, progress=None) -> None
fill_all(year, fy_start, fy_end, progress=None) -> None
stats() -> dict

The dashboard makes ~15 DB calls per load. This module caches each result for a
TTL that matches its volatility:

    - dashboard_stats           ->  KPI bucket
    - current_month_stats       ->  KPI bucket
    - monthly_sales             ->  chart bucket (per year, keyed)
    - fy_sales_chart            ->  chart bucket (per FY, keyed)
    - donut_*                   ->  chart bucket (per FY where relevant)
    - client_reminder           ->  fast bucket
    - quickquote_reminder       ->  fast bucket
    - recent_invoices           ->  fast bucket (per doc, keyed)

`fill_all()` / `warm()` fills every one of these keys at once. main.py runs
it on a worker thread while the splash screen is still up, so the dashboard's
first refresh() after login is served from memory instead of re-querying.

Any write to a document (invoice / proforma / quote / purchase / payment)
should call `invalidate_dashboard()` to force a refresh on next load.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Callable, Iterable, Optional, Tuple

# --------------------------------------------------------------------- #
# TTL buckets
# --------------------------------------------------------------------- #
TTL_KPI:   float = 20.0
TTL_CHART: float = 60.0
TTL_FAST:  float = 20.0

_LOCK = threading.RLock()
_STORE: dict[str, Tuple[float, Any]] = {}

# Which donuts depend on a financial year (the rest are all-time).
FY_DONUTS = ("consumables", "product_category", "docs")


# --------------------------------------------------------------------- #
# Core API
# --------------------------------------------------------------------- #
def _fresh(entry: Optional[Tuple[float, Any]]) -> bool:
    return entry is not None and entry[0] > time.time()


def get(key: str, default: Any = None) -> Any:
    with _LOCK:
        entry = _STORE.get(key)
        if _fresh(entry):
            return entry[1]
    return default


def set(key: str, value: Any, ttl: float = TTL_CHART) -> None:
    with _LOCK:
        _STORE[key] = (time.time() + float(ttl), value)


def invalidate(prefix: str = "") -> None:
    with _LOCK:
        if not prefix:
            _STORE.clear()
            return
        for k in [k for k in _STORE if k.startswith(prefix)]:
            _STORE.pop(k, None)


def cached(key: str,
           ttl: float,
           loader: Callable[[], Any],
           default: Any = None,
           on_error: Optional[Callable[[Exception], None]] = None) -> Any:
    """
    Return the cached value for `key`, else run `loader()` and store it.

    This is what makes the dashboard cheap after login: the splash screen
    has already filled these keys on a worker thread, so the first render is
    a memory read. A cold key (different year/FY selected, cache expired, or
    the prefetch failed) falls back to the original live query.
    """
    val = get(key)
    if val is not None:
        return val
    try:
        val = loader()
    except Exception as exc:
        if on_error is not None:
            try:
                on_error(exc)
            except Exception:
                pass
        return default
    set(key, default if val is None else val, ttl=ttl)
    # A live query that yields None (empty result set) must hand back
    # `default`, not None - otherwise the first cold paint gets None while
    # every later paint gets the default.
    return default if val is None else val


# --------------------------------------------------------------------- #
# Warm-up (used by the prefetch thread)
# --------------------------------------------------------------------- #
def warm_many(
    tasks: Iterable[Tuple[str, float, Callable[[], Any]]],
    progress: Optional[Callable[[int, int, str], None]] = None,
) -> None:
    tasks = list(tasks)
    total = len(tasks)
    for i, (key, ttl, loader) in enumerate(tasks, 1):
        try:
            value = loader()
        except Exception:
            value = None
        set(key, value, ttl=ttl)
        if progress is not None:
            try:
                progress(i, total, key)
            except Exception:
                pass


# --------------------------------------------------------------------- #
# Cache keys (one source of truth so the dashboard and the prefetch agree)
# --------------------------------------------------------------------- #
def stats_key():
    return "dash.stats"


def month_key():
    return "dash.month"


def monthly_key(year):
    return f"dash.monthly_sales::{year}"


def fy_sales_key(sy, ey):
    return f"dash.fy_sales::{sy}-{ey}"


def donut_key(name, sy=None, ey=None):
    if name in FY_DONUTS and sy is not None and ey is not None:
        return f"dash.donut.{name}::{sy}-{ey}"
    return f"dash.donut.{name}"


def reminder_key(kind):
    return f"dash.reminder.{kind}"


def recent_key(doc, limit):
    return f"dash.recent::{doc}::{limit}"


# --------------------------------------------------------------------- #
# Typed getters
# --------------------------------------------------------------------- #
def get_dashboard_stats():
    return get(stats_key())


def get_current_month_stats():
    return get(month_key())


def get_monthly_sales(year):
    return get(monthly_key(year))


def get_fy_sales_chart(sy, ey):
    return get(fy_sales_key(sy, ey))


def get_donut(name, sy=None, ey=None):
    return get(donut_key(name, sy, ey))


def get_client_reminder():
    return get(reminder_key("clients"))


def get_quickquote_reminder():
    return get(reminder_key("quickquote"))


def get_recent_invoices(doc, limit=8):
    return get(recent_key(doc, limit))


# --------------------------------------------------------------------- #
# fill_all / warm — the ONE function main.py's prefetch thread calls
# --------------------------------------------------------------------- #
def warm(
    year: int,
    sy: int,
    ey: int,
    progress: Optional[Callable[[int, int, str], None]] = None,
) -> None:
    """
    Run every dashboard query once and cache the results.

    Called from a worker thread while the splash screen animates, so the
    first dashboard render after login is a pure cache read. Each individual
    call is wrapped so one broken query cannot abort the rest; a key whose
    query failed simply stays unset, and the page then falls back to a live
    query.
    """
    from database import db_manager  # local import to avoid cycles

    # ensure_dashboard_indexes() issues CREATE INDEX DDL. It runs FIRST and on
    # its own because the subsequent SELECTs get much faster once the indexes
    # exist.
    try:
        db_manager.ensure_dashboard_indexes()
    except Exception:
        pass

    tasks: list[Tuple[str, float, Callable[[], Any]]] = [
        (stats_key(), TTL_KPI, db_manager.dashboard_stats),
        (month_key(), TTL_KPI, db_manager.current_month_stats),
        (monthly_key(year), TTL_CHART,
         lambda y=year: db_manager.monthly_sales("invtest2", "created", y)),
        (fy_sales_key(sy, ey), TTL_CHART,
         lambda s=sy, e=ey: db_manager.fy_sales_chart(s, e)),

        # Donuts
        (donut_key("consumables", sy, ey), TTL_CHART,
         lambda s=sy, e=ey: db_manager.donut_consumables(s, e)),
        (donut_key("user_category"), TTL_CHART,
         db_manager.donut_user_category),
        (donut_key("country"), TTL_CHART,
         db_manager.donut_client_country),
        (donut_key("product_category", sy, ey), TTL_CHART,
         lambda s=sy, e=ey: db_manager.donut_product_category(s, e)),
        (donut_key("billed"), TTL_CHART,
         db_manager.donut_billed_clients),
        (donut_key("docs", sy, ey), TTL_CHART,
         lambda s=sy, e=ey: db_manager.donut_doc_count(s, e)),
        (donut_key("client_type"), TTL_CHART,
         db_manager.donut_client_type),

        # Reminders + recent
        (reminder_key("clients"), TTL_FAST, db_manager.client_reminder),
        (reminder_key("quickquote"), TTL_FAST, db_manager.quickquote_reminder),
        (recent_key("tax", 8), TTL_FAST,
         lambda: db_manager.recent_invoices("tax", 8)),
    ]

    warm_many(tasks, progress=progress)


# Backwards-compatible alias: main.py calls dashboard_cache.fill_all(...).
fill_all = warm


# --------------------------------------------------------------------- #
# Invalidation
# --------------------------------------------------------------------- #
def invalidate_dashboard() -> None:
    """
    Call this after any save/delete that affects dashboard numbers.

    Invoices, proformas, quotes, purchases, payments, clients, products,
    accounts — anything that could change a KPI or chart.
    """
    invalidate()          # drop every cached key; next load re-queries


# --------------------------------------------------------------------- #
# Diagnostic
# --------------------------------------------------------------------- #
def stats() -> dict:
    with _LOCK:
        return {k: (v[1] if _fresh(v) else "<stale>")
                for k, v in _STORE.items()}