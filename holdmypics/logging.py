import os
import sys
from logging.config import dictConfig
from pathlib import Path
from typing import Optional

from flask import request, Response
from loguru import logger


def config_logging(name: str, file_name: str, log_dir: Optional[Path], log_level: str):
    dictConfig({"version": 1})
    logger.remove(0)
    fmt = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] | "
        "<level>{level:<8}</level> | "
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>"
    )
    handlers = [{"sink": sys.stderr, "format": fmt, "level": log_level}]
    logger.add(sys.stderr, format=fmt, level=log_level)
    if log_dir is not None:
        log_dir = Path(os.path.realpath(log_dir))
        if log_dir.is_dir():
            log_file = log_dir / (file_name + ".log")
            handlers.append(
                {
                    "sink": log_file,
                    "rotation": 3 * (1024 ** 2),
                    "level": "DEBUG",
                    "filter": {name: "DEBUG"},
                    "compression": "tar.gz",
                    "retention": 5,
                }
            )
            logger.add(
                log_file,
                rotation=3 * (1024 ** 2),
                level="DEBUG",
                filter={name: "DEBUG"},
                compression="tar.gz",
                retention=5,
            )
    # logger.configure(handlers=handlers)


def log_request(res: Response):
    code = res.status_code
    if code > 399:
        level = "WARNING"
    else:
        level = "INFO"
    path = request.path
    if request.query_string:
        path = "?".join([path, request.query_string.decode()])
    content_length = res.headers.get("Content-Length", 0)
    logger.log(level, f"{path} - {res.status_code} - {content_length}")
