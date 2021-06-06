import shlex
import shutil
import subprocess
from typing import Any

from loguru import logger

CTX_SETTINGS = {"max_content_width": min(shutil.get_terminal_size().columns, 130)}


def run(*args: str, no_log: bool = False, **kwargs: Any) -> subprocess.CompletedProcess:
    if not no_log:
        logger.info("Running command `{0}`", shlex.join(args))
    kwargs.setdefault("check", True)
    return subprocess.run(args, **kwargs)
