from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from ....containers import Container
from ....services import Service
from .. import utils
from ....models import Title
from ....config import shikimori_key, rule34_key
import json
router = APIRouter()

@router.get("/title", response_model=Title)
@inject
async def get_title_by_id(id: int, horny: bool | None = None, service: Service = Depends(Provide[Container.service])):
    key = f'animevost_{id}'
    cache_data = await service.GetCache(key)
    if cache_data:
        data = json.loads(cache_data)
    else:
        response = await utils.ApiPost('info', {'id': id})
        if not response:
            raise HTTPException(status_code=404, detail="Item not found")
        data = await utils.ResponseFormatting(response, full=True)
    result_data = data.copy()
    if horny:
        rule34_tag = data.get('rule34_tag')
        rule34_cache = None
        if rule34_tag:
            rule34_cache = await service.GetCache(rule34_key.format(rule34_tag))
            if rule34_cache:
                rule34_data = json.loads(rule34_cache)
        if not rule34_cache:
            rule34_data = await utils.rule34_search(data)
            if rule34_data:
                tag = rule34_data.get('tag')
                data['rule34_tag'] = tag
                rule34_data = rule34_data.get('data')
                if rule34_data:
                    await service.SetCache(rule34_key.format(tag), json.dumps(rule34_data))
        result_data['rule34'] = rule34_data
    else:
        shikimori_id = data.get('shikimori_id')
        cache_shikimori = None
        if shikimori_id:
            cache_shikimori = await service.GetCache(shikimori_key.format(shikimori_id))
            if cache_shikimori:
                shikimori_data = json.loads(cache_shikimori)
        if not cache_shikimori:
            shikimori_data = await utils.shikimori_search(data)
            if shikimori_data:
                await service.SetCache(shikimori_key.format(shikimori_data.get('id')), json.dumps(shikimori_data), 60*60*24)
                data['shikimori_id'] = shikimori_data.get('id')
        result_data['shikimori'] = shikimori_data
    await service.SetCache(key, json.dumps(data))
    return result_data
