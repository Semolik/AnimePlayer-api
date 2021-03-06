from .endpoints import search, autocomplete
from . import config
from fastapi import APIRouter
index_router = APIRouter(
    prefix=f"/{config.module_id}", tags=[config.ModuleTitle])
index_router.include_router(
    search.router)
index_router.include_router(
    autocomplete.router)
