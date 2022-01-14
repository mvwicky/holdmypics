from __future__ import annotations

import hashlib
import os
import re
from itertools import chain
from operator import itemgetter
from typing import Any, ClassVar, Optional

import attr
from loguru import logger

from ..utils import get_size, natsize
from . import bp
from .args import BaseImageArgs

FNAME_TBL = str.maketrans({"#": "", " ": "-", ".": "", "/": "-", "\\": "-"})


@attr.s(slots=True, auto_attribs=True, repr=False)
class GeneratedFiles(object):
    hash_function: ClassVar[hashlib._Hash] = hashlib.md5
    extensions: ClassVar[tuple[str, ...]] = ("png", "webp", "jpg", "jpeg", "gif")
    fmt_re: ClassVar[re.Pattern[str]] = re.compile(
        "\\.({0})$".format("|".join(extensions))
    )

    files: set[str] = attr.ib(factory=set)
    initted: bool = attr.ib(init=False, default=False)
    _images_folder: Optional[str] = attr.ib(init=False, default=None)
    _max_size: Optional[int] = attr.ib(init=False, default=None)
    _hash_file_names: Optional[bool] = attr.ib(init=False, default=None)

    def setup(self, images_folder: str, max_size: int, hash_file_names: bool) -> None:
        self._images_folder = images_folder
        self._max_size = max_size
        self._hash_file_names = hash_file_names
        self.find_current()
        self.initted = True

    def get_current_files(self) -> list[str]:
        folder = self.images_folder
        files = filter(self.fmt_re.search, os.listdir(folder))
        return [os.path.join(folder, f) for f in files]

    def find_current(self) -> None:
        self.files.update(self.get_current_files())

    def get_current_size(self) -> int:
        files = self.get_current_files()
        size = sum(map(get_size, files))
        logger.debug("Total: {0}, Max: {1}", *map(natsize, [size, self.max_size]))
        return size

    @property
    def max_size(self) -> int:
        if self._max_size is None:
            logger.warning("Getting max size property from blueprint")
            self._max_size = bp.max_size
        return self._max_size

    @property
    def images_folder(self) -> str:
        if self._images_folder is None:
            logger.warning("Getting images folder property from blueprint")
            self._images_folder = bp.images_folder
        return self._images_folder

    @property
    def hash_file_names(self) -> bool:
        if self._hash_file_names is None:
            logger.warning("Getting hash file names property from blueprint")
            self._hash_file_names = bp.hash_file_names
        return self._hash_file_names

    @property
    def need_to_clean(self) -> bool:
        return self.get_current_size() > self.max_size

    def hash_strings(self, *strings: str) -> str:
        hasher = self.hash_function()
        for s in strings:
            hasher.update(s.encode("utf-8"))
        return hasher.hexdigest()

    def params_hash(self, *params) -> str:
        return self.hash_strings(*map(repr, params))

    def get_file_name(
        self,
        size: tuple[int, int],
        bg: str,
        fg: str,
        fmt: str,
        args: BaseImageArgs,
        *extra: Any,
    ) -> str:
        if getattr(args, "text", None):
            args = attr.evolve(args, text=self.hash_strings(args.text))
        args = args.to_seq()
        params = chain(["x".join(map(str, size)), bg, fg, fmt], args, extra)
        base_name: str
        if not self.hash_file_names:
            base_name = "-".join(map(str, params)).translate(FNAME_TBL)
        else:
            base_name = self.params_hash(*params)
        name = ".".join((base_name, fmt))
        path = os.path.join(self.images_folder, name)
        self.files.add(path)
        return path

    def collect_for_cleaning(self) -> list[tuple[str, int, int]]:
        images_folder = self.images_folder
        files = (os.path.join(images_folder, f) for f in os.listdir(images_folder))
        files = (
            (f, get_size(f), os.path.getatime(f)) for f in filter(os.path.isfile, files)
        )
        return sorted(files, key=itemgetter(2))

    def clean(self) -> int:
        files = self.collect_for_cleaning()[::-1]
        total_size = sum(map(itemgetter(1), files))
        num_deleted, max_size = 0, self.max_size // 2
        while files and total_size > max_size:
            file, size, _ = files.pop()
            os.unlink(file)
            num_deleted += 1
            total_size -= size
        self.files.clear()
        self.find_current()
        return num_deleted


files = GeneratedFiles()
