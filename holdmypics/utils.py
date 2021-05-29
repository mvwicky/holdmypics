from __future__ import annotations

import math
import os
from functools import lru_cache
from typing import Optional, TypeVar, Union

from flask import Flask, current_app

from .constants import (
    COUNT_KEY,
    IMG_FORMATS_STR,
    UNSET,
    Unset,
    bg_color_default,
    fg_color_default,
    fmt_default,
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


def config_value(
    name: str, default: Union[_T, Unset] = UNSET, app: Optional[Flask] = None
) -> _T:
    if app is None:
        app = current_app
    value = app.config.get(name, default)
    if value is UNSET:
        raise ImproperlyConfigured("Unknown setting {0}".format(name))
    return value


def get_debug() -> bool:
    return config_value("DEBUG", False)


def make_rules() -> list[tuple[str, dict[str, str]]]:
    fmt_rule = f"<any({IMG_FORMATS_STR}):fmt>"
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


def get_count() -> int:
    from . import redisw

    count = redisw.client.get(COUNT_KEY)
    if count is not None:
        try:
            return int(count.decode())
        except ValueError:
            return 0
    return 0


@lru_cache(maxsize=128)
def get_size(path: str) -> int:
    return os.path.getsize(path)
