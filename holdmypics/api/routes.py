import random
import uuid
from typing import Callable
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import structlog
from flask import (
    Response,
    abort,
    after_this_request,
    current_app,
    redirect,
    request,
    send_file,
)
from funcy import merge
from PIL import features

from .._types import Dimension, ResponseType
from ..constants import FONT_NAMES, img_formats
from ..utils import make_rules
from . import bp
from .anim import make_anim
from .args import ImageArgs
from .files import files
from .img import make_image
from .utils import random_color

ViewFunc = Callable

logger = structlog.get_logger()

WEBP_ANIM = features.check_feature("webp_anim")
ANIM_FMTS = {"gif"}.union({"webp"} if WEBP_ANIM else set())
RAND_STR = "rand"


def image_response(size: Dimension, bg: str, fg: str, fmt: str, args: ImageArgs) -> str:
    return make_image(size, bg, fg, fmt, args)


def make_route(prefix: str = "") -> ViewFunc:
    rule_parts = make_rules()
    rules = []

    for part, defaults in rule_parts:
        rule = "/<dim:size>/" + part + "/"
        rules.append((rule, defaults))

    def func(f: ViewFunc) -> ViewFunc:
        for rule, defaults in rules:
            bp.add_url_rule(prefix + rule, None, f, defaults=defaults)
        return f

    return func


def do_cleanup(res: ResponseType) -> ResponseType:
    n = files.clean()
    if n > 0:
        current_app.logger.info("Cleaned %d file%s", n, "" if n == 1 else "s")
    return res


def font_redirect(font_name: str) -> ResponseType:
    if font_name.lower() in FONT_NAMES:
        parts = urlsplit(request.url)
        query = merge(parse_qs(parts.query), {"font": [font_name.lower()]})
        query_list = [(k, v) for k, v in query.items()]
        url = urlunsplit(parts._replace(query=urlencode(query_list, doseq=True)))
        return redirect(url)
    else:
        abort(400)


@make_route()
def image_route(
    size: Dimension, bg_color: str, fg_color: str, fmt: str
) -> ResponseType:
    log = logger.new(request_id=str(uuid.uuid4()))
    fmt = fmt.lower()
    if fmt not in img_formats:
        abort(400)
    args = ImageArgs.from_request()
    font_name = args.font_name
    if font_name not in FONT_NAMES:
        return font_redirect(font_name)

    bg_lower, fg_lower = map(str.lower, [bg_color, fg_color])  # type: str, str
    if RAND_STR in {bg_lower, fg_lower}:
        random.seed(args.seed)
        if bg_lower == RAND_STR:
            bg_color = random_color()
        if fg_lower == RAND_STR:
            fg_color = random_color()

    path = image_response(size, bg_color, fg_color, fmt, args)
    log.info("created image", size=size, fmt=fmt)
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
    res: Response = send_file(path, **kw)  # type: ignore
    return res


@make_route(prefix="anim")
def anim_route(size: Dimension, bg_color: str, fg_color: str, fmt: str) -> Response:
    if fmt not in ANIM_FMTS:
        abort(400)
    anim = make_anim(size, bg_color, fg_color, fmt)
    print(len(anim.getvalue()))

    return send_file(anim, mimetype=f"image/{fmt}")


@bp.route("/text")
def text_route() -> str:
    return "TEXT"
