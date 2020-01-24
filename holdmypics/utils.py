from typing import Any, Optional

from flask import current_app
from funcy import merge

from .constants import bg_color_default, fg_color_default, fmt_default, img_formats_str


def config_value(name: str, default: Optional[Any] = None):
    return current_app.config.get(name, default)


def get_debug():
    return config_value("DEBUG", False)


def make_rules():
    fmt_rule = f"<any({img_formats_str}):fmt>"
    colors_default = merge(bg_color_default, fg_color_default)
    rule_parts = [
        (fmt_rule, colors_default),
        ("<string:bg_color>", merge(fg_color_default, fmt_default)),
        # ("<string:bg_color>/<string:fg_color>", fmt_default),
        (f"<string:bg_color>/{fmt_rule}", fg_color_default),
        (f"<string:bg_color>/<string:fg_color>/{fmt_rule}", {}),
    ]
    return rule_parts
