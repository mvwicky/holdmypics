from typing import Mapping, Optional

import attr
import marshmallow as ma
from flask import request
from werkzeug.datastructures import ImmutableMultiDict

from .words import words

truthy = set()


def clamp_alpha(a: float) -> float:
    return max(0.0, min(float(a), 1.0))


class ImageArgsSchema(ma.Schema):
    text = ma.fields.String(missing=None)
    font_name = ma.fields.String(missing="overpass")
    dpi = ma.fields.Integer(missing=72)
    alpha = ma.fields.Float(missing=1.0)
    seed = ma.fields.String(missing=None)
    debug = ma.fields.Boolean(missing=False, truthy=truthy)
    random_text = ma.fields.Boolean(missing=False, truthy=truthy)

    @ma.post_load
    def make_args(self, data, **kwargs):
        return ImageArgs(**data)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImageArgs(object):
    text: Optional[str] = None
    font_name: str = "overpass"
    dpi: int = 72
    alpha: float = attr.ib(default=1.0, converter=clamp_alpha)
    seed: Optional[str] = None
    debug: bool = False
    random_text: bool = False

    @classmethod
    def from_request(cls, args: Optional[Mapping] = None) -> "ImageArgs":
        if args is not None:
            args = ImmutableMultiDict(args)
        else:
            args: ImmutableMultiDict = request.args
        kw = {
            "text": args.get("text", None),
            "font_name": args.get("font", "overpass"),
            "dpi": args.get("dpi", 72, type=int),
            "alpha": args.get("alpha", 1.0, type=float),
            "seed": args.get("seed", None),
            "debug": args.get("debug", None) is not None,
            "random_text": args.get("random_text", None) is not None,
        }
        return cls(**kw)  # type: ignore

    def real_args(self):
        if self.random_text:
            text = " ".join([words.random("predicates"), words.random("objects")])
        else:
            text = self.text
        return attr.evolve(self, text=text)


@attr.s(slots=True, auto_attribs=True, frozen=True)
class AnimArgs(object):
    frames: int = 10

    @classmethod
    def from_request(cls) -> "AnimArgs":
        kw = {"frames": request.args.get("frames", 10, type=int)}
        return cls(**kw)
