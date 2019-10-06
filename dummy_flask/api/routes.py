import functools
from typing import Optional, Text

from flask import request, send_file

from .. import redis_client
from .._types import Dimension
from ..constants import COUNT_KEY
from ..utils import config_value, make_rules
from . import bp
from .utils import make_image


@functools.lru_cache(maxsize=1)
def image_response(
    size: Dimension,
    bg_color: Text,
    fg_color: Text = "#000",
    fmt: Text = "png",
    text: Optional[Text] = None,
    filename: Optional[Text] = None,
    font_name: Optional[Text] = None,
    dpi: int = 72,
):

    im = make_image(size, bg_color, fg_color, fmt, text, font_name, dpi)
    if filename is None:
        filename = "img-{0}-{1}.{2}".format(
            "x".join(map(str, size)), bg_color.replace("#", ""), fmt
        )
    if not filename.endswith("." + fmt):
        filename = ".".join([filename, fmt])
    return im


def make_route():
    rule_parts = make_rules()
    rules = []

    for part, defaults in rule_parts:
        rule = "/<dim:size>/" + part + "/"
        rules.append((rule, defaults))

    rules = [rules.pop()]

    def func(f):
        for rule, defaults in rules:
            bp.add_url_rule(rule, None, f, defaults=defaults)
        return f

    return func


@make_route()
def image_route(size, bg_color, fg_color, fmt):
    redis_client.incr(COUNT_KEY)
    cache_time = config_value("MAX_AGE", 0)
    text = request.args.get("text", None)
    filename = request.args.get("filename", None)
    font_name = request.args.get("font", "overpass")
    dpi = request.args.get("dpi", 72, type=int)

    path = image_response(
        size,
        bg_color,
        fg_color,
        fmt,
        text=text,
        filename=filename,
        font_name=font_name,
        dpi=dpi,
    )
    kw = {"cache_timeout": cache_time}

    if filename is not None:
        if not filename.endswith("." + fmt):
            filename = ".".join([filename, fmt])
        kw.update({"as_attachment": False, "attachment_filename": None})
    res = send_file(path, **kw)
    allow_origins = request.headers.get("Origin", "*")
    res.headers["Access-Control-Allow-Origin"] = allow_origins
    return res
