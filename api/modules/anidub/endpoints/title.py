import json
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from ....containers import Container
from ....services import Service
from .. import utils
from ....responses import Message
from .. import config
from ....core.schemas.title import TitleStrId
from ....utils import rule_34, shikimori
router = APIRouter()


@router.get("/title", response_model=TitleStrId, responses={404: {"model": Message}})
@inject
async def get_title_by_id(id: str, horny: bool | None = None, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        data = json.loads(cache_data)
    else:
        data = await utils.GetTitleById(id)
    result_data, data = await rule_34.addDataToResponse(data) if horny else await shikimori.addDataToResponse(data)
    await service.SetCache(key, json.dumps(data))
    return result_data
