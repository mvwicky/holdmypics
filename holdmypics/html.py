from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

_AttVal = str | bool | int | None
_Attrs = Mapping[str, _AttVal] | Sequence[tuple[str, _AttVal]]

# def to_html_attrib()
#


def _to_iter(inp: _Attrs) -> Iterable[tuple[str, _AttVal]]:
    return inp if not isinstance(inp, Mapping) else inp.items()


def flatatt(attrs: _Attrs) -> str:
    kv_attrs: list[tuple[str, Any]] = []
    bool_attrs: list[str] = []
    for attr, value in _to_iter(attrs):
        if isinstance(value, bool):
            if value:
                bool_attrs.append(attr)
        elif value is not None:
            kv_attrs.append((attr, value))
    "".join(f" {k}" for k, v in sorted(kv_attrs))
    return "".join(
        (
            "".join(f' {k}="{v}"' for k, v in sorted(kv_attrs)),
            "".join(f" {k}" for k in sorted(bool_attrs)),
        )
    )


def format_attrs(attrs: _Attrs) -> str:
    return flatatt([(k.replace("_", "-"), v) for k, v in _to_iter(attrs)])


def format_attrs_kw(**attrs: _AttVal) -> str:
    return flatatt([(k.replace("_", "-"), v) for (k, v) in attrs.items()])
