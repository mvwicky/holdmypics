import imghdr
import io
import os
import random
from typing import Optional
from urllib.parse import urlencode

import pytesseract
import pytest
from cytoolz import valfilter
from flask import Flask, Response
from flask.testing import FlaskClient
from loguru import logger
from PIL import Image

SKIP_INDEX = os.environ.get("TESTS_SKIP_INDEX", None) is not None


def random_color() -> str:
    """Generate a random hex string."""
    return "".join(["{0:02x}".format(random.randrange(1 << 8)) for _ in range(3)])


bg_colors = ["Random", None]
fg_colors = ["Random", None]
fmts = ["webp", "png", "jpeg"]
texts = ["An bunch of words here", None]


def make_route(
    width: int, height: int, bg_color: str = None, fg_color: str = None, fmt: str = None
):
    if not any([bg_color, fg_color, fmt]):
        pytest.fail("Can't make a route with just size")
    parts = ["{0}x{1}".format(width, height), bg_color, fg_color, fmt]
    return "/api/" + "/".join(filter(bool, parts)) + "/"


def make_url(
    width: int, height: int, fmt: int, bg_color: str, fg_color: str, text: str
):
    path = make_route(width, height, bg_color, fg_color, fmt)
    if text is not None:
        query = urlencode({"text": text})
        return "?".join([path, query])
    else:
        return path


@pytest.mark.skipif(SKIP_INDEX, reason="Doesn't work.")
def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


@pytest.fixture(name="fg_color", params=fg_colors)
def fg_color_fixture(request):
    return random_color() if request.param else request.param


@pytest.fixture(name="bg_color", params=bg_colors)
def bg_color_fixture(request):
    return random_color() if request.param else request.param


@pytest.fixture(name="text", params=texts, ids=["Words", "None"])
def text_fixture(request):
    return request.param


@pytest.fixture(name="alpha", params=[0.75, None])
def alpha_fixture(request):
    return request.param


@pytest.fixture(name="args")
def args_fixture(text, dpi, alpha):
    return {"text": text, "dpi": dpi, "alpha": alpha}


@pytest.fixture(name="query")
def query_fixture(args):
    return args and urlencode(valfilter(bool, args))


def test_create_images_using_function(
    app: Flask,
    width: int,
    height: int,
    image_format: str,
    fg_color: str,
    bg_color: str,
    args: dict,
):
    from holdmypics.api.args import ImageArgs
    from holdmypics.api.img import make_image
    from holdmypics.api.utils import get_color

    with app.test_request_context():
        img_args = ImageArgs.from_request(valfilter(bool, args))
        size = (width, height)
        im = make_image(
            size,
            get_color(bg_color or "000"),
            get_color(fg_color or "aaa"),
            image_format,
            img_args,
        )
        assert im.size == size


def test_create_images_using_client(
    client: FlaskClient,
    width: int,
    height: int,
    image_format: str,
    fg_color: Optional[str],
    bg_color: Optional[str],
    query: str,
):
    url = make_route(width, height, bg_color, fg_color, image_format)
    if query is not None:
        url = "?".join([url, query])
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    img_type = imghdr.what("filename", h=res.data)
    assert img_type == image_format
    im = Image.open(io.BytesIO(res.data))
    assert im.size == (width, height)


@pytest.mark.parametrize(
    "random_text", [True, False], ids=["random_text", "no_random_text"]
)
def test_just_run_once(client: FlaskClient, random_text: bool):
    url = make_route(638, 328, "cef", "555", "png")
    args = {
        "text": "Some Random Text",
        "dpi": None,
        "alpha": None,
        "random_text": random_text,
    }
    query = urlencode(valfilter(bool, args))
    url = "?".join([url, query])
    res: Response = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    img_type = imghdr.what("filename", h=res.data)
    assert img_type == "png"
    im = Image.open(io.BytesIO(res.data))
    assert im.size == (638, 328)
    if random_text:
        headers = res.headers
        from_header = headers.get("X-Random-Text")
        assert from_header is not None
        from_ocr = pytesseract.image_to_string(im)
        logger.info("Got text from OCR: {0}", from_ocr)
        assert from_ocr == from_header


def test_forwarding_headers(client: FlaskClient):
    path = make_route(638, 328, "cef", "555", "png")
    args = {"text": "Some Random Text"}
    query = urlencode(args)
    url = "?".join([path, query])
    forwarded = "123.45.4.2,123.45.4.2"
    res: Response = client.get(url, headers=[("X-Forwarded-For", forwarded)])
    was_forwarded = res.headers.get("X-Was-Forwarded-For", None)
    assert was_forwarded == forwarded
