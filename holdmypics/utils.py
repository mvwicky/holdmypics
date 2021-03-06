from typing import Dict, List, Tuple, TypeVar, Union

from cytoolz import merge
from flask import current_app

from .constants import bg_color_default, fg_color_default, fmt_default, img_formats_str
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

_UNSET = object()


def config_value(name: str, default: Union[_T, object] = _UNSET) -> _T:
    value = current_app.config.get(name, default)
    if value is _UNSET:
        raise ImproperlyConfigured("Unknown setting {0}".format(name))
    return value


def get_debug() -> bool:
    return config_value("DEBUG", False)


def make_rules() -> List[Tuple[str, Dict[str, str]]]:
    fmt_rule = "<any({0}):fmt>".format(img_formats_str)
    colors_default = merge(bg_color_default, fg_color_default)
    bg_color = "<col:bg_color>"
    fg_color = "<col:fg_color>"

    return [
        (fmt_rule, colors_default),
        (bg_color, merge(fg_color_default, fmt_default)),
        ("/".join([bg_color, fmt_rule]), fg_color_default),
        ("/".join([bg_color, fg_color]), fmt_default),
        ("/".join([bg_color, fg_color, fmt_rule]), {}),
    ]
