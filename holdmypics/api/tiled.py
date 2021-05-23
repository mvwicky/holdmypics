from __future__ import annotations

import math
import os
from itertools import cycle

import attr
from loguru import logger
from PIL import Image, ImageDraw

from .base import BaseGeneratedImage
from .files import files

COLORS = cycle(
    ((0x55, 0x55, 0x55, 0xFF), (0xDD, 0xDD, 0xDD, 128), (0xEE, 0x77, 0x33, 0xFF))
)


@attr.s(slots=True, auto_attribs=True)
class GeneratedTiledImage(BaseGeneratedImage):
    cols: int
    rows: int

    def make(self) -> Image.Image:
        base = Image.new(self.mode, self.size, self.bg_color)
        draw_im = Image.new(base.mode, base.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(draw_im)
        width, height = self.size
        t_width = math.ceil(width / self.cols)
        t_height = math.ceil(height / self.rows)
        for i in range(self.rows):
            y1 = i * t_height
            y2 = y1 + t_height
            for j in range(self.cols):
                x1 = j * t_width
                x2 = x1 + t_width
                d.rectangle(((x1, y1), (x2, y2)), next(COLORS))
        out = Image.alpha_composite(base, draw_im)
        if self.fmt == "jpeg":
            out = out.convert("RGB")
        return out

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
