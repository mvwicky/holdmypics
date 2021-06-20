from __future__ import annotations

from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import Optional

import attr
from flask import current_app
from loguru import logger
from PIL.ImageFont import ImageFont, truetype

none_attr = partial(attr.ib, default=None, init=False, repr=False)


class UnknownFont(KeyError):
    pass


@attr.s(auto_attribs=True, slots=True)
class Font(object):
    file: Path = attr.ib(converter=Path)
    font_sizes: set[int] = attr.ib(converter=set)

    _sizes: dict[int, ImageFont] = attr.ib(factory=dict, init=False)

    def load(self, sizes: Sequence[int]):
        for size in sizes:
            self[size]

    def __getitem__(self, size: int) -> ImageFont:
        if size not in self._sizes:
            self._sizes[size] = truetype(str(self.file), size=size)
        return self._sizes[size]

    def __contains__(self, size: int) -> bool:
        return size in self.font_sizes


@attr.s(auto_attribs=True, slots=True)
class Fonts(object):
    font_sizes: list[int] = attr.ib(
        default=range(4, 289, 4), converter=list, init=False, repr=False
    )

    _font_dir: Optional[Path] = none_attr()
    _font_files: dict[str, Path] = none_attr()
    _fonts: dict[str, Font] = attr.ib(factory=dict, init=False, repr=False)
    _num_sizes: Optional[int] = none_attr()
    _font_names: set[str] = none_attr()
    _max_size: int = none_attr()
    _min_size: int = none_attr()

    @property
    def num_sizes(self) -> int:
        if self._num_sizes is None:
            self._num_sizes = len(self.font_sizes)
        return self._num_sizes

    @property
    def font_dir(self) -> Path:
        if self._font_dir is None:
            self._font_dir = Path(current_app.root_path) / "fonts"
        return self._font_dir

    @property
    def font_files(self) -> dict[str, Path]:
        if self._font_files is None:
            font_dir = self.font_dir
            self._font_files = {f.stem: f for f in font_dir.glob("*.ttf")}
        return self._font_files

    @property
    def font_names(self) -> set[str]:
        if self._font_names is None:
            self._font_names = set(self.font_files)
        return self._font_names

    @property
    def max_size(self) -> int:
        if self._max_size is None:
            self._max_size = max(self.font_sizes)
        return self._max_size

    @property
    def min_size(self) -> int:
        if self._min_size is None:
            self._min_size = min(self.font_sizes)
        return self._min_size

    def __getitem__(self, key: str) -> Font:
        if key not in self._fonts:
            font_file = self.font_files.get(key)
            if font_file is not None:
                logger.debug("Loading font {0}", key)
                self._fonts[key] = Font(font_file, self.font_sizes)
            else:
                raise UnknownFont(key)
        return self._fonts[key]


fonts = Fonts()
