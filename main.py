import sys

if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "c4.pyqt.invoice.app"
        )
    except Exception:
        pass

from PyQt6.QtCore import QCoreApplication, Qt, QThread, QTimer

QCoreApplication.setAttribute(
    Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)

from PyQt6.QtWidgets import QApplication

from ui.splash_screen import SplashScreen
from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.app_icon import app_icon, apply
from ui.theme import QSS
from utils import dashboard_cache


# --------------------------------------------------------------------------- #
#  Background dashboard prefetch
# --------------------------------------------------------------------------- #
# Building the shell + dashboard page and running its ~15 queries used to block
# the UI thread for seconds right after login (window "not responding"). Those
# queries do not depend on who logged in, so they are warmed here on a worker
# thread while the splash screen is still animating, and the splash is HELD
# until this thread finishes so the cache is actually warm by the time the user
# can log in. The `done` flag is polled on the UI thread, so the UI thread never
# blocks on the worker.
class _PrefetchThread(QThread):
    """Runs dashboard_cache.warm() off the UI thread."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboard-prefetch")

    def run(self):
        try:
            from datetime import date
            today = date.today()
            # Must match DashboardPage's combo defaults exactly, or the cache
            # keys would not line up and the first render would re-query:
            #   year_combo first item -> today's year
            #   fy_combo   first item -> today's year (i.e. "Apr <year> - Mar <year+1>")
            dashboard_cache.warm(today.year, today.year, today.year + 1)
        except Exception:
            # Purely an optimisation - a failed prefetch just means the
            # dashboard falls back to querying on first paint.
            pass
        finally:
            # Set unconditionally, even on failure, so the splash can never
            # sit waiting on a thread that already died.
            self.done = True


# How long the splash may be held waiting for the prefetch. A cold database
# with a huge invtest table can take a while on the CREATE INDEX DDL, and a user
# staring at a frozen splash is worse than a slightly slow first dashboard - so
# this is a hard ceiling, after which we proceed regardless.
PREFETCH_HOLD_MAX_MS = 20000


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(QSS)
    # Brand icon for every title bar / taskbar entry of the app: top-level
    # widgets (dialogs included) inherit the application icon automatically.
    app.setWindowIcon(app_icon())

    state = {"splash": None, "login": None, "main": None, "prefetch": None}

    splash = SplashScreen(duration_ms=2600)
    apply(splash)
    state["splash"] = splash

    # Kick off the heavy dashboard queries now; they run while the user is
    # still looking at the splash / typing their password.
    prefetch = _PrefetchThread()
    prefetch.done = False
    prefetch.start()
    state["prefetch"] = prefetch

    # Hold the splash until the prefetch is done (or the ceiling is hit), so
    # the dashboard's first render is a cache read rather than ~15 UI-thread
    # queries. This replaces the previous fire-and-forget behaviour that left
    # the cache cold and froze the window right after login.
    splash.hold()

    def release_splash():
        s = state.get("splash")
        if s is not None:
            s.release_finish()

    hold_deadline = [False]   # True once the ceiling has been hit

    def poll_prefetch():
        p = state.get("prefetch")
        ready = p is None or getattr(p, "done", False)
        if ready or hold_deadline[0]:
            hold_timer.stop()
            release_splash()

    hold_timer = QTimer()
    hold_timer.setInterval(120)
    hold_timer.timeout.connect(poll_prefetch)
    hold_timer.start()

    # Hard ceiling: never keep the splash up longer than PREFETCH_HOLD_MAX_MS.
    ceiling = QTimer()
    ceiling.setSingleShot(True)
    ceiling.setInterval(PREFETCH_HOLD_MAX_MS)
    ceiling.timeout.connect(lambda: hold_deadline.__setitem__(0, True))
    ceiling.start()

    def on_splash_done():
        s = state.get("splash")
        if s is not None:
            s.deleteLater()
        state["splash"] = None

        def on_login_success(admin_row):
            # ================================================ #
            # THE FIX: pass the whole admin row, not 3 keys.
            # ================================================ #
            user = dict(admin_row)

            window = MainWindow(user)
            apply(window)
            state["main"] = window
            # Open filling the screen. The user can still un-maximize (restore
            # down) and resize freely - showMaximized() only sets the initial
            # window state, it does not lock the size.
            window.showMaximized()
            state["login"] = None

        login = LoginWindow(on_success=on_login_success)
        apply(login)
        state["login"] = login
        # Same treatment as the dashboard so the two windows never open at
        # different sizes.
        login.showMaximized()

    splash.finished.connect(on_splash_done)
    splash.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())