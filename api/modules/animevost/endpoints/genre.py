from fastapi import APIRouter, BackgroundTasks, Depends

from api.utils.images import GetPostersWithBlur
from .. import utils, config
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
import json
from api.core.schemas.error import ErrorModel
from ....utils.messages import messages
from fastapi.responses import JSONResponse
from ....core.schemas.titles import TitlesPage
router = APIRouter()


@router.get("/genre", response_model=TitlesPage, responses={404: {"model": ErrorModel}})
@inject
async def get_genre(genre_link: str, background_tasks: BackgroundTasks, page: int | None = 1, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{genre_link}_genre_page_{page}'
    data = await service.GetCache(key)
    if data:
        data = json.loads(data)
    else:
        genre_exsits = await utils.FindGenre(genre_link, add_prelink=True)
        if not genre_exsits:
            return JSONResponse(status_code=404, content={"message": "Жанр не найден"})
        genre_data = await utils.GetGenre(f"{genre_exsits.get('prelink')}/{genre_exsits.get('link')}", page)
        if not genre_data or genre_data == 404:
            return JSONResponse(status_code=404, content={"message": messages[404]})
        elif isinstance(genre_data, int):
            return JSONResponse(status_code=genre_data, content={"message": messages['not_response']})
        await service.SetCache(key, json.dumps(genre_data))
        data = genre_data
    data = await GetPostersWithBlur(data, config.module_id, background_tasks, service)
    return data
