from typing import Optional

import attr
from flask import request


def clamp_alpha(a: float) -> float:
    return max(0.0, min(float(a), 1.0))


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImageArgs(object):
    text: Optional[str] = None
    filename: Optional[str] = None
    font_name: str = "overpass"
    dpi: int = 72
    alpha: float = attr.ib(default=1.0, converter=clamp_alpha)
    seed: str = None

    @classmethod
    def from_request(cls):
        font_name = request.args.get("font", "overpass")
        kw = {
            "text": request.args.get("text", None),
            "filename": request.args.get("filename", None),
            "font_name": font_name,
            "dpi": request.args.get("dpi", 72, type=int),
            "alpha": request.args.get("alpha", 1.0, type=float),
            "seed": request.args.get("seed", None),
        }
        return cls(**kw)
