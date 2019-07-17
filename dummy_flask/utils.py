import re
import hashlib
import os

from funcy import merge
from flask import current_app

from .constants import (
    HERE,
    bg_color_default,
    fg_color_default,
    fmt_default,
    img_formats,
)


def get_debug():
    return current_app.config.get("DEBUG", False)


def make_rules():
    fmt_rule = f"<any({img_formats}):fmt>"
    colors_default = merge(bg_color_default, fg_color_default)
    rule_parts = [
        ("<any(jpg,jpeg,gif,png):fmt>", colors_default),
        ("<string:bg_color>", merge(fg_color_default, fmt_default)),
        ("<string:bg_color>/<string:fg_color>", fmt_default),
        (f"<string:bg_color>/{fmt_rule}", fg_color_default),
        (f"<string:bg_color>/<string:fg_color>/{fmt_rule}", dict()),
    ]
    return rule_parts


class StyleFile(object):
    __slots__ = ("_orig_file", "_last_mtime", "_output_file", "_out_dir")

    static_dir = HERE / "static"
    white_re = re.compile(rb"\s\s")

    def __init__(self):
        self._orig_file = self.static_dir / "styles.css"
        self._last_mtime = 0
        self._output_file = None
        self._out_dir = self._orig_file.parent / "dist"
        self._out_dir.mkdir(exist_ok=True)

    @property
    def file_name(self):
        if self._output_file is None or self.outdated:
            self._output_file = str(self._make_output())
        return self._output_file

    @property
    def outdated(self):
        if not get_debug():
            return False
        mtime = os.path.getmtime(self._orig_file)
        if mtime > self._last_mtime:
            self._last_mtime = mtime
            self._output_file = None
            return True
        return True

    def _make_output(self):
        cts = self._orig_file.read_bytes()
        output_cts = cts.replace(b"\n", b" ").replace(b"  ", b" ")
        sha256 = hashlib.sha256()
        sha256.update(output_cts)
        digest = sha256.hexdigest()[:12]
        suffix = self._orig_file.suffix
        name = self._orig_file.stem + "." + digest + suffix
        out_file = self._out_dir / name
        out_file.write_bytes(output_cts)
        return out_file.relative_to(self.static_dir)


style_file = StyleFile()
