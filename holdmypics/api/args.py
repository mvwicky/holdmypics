from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional

import attr
import marshmallow as ma
from flask import request
from marshmallow.validate import Range
from webargs.flaskparser import parser

from ..constants import DEFAULT_FONT
from .words import words

truthy = set()


def clamp_alpha(a: float) -> float:
    return max(0.0, min(float(a), 1.0))


class BaseImageArgsSchema(ma.Schema):
    dpi = ma.fields.Integer(missing=72)
    seed = ma.fields.String(missing=None)
    debug = ma.fields.Boolean(missing=False, truthy=truthy)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class BaseImageArgs(object):
    dpi: int = 72
    seed: Optional[str] = None
    debug: bool = False

    def to_seq(self) -> tuple[Any, ...]:
        return attr.astuple(self)


class ImageArgsSchema(BaseImageArgsSchema):
    text = ma.fields.String(missing=None)
    font_name = ma.fields.String(missing=DEFAULT_FONT)
    alpha = ma.fields.Float(missing=1.0, validate=[Range(0.0, 1.0)])
    random_text = ma.fields.Boolean(missing=False, truthy=truthy)

    @ma.post_load
    def make_args(self, data: Mapping[str, Any], **kwargs: Any) -> "ImageArgs":
        return ImageArgs(**data)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImageArgs(BaseImageArgs):
    text: Optional[str] = None
    font_name: str = DEFAULT_FONT
    alpha: float = attr.ib(default=1.0, converter=clamp_alpha)
    random_text: bool = False

    @classmethod
    def from_request(
        cls: type["ImageArgs"], args: Optional[Mapping[str, Any]] = None
    ) -> "ImageArgs":
        return parser.parse(ImageArgsSchema(), request, location="query")

    def real_args(self) -> "ImageArgs":
        if not self.random_text:
            return self
        else:
            text = " ".join([words.random("predicates"), words.random("objects")])
            return attr.evolve(self, text=text)


class TiledImageArgsSchema(BaseImageArgsSchema):
    colors = ma.fields.List(ma.fields.String(), missing=list)
    alpha = ma.fields.Float(missing=1.0, validate=[Range(0.0, 1.0)])

    @ma.post_load
    def make_args(self, data: Mapping[str, Any], **kwargs: Any) -> "TiledImageArgs":
        return TiledImageArgs(**data)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class TiledImageArgs(BaseImageArgs):
    colors: list[str] = attr.ib(factory=list)
    alpha: float = attr.ib(default=1.0, converter=clamp_alpha)

    text: None = attr.ib(default=None, init=False)

    @classmethod
    def from_request(cls: type["TiledImageArgs"]) -> "TiledImageArgs":
        return parser.parse(TiledImageArgsSchema(), request, location="query")

    def to_seq(self) -> tuple[Any, ...]:
        return attr.astuple(attr.evolve(self, colors="-".join(self.colors)))


@attr.s(slots=True, auto_attribs=True, frozen=True)
class AnimArgs(object):
    frames: int = 10

    @classmethod
    def from_request(cls) -> "AnimArgs":
        kw = {"frames": request.args.get("frames", 10, type=int)}
        return cls(**kw)
