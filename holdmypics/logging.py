from __future__ import annotations

import sys
from logging.config import dictConfig
from pathlib import Path
from typing import Optional

import loguru
from flask import Request, Response, request
from loguru import logger

req: Request = request

MAX_LOG_SIZE = 1 * (1024 ** 2)


def file_filter(record: loguru.Record) -> bool:
    return "log_request" not in record["function"]


def make_file_handler(log_dir: Path, file_name: str, fmt: str) -> dict:
    log_file = log_dir.joinpath(file_name).with_suffix(".log")
    return {
        "sink": log_file,
        "rotation": MAX_LOG_SIZE,
        "level": "DEBUG",
        "compression": "tar.gz",
        "retention": 5,
        "filter": file_filter,
        "format": fmt,
    }


def config_logging(
    name: str, file_name: str, log_dir: Optional[Path], log_level: str
) -> None:
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
    if log_dir is not None:
        log_dir = Path(log_dir).resolve()
        if log_dir.is_dir():
            handlers.append(make_file_handler(log_dir, file_name, fmt))
    logger.configure(handlers=handlers)


def log_request(res: Response) -> None:
    code = res.status_code
    level = "WARNING" if code > 399 else "INFO"
    path = req.path
    if req.query_string:
        path = "?".join([path, req.query_string.decode()])
    addrs: str = req.headers.get("X-Forwarded-For", req.remote_addr)
    addr = addrs.split(",")[-1].strip()
    content_length = res.headers.get("Content-Length", 0, type=int)
    msg = "{0:7} {1:3d} {2} content-length={3:,} addr={4}"
    args = [req.method, res.status_code, path, content_length, addr]
    logger.log(level, msg, *args)
