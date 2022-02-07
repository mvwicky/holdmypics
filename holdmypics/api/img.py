from __future__ import annotations

import attr
from PIL import Image

from .args import ImageArgs
from .base import BaseGeneratedImage
from .text import draw_text
from .utils import TextArgs


@attr.s(slots=True, auto_attribs=True)
class GeneratedImage(BaseGeneratedImage[ImageArgs]):
    def make(self) -> Image.Image:
        im = self.new_image()
        # im.putalpha(Image.new("L", self.size, 255))
        args = self.args
        if args.text is not None:
            text_args = TextArgs(self.fg_color, args.text, args.font_name, args.debug)
            im = draw_text(im, text_args)
        if self.fmt == "jpeg":
            im = im.convert("RGB")
        return im
