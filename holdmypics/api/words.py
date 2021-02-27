from __future__ import annotations

import json
import random
from functools import partial
from pathlib import Path
from typing import Optional

import attr

from ..utils import config_value

none_attr = partial(attr.ib, default=None, init=False)

word_path_parts = ["node_modules", "friendly-words", "generated", "words.json"]
# https://unpkg.com/friendly-words@1.1.10/generated/words.json


@attr.s(auto_attribs=True, slots=True)
class Words(object):
    _word_file: Optional[Path] = none_attr()
    _word_data: Optional[dict[str, list[str]]] = none_attr()

    @property
    def word_file(self) -> Path:
        if self._word_file is None:
            base: Path = config_value("BASE_PATH", None)
            self._word_file = base.joinpath(*word_path_parts)
        return self._word_file

    @property
    def word_data(self) -> dict[str, list[str]]:
        if self._word_data is None:
            self._word_data = json.loads(self.word_file.read_text())
        return self._word_data

    @property
    def collections(self) -> list[str]:
        return self.word_data["collections"]

    @property
    def objects(self) -> list[str]:
        return self.word_data["objects"]

    @property
    def predicates(self) -> list[str]:
        return self.word_data["predicates"]

    @property
    def teams(self) -> list[str]:
        return self.word_data["teams"]

    def random(self, cat: str) -> str:
        words = self.word_data[cat]
        return random.choice(words)


words = Words()
