import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings

LOG_DIR = "./logs"
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("taskmgr")

# Define o nível a partir do settings (DEBUG, INFO, WARNING...)
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))

# Evita adicionar handlers duplicados em modo reload do uvicorn
if not logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    # Console
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # Arquivo com rotação
    fh = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=2_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
