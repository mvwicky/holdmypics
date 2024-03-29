from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Callable
from itertools import chain
from operator import itemgetter
from pathlib import Path
from typing import Any, ClassVar

import attrs
from loguru import logger

from ..utils import config_value, get_size, natsize
from .args import BaseImageArgs, TextImageArgs

FNAME_TBL = str.maketrans({"#": "", " ": "-", ".": "", "/": "-", "\\": "-"})
_extensions: tuple[str, ...] = ("png", "webp", "jpg", "jpeg", "gif")


@attrs.define(repr=False)
class GeneratedFiles:
    hash_function: ClassVar[Callable[..., hashlib._Hash]] = hashlib.md5
    fmt_re: ClassVar[re.Pattern[str]] = re.compile(f"\\.({'|'.join(_extensions)})$")

    files: set[str] = attrs.field(factory=set)
    _done_setup: bool = attrs.field(init=False, default=False)
    _images_folder: Path | None = attrs.field(init=False, default=None)
    _max_size: int | None = attrs.field(init=False, default=None)
    _hash_file_names: bool | None = attrs.field(init=False, default=None)

    @classmethod
    def hash_strings(cls, *strings: str) -> str:
        hasher = cls.hash_function()
        [hasher.update(s.encode("utf-8", errors="replace")) for s in strings]
        return hasher.hexdigest()

    @classmethod
    def params_hash(cls, *params: Any) -> str:
        return cls.hash_strings(*map(repr, params))

    def setup(self) -> None:
        folder = self.images_folder
        if not folder.is_dir():
            folder.mkdir(parents=True, exist_ok=True)
        self.find_current()
        self._done_setup = True

    def get_current_files(self) -> list[str]:
        folder = self.images_folder
        files = filter(self.fmt_re.search, os.listdir(folder))
        return [os.path.join(folder, f) for f in files]

    def find_current(self) -> None:
        self.files.update(self.get_current_files())

    def get_current_size(self) -> int:
        files = self.get_current_files()
        size = sum(map(get_size, files))
        logger.debug("Total: {0}, Max: {1}", *map(natsize, (size, self.max_size)))
        return size

    @property
    def max_size(self) -> int:
        if self._max_size is None:
            self._max_size = config_value("SAVED_IMAGES_MAX_SIZE", assert_is=int)
        return self._max_size

    @property
    def images_folder(self) -> Path:
        if self._images_folder is None:
            self._images_folder = config_value("SAVED_IMAGES_CACHE_DIR", assert_is=Path)
        return self._images_folder

    @property
    def hash_file_names(self) -> bool:
        if self._hash_file_names is None:
            self._hash_file_names = config_value("HASH_IMG_FILE_NAMES", assert_is=bool)
        return self._hash_file_names

    @property
    def need_to_clean(self) -> bool:
        return self.get_current_size() > self.max_size

    def get_file_name(
        self,
        size: tuple[int, int],
        bg: str,
        fg: str,
        fmt: str,
        args: BaseImageArgs,
        *extra: Any,
    ) -> str:
        if not self._done_setup:
            self.setup()
        if isinstance(args, TextImageArgs) and args.text:
            args = attrs.evolve(args, text=self.hash_strings(args.text))
        params = chain(("x".join(map(str, size)), bg, fg, fmt), args.to_seq(), extra)
        base_name: str
        if not self.hash_file_names:
            base_name = "-".join(map(str, params)).translate(FNAME_TBL)
        else:
            base_name = self.params_hash(*params)
        path = os.path.join(self.images_folder, f"{base_name}.{fmt}")
        self.files.add(path)
        return path

    def collect_for_cleaning(self) -> list[tuple[str, int, float]]:
        stats = ((f, f.stat()) for f in self.images_folder.iterdir() if f.is_file())
        files = ((str(f), st.st_size, st.st_atime) for f, st in stats)
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
