from __future__ import annotations

import enum

RAND_COLOR = "rand".casefold()

cache_time = int(24 * 60 * 60)

fg_color_default = {"fg_color": "aaa"}
bg_color_default = {"bg_color": "000"}

fmt_default = {"fmt": "png"}
all_defaults: dict[str, str] = {**fg_color_default, **bg_color_default, **fmt_default}
img_formats: tuple[str] = ("jpg", "jpeg", "gif", "png", "webp")
img_formats_str = ",".join(img_formats)

NO_CACHE = "max-age=0, no-store, must-revalidate"
COUNT_KEY = "image_count"
PX_PER_PT = 0.75


class Unset(enum.Enum):
    """Singleton type for situations where `None` may be a valid value.

    From: python.org/dev/peps/pep-0484/#support-for-singleton-types-in-unions
    """

    TOKEN = 0


UNSET = Unset.TOKEN
