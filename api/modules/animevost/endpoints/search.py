from fastapi import APIRouter, BackgroundTasks, Depends

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPostersWithBlur
from .. import utils, config
from api.containers import Container
from api.services import Service
from dependency_injector.wiring import inject, Provide
from api.core.schemas.titles import TitlesPage
from api.core.schemas.search import Search
import json
from api.utils.messages import GetMessage
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/search", response_model=TitlesPage, responses={404: {"model": ErrorModel}})
@inject
async def search_titles(search_data: Search, background_tasks: BackgroundTasks, service: Service = Depends(Provide[Container.service])):
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
