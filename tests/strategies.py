from __future__ import annotations

import re

from hypothesis import strategies as st

IMG_FORMATS = ("png", "webp", "jpeg", "gif")
DPI_VALUES = (None, 300, 72, 144, 216, 244, 488)


def _get_col_strategy():
    from holdmypics.converters import COLOR_REGEX

    return st.from_regex(re.compile(COLOR_REGEX), fullmatch=True)


dim_strategy = st.integers(min_value=128, max_value=8192)
size_strategy = st.tuples(dim_strategy, dim_strategy)
color_strategy = st.deferred(_get_col_strategy)
opt_color_strategy = st.one_of(st.none(), color_strategy)
fmt_strategy = st.sampled_from(IMG_FORMATS)
dpi_strategy = st.sampled_from(DPI_VALUES)
