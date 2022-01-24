from __future__ import annotations

import os
import re
from urllib.parse import urlencode

import pytest
from flask import url_for
from flask.testing import FlaskClient
from hypothesis import given

from holdmypics.converters import ColorConverter
from tests.utils import color_strategy

SKIP_INDEX = os.environ.get("TESTS_SKIP_INDEX", None) is not None


@pytest.mark.skipif(SKIP_INDEX, reason="Not testing client-side stuff.")
def test_index(client: FlaskClient):
    res = client.get("/")
    assert res.status_code == 200


def test_favicon(client: FlaskClient):
    res = client.get("/favicon.ico")
    assert res.status_code == 200
    assert res.content_type in ("image/x-icon", "image/vnd.microsoft.icon")


def test_timing_header(client: FlaskClient):
    with client.application.test_request_context():
        path = url_for(
            "api.image_route",
            size=(638, 328),
            bg_color="cef",
            fg_color="555",
            fmt="png",
        )
    res = client.get(path, follow_redirects=False)
    assert res.status_code == 200
    proc_time = res.headers.get("X-Processing-Time", 0, float)
    assert proc_time is not None


def test_forwarding_headers(client: FlaskClient):
    with client.application.test_request_context():
        path = url_for(
            "api.image_route",
            size=(638, 328),
            bg_color="cef",
            fg_color="555",
            fmt="png",
        )
    args = {"text": "Some Random Text"}
    url = f"{path}?{urlencode(args)}"
    forwarded = "123.45.4.2,123.45.4.2"
    res = client.get(url, headers=[("X-Forwarded-For", forwarded)])
    was_forwarded = res.headers.get("X-Was-Forwarded-For", None)
    assert was_forwarded == forwarded


@given(string=color_strategy)
def test_color_validator_accepts(string: str):
    assert re.match(ColorConverter.regex, string) is not None


@pytest.mark.parametrize("string", ["ee7733f"])
def test_color_validator_rejects(string: str):
    assert re.match(ColorConverter.regex, string) is None
