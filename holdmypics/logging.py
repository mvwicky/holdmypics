import os
import sys
from logging.config import dictConfig
from pathlib import Path
from typing import Optional

from loguru import logger


def config_logging(name: str, log_dir: Optional[Path], log_level):
    dictConfig({"version": 1})
    fmt = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] | "
        "<level>{level:<8}</level> | "
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>"
    )
    handlers = [{"sink": sys.stderr, "format": fmt, "level": log_level}]
    if log_dir is not None:
        log_dir = Path(os.path.realpath(log_dir))
        if log_dir.is_dir():
            log_file = log_dir / (name + ".log")
            handlers.append(
                {
                    "sink": log_file,
                    "rotation": 3 * (1024 ** 2),
                    "level": "DEBUG",
                    "filter": name,
                    "compression": "tar.gz",
                    "retention": 5,
                }
            )
    logger.configure(handlers=handlers)
