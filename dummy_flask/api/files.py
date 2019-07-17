import hashlib
import os
from typing import Text

from funcy import ignore

from . import bp
from ..utils import config_value
from .._types import Dimension


ignore_file = ignore(FileNotFoundError, default=None)


class GeneratedFiles(object):
    __slots__ = ("files",)

    hash_function = hashlib.md5
    extensions = ["png", "webp", "jpg", "jpeg"]

    def __init__(self):
        self.files = list()

    def params_hash(
        self,
        size: Dimension,
        bg: Text,
        fg: Text,
        fmt: Text,
        text: Text,
        font_name: Text,
    ):
        params = [size, bg, fg, fmt, text, font_name]
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
    ):
        name = self.params_hash(size, bg, fg, fmt, text, font_name) + "." + fmt
        path = os.path.join(bp.images_folder, name)
        self.files.append(path)
        if len(self.files) >= config_value("SAVED_IMAGES_MAX_NUM", 1):
            self.clean()
        return path

    def clean(self):
        files = [
            os.path.join(bp.images_folder, f)
            for f in os.listdir(bp.images_folder)
        ]
        files = filter(os.path.isfile, files)

        files = sorted(files, key=os.path.getmtime)
        print(files)


files = GeneratedFiles()
