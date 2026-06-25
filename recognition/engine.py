import json
import logging
import queue
import time
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from typing import Optional, Callable

from config.constants import get_model_path
from config.settings import app_settings
from hotkeys.sender import InputSender
from utils.feedback import play_success_sound

logger = logging.getLogger(__name__)

class RecognitionEngine:
    def __init__(self):
        self.model: Optional[Model] = None
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.last_trigger_time = 0.0
        self.text_buffer = ""
        self.last_text_time = 0.0
        self.stream: Optional[sd.RawInputStream] = None
        self.recognition_thread: Optional[threading.Thread] = None

    def initialize(self) -> bool:
        """Loads the Vosk model."""
        model_path = get_model_path(app_settings.general.model_language)
        if not model_path.exists():
            logger.error(f"Vosk model not found at {model_path}")
            return False
            
        try:
            logger.info(f"Loading Vosk model from {model_path}...")
            self.model = Model(str(model_path))
            logger.info("Vosk model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
            return False

    def start(self):
        """Starts listening to audio and running recognition."""
        if self.is_running:
            return

        if not self.model:
            if not self.initialize():
                logger.error("Cannot start recognition: Model not initialized.")
                return

        self.is_running = True
        self.audio_queue = queue.Queue()
        
        self.recognition_thread = threading.Thread(target=self._recognition_loop, daemon=True)
        self.recognition_thread.start()

    def stop(self):
        """Stops the audio stream and recognition loop."""
        self.is_running = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        # Unblock queue
        self.audio_queue.put(b"")

    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for sounddevice to push audio into queue."""
        if status:
            logger.warning(f"Audio status: {status}")
        self.audio_queue.put(bytes(indata))

    def _recognition_loop(self):
        """Main loop for processing audio with Vosk."""
        device_id = app_settings.audio.microphone_id
        samplerate = 16000
        
        # Build grammar based on our specific mappings
        mapping = app_settings.commands.mapping
        vocab = list(mapping.keys())
        # Provide a small grammar array to limit the recognizer strictly
        # We add some generic padding to make it a valid json list string
        grammar = json.dumps(vocab + ["[unk]"])
        
        recognizer = KaldiRecognizer(self.model, samplerate, grammar)

        try:
            with sd.RawInputStream(samplerate=samplerate, blocksize=8000, device=device_id,
                                dtype='int16', channels=1, callback=self._audio_callback) as self.stream:
                logger.info("Audio stream started.")
                
                while self.is_running:
                    data = self.audio_queue.get()
                    if not data:
                        continue
                        
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        text = result.get('text', '').strip()
                        if text:
                            logger.info(f"Recognized (AcceptWaveform): '{text}'")
                            self._handle_command(text)
                    else:
                        partial_result = json.loads(recognizer.PartialResult())
                        partial_text = partial_result.get('partial', '').strip()
                        # Some small models detect fast and trigger partials. 
                        # We mostly rely on AcceptWaveform, but if we need speed, we could parse partials too.
                        # For simplicity and stability, we stick to AcceptWaveform.
                        
        except Exception as e:
            logger.error(f"Recognition loop error: {e}")
        finally:
            self.is_running = False
            logger.info("Audio stream stopped.")

    def _handle_command(self, text: str):
        """Processes the recognized text, accumulating a buffer to handle delayed or out-of-order words."""
        current_time = time.time()
        
        # Clear buffer if older than 3 seconds
        if current_time - self.last_text_time > 3.0:
            self.text_buffer = text
        else:
            self.text_buffer += " " + text
            
        self.last_text_time = current_time
        
        mapping = app_settings.commands.mapping
        
        # Check buffer for commands, longer commands first
        for cmd, hotkey in sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True):
            cmd_words = set(cmd.split())
            buffer_words = set(self.text_buffer.split())
            
            # If all words of the command are in the buffer (handles out of order and delayed parts)
            if cmd_words.issubset(buffer_words):
                if current_time - self.last_trigger_time >= app_settings.audio.cooldown_seconds:
                    logger.info(f"Command '{cmd}' matches in buffer! Triggering hotkey: {hotkey}")
                    
                    success = InputSender.send_hotkey(hotkey)
                    if success:
                        self.last_trigger_time = current_time
                        play_success_sound()
                        # Clear buffer after successful trigger so it doesn't re-trigger
                        self.text_buffer = ""
                        return
                else:
                    logger.info(f"Command '{cmd}' ignored due to cooldown.")
                    
        logger.debug(f"Buffer '{self.text_buffer}' does not fully match any command yet.")

engine = RecognitionEngine()
