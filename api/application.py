"""Application module."""
from fastapi import FastAPI
from .modules.animevost.routers import animevost_router
from .containers import Container


app = FastAPI()
app.include_router(animevost_router)


container = Container()
container.config.redis_host.from_env("REDIS_HOST", "localhost")
container.config.redis_password.from_env("REDIS_PASSWORD", "password")
container.wire(packages=[
    '.modules.animevost',
    '.modules.animevost.endpoints',
])
