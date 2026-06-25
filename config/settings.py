import json
import logging
from pydantic import BaseModel, Field
from typing import Dict, Optional
from config.constants import CONFIG_FILE

logger = logging.getLogger(__name__)

class CommandSettings(BaseModel):
    mapping: Dict[str, str] = Field(default_factory=lambda: {
        "clip thirty": "ctrl+alt+shift+1",
        "clip one minute": "ctrl+alt+shift+2",
        "clip two minutes": "ctrl+alt+shift+3",
        "clip three minutes": "ctrl+alt+shift+4"
    })

class AudioSettings(BaseModel):
    microphone_id: Optional[int] = Field(default=None)
    cooldown_seconds: float = Field(default=2.0)
    audio_feedback_enabled: bool = Field(default=True)

class GeneralSettings(BaseModel):
    start_with_windows: bool = Field(default=False)
    minimize_to_tray: bool = Field(default=True)
    debug_logging: bool = Field(default=False)
    model_language: str = Field(default="en-US")
    setup_completed: bool = Field(default=False)

class AppSettings(BaseModel):
    commands: CommandSettings = Field(default_factory=CommandSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    general: GeneralSettings = Field(default_factory=GeneralSettings)

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write(self.model_dump_json(indent=4))
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    @classmethod
    def load(cls) -> "AppSettings":
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Migrate old commands format to mapping if necessary
                    if "commands" in data and "clip_thirty" in data["commands"]:
                        # Old format detected, convert to new
                        old_cmds = data["commands"]
                        data["commands"] = {
                            "mapping": {
                                "clip thirty": old_cmds.get("clip_thirty", "ctrl+alt+shift+1"),
                                "clip one minute": old_cmds.get("clip_one_minute", "ctrl+alt+shift+2"),
                                "clip two minutes": old_cmds.get("clip_two_minutes", "ctrl+alt+shift+3"),
                                "clip three minutes": old_cmds.get("clip_three_minutes", "ctrl+alt+shift+4")
                            }
                        }
                    return cls.model_validate(data)
            except Exception as e:
                logger.error(f"Failed to load config, using defaults. Error: {e}")
        
        # Save defaults if file doesn't exist or failed to load
        settings = cls()
        settings.save()
        return settings

# Global settings instance
app_settings = AppSettings.load()
