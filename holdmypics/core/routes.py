from __future__ import annotations

import functools
import re
from collections.abc import Iterable, Sequence
from typing import Any, TypedDict
from urllib.parse import urlencode

from flask import current_app, render_template, request, url_for
from markupsafe import Markup
from werkzeug.routing import Map, Rule

from .._types import ResponseType
from ..constants import DEFAULT_COLORS, DEFAULT_FONT, IMG_FORMATS
from ..fonts import fonts
from ..utils import config_value, get_count
from . import bp
from .forms import NumberInput, SelectInput, TextInput

RULE_RE = re.compile(r"(?:(?:dim|col):|any)")
ROBOTS = """User-agent: *
Disallow: /api/"""


class CommonContext(TypedDict):
    color_pattern: str
    width: int
    height: int
    max_width: int
    max_height: int
    img_dim: tuple[int, int]
    max_dim: tuple[int, int]
    num_fields: Sequence[NumberInput]
    fmt: str
    sel_fields: Sequence[SelectInput]


@functools.cache
def get_rules() -> list[str]:
    url_map: Map = current_app.url_map
    rules_iter: Iterable[Rule] = url_map.iter_rules(endpoint="api.image_route")
    return [RULE_RE.sub("", r.rule) for r in rules_iter]


def get_common_context(page: str) -> CommonContext:
    color_pattern = r"((([a-fA-F0-9]{3}){1,2})|(([a-fA-F0-9]{4}){1,2}))|rand"
    ns = page.upper()
    width = config_value(f"{ns}_DEFAULT_WIDTH", cast_as=int)
    height = config_value(f"{ns}_DEFAULT_HEIGHT", cast_as=int)
    max_width = config_value(f"{ns}_IMG_MAX_WIDTH", cast_as=int)
    max_height = config_value(f"{ns}_IMG_MAX_HEIGHT", cast_as=int)
    fmt = config_value(f"{ns}_DEFAULT_FORMAT", "png")

    num_kw = {"min": 1, "step": 1, "required": True}
    num_fields = [
        NumberInput(
            name="width", label="Width", value=width, max=max_width, **num_kw
        ).add_cy(),
        NumberInput(
            name="height", label="Height", value=height, max=max_height, **num_kw
        ).add_cy(),
    ]

    sel_fields = [
        SelectInput(
            name="fmt",
            label="Format",
            value=fmt,
            options=[(f, f) for f in IMG_FORMATS],
            help_text=Markup("<q>jpg</q> and <q>jpeg</q> are equivalent."),
        )
    ]

    return CommonContext(
        color_pattern=color_pattern,
        width=width,
        height=height,
        max_width=max_width,
        max_height=max_height,
        img_dim=(width, height),
        max_dim=(max_width, max_height),
        num_fields=num_fields,
        fmt=fmt,
        sel_fields=sel_fields,
    )


def get_index_context() -> dict[str, Any]:
    ctx = get_common_context("index")
    bg = config_value("INDEX_DEFAULT_BG", "cef")
    fg = config_value("INDEX_DEFAULT_FG", "555")
    text = config_value("INDEX_TEXT")
    font = DEFAULT_FONT
    img_url = url_for(
        "api.image_route", size=ctx["img_dim"], bg_color=bg, fg_color=fg, fmt=ctx["fmt"]
    )
    font_names: list[tuple[str, str]] = [
        ("", "None"),
        *((n, n.replace("-", " ").title()) for n in sorted(fonts.font_names)),
    ]
    col_kw = {
        "pattern": ctx["color_pattern"],
        "help_text": "Three, four, six, or eight hex digits.",
    }
    ctx["sel_fields"] = [
        *ctx["sel_fields"],
        SelectInput(
            name="font", value=font, options=font_names, label="Font", help_text=None
        ),
    ]

    return {
        **ctx,
        "rules": get_rules(),
        "img_url": img_url,
        "img_query": urlencode({"text": text, "font": font}),
        "bg_color": bg,
        "fg_color": fg,
        "text": text,
        "font_names": font_names,
        "img_formats": IMG_FORMATS,
        "font": font,
        "seed": None,
        "col_fields": [
            TextInput("bg", "Background Color", bg, **col_kw).add_cy(),
            TextInput("fg", "Text Color", fg, **col_kw).add_cy(),
        ],
        "title": "Hold My Pics",
    }


@functools.cache
def get_tiled_context() -> dict[str, Any]:
    ctx = get_common_context("tiled")
    cols = config_value("TILED_DEFAULT_COLUMNS", assert_is=int)
    rows = config_value("TILED_DEFAULT_ROWS", assert_is=int)
    num_kw = {"required": True, "min": 1, "step": 1}
    ctx["num_fields"] = [
        *ctx["num_fields"],
        NumberInput(name="cols", label="Columns", value=cols, **num_kw).add_cy(),
        NumberInput(name="rows", label="Rows", value=rows, **num_kw).add_cy(),
    ]
    return {**ctx, "cols": cols, "rows": rows}


def get_count_context():
    return {"count": f"{get_count():,}"}


@bp.route("/")
def index() -> ResponseType:
    context = {**get_index_context(), **get_count_context()}
    accept = request.accept_mimetypes
    if accept.accept_json and not accept.accept_html:
        return context
    else:
        return render_template("index.jinja", **context)


@bp.route("/tiled/")
def tiled() -> ResponseType:
    ctx = get_tiled_context()
    cols = ["".join(f"{c:02x}" for c in col) for col in DEFAULT_COLORS]
    kw = {"size": ctx["img_dim"], **{k: ctx[k] for k in ("cols", "rows", "fmt")}}
    img_url = url_for("api.tiled_route", **kw)
    context = {
        **ctx,
        **get_count_context(),
        "title": "Tiled",
        "img_url": img_url,
        "default_colors": ",".join(cols),
    }
    return render_template("tiled.jinja", **context)


@bp.route("/robots.txt")
def robots() -> ResponseType:
    headers = {"Content-Type": "text/plain", "Cache-Control": "public, max-age=86400"}
    return ROBOTS, 200, headers
