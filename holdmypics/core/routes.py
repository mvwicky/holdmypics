from urllib.parse import urlencode

from flask import Markup, render_template, url_for

from .. import redisw  # redis_client
from ..constants import COUNT_KEY, FONT_NAMES, img_formats
from ..utils import make_rules
from . import bp


def get_context():
    rule_parts = make_rules()
    count = redisw.client.get(COUNT_KEY)

    rules = [e[0].replace("string:", "").replace("any", "") for e in rule_parts]

    width, height = 638, 328
    bg_color, fg_color = "cef", "555"
    fmt = "png"
    text = "Something Funny"
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
    font_names = [(n, n.replace("-", " ").title()) for n in sorted(FONT_NAMES)]
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

    return {
        "rules": ["api/<size>/" + r + "/" for r in rules],
        "count": count.decode(),
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
    }


@bp.route("/")
def index():
    return render_template("base-out.html", **get_context())


# @bp.route("/grid/")
# def grid():
#     return render_template("grid.jinja", **get_context())
