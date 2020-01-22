import itertools as it

import pytest
from flask.testing import FlaskClient
from funcy import compact


size = "638x328"
bg_color = "123"
fg_color = "aaa"
bg_colors = ["123", None]
fg_colors = ["aaa", None]
fmts = ["webp", "png", "jpg"]


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


def test_counter(client):
    pass


# @pytest.mark.parametrize("route", routes)
# def test_full_params(client: FlaskClient, route):
# assert not files.max_files
# res = client.get(route, follow_redirects=True)
# assert res.status_code == 200
# files.clean()
# assert files.clean()


@pytest.mark.parametrize("width", [100, 300, 1000, 4096])
@pytest.mark.parametrize("height", [100, 300, 1000, 4096])
@pytest.mark.parametrize("fg_color", fg_colors)
@pytest.mark.parametrize("bg_color", bg_colors)
@pytest.mark.parametrize("fmt", fmts)
def test_different_params(client: FlaskClient, width, height, fmt, fg_color, bg_color):
    if any([bg_color, fg_color, fmt]):
        path = make_route(width, height, bg_color, fg_color, fmt)
        res = client.get(path, follow_redirects=False)
        assert res.status_code == 200
