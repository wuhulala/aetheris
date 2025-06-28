import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

####################################
# Load .env file
####################################

try:
    from dotenv import load_dotenv, find_dotenv

    load_dotenv(find_dotenv("./.env"))
except ImportError:
    print("dotenv not installed, skipping...")

# Define log levels dictionary
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}
ROOT_DIR = Path(__file__).parent  # the path containing this file
AGENTS_DIR = os.getenv("AGENTS_DIR", "./agents")
ROOT_LOG = os.path.join(os.getenv("LOG_DIR_PATH", "logs"))
WORKSPACE_TYPE = os.environ.get("WORKSPACE_TYPE", "local")
WORKSPACE_PATH = os.environ.get("WORKSPACE_PATH", "./data/workspaces")


log_level = os.getenv("GLOBAL_LOG_LEVEL", "INFO").upper()

logging.basicConfig(level=LOG_LEVELS[log_level])
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_dir = ROOT_LOG
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, "aetheris.log")
    file_handler = TimedRotatingFileHandler(log_path, when='H', interval=1, backupCount=24)
    file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    error_log_path = os.path.join(log_dir, "aetheris_error.log")
    error_file_handler = TimedRotatingFileHandler(error_log_path, when='D', interval=1, backupCount=24)
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(error_file_handler)
setup_logging()
