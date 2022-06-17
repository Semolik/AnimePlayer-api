import asyncio
import random
import aiohttp
from typing import List
from fastapi import APIRouter, Depends
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
async def get_random_titles(service: Service = Depends(Provide[Container.service])):
    key = f'random_{config.module_id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    titles = await get_page()
    if not isinstance(titles, dict):
        return JSONResponse(status_code=404, content={"message": messages[404]})
    session = aiohttp.ClientSession()
    titles = await asyncio.gather(*[call_request(titles.get('pages')) for _ in range(4)])
    await session.close()
    titles = [item for i in titles for item in i]
    await service.SetCache(key, json.dumps(titles), time = 60 * 20)
    return titles


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
