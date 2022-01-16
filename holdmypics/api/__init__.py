import os
from datetime import timedelta

from flask import Blueprint
from flask.blueprints import BlueprintSetupState
from flask_cors import CORS

from ..utils import config_value

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
    images_folder: str = config_value("SAVED_IMAGES_CACHE_DIR", app=state.app)
    max_size: int = config_value("SAVED_IMAGES_MAX_SIZE", app=state.app)
    hash_files: bool = config_value("HASH_IMG_FILE_NAMES", app=state.app)
    if not os.path.isdir(images_folder):
        os.makedirs(images_folder)
    bp.images_folder = images_folder  # type: ignore
    bp.max_size = max_size  # type: ignore
    bp.hash_file_names = hash_files  # type: ignore

    def _before_cb():
        from .files import files

        files.setup(images_folder, max_size, hash_files)

    bp.before_app_first_request(_before_cb)


from . import routes  # noqa: F401,E402,I202
