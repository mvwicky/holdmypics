from __future__ import annotations

from typing import Any

from werkzeug.routing import BaseConverter, Map, UnicodeConverter, ValidationError

from .constants import RAND_COLOR

RGB_REGEX = r"(?:(?:[A-Fa-f0-9]{3}){1,2})"
RGBA_REGEX = r"(?:(?:[A-Fa-f0-9]{4}){1,2})"
COLOR_REGEX = f"(?:{RGB_REGEX}|{RGBA_REGEX})"
RAND_REGEX = f"(?i:{RAND_COLOR})"


class DimensionConverter(BaseConverter):
    regex = r"(?:\d+(?:x\d+)?)"

    def to_python(self, value: str) -> tuple[int, int]:
        parts = value.split("x")
        if len(parts) == 1:
            parts = parts * 2
        if len(parts) != 2:
            raise ValidationError("Dimension must be one or two numbers")
        try:
            return tuple(map(int, parts[:2]))
        except ValueError as exc:
            raise ValidationError() from exc

    def to_url(self, parts: Any) -> str:
        return "x".join(super(DimensionConverter, self).to_url(p) for p in parts)


class ColorConverter(UnicodeConverter):
    regex = f"^(?:{COLOR_REGEX}|{RAND_REGEX})$"

    def __init__(self, map: "Map", *args: Any, **kwargs: Any) -> None:
        super().__init__(map, 3, 8, None)

    def to_python(self, value: str) -> str:
        return value
