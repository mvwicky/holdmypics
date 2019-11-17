import functools
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from flask import redirect, request, send_file
from funcy import merge

from .. import redis_client
from .._types import Dimension
from ..constants import COUNT_KEY, FONT_NAMES
from ..utils import config_value, make_rules
from . import bp
from .image_args import ImageArgs
from .utils import make_image


@functools.lru_cache()
def image_response(size: Dimension, bg: str, fg: str, fmt: str, args: ImageArgs):
    return make_image(size, bg, fg, fmt, args)


def make_route(prefix: str = ""):
    rule_parts = make_rules()
    rules = []

    for part, defaults in rule_parts:
        rule = "/<dim:size>/" + part + "/"
        rules.append((rule, defaults))

    def func(f):
        for rule, defaults in rules:
            bp.add_url_rule(prefix + rule, None, f, defaults=defaults)
        return f

    return func


@make_route()
def image_route(size: Dimension, bg_color: str, fg_color: str, fmt: str):
    redis_client.incr(COUNT_KEY)
    cache_time = config_value("MAX_AGE", 0)

    args = ImageArgs.from_request()
    font_name = args.font_name
    if font_name not in FONT_NAMES and font_name.lower() in FONT_NAMES:
        parts = urlsplit(request.url)
        query = merge(parse_qs(parts.query), {"font": [font_name.lower()]})
        query_list = [(k, v) for k, v in query.items()]
        url = urlunsplit(parts._replace(query=urlencode(query_list, doseq=True)))
        return redirect(url)

    path = image_response(size, bg_color, fg_color, fmt, args)
    mime_fmt = "jpeg" if fmt == "jpg" else fmt
    kw = {"cache_timeout": cache_time, "mimetype": f"image/{mime_fmt}"}

    filename = args.filename
    if filename is not None:
        if not filename.endswith("." + fmt):
            filename = ".".join([filename, fmt])
        kw.update({"as_attachment": False, "attachment_filename": None})
    res = send_file(path, **kw)
    # allow_origins = request.headers.get("Origin", "*")
    # res.headers["Access-Control-Allow-Origin"] = allow_origins
    return res


@make_route(prefix="anim")
def anim_route(size: Dimension, bg_color: str, fg_color: str, fmt: str):
    return "ANIM"


@bp.route("/text")
def text_route():
    return "TEXT"
