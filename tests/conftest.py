import pytest


@pytest.fixture()
def app():
    from config import Config
    from holdmypics import create_app

    class TestConfig(Config):
        TESTING = True
        SAVED_IMAGES_MAX_NUM = 100

    app = create_app(config_class=TestConfig)

    @app.before_first_request
    def _clean():
        from holdmypics.api.files import files

        files.clean()

    return app


@pytest.fixture()
def client(app):
    with app.test_client() as client:
        yield client
