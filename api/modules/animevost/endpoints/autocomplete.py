from fastapi import APIRouter, BackgroundTasks, Depends, Query

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPostersWithBlur
from .. import utils, config
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....core.schemas.autocomplete import autocompleteSearch
import json
from ....utils.messages import GetMessage
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/autocomplete", response_model=autocompleteSearch,  responses={404: {"model": ErrorModel}})
@inject
async def autocomplete_search_titles(background_tasks: BackgroundTasks,text: str = Query(default=None, min_length=config.autocomplete_min), service: Service = Depends(Provide[Container.service])):
    key = f'autocomplete_{config.module_id}_{"_".join(text.split(" "))}'
    cache_data = await service.GetCache(key)
    if cache_data:
        titles = json.loads(cache_data)
    else:
        titles = await utils.autocomplete_search(text)
        if isinstance(titles, int):
            return JSONResponse(status_code=titles, content=GetMessage(titles))
    titles = await GetPostersWithBlur(titles, config.module_id, background_tasks, service)
    await service.SetCache(key, json.dumps(titles))
    return titles
