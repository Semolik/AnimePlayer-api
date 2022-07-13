
import json
from fastapi import APIRouter, Depends, BackgroundTasks

from api.utils.images import GetPostersWithBlur
from .. import utils
from ....core.schemas.titles import TitlesPage
from api.core.schemas.error import ErrorModel
from fastapi.responses import JSONResponse
from api.utils.messages import messages
from api.services import Service
from dependency_injector.wiring import inject, Provide
from api.containers import Container
from .. import config
router = APIRouter()


@router.get("/", response_model=TitlesPage, responses={404: {"model": ErrorModel}})
@inject
async def get_page(background_tasks: BackgroundTasks, page: int | None = 1, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_page_{page}'
    data = await service.GetCache(key)
    if data:
        data = json.loads(data)
    else:
        response = await utils.ApiGet('last', {'page': page, 'quantity': config.page_quantity}, one=False, get_data=False)
        if isinstance(response, int):
            return utils.GetErrorResponse(response)
        data = response.get('data')
        if data is None:
            return JSONResponse(status_code=404, content={"message": messages[404]})
        data = {
            'titles': [await utils.ResponseFormatting(title) for title in data],
            'pages': await utils.GetPageCount(response, config.page_quantity),
        }
        await service.SetCache(key, json.dumps(data), time=60)
    data = await GetPostersWithBlur(data, config.module_id, background_tasks, service)
    return data
