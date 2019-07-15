import io
import os
from string import hexdigits
from typing import Text, Tuple, Optional

from PIL import Image, ImageFont, ImageDraw

Dimension = Tuple[int, int]

HERE = os.path.dirname(os.path.abspath(__file__))

font_file = os.path.join(HERE, "overpass-v3-latin-regular.ttf")
font_sizes = list(range(4, 289, 4))
fonts = {sz: ImageFont.truetype(font_file, size=sz) for sz in font_sizes}
MAX_SIZE = max(font_sizes)
MIN_SIZE = min(font_sizes)


def px_to_pt(px: float) -> float:
    return px * 0.75


def pt_to_px(pt: float) -> float:
    return pt / 0.75


def guess_size(height: int):
    s = int(px_to_pt(int(height * 0.75)))
    if s in fonts:
        return fonts[s], font_sizes.index(s)
    s_mod = s - (s % 4)
    if s_mod in fonts:
        return fonts[s_mod], font_sizes.index(s_mod)
    if s > MAX_SIZE:
        return fonts[MAX_SIZE], len(font_sizes) - 1
    elif s < MIN_SIZE:
        return fonts[MIN_SIZE], 0
    last = font_sizes[0]
    for i, sz in enumerate(font_sizes[1:]):
        if last < s < sz:
            return fonts[sz], i


def get_font(d: ImageDraw.Draw, sz: Dimension, text: Text):
    width, height = sz
    font, idx = guess_size(height)
    tsize = d.textsize(text, font)
    while tsize >= sz and idx > 0:
        idx -= 1
        font = fonts[font_sizes[idx]]
        tsize = d.textsize(text, font)
    return font, tsize


def draw_text(im: Image.Image, color: Text, text: Text):
    w, h = im.size
    txt = Image.new("RGBA", im.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font, tsize = get_font(d, (int(w * 0.9), h), text)
    print(font.size)
    yc = int((h - tsize[1]) / 2)
    xc = int((w - tsize[0]) / 2)
    d.text((xc, yc), text, font=font, fill=color)

    return Image.alpha_composite(im, txt)


def make_image(
    size: Dimension,
    bg_color: Text,
    fg_color: Text,
    fmt: Text = "png",
    text: Optional[Text] = None,
):
    fmt = "jpeg" if fmt == "jpg" else fmt
    mode = "RGB" if fmt == "jpeg" else "RGBA"
    bg_color = get_color(bg_color)
    fg_color = get_color(fg_color)
    im = Image.new(mode, size, bg_color)
    if text is not None:
        im = draw_text(im, fg_color, text)
    fp = io.BytesIO()
    im.save(fp, format=fmt)
    return fp


def get_color(color: Text):
    if color.startswith("#"):
        return color
    color_len = len(color)
    if color_len in {3, 6} and all([e in hexdigits for e in color]):
        return "#" + color
    return color
