import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import attr
import click
import toml
from humanize import naturalsize

CWD: Path = Path.cwd()
FileMeta = Dict[str, str]
FileMetaList = List[FileMeta]


def find_pyproject(start: Path = CWD) -> Path:
    pyproj = start / "pyproject.toml"
    if pyproj.is_file():
        return pyproj
    if start.parent == start:
        raise RuntimeError("Traversed to root, unable to find pyproject.toml")
    return find_pyproject(start.parent)


def fmt_hash(pkg_hash: str, indent: int = 4) -> str:
    spaces = " " * indent
    return f"{spaces}--hash={pkg_hash}"


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
        init_line = f"{self.name}=={self.version}"
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
        lock_data = toml.loads(self.lock_file.read_text())
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

    def write_out(self, msg: str, **kwargs):
        if not isinstance(msg, str):
            msg = str(msg)
        click.secho(msg, **kwargs)

    def sh(self, args: Sequence[str], **kwargs):
        cmd = args
        if not isinstance(cmd, str) and isinstance(cmd, Sequence):
            cmd = " ".join(cmd)
        self.write_out("Running command: `{0}`".format(cmd))
        kwargs.setdefault("cwd", str(self.root_dir))
        return subprocess.run(args, **kwargs)

    def freeze(self, dev: bool = False, no_hashes: bool = False):
        if not self.lock_file.is_file():
            self.sh(["poetry", "lock"], check=True)

        req_cts, num_pkgs = self.make_requirements(dev, no_hashes)
        file = self.req_file(dev)
        write = not file.is_file() or req_cts != file.read_text()
        if write:
            self.write_out(f"Writing new {file.name}")
            file.write_text(req_cts)
        else:
            self.write_out(f"{file.name} unchanged.")
        rel = os.path.relpath(file, self.root_dir)
        sz = naturalsize(os.path.getsize(file))
        self.write_out(f"Froze {num_pkgs} requirements to {rel} ({sz})")
        return write
