from __future__ import annotations

import math
from itertools import cycle
from typing import Any

import attr
from PIL import Image, ImageDraw

from ..constants import DEFAULT_COLORS
from .args import TiledImageArgs
from .base import BaseGeneratedImage


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
        colors = cycle(self.args.colors or DEFAULT_COLORS)
        cols, rect = self.cols, d.rectangle
        for i in range(self.rows):
            y1 = i * t_height
            y2 = y1 + t_height
            for j in range(cols):
                x1 = j * t_width
                x2 = x1 + t_width
                rect(((x1, y1), (x2, y2)), next(colors))
        base.alpha_composite(draw_im)
        if self.fmt == "jpeg":
            base = base.convert("RGB")
        return base

    def get_file_name_extra(self) -> tuple[Any, ...]:
        return (self.cols, self.rows)
