from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Generic, NamedTuple, Optional, TypeVar, Union

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
    value: Optional[_T] = None
    id: str = _id_factory
    help_text: Optional[str] = None
    required: bool = False
    extra: Mapping[str, Any] = field(factory=dict)

    def add_cy(self: _Inp, value: Optional[str] = None) -> _Inp:
        extra = {**self.extra, "data-cy": value or self.name}
        return evolve(self, extra=extra)


@define()
class TextInput(BaseInput[str]):
    pattern: Optional[str] = None


@define()
class NumberInput(BaseInput[Union[int, float]]):
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    step: Optional[Union[int, float]] = None


class SelectOption(NamedTuple):
    value: str
    name: str
    selected: Optional[bool] = None
    disabled: bool = False


@define()
class SelectInput(BaseInput[str]):
    options: list[SelectOption] = field(factory=list)
    help_text: Optional[str] = None
