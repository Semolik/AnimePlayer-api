"""Application module."""
from fastapi import FastAPI
from .modules.animevost.routers import animevost_router
from .modules.anidub.routers import anidub_router
from .containers import Container


app = FastAPI()
app.include_router(animevost_router)
app.include_router(anidub_router)


container = Container()
container.config.redis_host.from_env("REDIS_HOST", "localhost")
container.config.redis_password.from_env("REDIS_PASSWORD", "password")
container.wire(packages=[
    '.modules.animevost',
    '.modules.animevost.endpoints',
    '.modules.anidub',
    '.modules.anidub.endpoints',
])
