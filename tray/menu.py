import pystray
from PIL import Image, ImageDraw
import logging
from typing import Callable, Optional
from recognition.engine import engine
from config.constants import ASSETS_DIR

logger = logging.getLogger(__name__)

class TrayApp:
    def __init__(self, on_settings_clicked: Callable, on_exit_clicked: Callable):
        self.on_settings_clicked = on_settings_clicked
        self.on_exit_clicked = on_exit_clicked
        self.icon = None
        self._create_icon()

    def _create_icon_image(self):
        """Creates a simple fallback icon if none exists."""
        icon_path = ASSETS_DIR / "icon.ico"
        if icon_path.exists():
            return Image.open(icon_path)
            
        # Create a simple red/blue circular icon if no file
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        d = ImageDraw.Draw(image)
        d.ellipse((16, 16, 48, 48), fill=(255, 0, 0))
        return image

    def _create_icon(self):
        image = self._create_icon_image()
        
        # Define menu
        menu = pystray.Menu(
            pystray.MenuItem("Enable Voice Recognition", self.toggle_recognition, checked=lambda item: engine.is_running),
            pystray.MenuItem("Settings", self._on_settings),
            pystray.MenuItem("Exit", self._on_exit)
        )
        
        self.icon = pystray.Icon("VoiceClip", image, "VoiceClip", menu)
        # Double click default action
        self.icon.HAS_DEFAULT_ACTION = True
        # Set settings as default action (often triggered on double click)
        # Unfortunately pystray doesn't have a direct double click event on all platforms,
        # but setting a default action helps on Windows.

    def toggle_recognition(self, icon, item):
        if engine.is_running:
            engine.stop()
        else:
            engine.start()

    def _on_settings(self, icon, item):
        self.on_settings_clicked()

    def _on_exit(self, icon, item):
        engine.stop()
        self.icon.stop()
        self.on_exit_clicked()

    def run(self):
        if self.icon:
            logger.info("Starting System Tray Icon...")
            # Automatically start engine when tray app runs
            engine.start()
            self.icon.run()
