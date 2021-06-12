from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _pytest.config.argparsing import OptionGroup, Parser


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
