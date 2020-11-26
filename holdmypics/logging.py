import os
import sys
from logging.config import dictConfig
from pathlib import Path
from typing import Optional

from flask import Request, Response, request
from loguru import logger

req: Request = request


def config_logging(name: str, file_name: str, log_dir: Optional[Path], log_level: str):
    dictConfig({"version": 1})
    try:
        logger.remove(0)
    except Exception:
        return
    fmt_parts = [
        "<level>{level:<8}</level>",
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>",
    ]
    if log_dir is not None:  # TODO: Change this to a locality test
        fmt_parts.insert(0, "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>]")
    fmt = " | ".join(fmt_parts)
    handlers = [{"sink": sys.stderr, "format": fmt, "level": log_level}]
    logger.add(sys.stderr, format=fmt, level=log_level, filter={"": True})
    if log_dir is not None:
        log_dir = Path(os.path.realpath(log_dir))
        if log_dir.is_dir():
            log_file = log_dir / ".".join([file_name, "log"])
            handlers.append(
                {
                    "sink": log_file,
                    "rotation": 3 * (1024 ** 2),
                    "level": "DEBUG",
                    "filter": {name: "DEBUG", "plugin": "DEBUG", "tests": "DEBUG"},
                    "compression": "tar.gz",
                    "retention": 5,
                }
            )
            # logger.add(
            #     log_file,
            #     rotation=3 * (1024 ** 2),
            #     level="DEBUG",
            #     filter={name: "DEBUG"},
            #     compression="tar.gz",
            #     retention=5,
            # )
    logger.configure(handlers=handlers)


def log_request(res: Response):
    code = res.status_code
    if code > 399:
        level = "WARNING"
    else:
        level = "INFO"
    path = req.path
    if req.query_string:
        path = "?".join([path, req.query_string.decode()])
    addrs: str = req.headers.get("X-Forwarded-For", req.remote_addr)
    addr = addrs.split(",")[-1].strip()
    content_length = res.headers.get("Content-Length", 0, type=int)
    msg = "{0} status={1} content-length={2:,} addr={3}"
    logger.log(level, msg, path, res.status_code, content_length, addr)
