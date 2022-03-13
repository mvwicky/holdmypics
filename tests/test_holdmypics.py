from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING
from urllib.parse import urlencode

import pytest
from attrs import fields_dict
from flask import url_for
from flask.testing import FlaskClient
from hypothesis import given

from tests.utils import color_strategy

if TYPE_CHECKING:
    from holdmypics.api.args import BaseImageArgs, BaseImageArgsSchema

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


def match_color(color: str):
    from holdmypics.converters import ColorConverter

    return re.match(ColorConverter.regex, color)


@given(string=color_strategy)
def test_color_validator_accepts(string: str):
    assert match_color(string) is not None


@pytest.mark.parametrize("string", ["ee7733f"])
def test_color_validator_rejects(string: str):
    assert match_color(string) is None


def cmp_args(args_type: type[BaseImageArgs], schema_type: type[BaseImageArgsSchema]):
    args_fields = set(fields_dict(args_type))
    schema_fields = set(schema_type().fields)
    assert args_fields == schema_fields


def test_image_args_schemas():
    from holdmypics.api import args

    cmp_args(args.TextImageArgs, args.TextImageArgsSchema)
    cmp_args(args.TiledImageArgs, args.TiledImageArgsSchema)
