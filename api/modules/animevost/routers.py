from .endpoints import title, random
from . import config
from fastapi import APIRouter
animevost_router = APIRouter(prefix=f"/{config.module_id}",tags=[config.ModuleTitle])
animevost_router.include_router(
    random.router )
animevost_router.include_router(
    title.router)
