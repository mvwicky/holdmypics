from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

from flask import Blueprint
from flask.blueprints import BlueprintSetupState
from flask_cors import CORS

from ..utils import config_value

bp = Blueprint("api", __name__)
CORS(
    bp,
    max_age=timedelta(days=1),
    vary_header=True,
    expose_headers=["Content-Length"],
    allow_headers=["Upgrade-Insecure-Requests"],
)


@bp.record
def api_setup(state: BlueprintSetupState):
    images_folder = config_value(
        "SAVED_IMAGES_CACHE_DIR", app=state.app, assert_is=Path
    )
    if not os.path.isdir(images_folder):
        os.makedirs(images_folder)

    def _before_cb():
        from .files import files

        files.setup()

    bp.before_app_first_request(_before_cb)


from . import routes  # noqa: F401,E402,I202
