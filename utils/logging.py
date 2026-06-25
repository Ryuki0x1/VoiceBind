import logging
import logging.handlers
from pathlib import Path
from config.constants import LOG_DIR
from config.settings import app_settings
from datetime import datetime

def setup_logging():
    log_file_name = f"{datetime.now().strftime('%Y-%m-%d')}.log"
    log_file_path = LOG_DIR / log_file_name

    level = logging.DEBUG if app_settings.general.debug_logging else logging.INFO

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # File Handler
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("Logging initialized.")
