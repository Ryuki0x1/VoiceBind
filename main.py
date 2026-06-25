import sys
import logging
import threading
import time
import subprocess
import ctypes

from utils.logging import setup_logging
from config.constants import get_model_path
from tray.menu import TrayApp
from recognition.engine import engine
from config.settings import app_settings
from utils.startup import sync_startup_state

logger = logging.getLogger(__name__)

MUTEX_NAME = "VoiceClip-{B8A7C3D1-2E4F-4A8C-9B6D-7E1F0A2C3D4E}"


def _already_running():
    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if not mutex:
        return True
    return kernel32.GetLastError() == 183


class AppManager:
    def __init__(self):
        self.tray_app = None

    def _exe_path(self):
        if getattr(sys, 'frozen', False):
            return sys.argv[0]
        return [sys.executable, __file__]

    def show_settings(self, setup_mode=False):
        logger.info("Opening settings window...")
        args = self._exe_path()
        if not isinstance(args, list):
            args = [args]
        args.append("--settings")
        if setup_mode:
            args.append("--setup")
        subprocess.Popen(args, creationflags=subprocess.DETACHED_PROCESS)

    def exit_app(self):
        logger.info("Exiting application...")
        engine.stop()
        time.sleep(0.5)
        sys.exit(0)

    def run(self):
        logger.info("Starting VoiceClip Application...")
        sync_startup_state()
        engine.start()

        self.tray_app = TrayApp(
            on_settings_clicked=self.show_settings,
            on_exit_clicked=self.exit_app
        )

        try:
            self.tray_app.run()
        except KeyboardInterrupt:
            self.exit_app()


if __name__ == "__main__":
    setup_logging()

    if "--settings" in sys.argv:
        from ui.settings_window import open_settings_window
        open_settings_window(setup_mode="--setup" in sys.argv)
        sys.exit(0)

    if _already_running():
        logger.warning("VoiceClip is already running. Opening settings...")
        subprocess.Popen(
            [sys.executable, sys.argv[0], "--settings"],
            creationflags=subprocess.DETACHED_PROCESS
        )
        sys.exit(0)

    if not app_settings.general.setup_completed:
        logger.info("First run detected. Opening setup...")
        from ui.settings_window import open_settings_window
        open_settings_window(setup_mode=True)

    manager = AppManager()
    manager.run()
