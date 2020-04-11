from typing import Dict, List

from funcy import merge

cache_time = int(24 * 60 * 60)

fg_color_default = {"fg_color": "aaa"}
bg_color_default = {"bg_color": "000"}

fmt_default = {"fmt": "png"}
all_defaults: Dict[str, str] = merge(fg_color_default, bg_color_default, fmt_default)
img_formats: List[str] = ["jpg", "jpeg", "gif", "png", "webp"]
img_formats_str = ",".join(img_formats)


COUNT_KEY = "image_count"
PX_PER_PT = 0.75
