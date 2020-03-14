import os
from pathlib import Path
from typing import Dict, List, Set

from funcy import merge
from PIL import ImageFont

cache_time = int(24 * 60 * 60)
fg_color_default = {"fg_color": "aaa"}
bg_color_default = {"bg_color": "000"}
fmt_default = {"fmt": "png"}
all_defaults: Dict[str, str] = merge(fg_color_default, bg_color_default, fmt_default)
img_formats: List[str] = ["jpg", "jpeg", "gif", "png", "webp"]
img_formats_str = ",".join(img_formats)

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
font_dir = HERE / "fonts"
font_files = {f.stem: f for f in font_dir.glob("*.ttf")}
font_sizes = list(range(4, 289, 4))
fonts: Dict[str, Dict[int, ImageFont.ImageFont]] = {
    name: {sz: ImageFont.truetype(str(file), size=sz) for sz in font_sizes}
    for (name, file) in font_files.items()
}

FONT_NAMES: Set[str] = set(font_files)
MAX_SIZE: int = max(font_sizes)
MIN_SIZE: int = min(font_sizes)

COUNT_KEY = "image_count"
