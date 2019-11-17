import pytest
from flask.testing import FlaskClient

from dummy_flask.__version__ import __version__

size = "638x328"
bg_color = "123"
fg_color = "aaa"
fmt = "webp"

_routes = [
    f"{size}/{bg_color}/{fg_color}/{fmt}/",
    f"{size}/{bg_color}/{fg_color}/",
    f"{size}/{bg_color}/{fmt}/",
    f"{size}/{fmt}/",
    f"{size}/{bg_color}/",
]

routes = ["/api/" + r for r in _routes]


@pytest.fixture()
def app():
    from config import Config
    from dummy_flask import create_app

    class TestConfig(Config):
        TESTING = True
        SAVED_IMAGES_MAX_NUM = 0

    app = create_app(config_class=TestConfig)
    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


def test_version():
    assert __version__ == "0.4.0"


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


def test_counter(client):
    pass


@pytest.mark.parametrize("route", routes)
def test_full_params(client: FlaskClient, route):
    from dummy_flask.api.files import files

    res = client.get(route, follow_redirects=True)
    assert res.status_code == 200
    files.clean()
    # assert files.clean()
