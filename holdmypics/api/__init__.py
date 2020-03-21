import os
from datetime import timedelta

from flask import Blueprint, Config
from flask.blueprints import BlueprintSetupState
from flask_cors import CORS

cors_kw = {
    "max_age": timedelta(days=1),
    "vary_header": True,
    "expose_headers": ["Content-Length"],
    "allow_headers": ["Upgrade-Insecure-Requests"],
}

bp = Blueprint("api", __name__)
CORS(bp, **cors_kw)


@bp.record
def api_setup(state: BlueprintSetupState):
    cfg: Config = state.app.config
    images_folder = cfg["SAVED_IMAGES_CACHE_DIR"]
    max_files = cfg["SAVED_IMAGES_MAX_NUM"]
    if not os.path.isdir(images_folder):
        os.makedirs(images_folder)
    bp.images_folder = images_folder
    bp.max_files = max_files

    @bp.before_app_first_request
    def _before_cb():
        from .files import files

        files.find_current()


from . import routes  # noqa: F401
