from __future__ import annotations

import os

import attr
from loguru import logger
from PIL import Image

from .base import BaseGeneratedImage
from .files import files
from .utils import TextArgs, draw_text


@attr.s(slots=True, auto_attribs=True)
class GeneratedImage(BaseGeneratedImage):
    def make(self) -> Image.Image:
        im = Image.new(self.mode, self.size, self.bg_color)
        args = self.args
        if args.text is not None:
            text_args = TextArgs(self.fg_color, args.text, args.font_name, args.debug)
            im = draw_text(im, text_args)
        if self.fmt == "jpeg":
            im = im.convert("RGB")
        return im

    def get_path(self) -> str:
        path = files.get_file_name(
            self.size, self.bg_color, self.fg_color, self.fmt, self.args
        )
        if os.path.isfile(path):
            os.utime(path)
            logger.debug('Already existed: "{0}"', os.path.basename(path))
            return path
        else:
            self.save_img(self.make(), path)
        return path
