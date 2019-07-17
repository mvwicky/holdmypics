from flask import render_template

from . import bp
from ..utils import make_rules, style_file
from .. import redis_client


@bp.route("/")
def index():
    rule_parts = make_rules()
    count = redis_client.get("image_count")

    rules = [
        e[0].replace("string:", "").replace("any", "") for e in rule_parts
    ]

    kw = {
        "rules": ["api/<size>/" + r + "/" for r in rules],
        "count": count.decode(),
        "styles": style_file.file_name,
    }
    return render_template("base.jinja", **kw)
