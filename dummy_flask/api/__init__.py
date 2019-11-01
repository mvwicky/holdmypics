import os

from flask import Blueprint, Config
from flask.blueprints import BlueprintSetupState
from flask_cors import CORS

bp = Blueprint("api", __name__)
CORS(bp)


@bp.record
def api_setup(state: BlueprintSetupState):
    cfg: Config = state.app.config
    images_folder = cfg["SAVED_IMAGES_CACHE_DIR"]
    os.makedirs(images_folder, exist_ok=True)
    bp.images_folder = images_folder


from . import routes  # noqa: F401
