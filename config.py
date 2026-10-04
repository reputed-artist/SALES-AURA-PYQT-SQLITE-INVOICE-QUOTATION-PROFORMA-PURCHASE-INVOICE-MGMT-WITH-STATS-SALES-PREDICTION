"""
C4 PyQt - Application configuration
Mirrors CodeIgniter .env / app/Config values of the original project.
"""
import os
import sys

# ---------------------------------------------------------------------------
# Database (from c:\xampp\htdocs\C4\.env  ->  database.default.*)
# ---------------------------------------------------------------------------
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "db",
    "charset": "utf8mb4",
}

# ---------------------------------------------------------------------------
# Branding (from app/Views/Include/header.php)
# ---------------------------------------------------------------------------
APP_TITLE = "AntDev"
LOGO_MINI = "CT"          # <span class="logo-mini"><b>C</b>T</span>
LOGO_FULL = "AntDev"      # <span class="logo-lg"><b>Ant</b>Dev</span>

# Original project root (used to re-use uploaded pictures / product images)
ORIG_PROJECT_ROOT = r"c:\xampp\htdocs\C4"
ORIG_UPLOAD_DIR = os.path.join(ORIG_PROJECT_ROOT, "public", "uploads")

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
DEFAULT_HSN = "8443"

# AdminLTE colour palette replicated in ui/theme.py
COLORS = {
    "sidebar_bg": "#222d32",
    "sidebar_hover": "#1e282c",
    "sidebar_link": "#b8c7ce",
    "header_bg": "#3c8dbc",
    "content_bg": "#ecf0f5",
    "box_border": "#f4f4f4",
    "success": "#00a65a",
    "danger": "#dd4b39",
    "warning": "#f39c12",
    "info": "#00c0ef",
    "primary": "#3c8dbc",
    "purple": "#605ca8",
    "navy": "#001f3f",
    "teal": "#39cccc",
    "aqua": "#00c0ef",
    "green": "#00a65a",
    "red": "#dd4b39",
}
