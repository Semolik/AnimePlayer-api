from fastapi import APIRouter, BackgroundTasks, Depends

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPostersWithBlur
from .. import utils, config
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....core.schemas.autocomplete import autocompleteSearchStrIds
import json
from ....utils.messages import GetMessage
from fastapi.responses import JSONResponse
router = APIRouter()


@router.post("/autocomplete", response_model=autocompleteSearchStrIds,  responses={404: {"model": ErrorModel}})
@inject
async def autocomplete_search_titles(text: str, background_tasks: BackgroundTasks, service: Service = Depends(Provide[Container.service])):
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
