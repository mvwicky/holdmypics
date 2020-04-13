from typing import Mapping, Optional

import attr
from flask import request
from werkzeug.datastructures import ImmutableMultiDict


def clamp_alpha(a: float) -> float:
    return max(0.0, min(float(a), 1.0))


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImageArgs(object):
    text: Optional[str] = None
    filename: Optional[str] = None
    font_name: str = "overpass"
    dpi: int = 72
    alpha: float = attr.ib(default=1.0, converter=clamp_alpha)
    seed: Optional[str] = None
    debug: bool = False

    @classmethod
    def from_request(cls, args: Optional[Mapping] = None) -> "ImageArgs":
        if args is not None:
            args = ImmutableMultiDict(args)
        else:
            args: ImmutableMultiDict = request.args
        kw = {
            "text": args.get("text", None),
            "filename": args.get("filename", None),
            "font_name": args.get("font", "overpass"),
            "dpi": args.get("dpi", 72, type=int),
            "alpha": args.get("alpha", 1.0, type=float),
            "seed": args.get("seed", None),
            "debug": args.get("debug", None) is not None,
        }
        return cls(**kw)  # type: ignore


@attr.s(slots=True, auto_attribs=True, frozen=True)
class AnimArgs(object):
    frames: int = 10

    @classmethod
    def from_request(cls) -> "AnimArgs":
        kw = {"frames": request.args.get("frames", 10, type=int)}
        return cls(**kw)
