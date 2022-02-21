from __future__ import annotations

from typing import Any, Union

from flask import Response as FlaskResponse
from werkzeug import Response as WerkzeugResponse

Dimension = tuple[int, int]
ResObject = Union[FlaskResponse, WerkzeugResponse]
Res = Union[ResObject, str]
Hdrs = Union[list[tuple[str, str]], dict[str, Any]]
ResponseType = Union[
    Res, dict[str, Any], tuple[Res, int, Hdrs], tuple[Res, int], tuple[Res, Hdrs], str
]
