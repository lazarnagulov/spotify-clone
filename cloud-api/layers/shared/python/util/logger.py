import os
import logging
from pythonjsonlogger.json import JsonFormatter

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()

logger = logging.getLogger()
logger.setLevel(getattr(logging, log_level, logging.INFO))

if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
    formatter = JsonFormatter(
        fmt='%(asctime)s %(levelname)s %(name)s %(message)s',
        json_ensure_ascii=False
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

logger.propagate = False
