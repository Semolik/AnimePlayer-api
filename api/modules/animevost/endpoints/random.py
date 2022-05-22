import asyncio
import random
import aiohttp
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from ....modules.animevost import utils
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....models import TitleInfo
from ....modules.animevost import config
import json
router = APIRouter()


@router.get("/random", response_model=List[TitleInfo])
@inject
async def get_random_titles(service: Service = Depends(Provide[Container.service])):
    key = f'random_{config.module_id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    response = await utils.ApiGet('last', {'page': 1, 'quantity': 1}, get_data=False)
    if not response:
        raise HTTPException(status_code=404, detail="Item not found")
    page_quantity = 20
    count = response.get('state').get('count')
    pages = count // page_quantity
    session = aiohttp.ClientSession()
    titles = await asyncio.gather(*[call_request(session, pages, page_quantity) for x in range(4)])
    await session.close()
    titles = [item for i in titles for item in i]
    await service.SetCache(key, json.dumps(titles), time = 60)
    return titles


async def call_request(session, pages, page_quantity):
    titles = list()
    page_response = await utils.ApiGet('last', {'page': random.randint(1, pages), 'quantity': page_quantity}, session=session, not_close_session=True, one=False)
    if page_response:
        random.shuffle(page_response)
        page_response = page_response[:5]
        if len(page_response) > 5:
            page_response = page_response[:5]
        for title in page_response:
            titles.append(await utils.ResponseFormatting(title))
    return titles
