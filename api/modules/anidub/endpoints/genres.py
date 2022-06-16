from fastapi import APIRouter
from dependency_injector.wiring import inject, Provide
from ....core.schemas.genres import Genres
from .. import utils
from typing import List
from fastapi.responses import JSONResponse
router = APIRouter()


@router.get("/genres", response_model=Genres)
async def get_genres():
    genres = await utils.GetGenres()
    if not genres:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    return genres
