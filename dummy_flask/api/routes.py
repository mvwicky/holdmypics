import functools
import random
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from flask import abort, after_this_request, current_app, redirect, request, send_file
from funcy import merge

from .._types import Dimension
from ..constants import FONT_NAMES, img_formats
from ..utils import make_rules
from . import bp
from .files import files
from .image_args import ImageArgs
from .utils import make_image, random_color


RAND_STR = "rand".casefold()


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


def do_cleanup(res):
    n = files.clean()
    current_app.logger.info("Cleaned %d files", n)
    return res


# @bp.route("/rand/<dim:size>/")
# def random_image()


@make_route()
def image_route(size: Dimension, bg_color: str, fg_color: str, fmt: str):
    fmt = fmt.lower()
    if fmt not in img_formats:
        abort(403)
    args = ImageArgs.from_request()
    font_name = args.font_name
    if font_name not in FONT_NAMES and font_name.lower() in FONT_NAMES:
        parts = urlsplit(request.url)
        query = merge(parse_qs(parts.query), {"font": [font_name.lower()]})
        query_list = [(k, v) for k, v in query.items()]
        url = urlunsplit(parts._replace(query=urlencode(query_list, doseq=True)))
        return redirect(url)

    if RAND_STR in map(str.casefold, [bg_color, fg_color]):
        random.seed(args.seed)
        if bg_color.casefold() == RAND_STR:
            bg_color = random_color()
        if fg_color.casefold() == RAND_STR:
            fg_color = random_color()

    path = image_response(size, bg_color, fg_color, fmt, args)
    if files.need_to_clean:
        after_this_request(do_cleanup)

    mime_fmt = "jpeg" if fmt == "jpg" else fmt
    kw = {
        "mimetype": f"image/{mime_fmt}",
        "add_etags": not current_app.debug,
        "conditional": True,
    }

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
