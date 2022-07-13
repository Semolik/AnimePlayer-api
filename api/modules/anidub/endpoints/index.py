import json
from fastapi import APIRouter, BackgroundTasks, Depends

from api.core.schemas.error import ErrorModel
from api.utils.images import GetPostersWithBlur
from ....core.schemas.titles import TitlesPageStrId
from fastapi.responses import JSONResponse
from ....utils.messages import GetMessage
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....containers import Container
from .. import config, utils
router = APIRouter()


@router.get("/", response_model=TitlesPageStrId, responses={404: {"model": ErrorModel}})
@inject
async def get_page(background_tasks: BackgroundTasks, page: int | None = 1, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_page_{page}'
    titles = await service.GetCache(key)
    if titles:
        titles = json.loads(titles)
    else:
        titles = await utils.GetTitles(config.SiteLink+'anime'+(f'/page/{page}' if page else ''))
        if isinstance(titles, int):
            return JSONResponse(status_code=titles, content=GetMessage(titles))
        await service.SetCache(key, json.dumps(titles), time=60)
    titles = await GetPostersWithBlur(titles, config.module_id, background_tasks, service)
    return titles
