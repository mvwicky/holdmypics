import pytest


@pytest.fixture()
def app():
    from holdmypics import create_app

    from config import Config

    class TestConfig(Config):
        DEBUG = False
        TESTING = True
        SAVED_IMAGES_MAX_NUM = 250

    app = create_app(config_class=TestConfig)

    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
