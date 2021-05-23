import hashlib
import os

from .constants import HERE
from .utils import get_debug


class HashedFile(object):
    __slots__ = (
        "strip_newlines",
        "_orig_file",
        "_last_mtime",
        "_output_file",
        "_out_dir",
    )

    static_dir = HERE / "static"

    def __init__(self, file_name: str, strip_newlines: bool = True):
        self._orig_file = self.static_dir / file_name
        self.strip_newlines = strip_newlines
        self._last_mtime = 0
        self._output_file = None
        self._out_dir = self._orig_file.parent / "dist"
        self._out_dir.mkdir(exist_ok=True)

    @property
    def file_name(self):
        if self._output_file is None or self.outdated:
            self._output_file = self._make_output()
        return str(self._output_file.relative_to(self.static_dir))

    @property
    def outdated(self):
        if not get_debug():
            return False
        mtime = os.path.getmtime(self._orig_file)
        if mtime > self._last_mtime:
            self._last_mtime = mtime
            self._output_file.unlink()
            self._output_file = None
            return True
        return True

    def _make_output(self):
        cts = self._orig_file.read_bytes()
        if self.strip_newlines:
            output_cts = cts.replace(b"\n", b" ").replace(b"  ", b" ")
        else:
            output_cts = cts
        sha256 = hashlib.sha256()
        sha256.update(output_cts)
        digest = sha256.hexdigest()[:12]
        name = ".".join((self._orig_file.stem, digest))
        out_file = (self._out_dir / name).with_suffix(self._orig_file.suffix)
        out_file.write_bytes(output_cts)
        return out_file
