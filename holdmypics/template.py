from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING, Any

from loguru import logger

from .utils import format_attrs, format_attrs_kw

if TYPE_CHECKING:
    from flask import Flask


def format_attrs_ctx() -> dict[str, Any]:

    return {"format_attrs": format_attrs, "format_attrs_kw": format_attrs_kw}


def register(app: Flask, version: str) -> None:
    _version_ctx = partial(dict, version=version)

    app.context_processor(_version_ctx)
    app.context_processor(format_attrs_ctx)
    app.template_filter("fmt_attrs")(format_attrs)

    @app.template_filter("log")
    def _log_filter(inp: Any) -> str:
        logger.info("{0!r}", inp)
        return ""
