import sounddevice as sd
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def get_input_devices() -> List[Dict]:
    """Returns a list of available input audio devices."""
    devices = []
    try:
        hostapis = sd.query_hostapis()
        device_info_list = sd.query_devices()
        for i, dev in enumerate(device_info_list):
            if dev['max_input_channels'] > 0:
                hostapi_name = hostapis[dev['hostapi']]['name']
                devices.append({
                    'index': i,
                    'name': f"{dev['name']} ({hostapi_name})",
                    'channels': dev['max_input_channels'],
                    'default_samplerate': dev['default_samplerate']
                })
    except Exception as e:
        logger.error(f"Error enumerating audio devices: {e}")
    return devices

def get_default_input_device() -> Optional[int]:
    """Returns the index of the default input device."""
    try:
        return sd.default.device[0]
    except Exception as e:
        logger.error(f"Error getting default input device: {e}")
        return None
