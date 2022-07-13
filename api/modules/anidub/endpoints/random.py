import asyncio
import random
import aiohttp
from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends

from api.utils.images import GetPostersWithBlurList
from .. import utils
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....core.schemas.titles import TitleInfoStrId
from .. import config
from ....utils.messages import messages
from fastapi.responses import JSONResponse
from .index import get_page
import json
router = APIRouter()


@router.get("/random", response_model=List[TitleInfoStrId])
@inject
async def get_random_titles(background_tasks: BackgroundTasks, service: Service = Depends(Provide[Container.service])):
    key = f'random_{config.module_id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        titles = json.loads(cache_data)
    else:
        titles = await get_page(background_tasks=background_tasks)
        if not isinstance(titles, dict):
            return JSONResponse(status_code=404, content={"message": messages[404]})
        session = aiohttp.ClientSession()
        titles = await asyncio.gather(*[call_request(titles.get('pages')) for _ in range(4)])
        await session.close()
        titles = [item for i in titles for item in i]
        await service.SetCache(key, json.dumps(titles), time=60 * 20)
    return await GetPostersWithBlurList(titles, config.module_id, background_tasks, service)


async def call_request(pages):
    data = await get_page(random.randint(1, pages))
    titles = []
    if isinstance(data, dict):
        titles = data.get('titles')
        random.shuffle(titles)
        titles = titles[:5]
        if len(titles) > 5:
            titles = titles[:5]
    return titles
