from functools import partial
from pathlib import Path
from typing import Dict, List, Optional, Set

import attr
from flask import current_app
from PIL import ImageFont

none_attr = partial(attr.ib, default=None, init=False)


@attr.s(auto_attribs=True, slots=True)
class Fonts(object):
    font_sizes: List[int] = attr.ib(factory=partial(list, range(4, 289, 4)), init=False)
    _font_dir: Optional[Path] = none_attr()
    _font_files: Dict[str, Path] = none_attr()
    _fonts: Dict[str, Dict[int, ImageFont.ImageFont]] = none_attr()
    _num_sizes: Optional[int] = none_attr()
    _font_names: Set[str] = none_attr()
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
    def font_files(self) -> Dict[str, Path]:
        if self._font_files is None:
            font_dir = self.font_dir
            self._font_files = {f.stem: f for f in font_dir.glob("*.ttf")}
        return self._font_files

    @property
    def fonts(self) -> Dict[str, Dict[int, ImageFont.ImageFont]]:
        if self._fonts is None:
            sizes, files = self.font_sizes, self.font_files
            self._fonts = {
                name: {sz: ImageFont.truetype(str(file), size=sz) for sz in sizes}
                for (name, file) in files.items()
            }
        return self._fonts

    @property
    def font_names(self) -> Set[str]:
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

    def __getitem__(self, key: str):
        return self.fonts[key]


fonts = Fonts()
