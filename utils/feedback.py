import winsound
import logging
from config.settings import app_settings

logger = logging.getLogger(__name__)

def play_success_sound():
    if not app_settings.audio.audio_feedback_enabled:
        return

    try:
        # A simple chime: MB_ICONASTERISK (Information)
        winsound.MessageBeep(winsound.MB_ICONASTERISK)
    except Exception as e:
        logger.error(f"Failed to play success sound: {e}")
