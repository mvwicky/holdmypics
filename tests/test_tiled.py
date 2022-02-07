from __future__ import annotations

import os
from collections.abc import Callable
from typing import TYPE_CHECKING, Union
from urllib.parse import urlencode

from hypothesis import given, strategies as st

from tests.utils import (
    color_strategy,
    compact_dict,
    dpi_strategy,
    fmt_strategy,
    make_route,
    size_strategy,
)

if TYPE_CHECKING:
    from holdmypics import Holdmypics

cols_strategy = st.integers(min_value=1, max_value=100)
rows_strategy = st.integers(min_value=1, max_value=100)
colors_strategy = st.lists(color_strategy, min_size=1, max_size=15)
args_strategy = st.fixed_dictionaries({"colors": colors_strategy, "dpi": dpi_strategy})


def make_args(**kwargs: Union[str, int, None]):
    from holdmypics.api.args import TiledImageArgs

    return TiledImageArgs(**compact_dict(kwargs))


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    cols=cols_strategy,
    rows=rows_strategy,
    args=args_strategy,
)
def test_create_images_using_function(
    app_factory: Callable[[], "Holdmypics"],
    size: tuple[int, int],
    img_fmt: str,
    cols: int,
    rows: int,
    args: dict[str, Union[int, list[str]]],
):
    from holdmypics.api.tiled import GeneratedTiledImage

    with app_factory().test_request_context():
        img_args = make_args(**args)
        img = GeneratedTiledImage(size, img_fmt, "0000", "0000", img_args, cols, rows)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    cols=cols_strategy,
    rows=rows_strategy,
    args=args_strategy,
)
def test_create_images_using_client(
    app_factory: Callable[[], "Holdmypics"],
    size: tuple[int, int],
    img_fmt: str,
    cols: int,
    rows: int,
    args: dict[str, Union[int, list[str]]],
):
    app = app_factory()
    with app.test_client() as client:
        url = make_route(
            app, "api.tiled_route", fmt=img_fmt, size=size, cols=cols, rows=rows
        )
        url = "?".join((url, urlencode(compact_dict(args), doseq=True)))
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 200
