from __future__ import annotations

import io

from PIL import Image

from .utils import get_color, random_color


def make_anim(size: tuple[int, int], bg_color: str, fg_color: str, fmt: str):
    mode = "RGB"
    bg_color, fg_color = map(get_color, [bg_color, fg_color])
    im = Image.new(mode, size, bg_color)
    frames = []
    for _ in range(12):
        frames.append(Image.new(mode, size, get_color(random_color())))

    fp = io.BytesIO()
    im.save(fp, fmt, append_images=frames, duration=5000, save_all=True)
    return fp
