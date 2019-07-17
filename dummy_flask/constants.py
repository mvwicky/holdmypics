import os
from pathlib import Path

from funcy import merge
from PIL import ImageFont

cache_time = int(24 * 60 * 60)
fg_color_default = {"fg_color": "aaa"}
bg_color_default = {"bg_color": "000"}
fmt_default = {"fmt": "png"}
all_defaults = merge(fg_color_default, bg_color_default, fmt_default)
img_formats = ["jpg", "jpeg", "gif", "png", "webp"]
img_formats_str = ",".join(img_formats)

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
font_dir = HERE / "fonts"
font_files = {
    "overpass": font_dir / "overpass.ttf",
    "fira-sans": font_dir / "fira-sans.ttf",
    "roboto": font_dir / "roboto.ttf",
    "spectral": font_dir / "spectral.ttf",
}
font_sizes = list(range(4, 289, 4))
fonts = {
    name: {sz: ImageFont.truetype(str(file), size=sz) for sz in font_sizes}
    for (name, file) in font_files.items()
}

FONT_NAMES = set(list(font_files.keys()))
MAX_SIZE = max(font_sizes)
MIN_SIZE = min(font_sizes)
