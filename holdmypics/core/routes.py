import functools
import re
from urllib.parse import urlencode

from cytoolz import merge
from flask import Markup, render_template, request, url_for

from .. import redisw
from .._types import ResponseType
from ..constants import COUNT_KEY, img_formats
from ..fonts import fonts
from ..utils import config_value, make_rules
from . import bp

RULE_RE = re.compile(r"(?:col:|any)")
ROBOTS = """User-agent: *
Disallow: /api/"""


@functools.lru_cache(maxsize=2)
def get_context() -> dict:
    paths = (p for (p, _) in make_rules())
    rules = [RULE_RE.sub("", p) for p in paths]

    width, height = 638, 328
    max_width = config_value("INDEX_IMG_MAX_WIDTH")
    max_height = config_value("INDEX_IMG_MAX_HEIGHT")
    bg_color = config_value("INDEX_DEFAULT_BG", "cef")
    fg_color = config_value("INDEX_DEFAULT_FG", "555")
    fmt = config_value("INDEX_DEFAULT_FORMAT", "png")
    text = config_value("INDEX_TEXT")
    font = "overpass"
    img_url = url_for(
        "api.image_route",
        size=(width, height),
        bg_color=bg_color,
        fg_color=fg_color,
        fmt=fmt,
    )

    color_pattern = r"(([a-fA-F0-9]{3})|([a-fA-F0-9]{6}))|rand"
    img_query = urlencode({"text": text, "font": font})
    font_names = [(n, n.replace("-", " ").title()) for n in sorted(fonts.font_names)]
    num_fields = {"width": width, "height": height}
    col_fields = {
        "bg": {"value": bg_color, "label": "Background Color"},
        "fg": {"value": fg_color, "label": "Text Color"},
    }
    fmt_help = Markup("<q>jpg</q> and <q>jpeg</q> are equivalent.")
    sel_fields = {
        "fmt": {
            "value": fmt,
            "options": [(f, f) for f in img_formats],
            "label": "Format",
            "help_text": fmt_help,
        },
        "font": {"value": font, "options": font_names, "label": "Font"},
    }

    ofl_license = url_for("static", filename="licenses/ofl.txt")
    apache_license = url_for("static", filename="licenses/apache.txt")

    return {
        "rules": ["api/<size>/" + r + "/" for r in rules],
        "img_url": img_url,
        "img_query": img_query,
        "width": width,
        "height": height,
        "bg_color": bg_color,
        "fg_color": fg_color,
        "fmt": fmt,
        "text": text,
        "font_names": font_names,
        "img_formats": img_formats,
        "font": font,
        "seed": None,
        "color_pattern": color_pattern,
        "num_fields": num_fields,
        "col_fields": col_fields,
        "sel_fields": sel_fields,
        "title": "Hold My Pics",
        "img_dim": (width, height),
        "ofl_license": ofl_license,
        "apache_license": apache_license,
        "max_width": max_width,
        "max_height": max_height,
    }


@bp.route("/")
def index() -> ResponseType:
    get_context.cache_clear()
    count = redisw.client.get(COUNT_KEY)
    if count is not None:
        try:
            count = int(count.decode())
        except ValueError:
            count = 0
    else:
        count = 0
    context = merge(get_context(), {"count": f"{count:,}"})
    accept = request.accept_mimetypes
    if accept.accept_json and not accept.accept_html:
        return context
    else:
        return render_template("index.jinja", **context)


@bp.route("/robots.txt")
def robots() -> ResponseType:
    headers = {"Content-Type": "text/plain", "Cache-Control": "public, max-age=86400"}
    return ROBOTS, 200, headers
