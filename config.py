# config.py
"""
C4 PyQt — Application configuration.
Local SQLite storage configuration.

All writable paths (DB, uploads, backups, logs) resolve under
%LOCALAPPDATA%\\Sales Aura\\ via `utils.paths` — never inside the program's
own folder. This keeps the app runnable from "C:\\Program Files" without
admin rights and preserves user data across upgrades.

WHEN RUNNING FROM SOURCE:
    DB and writable folders default to the project-local `data/` and
    `dist/img/uploads` folders, so development is unchanged.
"""
import os

from utils.paths import (
    resource_path,
    user_data_dir,       # single source of truth (utils/paths.py)
    user_subdir,
    user_db_path,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR_NAME = "Sales Aura"
DB_NAME      = "sales_aura.db"


# ---------------------------------------------------------------------------
# Frozen / source mode detection — ONE definition
# ---------------------------------------------------------------------------
def is_frozen() -> bool:
    """True when running from a PyInstaller-built exe."""
    import sys
    return bool(getattr(sys, "frozen", False))


def _ensure_dir(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
    return path


# ---------------------------------------------------------------------------
# Database — live path + one-time seed copy
# ---------------------------------------------------------------------------
def get_db_path() -> str:
    """
    Absolute path to the LIVE database.

    Frozen : %LOCALAPPDATA%\\Sales Aura\\database\\sales_aura.db
    Source : <project>\\data\\sales_aura.db
    """
    if is_frozen():
        return user_db_path(DB_NAME)
    return os.path.join(BASE_DIR, "data", DB_NAME)


def _seed_candidates() -> list:
    """Locations to look for a seed DB, in order of preference."""
    import sys
    if is_frozen():
        return [
            resource_path("data", DB_NAME),
            os.path.join(os.path.dirname(os.path.abspath(sys.executable)),
                         "data", DB_NAME),
        ]
    return [os.path.join(BASE_DIR, "data", DB_NAME)]


def initialize_database() -> str:
    """
    Return the live DB path, creating it once from the bundled seed
    if it does not already exist.  Safe to call on every startup.
    """
    target = get_db_path()
    target_abs = os.path.abspath(target)
    _ensure_dir(os.path.dirname(target_abs))

    if os.path.exists(target_abs):
        return target_abs

    seed = next(
        (p for p in _seed_candidates()
         if os.path.isfile(p) and os.path.abspath(p) != target_abs),
        None,
    )

    if seed is None:
        # No seed (or seed == target). Create an empty DB only if it
        # genuinely does not exist.
        if not os.path.exists(target_abs):
            try:
                open(target_abs, "a").close()
            except Exception:
                pass
        return target_abs

    import shutil
    try:
        shutil.copy2(seed, target_abs)
    except Exception:
        if not os.path.exists(target_abs):
            try:
                open(target_abs, "a").close()
            except Exception:
                pass
    return target_abs
    

# Computed once at import time.
DB_FILE = initialize_database()


# ---------------------------------------------------------------------------
# Writable folders — ONE definition each
# ---------------------------------------------------------------------------
UPLOAD_DIR = user_subdir("uploads")
PDF_DIR    = user_subdir("pdf")
LOG_DIR    = user_subdir("logs")
DB_DIR     = user_subdir("database")

# Backups sit next to the live DB so Settings → Backup/Restore can find them.
BACKUP_DIR = _ensure_dir(os.path.join(os.path.dirname(DB_FILE), "backups"))


# ---------------------------------------------------------------------------
# Read-only assets shipped with the app
# ---------------------------------------------------------------------------
BUNDLE_IMG_DIR = resource_path("dist", "img")


# ---------------------------------------------------------------------------
# DSN-style config consumed by db_manager
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "engine":   "sqlite",
    "database": DB_FILE,
}


# ---------------------------------------------------------------------------
# Branding
# ---------------------------------------------------------------------------
APP_TITLE = "AntDev"
LOGO_MINI = "CT"
LOGO_FULL = "AntDev"

ORIG_PROJECT_ROOT = r"c:\xampp\htdocs\C4"
ORIG_UPLOAD_DIR   = os.path.join(ORIG_PROJECT_ROOT, "public", "uploads")


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_HSN = "8443"


# ---------------------------------------------------------------------------
# AdminLTE colour palette replicated in ui/theme.py
# ---------------------------------------------------------------------------
COLORS = {
    "sidebar_bg":    "#222d32",
    "sidebar_hover": "#1e282c",
    "sidebar_link":  "#b8c7ce",
    "header_bg":     "#3c8dbc",
    "content_bg":    "#ecf0f5",
    "box_border":    "#f4f4f4",
    "success":       "#00a65a",
    "danger":        "#dd4b39",
    "warning":       "#f39c12",
    "info":          "#00c0ef",
    "primary":       "#3c8dbc",
    "purple":        "#605ca8",
    "navy":          "#001f3f",
    "teal":          "#39cccc",
    "aqua":          "#00c0ef",
    "green":         "#00a65a",
    "red":           "#dd4b39",
}