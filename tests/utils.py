from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from flask import Flask, url_for

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def make_route(app: Flask | FlaskClient, endpoint: str, **kwargs: Any) -> str:
    if not isinstance(app, Flask):
        app = app.application
    with app.test_request_context():
        return url_for(endpoint, **kwargs)


def compact_dict(mapping: Mapping[str, Any]) -> Mapping[str, Any]:
    return {k: v for (k, v) in mapping.items() if v}


def size_id(sz: tuple[int, int]) -> str:
    return "{0}x{1}".format(*sz)
