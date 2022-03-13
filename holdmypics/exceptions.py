from __future__ import annotations


class HoldMyException(Exception):
    pass


class ImproperlyConfigured(HoldMyException):
    pass


class InvalidColor(ValueError, HoldMyException):
    def __init__(self, inp: str):
        super().__init__(f"Unable to create hex color from {inp!r}")
