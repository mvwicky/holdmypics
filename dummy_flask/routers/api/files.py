import hashlib
import os
from typing import Callable, ClassVar, List, Optional, Set, Union

import attr
from funcy import ignore, re_tester

from config import Config
from ..._types import Dimension

ignore_file = ignore(FileNotFoundError, default=None)

HashFunction = Callable[[Union[bytes, bytearray, memoryview]], "hashlib._Hash"]


@attr.s(slots=True, auto_attribs=True)
class GeneratedFiles(object):
    hash_function: ClassVar[HashFunction] = hashlib.md5
    extensions: ClassVar[List[str]] = ["png", "webp", "jpg", "jpeg", "gif"]

    files: Set[str] = attr.ib(factory=set)
    _max_files: Optional[int] = None
    _images_folder: Optional[str] = None

    @property
    def images_folder(self):
        if self._images_folder is None:
            self._images_folder = Config.SAVED_IMAGES_CACHE_DIR
        return self._images_folder

    def find_current(self):
        fmts = "\\.({0})$".format("|".join(self.extensions))
        pred = re_tester(fmts)
        files = filter(pred, os.listdir(self.images_folder))
        for file in files:
            self.files.add(os.path.join(self.images_folder, file))

    @property
    def max_files(self) -> int:
        if self._max_files is None:
            self._max_files = Config.SAVED_IMAGES_MAX_NUM
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
        phash = self.params_hash(size, bg, fg, fmt, *args)
        name = ".".join([phash, fmt])
        path = os.path.join(self.images_folder, name)
        self.files.add(path)

        return path

    def clean(self):
        files = [
            os.path.join(self.images_folder, f) for f in os.listdir(self.images_folder)
        ]
        files = sorted(filter(os.path.isfile, files), key=os.path.getmtime)
        num_deleted = 0
        if len(files) > self.max_files:
            to_delete = files[: self.max_files]
            num_deleted = len([os.unlink(f) for f in to_delete])
        self.files.clear()
        self.find_current()
        return num_deleted


files = GeneratedFiles()
