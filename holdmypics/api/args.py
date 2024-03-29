from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast

import marshmallow as ma
from attrs import astuple, define, evolve, field
from flask import request
from marshmallow import fields
from marshmallow.validate import Range, Regexp
from webargs.flaskparser import parser

from ..constants import DEFAULT_DPI, DEFAULT_FONT
from ..converters import ColorConverter
from .utils import resolve_color
from .words import words

truthy = fields.Boolean.truthy.union({""})
_col_regex = ColorConverter.regex


def clamp_alpha(a: float) -> float:
    return max(0.0, min(float(a), 1.0))


class BaseImageArgsSchema(ma.Schema):
    dpi = fields.Integer(missing=DEFAULT_DPI)
    seed = fields.String(missing=None)
    debug = fields.Boolean(missing=False, truthy=truthy)


class TextImageArgsSchema(BaseImageArgsSchema):
    text = fields.String(missing=None)
    font_name = fields.String(missing=DEFAULT_FONT, data_key="font")
    alpha = fields.Float(missing=1.0, validate=[Range(0.0, 1.0)])
    random_text = fields.Boolean(missing=False, truthy=truthy)

    @ma.post_load
    def make_args(self, data: Mapping[str, Any], **kwargs: Any) -> TextImageArgs:
        return TextImageArgs(**data).real_args()


class TiledImageArgsSchema(BaseImageArgsSchema):
    colors = fields.List(fields.String(validate=[Regexp(_col_regex)]), missing=list)
    alpha = fields.Float(missing=1.0, validate=[Range(0.0, 1.0)])
    col_major = fields.Boolean(missing=False, truthy=truthy)

    @ma.post_load
    def make_args(self, data: Mapping[str, Any], **kwargs: Any) -> TiledImageArgs:
        return TiledImageArgs(**data)


text_schema = TextImageArgsSchema()
tiled_schema = TiledImageArgsSchema()


@define(frozen=True)
class BaseImageArgs:
    dpi: int = DEFAULT_DPI
    seed: str | None = None
    debug: bool = False

    def to_seq(self) -> tuple[Any, ...]:
        return astuple(self)


@define(frozen=True)
class TextImageArgs(BaseImageArgs):
    text: str | None = None
    font_name: str = DEFAULT_FONT
    alpha: float = field(default=1.0, converter=clamp_alpha)
    random_text: bool = False

    @classmethod
    def from_request(cls: type[TextImageArgs]) -> TextImageArgs:
        args = parser.parse(text_schema, request, location="query")
        return cast(TextImageArgs, args)

    def real_args(self) -> TextImageArgs:
        if not self.random_text:
            return self
        else:
            text = f'{words.random("predicates")} {words.random("objects")}'
            return evolve(self, text=text)


def color_converter(inp: Any) -> Any:
    if not isinstance(inp, str) and isinstance(inp, Sequence):
        inp = [resolve_color(e) for e in inp]
    return inp


@define(frozen=True)
class TiledImageArgs(BaseImageArgs):
    colors: list[str] = field(factory=list, converter=color_converter)
    alpha: float = field(default=1.0, converter=clamp_alpha)
    col_major: bool = False

    @classmethod
    def from_request(cls: type[TiledImageArgs]) -> TiledImageArgs:
        args = parser.parse(tiled_schema, request, location="query")
        return cast(TiledImageArgs, args)

    def to_seq(self) -> tuple[Any, ...]:
        return astuple(evolve(self, colors="-".join(self.colors)))


@define(frozen=True)
class AnimArgs:
    frames: int = 10

    @classmethod
    def from_request(cls) -> AnimArgs:
        kw = {"frames": request.args.get("frames", 10, type=int)}
        return cls(**kw)
