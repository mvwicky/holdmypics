from __future__ import annotations

from environs import Env

env = Env()
env.read_env()

loglevel = "info"
_host, _port = env("HOST", default="0.0.0.0"), env.int("PORT", default=8080)
bind = [f"{_host}:{_port}"]

keyfile = env("KEYFILE", default=None)
certfile = env("CERTFILE", default=None)

worker_class = "gthread"
workers = env.int("WEB_CONCURRENCY", default=1)
worker_connections = env.int("WORKER_CONNECTIONS", default=100)
max_requests = env.int("MAX_REQUESTS", default=1000)
max_requests_jitter = env.int("MAX_REQUESTS_JITTER", default=1000)
reload = env.bool("RELOAD", default=False)

accesslog = "-"
errorlog = "-"
