import time
from typing import Optional, Text, Tuple

from environs import Env
from flask import Flask, render_template, request
from flask_redis import FlaskRedis
from funcy import merge

from .converters import DimensionConverter
from .utils import make_image

env = Env()
env.read_env()

REDIS_URL = env("REDIS_URL")

app = Flask(__name__)
app.url_map.converters["dim"] = DimensionConverter
app.config["REDIS_URL"] = REDIS_URL
redis_client = FlaskRedis(app)

Dimension = Tuple[int, int]

cache_time = int(24 * 60 * 60)
fg_color_default = {"fg_color": "aaa"}
bg_color_default = {"bg_color": "000"}
fmt_default = {"fmt": "png"}
all_defaults = merge(fg_color_default, bg_color_default, fmt_default)
img_formats = ",".join(["jpg", "jpeg", "gif", "png", "webp"])


@app.before_request
def before_request_cb():
    request.start_time = time.monotonic()


@app.after_request
def after_request_db(res):
    res.header["X-Processed-Time"] = time.monotonic() - request.start_time


def image_response(
    size: Dimension,
    bg_color: Text,
    fg_color: Text = "#000",
    fmt: Text = "png",
    text: Optional[Text] = None,
    filename: Optional[Text] = None,
    font_name: Optional[Text] = None,
):
    im = make_image(size, bg_color, fg_color, fmt, text, font_name)
    if filename is None:
        filename = "img-{0}-{1}.{2}".format(
            "x".join(map(str, size)), bg_color.replace("#", ""), fmt
        )
    if not filename.endswith("." + fmt):
        filename = ".".join([filename, fmt])
    return (
        im.getvalue(),
        {
            "Content-Type": f"image/{fmt}",
            "Cache-Control": f"public, max-age={cache_time}",
        },
    )


def make_rules():
    fmt_rule = f"<any({img_formats}):fmt>"
    colors_default = merge(bg_color_default, fg_color_default)
    rule_parts = [
        ("<any(jpg,jpeg,gif,png):fmt>", colors_default),
        ("<string:bg_color>", merge(fg_color_default, fmt_default)),
        ("<string:bg_color>/<string:fg_color>", fmt_default),
        (f"<string:bg_color>/{fmt_rule}", fg_color_default),
        (f"<string:bg_color>/<string:fg_color>/{fmt_rule}", None),
    ]
    return rule_parts


def make_route():
    rule_parts = make_rules()
    rules = list()

    for part, defaults in rule_parts:
        rule = "/api/<dim:size>/" + part + "/"
        rules.append((rule, defaults))

    def func(f):
        for rule, defaults in rules:
            app.add_url_rule(rule, None, f, defaults=defaults)
        return f

    return func


@make_route()
def image_route(size, bg_color, fg_color, fmt):
    redis_client.incr("image_count")
    text = request.args.get("text", None)
    filename = request.args.get("filename")
    font_name = request.args.get("font")
    return image_response(
        size,
        bg_color,
        fg_color,
        fmt,
        text=text,
        filename=filename,
        font_name=font_name,
    )


@app.route("/")
def index():
    rule_parts = make_rules()
    count = redis_client.get("image_count")

    rules = [
        e[0].replace("string:", "").replace("any", "") for e in rule_parts
    ]

    kw = {
        "rules": ["api/<size>/" + r + "/" for r in rules],
        "count": count.decode(),
    }
    return render_template("base.jinja", **kw)
