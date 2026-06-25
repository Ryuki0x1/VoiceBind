import sys
import logging
import threading
import time

from utils.logging import setup_logging
from config.constants import get_model_path
from tray.menu import TrayApp
from recognition.engine import engine
from config.settings import app_settings
from utils.startup import sync_startup_state
from ui.settings_window import open_settings_window

logger = logging.getLogger(__name__)

class AppManager:
    def __init__(self):
        self.tray_app = None

    def show_settings(self, setup_mode=False):
        logger.info("Opening settings window...")
        threading.Thread(target=open_settings_window, kwargs={"setup_mode": setup_mode}, daemon=True).start()

    def exit_app(self):
        logger.info("Exiting application...")
        engine.stop()
        time.sleep(0.5)
        sys.exit(0)

    def run(self):
        logger.info("Starting VoiceClip Application...")
        sync_startup_state()

        if not app_settings.general.setup_completed:
            logger.info("First run detected. Opening setup...")
            threading.Timer(1.0, self.show_settings, kwargs={"setup_mode": True}).start()
        else:
            model_path = get_model_path(app_settings.general.model_language)
            if not model_path.exists():
                logger.warning(f"Vosk model not found at {model_path}.")
                threading.Timer(1.0, self.show_settings).start()

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
    
    # We should run the app manager
    manager = AppManager()
    manager.run()
