import logging.config
import time
import subprocess

import click
from flask import Flask, request, send_from_directory
from flask_redis import FlaskRedis

from config import Config
from .converters import DimensionConverter

redis_client = FlaskRedis()

CACHE_CONTROL_MAX = "max-age=315360000, public, immutable"


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    gmsg = click.style("{message}", fg="green")
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "[{asctime}] {levelname} {name} in {module}: {message}",
                    "style": "{",
                },
                "werk": {"format": gmsg, "style": "{"},
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                    "formatter": "default",
                },
                "werk": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                    "formatter": "werk",
                },
            },
            "loggers": {
                "werkzeug": {"handlers": ["werk"]},
                app.name: {"level": "INFO", "handlers": ["wsgi"]},
            },
        }
    )

    app.url_map.converters["dim"] = DimensionConverter

    redis_client.init_app(app)

    from .core import bp as core_bp

    app.register_blueprint(core_bp)

    from .api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    from . import cli

    cli.register(app)

    if app.config.get("ENV") == "development":

        @app.before_first_request
        def _before_first():
            app.logger.info(click.style("BEFORE", fg="yellow"))
            subprocess.run(["make", "dev"])

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
        elapsed = time.monotonic() - request.start_time
        res.headers["X-Processing-Time"] = elapsed

        return res

    @app.route("/favicon.ico")
    def _favicon_route():
        return send_from_directory(app.root_path, "fav.png")

    return app
