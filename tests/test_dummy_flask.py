import pytest

from dummy_flask.__version__ import __version__


@pytest.fixture()
def app():
    from config import Config
    from dummy_flask import create_app

    class TestConfig(Config):
        TESTING = True

    app = create_app(TestConfig)
    yield app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client


def test_version():
    assert __version__ == "0.2.2"


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200


def test_counter(app):
    pass


def test_full_params(client):
    pass
