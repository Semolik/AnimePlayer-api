from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends

from api.utils.result_responce import GetResultResponce
from ....containers import Container
from ....services import Service
from .. import utils
from ....core.schemas.title import Title
from ....responses import Message
from fastapi.responses import JSONResponse
from ....utils import rule_34, shikimori
from .. import config

import json
router = APIRouter()


@router.get("/title", response_model=Title, responses={404: {"model": Message}})
@inject
async def get_title_by_id(id: int, horny: bool | None = None, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        data = json.loads(cache_data)
    else:
        response = await utils.ApiPost('info', {'id': id})
        if isinstance(response, int):
            return utils.GetErrorResponse(response)
        data = await utils.ResponseFormatting(response, full=True)
    return await GetResultResponce(key=key, service=service, data=data, search_function=utils.shikimori_search, horny=horny)

