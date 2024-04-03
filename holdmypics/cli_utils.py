from __future__ import annotations

import shlex
import shutil
from subprocess import CompletedProcess, run as _run
from typing import Any, Literal, overload

from loguru import logger

CTX_SETTINGS = {"max_content_width": min(shutil.get_terminal_size().columns, 130)}


@overload
def run(*args: str, text: Literal[True], **kwargs: Any) -> CompletedProcess[str]: ...


@overload
def run(
    *args: str, text: Literal[None, False], **kwargs: Any
) -> CompletedProcess[bytes]: ...


@overload
def run(
    *args: str, text: bool | None = ..., **kwargs: Any
) -> CompletedProcess[Any]: ...


def run(*args: str, no_log: bool = False, **kwargs: Any) -> CompletedProcess[Any]:
    if not no_log:
        logger.info("Running command `{0}`", shlex.join(args))
    kwargs.setdefault("check", True)
    return _run(args, **kwargs)
