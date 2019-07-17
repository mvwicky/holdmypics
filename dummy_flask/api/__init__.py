import os

from flask import Blueprint
from flask.blueprints import BlueprintSetupState

bp = Blueprint("api", __name__)


@bp.record
def api_setup(state: BlueprintSetupState):
    images_folder = os.path.join(bp.root_path, "images")
    os.makedirs(images_folder, exist_ok=True)
    bp.images_folder = images_folder


from . import routes  # noqa: F401
