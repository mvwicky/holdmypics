from __future__ import annotations

import math
from itertools import cycle
from typing import Any

from attrs import define
from PIL import Image, ImageDraw

from ..constants import DEFAULT_COLORS
from .args import TiledImageArgs
from .base import BaseGeneratedImage


@define()
class GeneratedTiledImage(BaseGeneratedImage[TiledImageArgs]):
    cols: int
    rows: int

    def make(self) -> Image.Image:
        width, height = self.size
        t_width, t_height = map(math.ceil, (width / self.cols, height / self.rows))
        colors = cycle(self.args.colors or DEFAULT_COLORS)
        draw_im = self.new_image(color=(255, 255, 255, 0))
        d = ImageDraw.Draw(draw_im)
        cols_range, rect = range(self.cols), d.rectangle
        for i in range(self.rows):
            y1 = i * t_height
            y2 = y1 + t_height
            for j in cols_range:
                x1 = j * t_width
                x2 = x1 + t_width
                rect(((x1, y1), (x2, y2)), next(colors))
        base = self.new_image()
        base.alpha_composite(draw_im)
        return base

    def get_file_name_extra(self) -> tuple[Any, ...]:
        return (self.cols, self.rows)
