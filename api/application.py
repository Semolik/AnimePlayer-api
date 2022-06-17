"""Application module."""
from fastapi import FastAPI
from .modules.animevost.routers import animevost_router
from .modules.anidub.routers import anidub_router
from .modules.utilities.routers import utilities_router
from .modules.index.routers import index_router
from .containers import Container


app = FastAPI()
app.include_router(index_router)
app.include_router(animevost_router)
app.include_router(anidub_router)
app.include_router(utilities_router)



container = Container()
container.config.redis_host.from_env("REDIS_HOST", "localhost")
container.config.redis_password.from_env("REDIS_PASSWORD", "password")
container.wire(packages=[
    '.utils.shikimori',
    '.utils.rule_34',
    '.modules.utilities',
    '.modules.utilities.endpoints',
    '.modules.animevost',
    '.modules.animevost.endpoints',
    '.modules.anidub',
    '.modules.anidub.endpoints',
])
