import hashlib
import os
from typing import Text, Optional

from funcy import ignore

from . import bp
from ..utils import config_value
from .._types import Dimension


ignore_file = ignore(FileNotFoundError, default=None)


class GeneratedFiles(object):
    __slots__ = ("files", "_max_files")

    hash_function = hashlib.md5
    extensions = ["png", "webp", "jpg", "jpeg"]

    def __init__(self):
        self.files = []
        self._max_files: Optional[int] = None

    @property
    def max_files(self):
        if self._max_files is None:
            self._max_files = config_value("SAVED_IMAGES_MAX_NUM", 1)
        return self._max_files

    def params_hash(self, *params):
        hasher = self.hash_function()
        for param in params:
            hasher.update(repr(param).encode("utf-8"))
        return hasher.hexdigest()

    def get_file_name(
        self,
        size: Dimension,
        bg: Text,
        fg: Text,
        fmt: Text,
        text: Text,
        font_name: Text,
        dpi: int,
    ):
        phash = self.params_hash(size, bg, fg, fmt, text, font_name, dpi)
        name = ".".join([phash, fmt])
        path = os.path.join(bp.images_folder, name)
        self.files.append(path)
        if len(self.files) > self.max_files:
            self.clean()
        return path

    def clean(self):
        files = [
            os.path.join(bp.images_folder, f)
            for f in os.listdir(bp.images_folder)
        ]
        files = sorted(filter(os.path.isfile, files), key=os.path.getmtime)
        num_deleted = 0
        if len(files) > self.max_files:
            to_delete = files[: self.max_files]
            num_deleted = len([os.unlink(f) for f in to_delete])
        return num_deleted


files = GeneratedFiles()
