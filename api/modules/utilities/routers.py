from .endpoints import sibnet
from . import config
from fastapi import APIRouter
utilities_router = APIRouter(
    prefix=f"/{config.module_id}", tags=[config.ModuleTitle])
utilities_router.include_router(
    sibnet.router)
