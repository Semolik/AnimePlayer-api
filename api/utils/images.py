import io
import json
import pathlib
from typing import Container
import aiohttp
import blurhash
from fastapi import BackgroundTasks, Depends
from api.services import Service
from dependency_injector.wiring import inject, Provide
from api.containers import Container


@inject
async def BlurhashImage(url, key, service: Service = Depends(Provide[Container.service])):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                file = io.BytesIO(await response.read())
                file.name = f'file.{pathlib.Path(url).suffix}'
                file.seek(0)
                hash = blurhash.encode(file, x_components=4, y_components=3)
                await service.SetCache(key, json.dumps({
                    'url': url,
                    'blurhash': hash,
                }), time=60 * 24)


async def GetPostersWithBlur(data, module_id, background_tasks, service):
    titles = data.get('titles')
    pages = data.get('pages')
    return {
        'titles': await GetPostersWithBlurList(titles, module_id, background_tasks, service),
        'pages': pages
    }


async def GetPostersWithBlurList(titles, module_id, background_tasks, service):
    result_titles = list()
    for title in titles:
        result_titles.append(await GetPosterWithBlur(title, module_id, background_tasks, service))
    return result_titles


@inject
async def GetPosterWithBlur(title, module_id, background_tasks, service):
    key = f'{module_id}_poster_{title.get("id")}'
    data = await service.GetCache(key)
    if data:
        title['poster'] = json.loads(data)
    else:
        poster = title.get('poster')
        title['poster'] = {
            'url': poster,
            'blurhash': None,
        }
        if poster:
            background_tasks.add_task(BlurhashImage, url=poster, key=key)
    return title
