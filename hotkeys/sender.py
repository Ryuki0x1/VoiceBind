import keyboard
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class InputSender:
    @staticmethod
    def send_hotkey(hotkey_str: str) -> bool:
        """
        Sends the specified hotkey sequence using the keyboard module.
        """
        if not hotkey_str:
            return False
            
        try:
            logger.info(f"Sending hotkey: {hotkey_str}")
            keyboard.send(hotkey_str)
            return True
        except Exception as e:
            logger.error(f"Failed to send hotkey '{hotkey_str}': {e}")
            return False

    @staticmethod
    def validate_hotkey(hotkey_str: str) -> bool:
        """
        Validates if the provided hotkey string can be parsed by the keyboard module.
        """
        if not hotkey_str:
            return False
        
        try:
            keyboard.parse_hotkey(hotkey_str)
            return True
        except ValueError:
            return False
