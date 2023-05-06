from __future__ import annotations

from typing import Any, TypeAlias

from flask import Response as FlaskResponse
from werkzeug import Response as WerkzeugResponse

Dimension: TypeAlias = tuple[int, int]
ResObject: TypeAlias = FlaskResponse | WerkzeugResponse
Res: TypeAlias = ResObject | str
Hdrs: TypeAlias = list[tuple[str, str]] | dict[str, Any]
ResponseType: TypeAlias = (
    Res
    | dict[str, Any]
    | tuple[Res, int, Hdrs]
    | tuple[Res, int]
    | tuple[Res, Hdrs]
    | str
)
