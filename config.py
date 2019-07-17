import logging

from environs import Env

logger = logging.getLogger(__name__)

env = Env()
env.read_env()


class BaseConfig(object):
    pass


class Config(BaseConfig):
    DEBUG = env.bool("DEBUG", default=False)
    REDIS_URL = env("REDIS_URL")
    MAX_AGE = env.int("MAX_AGE", default=86400)
