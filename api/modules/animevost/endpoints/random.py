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
from ....core.schemas.titles import TitleInfo
from .. import config
from ....utils.messages import messages
from fastapi.responses import JSONResponse
import json
router = APIRouter()


@router.get("/random", response_model=List[TitleInfo])
@inject
async def get_random_titles(background_tasks: BackgroundTasks, service: Service = Depends(Provide[Container.service])):
    key = f'random_{config.module_id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        titles = json.loads(cache_data)
    else:
        response = await utils.ApiGet('last', {'page': 1, 'quantity': 1}, get_data=False)
        if isinstance(response, int):
            return JSONResponse(status_code=404, content={"message": messages[404] if response == 404 else messages['not_response']})
        page_quantity = 20
        count = response.get('state').get('count')
        pages = count // page_quantity
        session = aiohttp.ClientSession()
        titles = await asyncio.gather(*[call_request(session, pages, page_quantity) for x in range(4)])
        await session.close()
        titles = [item for i in titles for item in i]
        await service.SetCache(key, json.dumps(titles), time=60 * 20)
    return await GetPostersWithBlurList(titles, config.module_id, background_tasks, service)


async def call_request(session, pages, page_quantity):
    titles = list()
    page_response = await utils.ApiGet('last', {'page': random.randint(1, pages), 'quantity': page_quantity}, session=session, not_close_session=True, one=False)
    if not isinstance(page_response, int):
        random.shuffle(page_response)
        page_response = page_response[:5]
        if len(page_response) > 5:
            page_response = page_response[:5]
        for title in page_response:
            titles.append(await utils.ResponseFormatting(title))
    return titles
