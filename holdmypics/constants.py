from __future__ import annotations

import enum

RAND_COLOR = "rand".casefold()
CACHE_TIME = int(24 * 60 * 60)

fg_color_default: dict[str, str] = {"fg_color": "aaa"}
bg_color_default: dict[str, str] = {"bg_color": "000"}
fmt_default: dict[str, str] = {"fmt": "png"}
all_defaults: dict[str, str] = {**fg_color_default, **bg_color_default, **fmt_default}

IMG_FORMATS = ("jpg", "jpeg", "gif", "png", "webp")
IMG_FORMATS_STR = ",".join(IMG_FORMATS)

DEFAULT_FONT = "overpass"
DEFAULT_DPI = 144
NO_CACHE = "max-age=0, no-store, must-revalidate"
COUNT_KEY = "image_count"
SIZE_KEY = "image_size"
PX_PER_PT = 0.75

DEFAULT_COLORS = (
    (0x55, 0x55, 0x55, 0xFF),
    (0xDD, 0xDD, 0xDD, 128),
    (0xEE, 0x77, 0x33, 0xFF),
)


class Unset(enum.Enum):
    """Singleton type for situations where `None` may be a valid value.

    From: python.org/dev/peps/pep-0484/#support-for-singleton-types-in-unions
    """

    TOKEN = 0


UNSET = Unset.TOKEN
