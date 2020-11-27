from flask import Blueprint

bp = Blueprint("core", __name__, template_folder="templates", static_folder="static")

from . import routes  # noqa: F401,E402
