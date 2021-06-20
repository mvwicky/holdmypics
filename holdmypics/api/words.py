from __future__ import annotations

import json
import random
from functools import partial
from pathlib import Path
from typing import Optional
from urllib.request import urlopen

import attr

from ..utils import config_value

none_attr = partial(attr.ib, default=None, init=False)

word_path_parts = ("node_modules", "friendly-words", "generated", "words.json")
WORDS_URL = "https://unpkg.com/friendly-words@1.2.0/generated/words.json"


def download_words(output_file: Path) -> None:
    output_dir = output_file.parent
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True)
    with urlopen(WORDS_URL) as res:
        output_file.write_bytes(res.read())


@attr.s(auto_attribs=True, slots=True)
class Words(object):
    _word_file: Optional[Path] = none_attr()
    _word_data: Optional[dict[str, list[str]]] = none_attr()

    @property
    def word_file(self) -> Path:
        if self._word_file is None:
            base: Path = config_value("BASE_PATH", None)
            self._word_file = base.joinpath(*word_path_parts)
            if not self._word_file.is_file():
                download_words(self._word_file)
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
