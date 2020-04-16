import os
import sys
import time
from logging.config import dictConfig
from pathlib import Path

from flask import Flask, request, send_from_directory
from flask_redis import FlaskRedis
from funcy import memoize
from loguru import logger
from whitenoise import WhiteNoise

from config import Config
from .converters import ColorConverter, DimensionConverter
from .wrapped_redis import WrappedRedis

redisw = WrappedRedis()
redis_client = FlaskRedis()

HERE: Path = Path(__file__).resolve().parent


CACHE_CONTROL_MAX = "max-age=315360000, public, immutable"


@memoize
def get_version() -> str:
    from .__version__ import __version__

    return __version__


def config_logging(config_class):
    dictConfig({"version": 1})
    fmt = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] | "
        "<level>{level:<8}</level> | "
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>"
    )
    handlers = [{"sink": sys.stderr, "format": fmt, "level": config_class.LOG_LEVEL}]
    if config_class.LOG_DIR is not None:
        log_dir = Path(os.path.realpath(config_class.LOG_DIR))
        if log_dir.is_dir():
            log_file = log_dir / (__name__ + ".log")
            handlers.append(
                {
                    "sink": log_file,
                    "rotation": 10 * 1024,
                    "level": "DEBUG",
                    "filter": __name__,
                    "compression": "tar.gz",
                    "retention": 5,
                }
            )
    logger.configure(handlers=handlers)


def wn_add_headers(headers, path, url):
    logger.info(f"Serving static file: {url}")
    headers["X-Powered-By"] = "Flask/WhiteNoise"


def create_app(config_class=Config):
    config_logging(config_class)

    app = Flask(__name__)
    app.config.from_object(config_class)

    hsts_seconds = app.config.get("HSTS_SECONDS", 0)
    hsts_preload = app.config.get("HSTS_PRELOAD", False)
    include_sub = app.config.get("HSTS_INCLUDE_SUBDOMAINS", False)
    if hsts_seconds:
        parts = [
            f"max-age={hsts_seconds}",
            "includeSubDomains" if include_sub else False,
            "preload" if hsts_preload else False,
        ]
        HSTS_HEADER = "; ".join(filter(bool, parts))
    else:
        HSTS_HEADER = None

    app.url_map.redirect_defaults = False
    app.url_map.converters.update({"dim": DimensionConverter, "col": ColorConverter})

    redisw.init_app(app, redis_client)

    from . import core, api, cli

    app.register_blueprint(core.bp)
    app.register_blueprint(api.bp, url_prefix="/api")
    cli.register(app)

    base_path = app.config.get("BASE_PATH")

    app.wsgi_app = WhiteNoise(
        app.wsgi_app, autorefresh=True, add_headers_function=wn_add_headers,
    )

    app.wsgi_app.add_files(str(HERE / "static"), prefix="static/")
    app.wsgi_app.add_files(str(base_path / "static"), prefix="static/")

    @app.before_request
    def before_request_cb():
        request.start_time = time.monotonic()

    @app.after_request
    def after_request_cb(res):
        logger.info(
            "{0} - {1} - {2}",
            request.path,
            res.status_code,
            res.headers.get("Content-Length", 0),
        )
        endpoint = request.endpoint
        if endpoint == "core.index":
            res.headers["Cache-Control"] = "max-age=0, no-store"
        elif endpoint == "static":
            name = request.path.split("/")[-1]
            parts = name.split(".")
            if len(parts) == 3:
                res.headers["Cache-Control"] = CACHE_CONTROL_MAX

        if HSTS_HEADER is not None:
            res.headers["Strict-Transport-Security"] = HSTS_HEADER
        res.headers["X-Powered-By"] = "Flask"
        elapsed = time.monotonic() - request.start_time
        res.headers["X-Processing-Time"] = elapsed

        return res

    @app.route("/favicon.ico")
    def _favicon_route():
        return send_from_directory(app.root_path, "fav.ico")

    @app.context_processor
    def _ctx():
        return {"version": get_version()}

    logger.debug(f"Created App {app!r}")
    return app
