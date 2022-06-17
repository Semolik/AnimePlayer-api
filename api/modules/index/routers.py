from .endpoints import search, available_modules
from . import config
from fastapi import APIRouter
index_router = APIRouter(
    prefix=f"/{config.module_id}", tags=[config.ModuleTitle])
index_router.include_router(
    available_modules.router)
index_router.include_router(
    search.router)
