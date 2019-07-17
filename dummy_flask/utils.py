from flask import current_app
from funcy import merge

from .constants import (
    bg_color_default,
    fg_color_default,
    fmt_default,
    img_formats,
)


def get_debug():
    return current_app.config.get("DEBUG", False)


def make_rules():
    fmt_rule = f"<any({img_formats}):fmt>"
    colors_default = merge(bg_color_default, fg_color_default)
    rule_parts = [
        ("<any(jpg,jpeg,gif,png):fmt>", colors_default),
        ("<string:bg_color>", merge(fg_color_default, fmt_default)),
        ("<string:bg_color>/<string:fg_color>", fmt_default),
        (f"<string:bg_color>/{fmt_rule}", fg_color_default),
        (f"<string:bg_color>/<string:fg_color>/{fmt_rule}", dict()),
    ]
    return rule_parts
