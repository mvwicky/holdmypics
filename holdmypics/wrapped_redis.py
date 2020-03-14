from typing import Union

import attr
from flask import Flask
from flask_redis import FlaskRedis


@attr.s(slots=True, auto_attribs=True)
class FakeRedis(object):
    count: int = 0

    def get(self, *args, **kwargs) -> bytes:
        return str(self.count).encode("utf-8")

    def incr(self, *args, **kwargs) -> int:
        self.count += 1
        return self.count


@attr.s(slots=True, auto_attribs=True)
class WrappedRedis(object):
    has_redis: bool = False
    client: Union[FlaskRedis, FakeRedis] = FakeRedis()

    def init_app(self, app: Flask, redis_client: FlaskRedis) -> None:
        self.has_redis = app.config.get("REDIS_URL", None) is not None
        if self.has_redis:
            redis_client.init_app(app)
            self.client = redis_client
        else:
            self.client = FakeRedis()
