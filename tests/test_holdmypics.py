from __future__ import annotations

import imghdr
import io
import os
from types import ModuleType
from typing import Optional
from urllib.parse import urlencode

import pytest
from flask import Response
from flask.testing import FlaskClient
from hypothesis import given, strategies as st
from loguru import logger
from PIL import Image

from holdmypics import create_app
from holdmypics.api.args import ImageArgs
from holdmypics.api.img import GeneratedImage
from holdmypics.converters import COLOR_REGEX

try:
    import pytesseract
except ImportError:
    pytesseract = None

SKIP_INDEX = os.environ.get("TESTS_SKIP_INDEX", None) is not None
IMG_FORMATS = ("png", "webp", "jpeg", "gif")

dim_strategy = st.integers(min_value=128, max_value=8192)
size_strategy = st.tuples(dim_strategy, dim_strategy)
color_strategy = st.from_regex(COLOR_REGEX, fullmatch=True)
opt_color_strategy = st.one_of(st.none(), color_strategy)
fmt_strategy = st.sampled_from(IMG_FORMATS)
text_strategy = st.one_of(st.none(), st.text(max_size=255))
dpi_strategy = st.one_of(st.none(), st.sampled_from((72, 300, 216, 244, 488)))
args_strategy = st.fixed_dictionaries({"text": text_strategy, "dpi": dpi_strategy})


def make_route(
    sz: tuple[int, int], bg_color: str = None, fg_color: str = None, fmt: str = None
) -> str:
    if not any((bg_color, fg_color, fmt)):
        pytest.fail("Can't make a route with just size")
    parts = ["{0}x{1}".format(*sz), bg_color, fg_color, fmt]
    return "".join(["/api/", "/".join(filter(None, parts)), "/"])


@pytest.mark.skipif(SKIP_INDEX, reason="Not testing client-side stuff.")
def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


def test_favicon(client: FlaskClient):
    url = "/favicon.ico"
    res: Response = client.get(url)
    assert res.status_code == 200
    assert res.content_type in {"image/x-icon", "image/vnd.microsoft.icon"}


@given(
    size=size_strategy,
    image_format=fmt_strategy,
    fg_color=color_strategy,
    bg_color=color_strategy,
    args=args_strategy,
)
def test_create_images_using_function(
    config: ModuleType,
    size: tuple[int, int],
    image_format: str,
    fg_color: str,
    bg_color: str,
    args: dict,
):
    app = create_app(config)
    with app.test_request_context():
        img_args = ImageArgs(**{k: v for (k, v) in args.items() if v})
        img = GeneratedImage(size, image_format, bg_color, fg_color, img_args)
        assert img.get_save_kw()
        p = img.get_path()
        assert os.path.isfile(p)
        assert os.path.getsize(p)
        im = Image.open(p)
        assert im.size == size


@given(
    size=size_strategy,
    image_format=fmt_strategy,
    fg_color=opt_color_strategy,
    bg_color=opt_color_strategy,
    args=args_strategy,
)
def test_create_images_using_client(
    config: ModuleType,
    size: tuple[int, int],
    image_format: str,
    fg_color: Optional[str],
    bg_color: Optional[str],
    args: dict,
):
    app = create_app(config)
    with app.test_client() as client:
        query = args and urlencode({k: v for (k, v) in args.items() if v})
        url = make_route(size, bg_color, fg_color, image_format)
        if query:
            url = "?".join([url, query])
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 200
        img_type = imghdr.what("filename", h=res.data)
        assert img_type == image_format
        im = Image.open(io.BytesIO(res.data))
        assert im.size == size


@pytest.mark.skipif(pytesseract is None, reason="pytesseract not installed")
def test_random_text(client: FlaskClient):
    url = make_route((638, 328), "cef", "555", "png")
    args = {"text": "Some Random Text", "dpi": None, "random_text": True}
    query = urlencode({k: v for (k, v) in args.items() if v})
    url = "?".join([url, query])
    res: Response = client.get(url, follow_redirects=False)
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
    url = "?".join([path, query])
    forwarded = "123.45.4.2,123.45.4.2"
    res: Response = client.get(url, headers=[("X-Forwarded-For", forwarded)])
    was_forwarded = res.headers.get("X-Was-Forwarded-For", None)
    assert was_forwarded == forwarded
