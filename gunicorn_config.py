from environs import Env

env = Env()
env.read_env()

loglevel = "info"
bind = env("BIND", default=None)
if bind is None:
    del bind

worker_class = "gthread"
workers = env.int("WEB_CONCURRENCY", default=1)
worker_connections = env.int("WORKER_CONNECTIONS", default=100)
max_requests = env.int("MAX_REQUESTS", default=1000)
max_requests_jitter = env.int("MAX_REQUESTS_JITTER", default=1000)
reload = env.bool("RELOAD", default=False)

accesslog = "-"
errorlog = "-"
