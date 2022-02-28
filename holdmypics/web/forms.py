from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, NamedTuple, Optional, TypeVar, Union

import attr

_T = TypeVar("_T")
_Inp = TypeVar("_Inp", bound="BaseInput")


def _default_id(obj: BaseInput) -> str:
    return obj.name


@attr.s(slots=True, auto_attribs=True)
class BaseInput(Generic[_T]):
    name: str
    label: str
    value: Optional[_T] = None
    id: str = attr.ib(default=attr.Factory(_default_id, True))
    help_text: Optional[str] = None
    required: bool = False
    extra: Mapping[str, Any] = attr.ib(factory=dict)

    def add_cy(self: _Inp, value: Optional[str] = None) -> _Inp:
        extra = {**self.extra, "data-cy": value or self.name}
        return attr.evolve(self, extra=extra)


@attr.s(slots=True, auto_attribs=True)
class TextInput(BaseInput[str]):
    pattern: Optional[str] = None


@attr.s(slots=True, auto_attribs=True)
class NumberInput(BaseInput[Union[int, float]]):
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None


class SelectOption(NamedTuple):
    value: str
    name: str
    selected: Optional[bool] = None
    disabled: bool = False


@attr.s(slots=True, auto_attribs=True)
class SelectInput(BaseInput[str]):
    options: list[SelectOption] = attr.ib(factory=list)
    help_text: Optional[str] = None
