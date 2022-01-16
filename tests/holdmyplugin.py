from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.config.argparsing import OptionGroup, Parser
    from _pytest.python import Metafunc


def pytest_addoption(parser: "Parser"):
    group: "OptionGroup" = parser.getgroup("holdmypics")
    group.addoption(
        "--formats",
        nargs="+",
        choices=["webp", "png", "jpeg", "gif"],
        default=["png", "jpeg"],
        help="The image formats to test.",
        dest="image_formats",
    )
    group.addoption("--image-dir", default=None, help="Saved images output directory")


def pytest_generate_tests(metafunc: "Metafunc"):
    if "image_format" in metafunc.fixturenames:
        metafunc.parametrize(
            "image_format", metafunc.config.getoption("image_formats", [])
        )
