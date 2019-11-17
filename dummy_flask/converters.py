from werkzeug.routing import BaseConverter, ValidationError


class DimensionConverter(BaseConverter):
    regex = r"(?:\d+(?:x\d+)?)"

    def to_python(self, value):
        parts = value.split("x")
        if len(parts) == 1:
            parts = parts * 2
        if len(parts) != 2:
            raise ValidationError
        if not all(p.isnumeric() for p in parts):
            raise ValidationError
        return tuple(int(p) for p in parts)

    def to_url(self, parts):
        return "x".join(super(DimensionConverter, self).to_url(p) for p in parts)
