from __future__ import annotations

import math
import os
from itertools import cycle

import attr
from loguru import logger
from PIL import Image, ImageDraw

from ..constants import DEFAULT_COLORS
from .args import TiledImageArgs
from .base import BaseGeneratedImage
from .files import files

COLORS = cycle(DEFAULT_COLORS)


@attr.s(slots=True, auto_attribs=True)
class GeneratedTiledImage(BaseGeneratedImage[TiledImageArgs]):
    cols: int
    rows: int

    def make(self) -> Image.Image:
        base = Image.new(self.mode, self.size, self.bg_color)
        draw_im = Image.new(self.mode, base.size, (255, 255, 255, 0))
        d = ImageDraw.Draw(draw_im)
        width, height = self.size
        t_width = math.ceil(width / self.cols)
        t_height = math.ceil(height / self.rows)
        colors = cycle(self.args.colors) if self.args.colors else COLORS
        for i in range(self.rows):
            y1 = i * t_height
            y2 = y1 + t_height
            for j in range(self.cols):
                x1 = j * t_width
                x2 = x1 + t_width
                d.rectangle(((x1, y1), (x2, y2)), next(colors))
        base.alpha_composite(draw_im)
        if self.fmt == "jpeg":
            base = base.convert("RGB")
        return base

    def get_path(self) -> str:
        path = files.get_file_name(
            self.size,
            self.bg_color,
            self.fg_color,
            self.fmt,
            self.args,
            self.cols,
            self.rows,
        )
        if os.path.isfile(path):
            os.utime(path)
            logger.debug('Already existed: "{0}"', os.path.basename(path))
            return path
        else:
            self.save_img(self.make(), path)
        return path
