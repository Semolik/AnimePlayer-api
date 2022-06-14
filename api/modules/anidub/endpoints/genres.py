from fastapi import APIRouter, Depends
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
# from ....models import Genres
from ....core.schemas.genres import Genres
from .. import config, utils

from typing import List

from fastapi.responses import JSONResponse
router = APIRouter()


@router.get("/genres", response_model=Genres)
async def get_genres():
    genres = await utils.GetGenres()
    if not genres:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    return genres
