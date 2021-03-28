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
    images_folder: str = cfg["SAVED_IMAGES_CACHE_DIR"]
    max_size: int = cfg["SAVED_IMAGES_MAX_SIZE"]
    hash_files: bool = cfg["HASH_IMG_FILE_NAMES"]
    if not os.path.isdir(images_folder):
        os.makedirs(images_folder)
    bp.images_folder = images_folder
    bp.max_size = max_size
    bp.hash_file_names = hash_files

    def _before_cb():
        from .files import files

        files.setup(images_folder, max_size, hash_files)
        files.find_current()

    bp.before_app_first_request(_before_cb)


from . import routes  # noqa: F401,E402
