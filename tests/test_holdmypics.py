import imghdr
import io
import random
from typing import Optional
from urllib.parse import urlencode

import pytest
from flask import Flask
from flask.testing import FlaskClient
from funcy import compact
from PIL import Image


def random_color() -> str:
    """Generate a random hex string."""
    return "".join([f"{random.randrange(1 << 8):02x}" for _ in range(3)])


bg_colors = ["Random", None]
fg_colors = ["Random", None]
fmts = ["webp", "png", "jpeg"]
texts = ["An bunch of words here", None]


def make_route(
    width: int, height: int, bg_color: str = None, fg_color: str = None, fmt: str = None
):
    if not any([bg_color, fg_color, fmt]):
        pytest.fail("Can't make a route with just size")
    parts = [f"{width}x{height}", bg_color, fg_color, fmt]
    return "/api/" + "/".join(compact(parts)) + "/"


def make_url(
    width: int, height: int, fmt: int, bg_color: str, fg_color: str, text: str
):
    path = make_route(width, height, bg_color, fg_color, fmt)
    if text is not None:
        query = urlencode({"text": text})
        return "?".join([path, query])
    else:
        return path


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


@pytest.fixture(name="width", params=[100, 1000])
def width_fixture(request):
    return request.param


@pytest.fixture(name="height", params=[100, 1000])
def height_fixture(request):
    return request.param


@pytest.fixture(name="fg_color", params=fg_colors)
def fg_color_fixture(request):
    return random_color() if request.param else request.param


@pytest.fixture(name="bg_color", params=bg_colors)
def bg_color_fixture(request):
    return random_color() if request.param else request.param


@pytest.fixture(name="fmt", params=fmts)
def fmt_fixture(request):
    return request.param


@pytest.fixture(name="text", params=texts, ids=["Words", "None"])
def text_fixture(request):
    return request.param


@pytest.fixture(name="dpi", params=[72, None])
def dpi_fixture(request):
    return request.param


@pytest.fixture(name="alpha", params=[0.77, None])
def alpha_fixture(request):
    return request.param


@pytest.fixture(name="args")
def args_fixture(text, dpi, alpha):
    return {"text": text, "dpi": dpi, "alpha": alpha}


@pytest.fixture(name="query")
def query_fixture(args):
    if args:
        return urlencode(args)
    else:
        return None


def test_from_function(
    app: Flask,
    width: int,
    height: int,
    fmt: str,
    fg_color: str,
    bg_color: str,
    args: dict,
):
    from holdmypics.api.args import ImageArgs
    from holdmypics.api.img import make_image
    from holdmypics.api.utils import get_color

    with app.test_request_context():
        img_args = ImageArgs.from_request(compact(args))
        size = (width, height)
        im = make_image(
            size,
            get_color(bg_color or "000"),
            get_color(fg_color or "aaa"),
            fmt,
            img_args,
        )
        assert im.size == size


def test_different_params(
    client: FlaskClient,
    width: int,
    height: int,
    fmt: str,
    fg_color: Optional[str],
    bg_color: Optional[str],
    query: str,
):
    url = make_route(width, height, bg_color, fg_color, fmt)
    if query is not None:
        url = "?".join([url, query])
    res = client.get(url, follow_redirects=False)
    assert res.status_code == 200
    img_type = imghdr.what("filename", h=res.data)
    assert img_type == fmt
    im = Image.open(io.BytesIO(res.data))
    assert im.size == (width, height)
