from environs import Env

env = Env()
env.read_env()

# bind = ["127.0.0.1:8081"]
worker_class = "gevent"
worker_connections = env.int("WORKER_CONNECTIONS", default=100)
max_requests = env.int("MAX_REQUESTS", default=1000)
max_requests_jitter = env.int("MAX_REQUESTS_JITTER", default=1000)
reload = env.bool("RELOAD", default=False)

accesslog = "-"
errorlog = "-"
