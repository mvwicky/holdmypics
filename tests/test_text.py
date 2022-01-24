from __future__ import annotations

import imghdr
import io
import os
import time
from types import ModuleType
from typing import Optional, Union
from urllib.parse import urlencode

import pytest
from flask import Flask
from flask.testing import FlaskClient
from hypothesis import example, given
from loguru import logger
from PIL import Image

from holdmypics import create_app
from holdmypics.api.args import ImageArgs
from holdmypics.api.img import GeneratedImage
from tests.utils import (
    args_strategy,
    color_strategy,
    fmt_strategy,
    opt_color_strategy,
    size_strategy,
)


def make_route(
    sz: tuple[int, int],
    bg_color: Optional[str] = None,
    fg_color: Optional[str] = None,
    fmt: Optional[str] = None,
) -> str:
    parts = (bg_color, fg_color, fmt)
    if not any(parts):
        pytest.fail("Can't make a route with just size")
    return f"/api/{sz[0]}x{sz[1]}/{'/'.join(filter(None, parts))}/"


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


def test_random_text_header(client: FlaskClient):
    path = make_route((638, 328), "cef", "555", "png")
    args = {"dpi": None, "random_text": True}
    query = urlencode({k: v for (k, v) in args.items() if v})
    url = "?".join((path, query))
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    assert "X-Random-Text" in res.headers


def test_random_text_ocr(client: FlaskClient):
    pytesseract = pytest.importorskip("pytesseract", reason="pytesseract not installed")
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
