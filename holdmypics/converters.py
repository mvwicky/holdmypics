from werkzeug.routing import BaseConverter, ValidationError

from ._types import Dimension

COLOR_REGEX = r"(?:(?:[A-Fa-f0-9]{3}){1,2})"
RAND_REGEX = r"(?i:rand)"


class DimensionConverter(BaseConverter):
    regex = r"(?:\d+(?:x\d+)?)"

    def to_python(self, value: str) -> Dimension:
        parts = value.split("x")
        if len(parts) == 1:
            parts = parts * 2
        if len(parts) != 2:
            raise ValidationError
        if not all(p.isnumeric() for p in parts):
            raise ValidationError
        x, y = parts[:2]
        return int(x), int(y)

    def to_url(self, parts):
        return "x".join(super(DimensionConverter, self).to_url(p) for p in parts)


class ColorConverter(BaseConverter):
    regex = f"(?:{COLOR_REGEX}|{RAND_REGEX})"

    def to_python(self, value: str) -> str:
        return value
