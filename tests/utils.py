from __future__ import annotations

import re
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Union

from flask import Flask, url_for
from hypothesis import strategies as st

if TYPE_CHECKING:
    from flask.testing import FlaskClient

IMG_FORMATS = ("png", "webp", "jpeg", "gif")
DPI_VALUES = (300, 72, 144, 216, 244, 488)


def _get_col_strategy():
    from holdmypics.converters import COLOR_REGEX

    return st.from_regex(re.compile(COLOR_REGEX), fullmatch=True)


dim_strategy = st.integers(min_value=128, max_value=8192)
size_strategy = st.tuples(dim_strategy, dim_strategy)
color_strategy = st.deferred(_get_col_strategy)
opt_color_strategy = st.one_of(st.none(), color_strategy)
fmt_strategy = st.sampled_from(IMG_FORMATS)
dpi_strategy = st.one_of(st.none(), st.sampled_from(DPI_VALUES))


def make_route(app: Union["Flask", "FlaskClient"], endpoint: str, **kwargs: Any) -> str:
    if not isinstance(app, Flask):
        app = app.application
    with app.test_request_context():
        return url_for(endpoint, **kwargs)


def compact_dict(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    return {k: v for (k, v) in mapping.items() if v}
