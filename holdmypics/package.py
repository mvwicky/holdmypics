import os
import subprocess
from pathlib import Path
from typing import Optional, Sequence

import attr
from humanize import naturalsize
from loguru import logger

CWD: Path = Path.cwd()


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
    def find_root(cls):
        pyproject = find_pyproject()
        return cls(root_dir=pyproject.parent)

    @property
    def lock_file(self):
        if self._lock_file is None:
            self._lock_file = self.root_dir / "poetry.lock"
        return self._lock_file

    def req_file(self, dev: bool):
        name = "".join(["requirements", "-dev" if dev else "", ".txt"])
        return self.root_dir / name

    def sh(self, args: Sequence[str], **kwargs) -> subprocess.CompletedProcess:
        cmd = args
        if not isinstance(cmd, str) and isinstance(cmd, Sequence):
            cmd = " ".join(cmd)
        logger.info("Running command {0}", cmd)
        kwargs.setdefault("check", True)
        kwargs.setdefault("cwd", str(self.root_dir))
        return subprocess.run(args, **kwargs)

    def export(self, dev: bool, no_hashes: bool) -> str:
        args = ["poetry", "export", "--format", "requirements.txt"]
        if dev:
            args.extend(["--dev", "-E", "tests"])
        if no_hashes:
            args.append("--without-hashes")
        cmd = self.sh(args, stdout=subprocess.PIPE, text=True)
        return cmd.stdout

    def freeze(self, dev: bool = False, no_hashes: bool = False) -> bool:
        if not self.lock_file.is_file():
            self.sh(["poetry", "lock"])

        req_cts = self.export(dev, no_hashes)
        file = self.req_file(dev)
        write = not file.is_file() or req_cts != file.read_text()
        if write:
            logger.info("Writing new {0.name}", file)
            file.write_text(req_cts)
        else:
            logger.info("{0.name} unchanged.", file)
        rel = os.path.relpath(file, self.root_dir)
        sz = naturalsize(os.path.getsize(file))
        logger.success("Froze requirements to {0} ({1})", rel, sz)
        return write
