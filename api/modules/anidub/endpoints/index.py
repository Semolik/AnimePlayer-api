import json
from fastapi import APIRouter, Depends

from ....models import TitlesPageStrId
from ....responses import Message
from fastapi.responses import JSONResponse
from ....utils.messages import messages
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....containers import Container
from .. import config, utils
router = APIRouter()


@router.get("/", response_model=TitlesPageStrId, responses={404: {"model": Message}})
@inject
async def get_page(page: int | None = 1, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_page_{page}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    titles = await utils.GetTitles(config.SiteLink+'anime'+(f'/page/{page}' if page else ''))
    await service.SetCache(key, json.dumps(titles), time=60)
    return titles
