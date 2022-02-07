from __future__ import annotations

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
        metafunc.parametrize(
            "image_format", metafunc.config.getoption("image_formats", [])
        )
