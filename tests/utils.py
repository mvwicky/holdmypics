import re

from hypothesis import strategies as st

from holdmypics.converters import COLOR_REGEX

IMG_FORMATS = ("png", "webp", "jpeg", "gif")

dim_strategy = st.integers(min_value=128, max_value=8192)
size_strategy = st.tuples(dim_strategy, dim_strategy)
color_strategy = st.from_regex(re.compile(COLOR_REGEX), fullmatch=True)
opt_color_strategy = st.one_of(st.none(), color_strategy)
fmt_strategy = st.sampled_from(IMG_FORMATS)
text_strategy = st.one_of(st.none(), st.text(max_size=255))
dpi_strategy = st.one_of(st.none(), st.sampled_from((72, 300, 144, 216, 244, 488)))
args_strategy = st.fixed_dictionaries({"text": text_strategy, "dpi": dpi_strategy})
