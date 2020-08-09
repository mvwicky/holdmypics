from typing import TYPE_CHECKING, Any, Optional, Sequence

from loguru import logger

if TYPE_CHECKING:
    from _pytest.config import Config
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


def param_list(
    metafunc: "Metafunc", name: str, pname: str = None, base_name: Optional[str] = None
):
    if pname is None:
        pname = name + "s"
    if name in metafunc.fixturenames:
        items = metafunc.config.getoption(pname)
        parametrize(metafunc, name, items, base_name)


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


def idfn(base: str):
    def name_fn(value):
        return f"{base}={value}"

    return name_fn


def parametrize(
    metafunc: "Metafunc",
    name: str,
    items: Sequence[Any],
    base_name: Optional[str] = None,
):
    metafunc.parametrize(name, items, ids=idfn(base_name or name))


def pytest_generate_tests(metafunc: "Metafunc"):
    config = metafunc.config
    fixtures = metafunc.fixturenames
    param_list(metafunc, "image_format", None, "fmt")
    if "height" in fixtures:
        parametrize(metafunc, "height", config.getoption("heights"), "h")
    if "width" in fixtures:
        parametrize(metafunc, "width", config.getoption("widths"), "w")
    if "dpi" in fixtures:
        dpis = config.getoption("dpis")
        opt: bool = config.getoption("no_empty_dpi", False)
        ini: bool = config.getini("empty-dpi")
        if not opt and ini and None not in dpis:
            dpis.append(None)
        parametrize(metafunc, "dpi", dpis)
