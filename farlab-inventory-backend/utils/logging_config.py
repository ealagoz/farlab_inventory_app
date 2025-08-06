# In utils/logging_config.py
import logging
import sys
from logging.handlers import RotatingFileHandler

# --- Configuration ---
LOG_LEVEL = "INFO"  # Set the default log level (e.g. DEBUG, INFO, WARNING)
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s- %(message)s"
LOG_FILE = "farlab_inventory.log"  # The name of the log file
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Number of backup log files to keep

# --- Formatter ---
# Create a formatter to standardize the log message format
formatter = logging.Formatter(LOG_FORMAT)

# --- Handlers ---
# 1. Console Handler: For printing logs to the console (useful for development)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# 2. File handler: For writing logs to a file
# RotatingFileHandler ensures that log files donot grow indefinetely
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT
)
file_handler.setFormatter(formatter)

# --- Logger Setup ---


def get_logger(name: str) -> logging.Logger:
    """"
    Creates and configures a logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    # Add handlers only if they havenot been added already
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
