import os
import sys
import winreg
import logging
from pathlib import Path
from config.settings import app_settings

logger = logging.getLogger(__name__)

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "VoiceClip"

def get_executable_path() -> str:
    """Returns the path to the current executable."""
    if getattr(sys, 'frozen', False):
        return sys.executable
    else:
        # If running from script, we use pythonw.exe to run without console
        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
        main_script = Path(__file__).resolve().parent.parent / "main.py"
        return f'"{python_exe}" "{main_script}"'

def is_startup_enabled() -> bool:
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return value == get_executable_path()
    except FileNotFoundError:
        return False
    except Exception as e:
        logger.error(f"Error checking startup registry key: {e}")
        return False

def enable_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_executable_path())
        winreg.CloseKey(key)
        logger.info("Added to Windows startup.")
    except Exception as e:
        logger.error(f"Failed to enable startup: {e}")

def disable_startup():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, winreg.KEY_SET_VALUE)
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        logger.info("Removed from Windows startup.")
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.error(f"Failed to disable startup: {e}")

def sync_startup_state():
    """Syncs the registry with the current settings."""
    if app_settings.general.start_with_windows:
        enable_startup()
    else:
        disable_startup()
