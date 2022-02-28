from __future__ import annotations

from typing import cast

import pytest


def pytest_addoption(parser: pytest.Parser):
    group: pytest.OptionGroup = parser.getgroup("holdmypics")
    group.addoption(
        "--formats",
        nargs="+",
        choices=["webp", "png", "jpeg", "gif"],
        default=["png", "jpeg"],
        help="The image formats to test.",
        dest="image_formats",
    )
    group.addoption("--image-dir", default=None, help="Saved images output directory")


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "image_format" in metafunc.fixturenames:
        fmt = metafunc.config.getoption("image_formats", [])  # type: ignore
        metafunc.parametrize("image_format", cast(list[str], fmt))
