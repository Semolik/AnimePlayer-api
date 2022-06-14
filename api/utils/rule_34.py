import json
import string
import aiohttp
from ..settings import headers
from pygelbooru import Gelbooru, API_RULE34
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from ..containers import Container
from ..services import Service
from ..config import rule34_key
gelbooru = Gelbooru(api=API_RULE34)


async def SearchOnRule34(name='', tag=None):
    try:
        if not name and tag:
            return
        remove = string.punctuation
        remove = remove.replace("-", "")
        name = name.translate(
            {ord(char): None for char in remove}).lower().split(' ')
        async with aiohttp.ClientSession() as session:
            while len(name) > 0 and not tag:
                try:
                    async with session.get(f"https://rule34.xxx/public/autocomplete.php?q={'_'.join(name)}", headers=headers) as response:
                        print(f'--- rule34 status {response.status}')
                        if response.status == 200:
                            result = await response.json(content_type='text/html')
                            if result:
                                tag = result[0].get('value')
                except Exception as e:
                    print(str(e))
                if tag:
                    result = await gelbooru.search_posts(tags=[tag])
                    return {
                        'tag': tag,
                        'data': [i._payload for i in result]
                    }
                name.pop()
    except:
        return None


@inject
async def addDataToResponse(data, service: Service = Depends(Provide[Container.service])):
    result_data = data.copy()
    rule34_tag = data.get('rule34_tag')
    rule34_cache = None
    if rule34_tag:
        rule34_cache = await service.GetCache(rule34_key.format(rule34_tag))
        if rule34_cache:
            rule34_data = json.loads(rule34_cache)
    if not rule34_cache:
        rule34_data = await SearchOnRule34(data.get('en_title'))
        if rule34_data:
            tag = rule34_data.get('tag')
            data['rule34_tag'] = tag
            rule34_data = rule34_data.get('data')
            if rule34_data:
                await service.SetCache(rule34_key.format(tag), json.dumps(rule34_data))
    result_data['rule34'] = rule34_data
    return result_data, data
