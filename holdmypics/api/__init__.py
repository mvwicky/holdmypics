from __future__ import annotations

from datetime import timedelta

from flask import Blueprint
from flask_cors import CORS

bp = Blueprint("api", __name__)
CORS(
    bp,
    max_age=timedelta(days=1),
    vary_header=True,
    expose_headers=["Content-Length"],
    allow_headers=["Upgrade-Insecure-Requests"],
)


from . import routes  # noqa: F401, E402
