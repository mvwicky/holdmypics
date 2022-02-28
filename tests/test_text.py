from __future__ import annotations

import imghdr
import io
import os
import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Optional, Union
from urllib.parse import urlencode

import pytest
from flask.testing import FlaskClient
from hypothesis import example, given, strategies as st
from loguru import logger
from PIL import Image

from tests.utils import (
    color_strategy,
    compact_dict,
    dpi_strategy,
    fmt_strategy,
    make_route,
    opt_color_strategy,
    size_strategy,
)

if TYPE_CHECKING:
    from holdmypics import Holdmypics

text_strategy = st.one_of(st.none(), st.text(max_size=255))
args_strategy = st.fixed_dictionaries({"text": text_strategy, "dpi": dpi_strategy})


def make_args(**kwargs: Union[str, int, None]):
    from holdmypics.api.args import TextImageArgs

    return TextImageArgs(**compact_dict(kwargs))


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    fg=color_strategy,
    bg=color_strategy,
    args=args_strategy,
)
@example(
    size=(1920, 1080),
    img_fmt="png",
    fg="fff",
    bg="000",
    args={"text": "Some Text", "dpi": 300},
)
def test_create_images_using_function(
    app_factory: Callable[[], Holdmypics],
    size: tuple[int, int],
    img_fmt: str,
    fg: str,
    bg: str,
    args: dict[str, Union[str, int, None]],
):
    from holdmypics.api.text import GeneratedTextImage

    start = time.perf_counter()
    with app_factory().test_request_context():
        img_args = make_args(**args)
        img = GeneratedTextImage(size, img_fmt, bg, fg, img_args)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)
        im = Image.open(p)
        assert im.size == size
    logger.debug("Elapsed: {0:.4f}", time.perf_counter() - start)


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    fg=opt_color_strategy,
    bg=opt_color_strategy,
    args=args_strategy,
)
def test_create_images_using_client(
    app_factory: Callable[[], Holdmypics],
    size: tuple[int, int],
    img_fmt: str,
    fg: Optional[str],
    bg: Optional[str],
    args: dict[str, Union[str, int, None]],
):
    if bg is None and fg:
        bg, fg = fg, None
    start = time.perf_counter()
    app = app_factory()
    with app.test_client() as client:
        url = make_route(
            app, "api.image_route", size=size, bg_color=bg, fg_color=fg, fmt=img_fmt
        )
        if args:
            url = "?".join((url, urlencode(compact_dict(args))))
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 200
        img_type = imghdr.what("filename", h=res.data)
        assert img_type == img_fmt
        im = Image.open(io.BytesIO(res.data))
        assert im.size == size
    logger.debug("Elapsed: {0:.4f}", time.perf_counter() - start)


def test_random_text_header(client: FlaskClient):
    path = make_route(
        client,
        "api.image_route",
        size=(638, 328),
        bg_color="cef",
        fg_color="555",
        fmt="png",
    )
    args = {"dpi": None, "random_text": True}
    query = urlencode({k: v for (k, v) in args.items() if v})
    url = "?".join((path, query))
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    assert "X-Random-Text" in res.headers


def test_random_text_ocr(client: FlaskClient):
    pytesseract = pytest.importorskip("pytesseract", reason="pytesseract not installed")
    path = make_route(
        client,
        "api.image_route",
        size=(638, 328),
        bg_color="cef",
        fg_color="555",
        fmt="png",
    )
    args = {"text": "Some Random Text", "dpi": None, "random_text": True}
    query = urlencode({k: v for (k, v) in args.items() if v})
    url = "?".join((path, query))
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    img_type = imghdr.what("filename", h=res.data)
    assert img_type == "png"
    im = Image.open(io.BytesIO(res.data))
    from_header = res.headers.get("X-Random-Text")
    assert from_header is not None
    from_ocr = pytesseract.image_to_string(im).strip()
    logger.info("Got text from OCR: {0}", from_ocr)
    assert from_ocr.casefold() == from_header.casefold()


def _sz_id(sz: tuple[int, int]) -> str:
    return "{0}x{1}".format(*sz)


@pytest.mark.parametrize(
    "font_name", ["overpass", "fira-mono", "fira-sans", "roboto", "spectral"]
)
@pytest.mark.parametrize("size", [(3840, 2160), (960, 540)], ids=_sz_id)
def test_text_with_fonts(
    app: Holdmypics, image_format: str, font_name: str, size: tuple[int, int]
):
    from holdmypics.api.text import GeneratedTextImage

    with app.test_request_context():
        img_args = make_args(text=f"Text with font: {font_name}", font_name=font_name)
        img = GeneratedTextImage(size, image_format, "cef", "555", img_args)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)
