"""
Cached wrappers around every db_manager call the dashboard uses.

The dashboard makes ~15 DB calls per load. This module caches each result for a
TTL that matches its volatility:

    - dashboard_stats           ->  5 min  (KPIs, changes on any save)
    - current_month_stats       ->  5 min
    - monthly_sales             ->  10 min (per year, keyed)
    - fy_sales_chart            ->  10 min (per FY, keyed)
    - donut_*                   ->  10 min (per FY where relevant)
    - client_reminder           ->  2 min (changes as proformas come in)
    - quickquote_reminder       ->  2 min
    - recent_invoices           ->  2 min (per doc, keyed)

`warm()` fills every one of these keys at once. main.py runs it on a worker
thread while the splash screen is still up, so the dashboard's first refresh()
after login is served from memory instead of re-querying.

Any write to a document (invoice / proforma / quote / purchase / payment)
should call `invalidate_dashboard()` to force a refresh on next load.
"""
from database import db_manager
from utils.cache import cache


# --------------------------------------------------------------------- TTLs
TTL_KPI = 300            #  5 min
TTL_CHART = 600          # 10 min
TTL_FAST = 120           #  2 min

# Which donuts depend on a financial year (the rest are all-time).
FY_DONUTS = ("consumables", "product_category", "docs")


# --------------------------------------------------------------- cache keys
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


# Short aliases kept so existing code keeps working.
_k_stats = stats_key
_k_month = month_key
_k_monthly = monthly_key
_k_fy_sales = fy_sales_key
_k_donut = donut_key
_k_reminder = reminder_key
_k_recent = recent_key


# ------------------------------------------------------------ cache-or-fetch
def cached(key, ttl, live, default=None, on_error=None):
    """Return the cached value for `key`, else run `live()` and store it.

    This is what makes the dashboard cheap after login: the splash screen has
    already filled these keys on a worker thread, so the first render is a
    memory read. A cold key (different year/FY selected, cache expired, or the
    prefetch failed) simply falls back to the original live query.

    `on_error` is called with the exception when the live query raises, so the
    page can still surface a DB error the way it always has.
    """
    val = cache.get(key)
    if val is not None:
        return val
    try:
        val = live()
    except Exception as exc:
        if on_error is not None:
            on_error(exc)
        return default
    cache.set(key, default if val is None else val, ttl=ttl)
    # Return the same value that was cached. A live query that yields None
    # (empty result set) must hand back `default`, not None - otherwise the
    # first cold paint gets None while every later paint gets the default,
    # and callers like donuts' set_data(None) blow up only on that first call.
    return default if val is None else val


# ------------------------------------------------------------------ getters
def get_dashboard_stats():
    return cache.get(stats_key())


def get_current_month_stats():
    return cache.get(month_key())


def get_monthly_sales(year):
    return cache.get(monthly_key(year))


def get_fy_sales_chart(sy, ey):
    return cache.get(fy_sales_key(sy, ey))


def get_donut(name, sy=None, ey=None):
    return cache.get(donut_key(name, sy, ey))


def get_client_reminder():
    return cache.get(reminder_key("clients"))


def get_quickquote_reminder():
    return cache.get(reminder_key("quickquote"))


def get_recent_invoices(doc, limit=8):
    return cache.get(recent_key(doc, limit))


# ------------------------------------------------------------------ fillers
def warm(year, sy, ey):
    """Run every dashboard query once and cache the results.

    Called from a worker thread while the splash screen animates, so the first
    dashboard render after login is a pure cache read. Each individual call is
    wrapped so one broken query cannot abort the rest (or blank the page); a key
    whose query failed simply stays unset, and the page then falls back to a
    live query.

    The whole fill runs inside `cache.batch()` so the ~15 writes cost ONE
    pickle to disk at the end instead of 15 sequential disk writes - that was
    a large part of why the prefetch used to overrun the splash.
    """
    def put(key, ttl, fn, default):
        try:
            value = fn()
        except Exception:
            return
        cache.set(key, default if value is None else value, ttl=ttl,
                  persist=False)

    # ensure_dashboard_indexes() issues CREATE INDEX DDL. That can take a long
    # time on a large invtest/invtest2 and there is no statement timeout on it,
    # so it runs FIRST and on its own; everything after it is plain SELECTs
    # that get much faster once the indexes exist.
    try:
        db_manager.ensure_dashboard_indexes()
    except Exception:
        pass

    with cache.batch():
        put(stats_key(), TTL_KPI, db_manager.dashboard_stats, {})
        put(month_key(), TTL_KPI, db_manager.current_month_stats, {})
        put(monthly_key(year), TTL_CHART,
            lambda: db_manager.monthly_sales("invtest2", "created", year),
            [0] * 12)
        put(fy_sales_key(sy, ey), TTL_CHART,
            lambda: db_manager.fy_sales_chart(sy, ey), [])

        donuts = {
            "consumables":      lambda: db_manager.donut_consumables(sy, ey),
            "user_category":    db_manager.donut_user_category,
            "country":          db_manager.donut_client_country,
            "product_category": lambda: db_manager.donut_product_category(sy, ey),
            "billed":           db_manager.donut_billed_clients,
            "docs":             lambda: db_manager.donut_doc_count(sy, ey),
            "client_type":      db_manager.donut_client_type,
        }
        for name, fn in donuts.items():
            put(donut_key(name, sy, ey), TTL_CHART, fn, [])

        put(reminder_key("clients"), TTL_FAST, db_manager.client_reminder, [])
        put(reminder_key("quickquote"), TTL_FAST,
            db_manager.quickquote_reminder, [])
        put(recent_key("tax", 8), TTL_FAST,
            lambda: db_manager.recent_invoices("tax", 8), [])


# Backwards-compatible alias.
fill_all = warm


# ---------------------------------------------------------------- invalidation
def invalidate_dashboard():
    """Call this after any save/delete that affects dashboard numbers.

    Invoices, proformas, quotes, purchases, payments, clients, products,
    accounts, anything that could change a KPI or chart.
    """
    cache.invalidate_all()