# config.py
"""
C4 PyQt — Application configuration.
Local SQLite storage configuration.
"""
import os
<<<<<<< HEAD
import shutil
import sys

from utils.paths import (
    app_root,
    bundled_seed_db,
    resource_path,
    user_data_dir,
    user_subdir,
    user_db_path,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR_NAME = "Sales Aura"
DB_NAME      = "sales_aura.db"
=======
import sys
>>>>>>> 3e4104e24bf0fa17c5d25c77d7ba1bc88d7f7a71

# ---------------------------------------------------------------------------
# Writable locations (always under %LOCALAPPDATA%\Sales Aura on Windows)
# ---------------------------------------------------------------------------
UPLOAD_DIR = user_subdir("uploads")
BACKUP_DIR = user_subdir("backups")
PDF_DIR    = user_subdir("pdf")
LOG_DIR    = user_subdir("logs")
DB_DIR     = user_subdir("database")

# Read-only asset folder inside the bundle
BUNDLE_IMG_DIR = resource_path("dist", "img")


def is_frozen() -> bool:
    """True when running from a PyInstaller-built exe."""
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

    Always writable, always under %LOCALAPPDATA%\\Sales Aura\\database\\.
    Same path whether frozen or running from source (so a dev DB and a
    production DB never collide — dev uses its own copy).
    """
    if is_frozen():
        return user_db_path(DB_NAME)
    # Running from source: keep the dev DB beside the project
    return os.path.join(BASE_DIR, "data", DB_NAME)


def initialize_database() -> str:
    """
    Return the live DB path, creating it once from the bundled seed
    if it does not exist yet. Safe to call on every startup.
    """
    target = get_db_path()
    _ensure_dir(os.path.dirname(target))

    if os.path.exists(target):
        return target

    # Locate the seed DB that shipped with the app
    if is_frozen():
        bundled_db = bundled_seed_db(DB_NAME)
    else:
        bundled_db = os.path.join(BASE_DIR, "data", DB_NAME)

    if not os.path.isfile(bundled_db):
        # The seed is missing — create an empty DB. The app's
        # init_sqlite_database() will build the schema on first query.
        try:
            open(target, "a").close()
        except Exception:
            pass
        return target

    try:
        shutil.copy2(bundled_db, target)
    except Exception:
        # Fall back to an empty DB rather than refusing to start
        try:
            open(target, "a").close()
        except Exception:
            pass
    return target


# Live DB path — computed once at import time.
DB_FILE = initialize_database()

# Settings → Backup destination
BACKUP_DIR = _ensure_dir(os.path.join(os.path.dirname(DB_FILE), "backups"))

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

<<<<<<< HEAD
=======
# ---------------------------------------------------------------------------
# Writable storage (PyInstaller / "Program Files" safe)
# ---------------------------------------------------------------------------
# Anything the app WRITES (profile picture, company logo, product images,
# exports, cache) must never land inside the program's own folder. When frozen
# that folder is `Program Files\Sales Aura\internal` - read-only for a normal
# user, so writing there fails with "Errno 13 Permission denied".
#
# Reads keep using the bundle (see ui/pages/settings_page.py::_app_base_dir),
# but writes go to a per-user, always-writable directory:
#
#   %LOCALAPPDATA%\Sales Aura\        (C:\Users\<you>\AppData\Local\...)
#   - writable without administrator rights
#   - persists across updates, so uploads are not lost on reinstall
#
# When running from source this resolves to the project's own
# dist/img/uploads, exactly as before, so development is unchanged.
APP_DIR_NAME = "Sales Aura"


def is_frozen() -> bool:
    """True when running from a PyInstaller-built exe."""
    return bool(getattr(sys, "frozen", False))


def _writable(path: str) -> bool:
    """True if we can actually create/write a file in `path`."""
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, ".write_test")
        with open(probe, "wb") as f:
            f.write(b"0")
        os.remove(probe)
        return True
    except Exception:
        return False


def user_data_dir() -> str:
    """Per-user writable root for anything the app writes."""
    if not is_frozen():
        # Development: keep the historical project-local location.
        base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, "dist", "img")

    root = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    candidates = []
    if root:
        candidates.append(os.path.join(root, APP_DIR_NAME))
    # Last resort: a folder beside the exe (works when installed per-user).
    candidates.append(os.path.join(os.path.dirname(sys.executable),
                                   APP_DIR_NAME + " Data"))
    for cand in candidates:
        if _writable(cand):
            return cand
    # Nothing was writable; return the first choice so the caller's error
    # message names a sensible path instead of the Program Files bundle.
    return candidates[0]


def ensure_dir(path: str) -> str:
    """Create `path` (best effort) and return it."""
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
    return path


# Folder that receives user uploads (avatar, company logo, product images).
UPLOAD_DIR = ensure_dir(os.path.join(user_data_dir(), "uploads"))

# Read-only bundle folder that ships the built-in artwork.
BUNDLE_IMG_DIR = os.path.join(
    getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))),
    "dist", "img")


# Default HSN used by the invoice forms
>>>>>>> 3e4104e24bf0fa17c5d25c77d7ba1bc88d7f7a71
DEFAULT_HSN = "8443"

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