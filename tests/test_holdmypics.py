import imghdr
import io
import os
from typing import Optional
from urllib.parse import urlencode

import pytest
from cytoolz import valfilter
from flask import Response
from flask.testing import FlaskClient
from hypothesis import given, strategies as st
from loguru import logger
from PIL import Image

from holdmypics import create_app
from holdmypics.api.args import ImageArgs
from holdmypics.api.img import save_image
from holdmypics.converters import COLOR_REGEX

try:
    import pytesseract
except ImportError:
    pytesseract = None

SKIP_INDEX = os.environ.get("TESTS_SKIP_INDEX", None) is not None
IMG_FORMATS = ["png", "webp", "jpeg", "gif"]


def make_route(
    width: int, height: int, bg_color: str = None, fg_color: str = None, fmt: str = None
) -> str:
    if not any([bg_color, fg_color, fmt]):
        pytest.fail("Can't make a route with just size")
    parts = ["{0}x{1}".format(width, height), bg_color, fg_color, fmt]
    return "".join(["/api/", "/".join(filter(bool, parts)), "/"])


def make_url(
    width: int, height: int, fmt: int, bg_color: str, fg_color: str, text: str
):
    path = make_route(width, height, bg_color, fg_color, fmt)
    if text is not None:
        query = urlencode({"text": text})
        return "?".join([path, query])
    else:
        return path


@pytest.mark.skipif(SKIP_INDEX, reason="Not testing client-side stuff.")
def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


dim_strategy = st.integers(min_value=1, max_value=8192)
color_strategy = st.from_regex(COLOR_REGEX, fullmatch=True)
opt_color_strategy = st.one_of(st.none(), color_strategy)
alpha_strategy = st.one_of(
    st.none(),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
text_strategy = st.one_of(st.none(), st.text(max_size=255))
dpi_strategy = st.one_of(st.none(), st.integers(min_value=72, max_value=488))
args_strategy = st.fixed_dictionaries(
    {"text": text_strategy, "alpha": alpha_strategy, "dpi": dpi_strategy}
)


def test_favicon(client: FlaskClient):
    url = "/favicon.ico"
    res: Response = client.get(url)
    assert res.status_code == 200
    assert res.content_type in ["image/x-icon", "image/vnd.microsoft.icon"]


@given(
    width=dim_strategy,
    height=dim_strategy,
    image_format=st.sampled_from(IMG_FORMATS),
    fg_color=color_strategy,
    bg_color=color_strategy,
    args=args_strategy,
)
def test_create_images_using_function(
    config,
    width: int,
    height: int,
    image_format: str,
    fg_color: str,
    bg_color: str,
    args: dict,
):
    app = create_app(config)
    logger.info("fg color: {}, bg color: {}", fg_color, bg_color)

    with app.test_request_context():
        img_args = ImageArgs.from_request(valfilter(bool, args))
        size = (width, height)
        p = save_image(size, bg_color, fg_color, image_format, img_args)
        im = Image.open(p)
        assert im.size == size


@given(
    width=dim_strategy,
    height=dim_strategy,
    image_format=st.sampled_from(IMG_FORMATS),
    fg_color=opt_color_strategy,
    bg_color=opt_color_strategy,
    args=args_strategy,
)
def test_create_images_using_client(
    config,
    width: int,
    height: int,
    image_format: str,
    fg_color: Optional[str],
    bg_color: Optional[str],
    args: dict,
):
    app = create_app(config)
    with app.test_client() as client:
        query = args and urlencode(valfilter(bool, args))
        url = make_route(width, height, bg_color, fg_color, image_format)
        if query:
            url = "?".join([url, query])
        res = client.get(url, follow_redirects=False)
        assert res.status_code == 200
        img_type = imghdr.what("filename", h=res.data)
        assert img_type == image_format
        im = Image.open(io.BytesIO(res.data))
        assert im.size == (width, height)


@pytest.mark.skipif(pytesseract is None, reason="pytesseract not installed")
def test_random_text(client: FlaskClient):
    url = make_route(638, 328, "cef", "555", "png")
    args = {"text": "Some Random Text", "dpi": None, "alpha": None, "random_text": True}
    query = urlencode(valfilter(bool, args))
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
    path = make_route(638, 328, "cef", "555", "png")
    args = {"text": "Some Random Text"}
    query = urlencode(args)
    url = "?".join([path, query])
    forwarded = "123.45.4.2,123.45.4.2"
    res: Response = client.get(url, headers=[("X-Forwarded-For", forwarded)])
    was_forwarded = res.headers.get("X-Was-Forwarded-For", None)
    assert was_forwarded == forwarded
