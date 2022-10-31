from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Union
from urllib.parse import urlencode

import pytest
from hypothesis import example, given, strategies as st
from loguru import logger

from tests.strategies import color_strategy, dpi_strategy, fmt_strategy, size_strategy
from tests.utils import compact_dict, make_route, size_id

if TYPE_CHECKING:
    from holdmypics import Holdmypics

cols_strategy = st.integers(min_value=1, max_value=100)
rows_strategy = st.integers(min_value=1, max_value=100)
colors_strategy = st.lists(color_strategy, min_size=1, max_size=15)
args_strategy = st.fixed_dictionaries({"colors": colors_strategy, "dpi": dpi_strategy})


def make_args(**kwargs: Union[str, int, list[str], None]):
    from holdmypics.api.args import TiledImageArgs

    return TiledImageArgs(**compact_dict(kwargs))


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    cols=cols_strategy,
    rows=rows_strategy,
    args=args_strategy,
)
@example(
    size=(1920, 1080),
    img_fmt="png",
    cols=19,
    rows=10,
    args={"colors": ["rand", "rand"], "dpi": 216},
)
@example(
    size=(3762, 5809),
    img_fmt="webp",
    cols=83,
    rows=33,
    args={"colors": ["74F"], "dpi": 72},
)
def test_create_images_using_function(
    app_factory: Callable[[], Holdmypics],
    size: tuple[int, int],
    img_fmt: str,
    cols: int,
    rows: int,
    args: dict[str, Union[int, list[str]]],
):
    from holdmypics.api.tiled import GeneratedTiledImage

    start = time.perf_counter()
    with app_factory().test_request_context():
        img_args = make_args(**args)
        img = GeneratedTiledImage(size, img_fmt, "0000", "0000", img_args, cols, rows)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)
    logger.debug("Elapsed: {0:.4f}", time.perf_counter() - start)


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    cols=cols_strategy,
    rows=rows_strategy,
    args=args_strategy,
)
@example(
    size=(1920, 1080),
    img_fmt="png",
    cols=19,
    rows=10,
    args={"colors": ["rand", "rand"], "dpi": 216},
)
def test_create_images_using_client(
    app_factory: Callable[[], Holdmypics],
    size: tuple[int, int],
    img_fmt: str,
    cols: int,
    rows: int,
    args: dict[str, Union[int, list[str]]],
):

    start = time.perf_counter()
    app = app_factory()
    with app.test_client() as client:
        url = make_route(
            app, "api.tiled_route", fmt=img_fmt, size=size, cols=cols, rows=rows
        )
        url = "?".join((url, urlencode(compact_dict(args), doseq=True)))
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 200
    logger.debug("Elapsed: {0:.4f}", time.perf_counter() - start)


@pytest.mark.parametrize(("cols", "rows"), [(19, 10), (5, 5)])
@pytest.mark.parametrize("size", [(6408, 8154), (3840, 2160), (960, 540)], ids=size_id)
def test_tiled_make_examples(
    app: Holdmypics, image_format: str, size: tuple[int, int], cols: int, rows: int
):
    from holdmypics.api.tiled import GeneratedTiledImage

    start = time.perf_counter()
    with app.test_request_context():
        args = make_args(colors=["rand", "rand", "rand"])
        img = GeneratedTiledImage(size, image_format, "0000", "0000", args, cols, rows)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)
    logger.debug("Elapsed: {0:.4f}", time.perf_counter() - start)
