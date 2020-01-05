from fastapi import FastAPI

from config import Config
from .__version__ import __version__
from .routers import api

app = FastAPI(
    title=Config.APP_TITLE,
    version=__version__,
    description="A placeholder image generator site.",
)

app.include_router(api.router, prefix="/api")
