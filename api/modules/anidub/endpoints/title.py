import json
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, BackgroundTasks, Depends

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPosterWithBlur, GetPostersWithBlurList
from api.utils.result_responce import GetResultResponce
from ....containers import Container
from ....services import Service
from .. import utils
from .. import config
from ....core.schemas.title import TitleStrId
from ....utils import rule_34, shikimori
from ....utils.messages import GetMessage
from fastapi.responses import JSONResponse
router = APIRouter()


# @router.get("/title",  responses={404: {"model": ErrorModel}})
@router.get("/title", response_model=TitleStrId, responses={404: {"model": ErrorModel}})
@inject
async def get_title_by_id(id: str, background_tasks: BackgroundTasks, horny: bool | None = None, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        data = json.loads(cache_data)
    else:
        data = await utils.GetTitleById(id)
        if isinstance(data, int):
            return JSONResponse(status_code=data, content=GetMessage(data))
    data = await GetPosterWithBlur(data, config.module_id, background_tasks, service)
    related = data.get('related')
    if related:
        for i, related_list in enumerate(related):
            items = related_list.get('items')
            data['related'][i]['items'] = await GetPostersWithBlurList(items, config.module_id, background_tasks, service)
    return await GetResultResponce(key=key, service=service, data=data, horny=horny)
