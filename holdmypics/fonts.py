from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Optional, Union

from attrs import define, field
from flask import current_app
from loguru import logger
from PIL.ImageFont import FreeTypeFont, ImageFont, truetype


class UnknownFont(KeyError):
    pass


@define()
class Font(object):
    file: Path = field(converter=Path)
    font_sizes: set[int] = field(converter=set)

    _sizes: dict[int, Union[ImageFont, FreeTypeFont]] = field(factory=dict, init=False)

    def load(self, sizes: Sequence[int]):
        for size in sizes:
            self[size]

    def __getitem__(self, size: int) -> Union[ImageFont, FreeTypeFont]:
        if size not in self._sizes:
            self._sizes[size] = truetype(str(self.file), size=size)
        return self._sizes[size]

    def __contains__(self, size: int) -> bool:
        return size in self.font_sizes


@define()
class Fonts(object):
    font_sizes: list[int] = field(
        default=range(4, 289, 4), converter=list, init=False, repr=False
    )

    _font_dir: Optional[Path] = field(default=None, init=False, repr=False)
    _font_files: Optional[dict[str, Path]] = field(default=None, init=False, repr=False)
    _fonts: dict[str, Font] = field(factory=dict, init=False, repr=False)
    _num_sizes: Optional[int] = field(default=None, init=False, repr=False)
    _font_names: Optional[set[str]] = field(default=None, init=False, repr=False)
    _max_size: Optional[int] = field(default=None, init=False, repr=False)
    _min_size: Optional[int] = field(default=None, init=False, repr=False)

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
                self._fonts[key] = Font(font_file, set(self.font_sizes))
            else:
                raise UnknownFont(key)
        return self._fonts[key]


fonts = Fonts()
