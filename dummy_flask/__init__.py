import time

from flask import Flask, request
from flask_redis import FlaskRedis

from config import Config
from .converters import DimensionConverter

redis_client = FlaskRedis()

CACHE_CONTROL_MAX = "max-age=315360000, public, immutable"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.url_map.converters["dim"] = DimensionConverter

    redis_client.init_app(app)

    from .core import bp as core_bp

    app.register_blueprint(core_bp)

    from .api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    @app.before_request
    def before_request_cb():
        request.start_time = time.monotonic()

    @app.after_request
    def after_request_cb(res):
        endpoint = request.endpoint
        if endpoint == "core.index":
            res.headers["Cache-Control"] = "max-age=0, no-store"
        elif endpoint == "static":
            name = request.path.split("/")[-1]
            parts = name.split(".")
            if len(parts) == 3:
                res.headers["Cache-Control"] = CACHE_CONTROL_MAX

        res.headers["X-Powered-By"] = "Flask"
        res.headers["X-Processed-Time"] = time.monotonic() - request.start_time

        return res

    return app
