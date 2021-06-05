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
    group.addoption(
        "--widths",
        nargs="+",
        type=int,
        default=[4096],
        help="The width values to create.",
    )
    group.addoption(
        "--heights",
        nargs="+",
        type=int,
        default=[2160],
        help="The height values to create.",
    )
    group.addoption(
        "--dpis", nargs="+", default=[72], type=int, help="The dpi values to use."
    )
    group.addoption("--no-empty-dpi", action="store_true", dest="no_empty_dpi")
    parser.addini("empty-dpi", "Add a `None` value for dpi.", type="bool", default=True)
    parser.addini("trace-mem", "Trace memory allocations.", type="bool", default=False)
