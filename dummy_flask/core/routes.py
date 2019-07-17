from urllib.parse import urlencode

from flask import render_template, url_for

from .. import redis_client
from ..hashed_file import HashedFile
from ..utils import make_rules
from ..constants import FONT_NAMES
from . import bp

style_file = HashedFile("styles.css", strip_newlines=False)
main_js = HashedFile("main.js", strip_newlines=False)


@bp.route("/")
def index():
    rule_parts = make_rules()
    count = redis_client.get("image_count")

    rules = [
        e[0].replace("string:", "").replace("any", "") for e in rule_parts
    ]

    width, height = 638, 328
    bg_color, fg_color = "cef", "555"
    fmt = "webp"
    text = "Something Funny"
    img_url = url_for(
        "api.image_route",
        size=(width, height),
        bg_color=bg_color,
        fg_color=fg_color,
        fmt=fmt,
    )
    img_query = urlencode({"text": text, "font": "overpass"})
    font_names = [(n, n.replace("-", " ").title()) for n in sorted(FONT_NAMES)]
    kw = {
        "rules": ["api/<size>/" + r + "/" for r in rules],
        "count": count.decode(),
        "styles": style_file.file_name,
        "main_js": main_js.file_name,
        "img_url": img_url,
        "img_query": img_query,
        "width": width,
        "height": height,
        "bg_color": bg_color,
        "fg_color": fg_color,
        "fmt": fmt,
        "text": text,
        "font_names": font_names,
    }
    return render_template("base.jinja", **kw)
