from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, NamedTuple, TypeVar

from attrs import Factory, define, evolve, field

_T = TypeVar("_T")
_Inp = TypeVar("_Inp", bound="BaseInput")


def _default_id(obj: BaseInput[Any]) -> str:
    return obj.name


_id_factory = Factory(_default_id, True)


@define()
class BaseInput(Generic[_T]):
    name: str
    label: str
    value: _T | None = None
    id: str = _id_factory
    help_text: str | None = None
    required: bool = False
    extra: Mapping[str, Any] = field(factory=dict)

    def add_cy(self: _Inp, value: str | None = None) -> _Inp:
        extra = {**self.extra, "data-cy": value or self.name}
        return evolve(self, extra=extra)


@define()
class TextInput(BaseInput[str]):
    pattern: str | None = None


@define()
class NumberInput(BaseInput[int | float]):
    min: int | float | None = None
    max: int | float | None = None
    step: int | float | None = None


class SelectOption(NamedTuple):
    value: str
    name: str
    selected: bool | None = None
    disabled: bool = False


@define()
class SelectInput(BaseInput[str]):
    options: list[SelectOption] = field(factory=list)
    help_text: str | None = None
