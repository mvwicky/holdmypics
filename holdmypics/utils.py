from __future__ import annotations

import math
import os
from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from typing import Any, Optional, TypeVar, Union, cast

from flask import Flask, current_app
from loguru import logger

from .constants import (
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
_AttVal = Union[str, bool, int, None]


def config_value(
    name: str,
    default: Union[_T, Unset] = UNSET,
    app: Optional[Flask] = None,
    cast_as: Optional[Callable[[Any], _T]] = None,
    assert_is: Optional[type[_T]] = None,
) -> _T:
    app = app if app is not None else current_app
    value = app.config.get(name, default)
    if value is UNSET:
        raise ImproperlyConfigured("Unknown setting {0}".format(name))
    if cast_as is not None:
        value = cast_as(value)
    if assert_is:
        if not isinstance(value, assert_is):
            raise ImproperlyConfigured(
                f"Expected {name} to be {assert_is} got {type(value)}"
            )
    logger.trace("Got config value. [key={0} value={1}]", name, value)
    return cast(Any, value)


def get_debug() -> bool:
    return config_value("DEBUG", False)


def make_rules() -> list[tuple[str, dict[str, str]]]:
    fmt_rule = f"<any({IMG_FORMATS_STR}):fmt>"
    colors_default = {**bg_color_default, **fg_color_default}
    bg_color, fg_color = "<col:bg_color>", "<col:fg_color>"

    return [
        (fmt_rule, colors_default),
        (bg_color, {**fg_color_default, **fmt_default}),
        ("/".join((bg_color, fmt_rule)), fg_color_default),
        ("/".join((bg_color, fg_color)), fmt_default),
        ("/".join((bg_color, fg_color, fmt_rule)), {}),
    ]


UNITS = ("B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")


def natsize(num: Union[float, int], fmt: str = "{0:.2f}") -> str:
    num = num * (-1 if num < 0 else 1)
    if num < 1:
        return f"{fmt.format(num)} {UNITS[0]}"
    exp = min(math.floor(math.log10(num) / 3), len(UNITS) - 1)
    num = num / 1000**exp
    return f"{fmt.format(num)} {UNITS[exp]}"


@lru_cache(maxsize=128)
def get_size(path: str) -> int:
    return os.path.getsize(path)


def flatatt(attrs: Union[Mapping[str, _AttVal], Sequence[tuple[str, _AttVal]]]) -> str:
    kv_attrs: list[tuple[str, Any]] = []
    bool_attrs: list[str] = []
    attrs_iter = attrs if not isinstance(attrs, Mapping) else attrs.items()
    for attr, value in attrs_iter:
        if isinstance(value, bool):
            if value:
                bool_attrs.append(attr)
        elif value is not None:
            kv_attrs.append((attr, value))
    return "".join(
        (
            "".join(f' {k}="{v}"' for k, v in sorted(kv_attrs)),
            "".join(f" {k}" for k in sorted(bool_attrs)),
        )
    )


def format_attrs(
    attrs: Union[Mapping[str, _AttVal], Sequence[tuple[str, _AttVal]]]
) -> str:
    attrs_iter = attrs if not isinstance(attrs, Mapping) else attrs.items()
    return flatatt([(k.replace("_", "-"), v) for k, v in attrs_iter])


def format_attrs_kw(**attrs: _AttVal) -> str:
    return flatatt([(k.replace("_", "-"), v) for (k, v) in attrs.items()])
