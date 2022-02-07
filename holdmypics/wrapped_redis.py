from __future__ import annotations

from typing import Any, Optional, Union

import attr
from flask import Flask
from flask_redis import FlaskRedis

from .constants import COUNT_KEY, SIZE_KEY


@attr.s(slots=True, auto_attribs=True)
class FakeRedis(object):
    _store: dict[str, Any] = attr.ib(factory=dict, init=False)

    def get(self, name: str) -> Optional[bytes]:
        value = self._store.get(name)
        if value is not None:
            return str(value).encode("utf-8")
        return value

    def incrby(self, name: str, amount: int = 1) -> int:
        self._store.setdefault(name, 0)
        self._store[name] += amount
        return self._store[name]

    def incr(self, name: str) -> int:
        return self.incrby(name, 1)


@attr.s(slots=True, auto_attribs=True)
class WrappedRedis(object):
    has_redis: bool = False
    client: Union[FlaskRedis, FakeRedis] = FakeRedis()

    def init_app(self, app: Flask) -> None:
        self.has_redis = bool(app.config.get("REDIS_URL"))
        if self.has_redis:
            self.client = FlaskRedis()
            self.client.init_app(app)
        else:
            self.client = FakeRedis()

    def _get_int(self, name: str, default: int = 0) -> int:
        value = self.client.get(name)
        if value is not None:
            try:
                return int(value.decode())
            except ValueError:
                return default
        return default

    def incr_count(self) -> int:
        return self.client.incr(COUNT_KEY)

    def incr_size(self, size: int) -> int:
        return self.client.incrby(SIZE_KEY)

    def get_count(self) -> int:
        return self._get_int(COUNT_KEY)

    def get_size(self) -> int:
        return self._get_int(SIZE_KEY)
