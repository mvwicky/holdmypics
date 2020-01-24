import time
from logging.config import dictConfig

from flask import Flask, request, send_from_directory
from flask_redis import FlaskRedis

from config import Config
from .converters import ColorConverter, DimensionConverter

redis_client = FlaskRedis()

CACHE_CONTROL_MAX = "max-age=315360000, public, immutable"


def config_logging():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "wsgi": {
                    "format": "[{asctime}] {levelname} {name} in {module}: {message}",
                    "style": "{",
                },
                "werk": {"format": "{message}", "style": "{"},
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                    "formatter": "wsgi",
                },
                "werk": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                    "formatter": "werk",
                },
            },
            "loggers": {
                "werkzeug": {"handlers": ["werk"]},
                __name__: {"level": "INFO", "handlers": ["wsgi"]},
            },
        }
    )


def create_app(config_class=Config):
    config_logging()

    app = Flask(__name__)
    app.config.from_object(config_class)

    hsts_seconds = app.config["HSTS_SECONDS"]
    HSTS_HEADER = f"max-age={hsts_seconds}; includeSubDomains"

    app.url_map.redirect_defaults = False
    app.url_map.converters.update({"dim": DimensionConverter, "col": ColorConverter})

    redis_client.init_app(app)

    from .core import bp as core_bp

    app.register_blueprint(core_bp)

    from .api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    from . import cli

    cli.register(app)

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

        res.headers["Strict-Transport-Security"] = HSTS_HEADER
        res.headers["X-Powered-By"] = "Flask"
        elapsed = time.monotonic() - request.start_time
        res.headers["X-Processing-Time"] = elapsed

        return res

    @app.route("/favicon.ico")
    def _favicon_route():
        return send_from_directory(app.root_path, "fav.png")

    from .__version__ import __version__

    @app.context_processor
    def _ctx():
        return {"version": __version__}

    return app
