from fastapi import APIRouter, BackgroundTasks, Depends

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPostersWithBlur
from .. import utils, config
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....core.schemas.titles import TitlesPageStrId
from ....core.schemas.search import Search
import json

from ....utils.messages import GetMessage
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/search", response_model=TitlesPageStrId, responses={404: {"model": ErrorModel}})
@inject
async def search_titles(search_data: Search,background_tasks: BackgroundTasks, service: Service = Depends(Provide[Container.service])):
    key = f'search_{config.module_id}_{"_".join(search_data.text.split(" "))}_{search_data.page}'
    cache_data = await service.GetCache(key)
    if cache_data:
        titles =  json.loads(cache_data)
    else:
        titles = await utils.search(text=search_data.text, page=search_data.page)
        if isinstance(titles, int):
            return JSONResponse(status_code=titles, content=GetMessage(titles))
        await service.SetCache(key, json.dumps(titles))
    titles = await GetPostersWithBlur(titles, config.module_id, background_tasks, service)
    return titles
