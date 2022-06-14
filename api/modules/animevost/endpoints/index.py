
import json
from fastapi import APIRouter, Depends
from ....modules.animevost import utils
from ....core.schemas.titles import TitlesPage
from ....responses import Message
from fastapi.responses import JSONResponse
from ....utils.messages import messages
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....containers import Container
from .. import config
router = APIRouter()


@router.get("/", response_model=TitlesPage, responses={404: {"model": Message}})
@inject
async def get_page(page: int | None = 1, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_page_{page}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    response = await utils.ApiGet('last', {'page': page, 'quantity': config.page_quantity}, one=False, get_data=False)
    if not response:
        return JSONResponse(status_code=404, content={"message": messages[404]})
    data = response.get('data')
    if data is None:
        return JSONResponse(status_code=404, content={"message": messages[404]})
    data = {
        'titles': [await utils.ResponseFormatting(title) for title in data],
        'pages': await utils.GetPageCount(response, config.page_quantity),
    }
    await service.SetCache(key, json.dumps(data), time=60)
    return data
