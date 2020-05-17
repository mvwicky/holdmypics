import re
import time
from functools import partial
from pathlib import Path
from typing import Optional

from flask import Flask, Response, request, send_from_directory
from flask_redis import FlaskRedis
from loguru import logger
from werkzeug.debug import DebuggedApplication
from whitenoise import WhiteNoise

from config import Config
from .converters import ColorConverter, DimensionConverter
from .logging import config_logging, log_request
from .wrapped_redis import WrappedRedis

redisw = WrappedRedis()
redis_client = FlaskRedis()

HERE: Path = Path(__file__).resolve().parent


CACHE_CONTROL_MAX = "max-age=315360000, public, immutable"

exts = ["woff", "woff2", "js", "css"]
exts_rev = [e[::-1] + "." for e in exts]
exts_group = "|".join(exts_rev)
EXT_RE = re.compile("^(?:{0})".format(exts_group))


def wn_add_headers(headers, path, url):
    logger.info("Serving static file: {0}", url)
    headers["X-Powered-By"] = "Flask/WhiteNoise"


def immutable_file_test(path: str, url: str) -> bool:
    parts = url.rsplit("/", 1)
    if len(parts) == 1:
        return False
    filename: str = parts[1]
    is_immutable = filename.count(".") > 1 and bool(EXT_RE.match(filename[::-1]))
    if is_immutable:
        logger.debug("File is immutable: {0}", url)
    return is_immutable


def configure_hsts(app: Flask):
    hsts_seconds = app.config.get("HSTS_SECONDS", 0)
    hsts_preload = app.config.get("HSTS_PRELOAD", False)
    include_sub = app.config.get("HSTS_INCLUDE_SUBDOMAINS", False)
    if hsts_seconds:
        parts = [
            "max-age={0}".format(hsts_seconds),
            "includeSubDomains" if include_sub else False,
            "preload" if hsts_preload else False,
        ]
        return "; ".join(filter(bool, parts))
    else:
        return None


def after_request_callback(hsts_header: Optional[str], res: Response):
    log_request(res)
    endpoint = request.endpoint
    if endpoint == "core.index":
        res.headers["Cache-Control"] = "max-age=0, no-store"
    elif endpoint == "static":
        name = request.path.split("/")[-1]
        parts = name.split(".")
        if len(parts) == 3:
            res.headers["Cache-Control"] = CACHE_CONTROL_MAX

    if hsts_header is not None:
        res.headers["Strict-Transport-Security"] = hsts_header
    forwarded = request.headers.get("X-Forwarded-For", None)
    if forwarded is not None:
        res.headers["X-Was-Forwarded-For"] = forwarded
    res.headers["X-Powered-By"] = "Flask"
    elapsed = time.monotonic() - request.start_time
    res.headers["X-Processing-Time"] = elapsed
    return res


def create_app(config=Config):
    log_file_name = config.LOG_FILE_NAME or __name__
    config_logging(__name__, log_file_name, config.LOG_DIR, config.LOG_LEVEL)

    app = Flask(__name__)
    app.config.from_object(config)

    HSTS_HEADER = configure_hsts(app)

    app.url_map.redirect_defaults = False
    app.url_map.converters.update({"dim": DimensionConverter, "col": ColorConverter})

    redisw.init_app(app, redis_client)

    from . import core, api, cli, __version__

    app.register_blueprint(core.bp)
    app.register_blueprint(api.bp, url_prefix="/api")
    cli.register(app)

    base_path = app.config.get("BASE_PATH")

    app.wsgi_app = WhiteNoise(
        app.wsgi_app,
        autorefresh=True,
        add_headers_function=wn_add_headers,
        immutable_file_test=immutable_file_test,
    )

    app.wsgi_app.add_files(str(HERE / "static"), prefix="static/")
    app.wsgi_app.add_files(str(base_path / "static"), prefix="static/")

    if config.DEBUG:
        app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    @app.before_request
    def before_request_cb():
        request.start_time = time.monotonic()

    app.after_request(partial(after_request_callback, HSTS_HEADER))

    @app.route("/favicon.ico")
    def _favicon_route():
        return send_from_directory(app.root_path, "fav.ico")

    @app.context_processor
    def _ctx():
        return {"version": __version__.__version__}

    logger.debug("Created App {0!r}", app)
    return app
