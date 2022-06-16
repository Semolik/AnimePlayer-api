from fastapi import APIRouter
from .. import utils
from fastapi.responses import JSONResponse
from ....core.schemas.genres import Genres

router = APIRouter()


@router.get("/genres", response_model=Genres)
async def get_genres():
    genres = await utils.GetGenres()
    if not genres:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    return genres
