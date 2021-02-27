from __future__ import annotations

import hashlib
import os
import re
from typing import Optional

import attr
from flask import current_app

from .._types import Dimension
from . import bp
from .args import ImageArgs

fname_tbl = str.maketrans({"#": "", " ": "-", ".": "", "/": "-", "\\": "-"})


class GeneratedFiles(object):
    __slots__ = ("files", "_max_files")

    hash_function = hashlib.md5
    extensions = ["png", "webp", "jpg", "jpeg", "gif"]
    fmt_re: re.Pattern = re.compile("\\.({0})$".format("|".join(extensions)))

    def __init__(self) -> None:
        self.files: set[str] = set()
        self._max_files: Optional[int] = None

    def find_current(self) -> None:
        images_folder = self.images_folder
        files = filter(self.fmt_re.search, os.listdir(images_folder))
        for file in files:
            self.files.add(os.path.join(images_folder, file))

    @property
    def max_files(self) -> int:
        if self._max_files is None:
            self._max_files = bp.max_files  # type: ignore
        return self._max_files

    @property
    def images_folder(self) -> str:
        return bp.images_folder  # type: ignore

    @property
    def need_to_clean(self) -> bool:
        return len(self.files) > self.max_files

    def hash_strings(self, *strings: str) -> str:
        hasher = self.hash_function()  # type: ignore
        for s in strings:
            hasher.update(s.encode("utf-8"))
        return hasher.hexdigest()

    def params_hash(self, *params) -> str:
        return self.hash_strings(*map(repr, params))

    def get_file_name(
        self, size: Dimension, bg: str, fg: str, fmt: str, args: ImageArgs
    ) -> str:
        if args.text:
            args = attr.evolve(args, text=self.hash_strings(args.text))
        args = attr.astuple(args)
        if not current_app.config.get("HASH_IMG_FILE_NAMES", True):
            parts = ["x".join(map(str, size)), bg, fg] + list(args)
            base_name = "-".join(map(str, parts)).translate(fname_tbl)
            name = ".".join([base_name, fmt])
        else:
            phash = self.params_hash(size, bg, fg, fmt, *args)
            name = ".".join([phash, fmt])
        path = os.path.join(self.images_folder, name)
        self.files.add(path)

        return path

    def collect_for_cleaning(self) -> list[str]:
        images_folder = self.images_folder
        files = [os.path.join(images_folder, f) for f in os.listdir(images_folder)]
        return sorted(filter(os.path.isfile, files), key=os.path.getatime)

    def clean(self) -> int:
        files = self.collect_for_cleaning()
        num_deleted, num_files = 0, len(files)
        if len(files) > self.max_files:
            n = max(num_files - self.max_files, num_files // 2)
            to_delete, num_deleted = files[:n], 0
            for f in to_delete:
                os.unlink(f)
                num_deleted += 1
        self.files.clear()
        self.find_current()
        return num_deleted


files = GeneratedFiles()
