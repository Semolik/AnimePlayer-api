from .endpoints import index
from . import config
from fastapi import APIRouter
anidub_router = APIRouter(
    prefix=f"/{config.module_id}", tags=[config.ModuleTitle])
anidub_router.include_router(
    index.router)
