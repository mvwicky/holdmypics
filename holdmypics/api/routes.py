from __future__ import annotations

import mimetypes
import random
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from flask import (
    Response,
    abort,
    after_this_request,
    current_app,
    redirect,
    request,
    send_file,
)
from loguru import logger
from PIL import features

from holdmypics.api.base import BaseGeneratedImage
from .. import redisw
from .._types import ResObject, ResponseType
from ..constants import IMG_FORMATS, IMG_FORMATS_STR, NO_CACHE
from ..fonts import fonts
from ..utils import make_rules
from . import bp
from .anim import make_anim
from .args import TextImageArgs, TiledImageArgs
from .files import files
from .text import GeneratedTextImage
from .tiled import GeneratedTiledImage
from .utils import RAND_COLOR

WEBP_ANIM = features.check_feature("webp_anim")
ANIM_FMTS = {"gif"}.union({"webp"} if WEBP_ANIM else set())


def make_route(prefix: str = "") -> Callable:
    rule_parts = make_rules()
    rules: list[tuple[str, dict[str, Any]]] = []

    for part, defaults in rule_parts:
        rules.append((f"/<dim:size>/{part}/", defaults))

    def func(f: Callable[..., ResponseType]) -> Callable[..., ResponseType]:
        for rule, defaults in rules:
            bp.add_url_rule(f"{prefix}{rule}", None, f, defaults=defaults)
        return f

    return func


def do_cleanup(res: Response) -> Response:
    n = files.clean()
    if n > 0:
        logger.info("Removed {0} file{1}", n, "" if n == 1 else "s")
    return res


def font_redirect(font_name: str) -> ResponseType:
    if font_name.lower() in fonts.font_names:
        parts = urlsplit(request.url)
        query = {**parse_qs(parts.query), "font": [font_name.lower()]}
        query_list = [(k, v) for k, v in query.items()]
        url = urlunsplit(parts._replace(query=urlencode(query_list, doseq=True)))
        return redirect(url)
    else:
        logger.warning("Unknown font: `{0}`", font_name)
        abort(400)


def check_size(size: tuple[int, int]) -> None:
    if not all(size):
        logger.warning("Invalid size: {0}", size)
        abort(400)


def check_format(fmt: str) -> str:
    fmt = fmt.lower()
    if fmt not in IMG_FORMATS:
        logger.warning("Unknown format: `{0}`", fmt)
        abort(400)
    return fmt


def get_send_file_kwargs(path: str) -> dict[str, Any]:
    mime = mimetypes.guess_type(path)[0]
    return {"mimetype": mime, "etag": not current_app.debug, "conditional": True}


@bp.route("/count/")
def count_route():
    return {"count": redisw.get_count()}


@bp.route("/stats/")
def stats_route():
    return {"count": redisw.get_count(), "size": redisw.get_size()}


def get_img_response(img: BaseGeneratedImage) -> ResObject:
    path = img.get_path()
    if files.need_to_clean:
        after_this_request(do_cleanup)
    kw = get_send_file_kwargs(path)
    return send_file(path, **kw)


@make_route()
def image_route(
    size: tuple[int, int], bg_color: str, fg_color: str, fmt: str
) -> ResponseType:
    check_size(size)
    fmt = check_format(fmt)
    args = TextImageArgs.from_request()
    if args.font_name not in fonts.font_names:
        return font_redirect(args.font_name)

    bg_lower, fg_lower = map(str.casefold, (bg_color, fg_color))
    if RAND_COLOR in {bg_lower, fg_lower}:
        random.seed(args.seed)

    img = GeneratedTextImage(size, fmt, bg_color, fg_color, args)
    res = get_img_response(img)
    if args.random_text or RAND_COLOR in {bg_lower, fg_lower}:
        res.headers["Cache-Control"] = NO_CACHE
    if args.random_text and args.text:
        res.headers["X-Random-Text"] = args.text

    return res


@make_route(prefix="anim")
def anim_route(
    size: tuple[int, int], bg_color: str, fg_color: str, fmt: str
) -> ResponseType:
    check_size(size)
    if fmt not in ANIM_FMTS:
        abort(400)
    anim = make_anim(size, bg_color, fg_color, fmt)
    print(len(anim.getvalue()))

    return send_file(anim, mimetype=f"image/{fmt}")


@bp.route("/text")
def text_route() -> str:
    return "TEXT"


@bp.route(f"/tiled/<dim:size>/<int:cols>/<int:rows>/<any({IMG_FORMATS_STR}):fmt>/")
def tiled_route(size: tuple[int, int], cols: int, rows: int, fmt: str) -> ResponseType:
    check_size(size)
    fmt = check_format(fmt)
    args = TiledImageArgs.from_request()
    img = GeneratedTiledImage(size, fmt, "0000", "0000", args, cols, rows)
    res = get_img_response(img)
    res.headers["Cache-Control"] = NO_CACHE

    return res
