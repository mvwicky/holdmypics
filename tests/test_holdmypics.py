import imghdr
import io
import itertools as it
from typing import Optional

import pytest
from flask.testing import FlaskClient
from funcy import compact
from PIL import Image

size = "638x328"
bg_color = "123"
fg_color = "aaa"
bg_colors = ["123", None]
fg_colors = ["aaa", None]
fmts = ["webp", "png", "jpeg", "gif"]


def make_route(
    width: int, height: int, bg_color: str = None, fg_color: str = None, fmt: str = None
):
    if not any([bg_color, fg_color, fmt]):
        pytest.fail("Can't make a route with just size")
    parts = [f"{width}x{height}", bg_color, fg_color, fmt]
    return "/api/" + "/".join(compact(parts)) + "/"


_routes = it.chain.from_iterable(
    (
        [
            f"{size}/{bg_color}/{fg_color}/{fmt}/",
            f"{size}/{bg_color}/{fg_color}/",
            f"{size}/{bg_color}/{fmt}/",
            f"{size}/{fmt}/",
            f"{size}/{bg_color}/",
        ]
        for fmt in fmts
    )
)

routes = ["/api/" + r for r in _routes]


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


# @pytest.mark.parametrize("route", routes)
# def test_full_params(client: FlaskClient, route):
# assert not files.max_files
# res = client.get(route, follow_redirects=True)
# assert res.status_code == 200
# files.clean()
# assert files.clean()


@pytest.mark.parametrize("width", [100, 4096])
@pytest.mark.parametrize("height", [100, 4096])
@pytest.mark.parametrize("fg_color", fg_colors)
@pytest.mark.parametrize("bg_color", bg_colors)
@pytest.mark.parametrize("fmt", fmts)
def test_different_params(
    client: FlaskClient,
    width: int,
    height: int,
    fmt: str,
    fg_color: Optional[str],
    bg_color: Optional[str],
):
    if any([bg_color, fg_color, fmt]):
        path = make_route(width, height, bg_color, fg_color, fmt)
        res = client.get(path, follow_redirects=False)
        assert res.status_code == 200
        img_type = imghdr.what("filename", h=res.data)
        assert img_type == fmt
        im = Image.open(io.BytesIO(res.data))
        assert im.size == (width, height)
