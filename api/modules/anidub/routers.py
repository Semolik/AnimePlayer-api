from .endpoints import index, genres, title, genre, search, random, autocomplete
from . import config
from fastapi import APIRouter
anidub_router = APIRouter(
    prefix=f"/{config.module_id}", tags=[config.ModuleTitle])
anidub_router.include_router(
    index.router)
anidub_router.include_router(
    title.router)
anidub_router.include_router(
    random.router)
anidub_router.include_router(
    genres.router)
anidub_router.include_router(
    genre.router)
anidub_router.include_router(
    search.router)
anidub_router.include_router(
    autocomplete.router)
