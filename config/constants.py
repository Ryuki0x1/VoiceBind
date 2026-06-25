import os
import sys
from pathlib import Path

# When frozen (PyInstaller):
#   DATA_DIR = sys._MEIPASS (where bundled files like models are extracted)
#   CONFIG_DIR = next to EXE (persistent user config/logs)
if getattr(sys, 'frozen', False):
    DATA_DIR = Path(sys._MEIPASS)
    CONFIG_DIR = Path(sys.executable).parent
else:
    DATA_DIR = Path(__file__).resolve().parent.parent
    CONFIG_DIR = DATA_DIR

APP_NAME = "VoiceClip"
VERSION = "1.0.0"

CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = CONFIG_DIR / "logs"
MODELS_DIR = DATA_DIR / "models"
ASSETS_DIR = DATA_DIR / "assets"

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Model Mappings
MODEL_FOLDERS = {
    "en-US": "vosk-model-small-en-us",
    "en-IN": "vosk-model-en-in-0.5"
}

def get_model_path(language: str) -> Path:
    folder_name = MODEL_FOLDERS.get(language, "vosk-model-small-en-us")
    return MODELS_DIR / folder_name
