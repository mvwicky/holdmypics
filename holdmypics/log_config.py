from __future__ import annotations

import logging
import logging.config
import sys
from pathlib import Path
from typing import Optional, Union, cast

import loguru
from flask import Flask, Response, request
from loguru import logger

from .utils import get_size, natsize


class InterceptHandler(logging.Handler):
    """Intercepts stdlib logging messages.

    From:
        loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        if frame is not None:
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
                if frame is None:
                    break
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def file_filter(record: loguru.Record) -> bool:
    return "log_request" not in record["function"]


def make_file_handler(
    log_dir: Path, file_name: str, fmt: str, max_size: int, level: Union[str, int]
) -> dict:
    log_file = log_dir.joinpath(file_name).with_suffix(".log")
    return {
        "sink": log_file,
        "rotation": max_size,
        "level": level,
        "compression": "tar.gz",
        "retention": 5,
        "filter": file_filter,
        "format": fmt,
    }


def config_logging(app: Flask) -> None:
    file_name: str = app.config.get("LOG_FILE_NAME") or app.name
    log_dir: Optional[Path] = app.config.get("LOG_DIR")
    log_level = cast(str, app.config.get("LOG_LEVEL"))
    max_log_size = cast(int, app.config.get("MAX_LOG_SIZE"))
    logging.config.dictConfig(
        {
            "version": 1,
            "handlers": {
                "intercept": {"class": "holdmypics.log_config.InterceptHandler"}
            },
            "root": {"handlers": ["intercept"], "level": "DEBUG"},
        }
    )
    try:
        logger.remove(0)
    except Exception:
        return
    fmt_parts = [
        # TODO: Change this to a locality test
        "" if log_dir is None else "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>]",
        "<level>{level:<8}</level>",
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>",
    ]
    fmt = " | ".join(filter(None, fmt_parts))
    handlers = [{"sink": sys.stderr, "format": fmt, "level": log_level}]
    if log_dir is not None:
        log_dir = Path(log_dir).resolve()
        if log_dir.is_dir():
            handlers.append(
                make_file_handler(log_dir, file_name, fmt, max_log_size, "DEBUG")
            )
    logger.configure(handlers=handlers)


def log_request(res: Response) -> None:
    code = res.status_code
    level = "WARNING" if code > 399 else "INFO"
    path = request.path
    if request.query_string:
        path = "?".join((path, request.query_string.decode()))
    addrs: str = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    addr = addrs.split(",")[-1].strip()
    content_length = res.headers.get("Content-Length", 0, type=int) or 0
    args = [request.method, res.status_code, path, natsize(content_length), addr]
    logger.log(level, "{0:7} {1:3d} {2} content-length={3} addr={4}", *args)


def log_static_file(path: str, url: str) -> None:
    try:
        size = natsize(get_size(path))
    except Exception:
        size = "<unknown>"
    logger.info("Static File {0} size={1}", url, size)
