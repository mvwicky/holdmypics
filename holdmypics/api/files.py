import hashlib
import os
from typing import Optional

from flask import current_app
from funcy import ignore, re_tester

from .._types import Dimension
from . import bp

ignore_file = ignore(FileNotFoundError, default=None)

fname_tbl = str.maketrans({"#": "", " ": "-", ".": ""})


class GeneratedFiles(object):
    __slots__ = ("files", "_max_files")

    hash_function = hashlib.md5
    extensions = ["png", "webp", "jpg", "jpeg"]

    def __init__(self):
        self.files = set()
        self._max_files: Optional[int] = None

    def find_current(self):
        fmts = "\\.({0})$".format("|".join(self.extensions))
        pred = re_tester(fmts)
        files = filter(pred, os.listdir(bp.images_folder))
        for file in files:
            self.files.add(os.path.join(bp.images_folder, file))

    @property
    def max_files(self) -> int:
        if self._max_files is None:
            self._max_files = bp.max_files
        return self._max_files

    @property
    def need_to_clean(self) -> bool:
        return len(self.files) > self.max_files

    def params_hash(self, *params):
        hasher = self.hash_function()
        for param in params:
            hasher.update(repr(param).encode("utf-8"))
        return hasher.hexdigest()

    def get_file_name(self, size: Dimension, bg: str, fg: str, fmt: str, *args,) -> str:
        if current_app.config.get("DEBUG", False):
            parts = ["x".join(map(str, size)), bg, fg] + list(args)
            base_name = "-".join(map(str, parts)).translate(fname_tbl)
            name = ".".join([base_name, fmt])
        else:
            phash = self.params_hash(size, bg, fg, fmt, *args)
            name = ".".join([phash, fmt])
        path = os.path.join(bp.images_folder, name)
        self.files.add(path)

        return path

    def collect_for_cleaning(self):
        files = [
            os.path.join(bp.images_folder, f) for f in os.listdir(bp.images_folder)
        ]
        return sorted(filter(os.path.isfile, files), key=os.path.getatime)

    def clean(self):
        files = self.collect_for_cleaning()
        num_deleted, num_files = 0, len(files)
        if len(files) > self.max_files:
            num = num_files - self.max_files
            to_delete = files[:num]
            num_deleted = len([os.unlink(f) for f in to_delete])
        self.files.clear()
        self.find_current()
        return num_deleted


files = GeneratedFiles()
