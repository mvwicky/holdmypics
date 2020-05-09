from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from _pytest.config import Config
    from _pytest.config.argparsing import Parser, OptionGroup
    from _pytest.python import Metafunc


def pytest_addoption(parser: "Parser"):
    group = parser.getgroup("holdmypics")  # type: OptionGroup
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
        "--dpis", nargs="+", default=[72], type=int, help="The dpi values to use.",
    )
    group.addoption("--no-empty-dpi", action="store_true", dest="no_empty_dpi")
    parser.addini("empty-dpi", "Add a `None` value for dpi.", type="bool", default=True)
    parser.addini("trace-mem", "Trace memory allocations.", type="bool", default=False)


def param_list(metafunc: "Metafunc", name: str, pname: str = None):
    if pname is None:
        pname = name + "s"
    if name in metafunc.fixturenames:
        items = metafunc.config.getoption(pname)
        metafunc.parametrize(name, items)


def pytest_configure(config: "Config"):
    fmt = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] | "
        "<level>{level:<8}</level> | "
        "<blue>{name}</blue>:<cyan>{line}</cyan> - <bold>{message}</bold>"
    )
    logger.add(
        "log/holdmyplugin.log",
        format=fmt,
        level="DEBUG",
        filter={__name__: "DEBUG", "tests": "DEBUG"},
    )


def pytest_generate_tests(metafunc: "Metafunc"):
    config = metafunc.config
    fixtures = metafunc.fixturenames
    param_list(metafunc, "image_format")
    if "height" in fixtures:
        heights = config.getoption("heights")
        metafunc.parametrize("height", heights)
    if "width" in fixtures:
        widths = config.getoption("widths")
        metafunc.parametrize("width", widths)
    if "dpi" in fixtures:
        dpis = config.getoption("dpis")
        opt: bool = config.getoption("no_empty_dpi", False)
        ini: bool = config.getini("empty-dpi")
        if not opt and ini and None not in dpis:
            dpis.append(None)
        metafunc.parametrize("dpi", dpis)
