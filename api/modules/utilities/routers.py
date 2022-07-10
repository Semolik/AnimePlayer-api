from .endpoints import sibnet, moduleinfo
from . import config
from fastapi import APIRouter
utilities_router = APIRouter(
    prefix=f"/{config.module_id}", tags=[config.ModuleTitle])
utilities_router.include_router(
    sibnet.router)
utilities_router.include_router(
    moduleinfo.router)
