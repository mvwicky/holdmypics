from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Literal
from urllib.request import urlopen

from attrs import define, field

from ..utils import config_value

WordType = Literal["collections", "objects", "predicates", "teams"]

word_path_parts = ("node_modules", "friendly-words", "generated", "words.json")
WORDS_URL = "https://unpkg.com/friendly-words@1.2.0/generated/words.json"


def download_words(output_file: Path) -> None:
    output_dir = output_file.parent
    if not output_dir.is_dir():
        output_dir.mkdir(parents=True)
    with urlopen(WORDS_URL) as res:
        output_file.write_bytes(res.read())


@define()
class Words:
    _word_file: Path | None = field(default=None, init=False)
    _word_data: dict[WordType, list[str]] | None = field(
        default=None, init=False, repr=False
    )

    @property
    def word_file(self) -> Path:
        if self._word_file is None:
            base = config_value("BASE_PATH", assert_is=Path)
            self._word_file = base.joinpath(*word_path_parts)
            if not self._word_file.is_file():
                download_words(self._word_file)
        return self._word_file

    @property
    def word_data(self) -> dict[WordType, list[str]]:
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

    def random(self, cat: WordType) -> str:
        words = self.word_data[cat]
        return random.choice(words)


words = Words()
