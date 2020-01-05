import enum
import io
from string import hexdigits

from PIL import Image, ImageDraw

from ..._types import Dimension
from ...constants import MAX_SIZE, MIN_SIZE, font_sizes, fonts
from .image_args import ImageQueryArgs


class ImageFormat(str, enum.Enum):
    jpg = "jpeg"
    jpeg = "jpeg"
    png = "png"
    gif = "gif"
    webp = "webp"


def px_to_pt(px: float) -> float:
    return px * 0.75


def pt_to_px(pt: float) -> float:
    return pt / 0.75


def guess_size(height: int, font_name: str):
    font = fonts[font_name]
    s = int(px_to_pt(int(height * 0.75)))
    if s in font:
        return font[s], font_sizes.index(s)
    s_mod = s - (s % 4)
    if s_mod in font:
        return font[s_mod], font_sizes.index(s_mod)
    if s > MAX_SIZE:
        return font[MAX_SIZE], len(font_sizes) - 1
    elif s < MIN_SIZE:
        return font[MIN_SIZE], 0
    last = font_sizes[0]
    for i, sz in enumerate(font_sizes[1:]):
        if last < s < sz:
            return font[sz], i


def get_font(d: ImageDraw.Draw, sz: Dimension, text: str, font_name: str):
    face = fonts[font_name]
    width, height = sz
    font, idx = guess_size(height, font_name)
    tsize = d.textsize(text, font)
    while tsize >= sz and idx > 0:
        idx -= 1
        font = face[font_sizes[idx]]
        tsize = d.textsize(text, font)
    return font, tsize


def draw_text(im: Image.Image, color: str, args: ImageQueryArgs):
    w, h = im.size
    txt = Image.new("RGBA", im.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)
    font, tsize = get_font(d, (int(w * 0.9), h), args.text, args.font_name)
    yc = int((h - tsize[1]) / 2)
    xc = int((w - tsize[0]) / 2)
    d.text((xc, yc), args.text, font=font, fill=color)

    return Image.alpha_composite(im, txt)


fmt_kw = {
    "jpeg": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "png": lambda args: {"optimize": True, "dpi": (args.dpi, args.dpi)},
    "webp": lambda _: {"quality": 100, "method": 6},
    "gif": lambda _: {"optimize": True},
}


def create_image_sync(
    size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageQueryArgs
) -> Image.Image:
    mode = "RGBA"
    bg_color = get_color(bg_color)
    fg_color = get_color(fg_color)
    im = Image.new(mode, size, bg_color)
    if args.alpha < 1:
        alpha_im = Image.new("L", size, int(args.alpha * 255))
        im.putalpha(alpha_im)
    if args.text is not None and fmt != "jpeg":
        im = draw_text(im, fg_color, args)
    if fmt == "jpeg":
        im = im.convert("RGB")
    return im


def im_to_bytes(im: Image.Image, fmt: str, args: ImageQueryArgs) -> io.BytesIO:
    save_kw = {"format": fmt}
    kw_func = fmt_kw.get(fmt, lambda _: {})
    save_kw.update(kw_func(args))
    output = io.BytesIO()
    im.save(output, **save_kw)
    return output


# def make_image(
#     size: Dimension, bg_color: str, fg_color: str, fmt: str, args: ImageQueryArgs
# ):
#     fmt = "jpeg" if fmt == "jpg" else fmt
#     bg_color = get_color(bg_color)
#     fg_color = get_color(fg_color)
#     path = files.get_file_name(size, bg_color, fg_color, fmt, *attr.astuple(args))

#     if files.need_to_clean:

#         @after_this_request
#         def _clean(res):
#             click.echo("Cleaning")
#             files.clean()
#             return res

#     if os.path.isfile(path):
#         return path
#     else:
#         im = create_image(size, bg_color, fg_color, fmt, args)
#         save_kw = {}
#         kw_func = fmt_kw.get(fmt, None)
#         if kw_func is not None:
#             save_kw.update(kw_func(args))
#         im.save(path, **save_kw)
#         return path


def get_color(color: str) -> str:
    color = color.lstrip("#")
    color_len = len(color)
    if color_len in {3, 6} and all(e in hexdigits for e in color):
        return "#" + color
    return color
