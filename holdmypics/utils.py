from typing import Dict, List, Optional, Tuple, TypeVar

from flask import current_app
from funcy import merge

from .constants import bg_color_default, fg_color_default, fmt_default, img_formats_str

_T = TypeVar("_T")


def config_value(name: str, default: Optional[_T] = None) -> _T:
    return current_app.config.get(name, default)


def get_debug() -> bool:
    return config_value("DEBUG", False)


def make_rules() -> List[Tuple[str, Dict[str, str]]]:
    fmt_rule = f"<any({img_formats_str}):fmt>"
    colors_default = merge(bg_color_default, fg_color_default)
    return [
        (fmt_rule, colors_default),
        ("<string:bg_color>", merge(fg_color_default, fmt_default)),
        # ("<string:bg_color>/<string:fg_color>", fmt_default),
        (f"<string:bg_color>/{fmt_rule}", fg_color_default),
        (f"<string:bg_color>/<string:fg_color>/{fmt_rule}", {}),
    ]
