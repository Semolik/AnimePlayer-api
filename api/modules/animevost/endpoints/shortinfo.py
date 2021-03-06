from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, BackgroundTasks, Depends

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPosterWithBlur
from ....containers import Container
from ....services import Service
from .. import utils
from ....core.schemas.shortinfo import ShortInfoItem

from .. import config
from ....utils.result_responce import GetResultResponceWithErrorIfNotLoaded

import json
router = APIRouter()


@router.get("/shortinfo", response_model=ShortInfoItem, responses={404: {"model": ErrorModel}})
@inject
async def get_title_short_info_by_id(id: int, background_tasks: BackgroundTasks, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{id}_short_info'
    cache_data = await service.GetCache(key)
    if cache_data:
        data = json.loads(cache_data)
    else:
        response = await utils.ApiPost('info', {'id': id})
        if isinstance(response, int):
            return utils.GetErrorResponse(response)
        data = await utils.ResponseFormatting(response)
    data = await GetPosterWithBlur(data, config.module_id, background_tasks, service)
    return await GetResultResponceWithErrorIfNotLoaded(key=key, service=service, data=data, search_function=utils.shikimori_search, horny=False)
