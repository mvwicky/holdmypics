from typing import Optional

import attr
from flask import request


@attr.s(slots=True, auto_attribs=True, frozen=True)
class ImageArgs(object):
    text: Optional[str] = None
    filename: Optional[str] = None
    font_name: str = "overpass"
    dpi: int = 72

    @classmethod
    def from_request(cls):
        font_name = request.args.get("font", "overpass")
        kw = {
            "text": request.args.get("text", None),
            "filename": request.args.get("filename", None),
            "font_name": font_name,
            "dpi": request.args.get("dpi", 72, type=int),
        }
        return cls(**kw)
