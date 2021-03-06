import json
import re
import aiohttp
from .. import config
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ....core.schemas.series import seriesItemWithoutName
from ....settings import headers
from ....utils.messages import messages
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from ....containers import Container
from ....services import Service
router = APIRouter()



@router.get("/sibnet", response_model=seriesItemWithoutName)
@inject
async def get_sibnet_video_by_id(sibnet_id: int, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}_{sibnet_id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    async with aiohttp.ClientSession() as session:
        page_url = f'https://video.sibnet.ru/video{sibnet_id}'
        response = await session.get(page_url, headers=headers)
        status = response.status
        if status != 200:
            return JSONResponse(status_code=status, content={"message": messages[{500: 'not_response', 404: 404}[status]]})

        html = await response.text()
        p = next(re.finditer(r"\/v\/.+\d+.mp4", html), None)
        if not p:
            return JSONResponse(status_code=404, content={"message": "Ошибка получения ссылки"})
        poster = next(re.finditer(
            r"'\/upload\/cover\/.+\d+.(jpg|png)'", html), None)
        if poster:
            poster = "https://video.sibnet.ru"+poster.group(0)[1:-1]
        size = 720
        file_url = 'https://video.sibnet.ru' + p.group(0)
        r = await session.head(file_url, headers={'Referer': page_url})
        if r.status == 200:
            url = await r.text()
        elif r.status == 302:
            url = r.headers.get('Location')
            if not url.startswith('//'):
                return JSONResponse(status_code=500, content={"message": "Ошибка получения ссылки"})
        data = {
            'sources': [
                {
                    'src': url,
                    'size': size,
                },
            ],
            'poster': poster,
        }
        await service.SetCache(key, json.dumps(data))
        return data
