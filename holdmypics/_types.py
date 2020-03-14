from typing import Tuple, Union

from flask import Response as FlaskResponse
from werkzeug import Response as WerkzeugResponse

Dimension = Tuple[int, int]
ResponseType = Union[FlaskResponse, WerkzeugResponse, str]
