import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import attr
import tomlkit as toml
from humanize import naturalsize
from loguru import logger

CWD: Path = Path.cwd()
FileMeta = Dict[str, str]
FileMetaList = List[FileMeta]


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


def fmt_hash(pkg_hash: str, indent: int = 4) -> str:
    spaces = " " * indent
    return "{0}--hash={1}".format(spaces, pkg_hash)


@attr.s(slots=True, auto_attribs=True)
class Dependency(object):
    name: str
    version: str
    hashes: List[str] = attr.ib(factory=list, repr=False)
    marker: str = attr.ib(default="", repr=False)

    @classmethod
    def from_lock(cls, elem: Dict[str, str], metadata: FileMetaList) -> "Dependency":
        name, version = elem["name"], elem["version"]
        marker = elem.get("marker", "")
        if "extra == " in marker:
            marker = ""
        hashes = [e["hash"] for e in metadata]
        return cls(name=name, version=version, hashes=hashes, marker=marker)

    def to_line(self, indent: int = 4, no_hashes: bool = False) -> str:
        init_line = "{0.name}=={0.version}".format(self)
        if self.marker:
            init_line = "; ".join([init_line, self.marker])
        if no_hashes:
            return init_line
        init_line = " ".join([init_line, "\\"])
        line = [init_line]
        line.extend([fmt_hash(h, indent) + " \\" for h in self.hashes[:-1]])
        line.append(fmt_hash(self.hashes[-1], indent))
        return "\n".join(line)


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

    def read_lock(self, dev: bool = False):
        lock_data = toml.parse(self.lock_file.read_text())
        file_meta = lock_data["metadata"]["files"]
        for elem in lock_data["package"]:
            if dev or elem["category"] != "dev":
                name = elem["name"]
                yield Dependency.from_lock(elem, file_meta[name])

    def make_requirements(self, dev: bool = False, no_hashes: bool = False):
        frozen_pkgs = []
        for dep in self.read_lock(dev):  # type: Dependency
            frozen_pkgs.append(dep.to_line(no_hashes=no_hashes))
        req = "\n".join(frozen_pkgs) + "\n"
        return req, len(frozen_pkgs)

    def sh(self, args: Sequence[str], **kwargs):
        cmd = args
        if not isinstance(cmd, str) and isinstance(cmd, Sequence):
            cmd = " ".join(cmd)
        logger.info("Running command {0}", cmd)
        kwargs.setdefault("cwd", str(self.root_dir))
        return subprocess.run(args, **kwargs)

    def freeze(self, dev: bool = False, no_hashes: bool = False):
        if not self.lock_file.is_file():
            self.sh(["poetry", "lock"], check=True)

        req_cts, num_pkgs = self.make_requirements(dev, no_hashes)
        file = self.req_file(dev)
        write = not file.is_file() or req_cts != file.read_text()
        if write:
            logger.info("Writing new {0.name}", file)
            file.write_text(req_cts)
        else:
            logger.info("{0.name} unchanged.", file)
        rel = os.path.relpath(file, self.root_dir)
        sz = naturalsize(os.path.getsize(file))
        logger.success("Froze {0} requirements to {1} ({2})", num_pkgs, rel, sz)
        return write
