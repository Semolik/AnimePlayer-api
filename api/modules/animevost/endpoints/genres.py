from fastapi import APIRouter, Depends
from ....modules.animevost import utils
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....models import TitlesPage, Genre
from ....modules.animevost import config
import json
from typing import List
from ....responses import Message
from ....utils.messages import messages
from fastapi.responses import JSONResponse
router = APIRouter()


@router.get("/genres", response_model=List[Genre])
async def get_genres():
    genres = await utils.GetGenres()
    if not genres:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    return genres


@router.get("/genre", response_model=TitlesPage, responses={404: {"model": Message}})
@inject
async def get_genre(genre_link: str, page: int | None = 1, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{genre_link}_genre_page_{page}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    genre_exsits = await utils.FindGenre(genre_link, add_prelink=True)
    if not genre_exsits:
        return JSONResponse(status_code=404, content={"message": "Жанр не найден"})
    genre_data = await utils.GetGenre(f"{genre_exsits.get('prelink')}/{genre_exsits.get('link')}", page)
    if not genre_data:
        return JSONResponse(status_code=404, content={"message": messages[404]})
    elif isinstance(genre_data, int):
        return JSONResponse(status_code=genre_data, content={"message": messages['not_response']})
    await service.SetCache(key, json.dumps(genre_data))
    return genre_data
