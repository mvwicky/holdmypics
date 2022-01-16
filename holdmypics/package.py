from __future__ import annotations

import os
from collections.abc import Sequence
from pathlib import Path
from subprocess import CompletedProcess
from typing import Any, Optional

import attr
from loguru import logger

from .cli_utils import run
from .utils import natsize

CWD = Path.cwd()


def find_path_named(name: str, start: Path = CWD, file_only: bool = False) -> Path:
    p = start / name
    if p.exists():
        if not file_only or p.is_file():
            return p
    if p.parent == p:
        raise RuntimeError("Traversed to root, unable to find {0}".format(name))
    return find_path_named(name, p.parent, file_only=file_only)


def find_pyproject(start: Path = CWD) -> Path:
    return find_path_named("pyproject.toml", file_only=True)


@attr.s(slots=True, auto_attribs=True, repr=False)
class Package(object):
    root_dir: Path = attr.ib(default=CWD, converter=Path)

    _lock_file: Optional[Path] = attr.ib(default=None, init=False, repr=False)

    @classmethod
    def find_root(cls) -> "Package":
        pyproject = find_pyproject()
        return cls(root_dir=pyproject.parent)

    @property
    def lock_file(self) -> Path:
        if self._lock_file is None:
            self._lock_file = self.root_dir / "poetry.lock"
        return self._lock_file

    def req_file(self, dev: bool) -> Path:
        return self.root_dir / f"requirements-{'-dev' if dev else '.txt'}"

    def sh(self, args: Sequence[str], **kwargs: Any) -> CompletedProcess:
        kwargs = {"cwd": self.root_dir, **kwargs}
        return run(*args, **kwargs)

    def export(self, dev: bool, hashes: bool) -> str:
        args = ["poetry", "export", "--format", "requirements.txt"]
        if dev:
            args.extend(["--dev", "-E", "tests"])
        if not hashes:
            args.append("--without-hashes")
        cmd = self.sh(args, capture_output=True, text=True)
        return cmd.stdout

    def freeze(self, dev: bool = False, hashes: bool = True) -> bool:
        if not self.lock_file.is_file():
            self.sh(["poetry", "lock"])

        req_cts = self.export(dev, hashes)
        file = self.req_file(dev)
        write = not file.is_file() or req_cts != file.read_text()
        if write:
            logger.info("Writing new {0.name}", file)
            file.write_text(req_cts)
        else:
            logger.info("{0.name} unchanged.", file)
        rel = os.path.relpath(file, self.root_dir)
        sz = natsize(os.path.getsize(file))
        logger.success("Froze requirements to {0} ({1})", rel, sz)
        return write
