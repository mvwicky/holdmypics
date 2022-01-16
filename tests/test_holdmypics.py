from __future__ import annotations

import imghdr
import io
import os
import re
import time
from types import ModuleType
from typing import Optional, Union
from urllib.parse import urlencode

import pytest
from flask import Flask
from flask.testing import FlaskClient
from hypothesis import example, given, strategies as st
from loguru import logger
from PIL import Image

from holdmypics import create_app
from holdmypics.api.args import ImageArgs
from holdmypics.api.img import GeneratedImage
from holdmypics.converters import COLOR_REGEX

try:
    import pytesseract  # type: ignore
except ImportError:
    pytesseract = None

SKIP_INDEX = os.environ.get("TESTS_SKIP_INDEX", None) is not None
IMG_FORMATS = ("png", "webp", "jpeg", "gif")

dim_strategy = st.integers(min_value=128, max_value=8192)
size_strategy = st.tuples(dim_strategy, dim_strategy)
color_strategy = st.from_regex(re.compile(COLOR_REGEX), fullmatch=True)
opt_color_strategy = st.one_of(st.none(), color_strategy)
fmt_strategy = st.sampled_from(IMG_FORMATS)
text_strategy = st.one_of(st.none(), st.text(max_size=255))
dpi_strategy = st.one_of(st.none(), st.sampled_from((72, 300, 144, 216, 244, 488)))
args_strategy = st.fixed_dictionaries({"text": text_strategy, "dpi": dpi_strategy})


def make_route(
    sz: tuple[int, int],
    bg_color: Optional[str] = None,
    fg_color: Optional[str] = None,
    fmt: Optional[str] = None,
) -> str:
    if not any((bg_color, fg_color, fmt)):
        pytest.fail("Can't make a route with just size")
    parts = ("{0}x{1}".format(*sz), bg_color, fg_color, fmt)
    return "".join(["/api/", "/".join(filter(None, parts)), "/"])


@pytest.mark.skipif(SKIP_INDEX, reason="Not testing client-side stuff.")
def test_index(client: FlaskClient):
    res = client.get("/")
    assert res.status_code == 200


def test_favicon(client: FlaskClient):
    res = client.get("/favicon.ico")
    assert res.status_code == 200
    assert res.content_type in ("image/x-icon", "image/vnd.microsoft.icon")


@given(
    size=size_strategy,
    img_fmt=fmt_strategy,
    fg_color=color_strategy,
    bg_color=color_strategy,
    args=args_strategy,
)
@example(
    size=(1920, 1080),
    img_fmt="png",
    fg_color="fff",
    bg_color="000",
    args={"text": "Some Text", "dpi": 300},
)
def test_create_images_using_function(
    config: ModuleType,
    size: tuple[int, int],
    img_fmt: str,
    fg_color: str,
    bg_color: str,
    args: dict[str, Union[str, int, None]],
):
    start = time.perf_counter()
    app = create_app(config)
    with app.test_request_context():
        img_args = ImageArgs(**{k: v for (k, v) in args.items() if v})
        img = GeneratedImage(size, img_fmt, bg_color, fg_color, img_args)
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
    fg_color=opt_color_strategy,
    bg_color=opt_color_strategy,
    args=args_strategy,
)
def test_create_images_using_client(
    config: ModuleType,
    size: tuple[int, int],
    img_fmt: str,
    fg_color: Optional[str],
    bg_color: Optional[str],
    args: dict[str, Union[str, int, None]],
):
    start = time.perf_counter()
    app = create_app(config)
    with app.test_client() as client:
        url = make_route(size, bg_color, fg_color, img_fmt)
        if args:
            url = "?".join((url, urlencode({k: v for (k, v) in args.items() if v})))
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 200
        img_type = imghdr.what("filename", h=res.data)
        assert img_type == img_fmt
        im = Image.open(io.BytesIO(res.data))
        assert im.size == size
    logger.debug("Elapsed: {0:.4f}", time.perf_counter() - start)


def test_timing_header(client: FlaskClient):
    path = make_route((638, 328), "cef", "555", "png")
    res = client.get(path, follow_redirects=False)
    assert res.status_code == 200
    proc_time = res.headers.get("X-Processing-Time", 0, float)
    assert proc_time is not None


def test_random_text_header(client: FlaskClient):
    path = make_route((638, 328), "cef", "555", "png")
    args = {"dpi": None, "random_text": True}
    query = urlencode({k: v for (k, v) in args.items() if v})
    url = "?".join((path, query))
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    assert "X-Random-Text" in res.headers


@pytest.mark.skipif(pytesseract is None, reason="pytesseract not installed")
def test_random_text_ocr(client: FlaskClient):
    assert pytesseract is not None
    path = make_route((638, 328), "cef", "555", "png")
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


def test_forwarding_headers(client: FlaskClient):
    path = make_route((638, 328), "cef", "555", "png")
    args = {"text": "Some Random Text"}
    query = urlencode(args)
    url = "?".join((path, query))
    forwarded = "123.45.4.2,123.45.4.2"
    res = client.get(url, headers=[("X-Forwarded-For", forwarded)])
    was_forwarded = res.headers.get("X-Was-Forwarded-For", None)
    assert was_forwarded == forwarded


def _sz_id(sz: tuple[int, int]) -> str:
    return "{0}x{1}".format(*sz)


# @pytest.mark.parametrize("fmt", ["png", "webp"])
@pytest.mark.parametrize(
    "font_name", ["overpass", "fira-mono", "fira-sans", "roboto", "spectral"]
)
@pytest.mark.parametrize("size", [(3840, 2160), (1920, 1080), (960, 540)], ids=_sz_id)
def test_text_with_fonts(
    app: Flask, image_format: str, font_name: str, size: tuple[int, int]
):
    with app.test_request_context():
        img_args = ImageArgs(text=f"Text with font: {font_name}", font_name=font_name)
        img = GeneratedImage(size, image_format, "cef", "555", img_args)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)
