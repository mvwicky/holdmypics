from __future__ import annotations

import math
from typing import TypeVar, Union

from flask import current_app

from .constants import (
    UNSET,
    Unset,
    bg_color_default,
    fg_color_default,
    fmt_default,
    img_formats_str,
)
from .exceptions import ImproperlyConfigured

try:
    from memory_profiler import profile
except ImportError:

    def profile(f=None):
        if f is None:

            def inner(f):
                return f

            return inner

        return f


_T = TypeVar("_T")


def config_value(name: str, default: Union[_T, Unset] = UNSET) -> _T:
    value = current_app.config.get(name, default)
    if value is UNSET:
        raise ImproperlyConfigured("Unknown setting {0}".format(name))
    return value


def get_debug() -> bool:
    return config_value("DEBUG", False)


def make_rules() -> list[tuple[str, dict[str, str]]]:
    fmt_rule = "<any({0}):fmt>".format(img_formats_str)
    colors_default = {**bg_color_default, **fg_color_default}
    bg_color, fg_color = "<col:bg_color>", "<col:fg_color>"

    return [
        (fmt_rule, colors_default),
        (bg_color, {**fg_color_default, **fmt_default}),
        ("/".join([bg_color, fmt_rule]), fg_color_default),
        ("/".join([bg_color, fg_color]), fmt_default),
        ("/".join([bg_color, fg_color, fmt_rule]), {}),
    ]


UNITS = ("B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def natsize(num: Union[float, int], fmt: str = "{0:.2f}") -> str:
    num = num * (-1 if num < 0 else 1)
    if num < 1:
        return " ".join([fmt.format(num), UNITS[0]])
    exp = min(math.floor(math.log10(num) / 3), len(UNITS) - 1)
    num = num / 1000 ** exp
    return " ".join([fmt.format(num), UNITS[exp]])
