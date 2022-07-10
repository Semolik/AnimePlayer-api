import json
import aiohttp
from ..config import ShikimoriLink
from requests.utils import requote_uri
from ..settings import headers
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from ..containers import Container
from ..services import Service
from lxml import etree
import ssl
import certifi
from ..config import ShikimoriLink, shikimori_api, shikimori_key


async def SearchOnShikimori(name, kind=None):
    if not name:
        return
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=conn) as session:
        response = await session.get(f'https://shikimori.one/animes/autocomplete/v2?search={requote_uri(name)}', headers=headers)
        if response.status not in (200, 404):
            return
        html = await response.text()
        tree = etree.HTML(html)
        titles = tree.xpath('//div[@class="b-db_entry-variant-list_item"]')
        shikimori_id = None
        if titles:
            for title in titles:
                if not kind:
                    shikimori_id = title.attrib.get('data-id')
                    break
                tags = title.xpath('//div[@class="b-tag"]')
                if tags:
                    if tags[0].attrib.get('data-href') == ShikimoriLink+'animes/kind/'+kind or not kind:
                        shikimori_id = title.attrib.get('data-id')
                        break
            if not shikimori_id:
                shikimori_id = titles[0].attrib.get('data-id')
            shikimori_req = shikimori_api.animes(shikimori_id)
            shikimori_data = shikimori_req.GET()
            if shikimori_data.get('screenshots'):
                screenshots = []
                for i in shikimori_req.screenshots.GET():
                    item = {}
                    for j in i:
                        item[j] = ShikimoriLink+i[j]
                    screenshots.append(item)
                shikimori_data['screenshots'] = screenshots
            score = shikimori_data.get('score')
            if score:
                shikimori_data['score'] = float(score)
            shikimori_data['url'] = ShikimoriLink+shikimori_data.get('url')
            image = shikimori_data.get('image')
            if image:
                for i in image:
                    image[i] = ShikimoriLink+image[i]
                shikimori_data['image'] = image
            return shikimori_data


@inject
async def addDataToResponse(data, shikimori_search_function=None, service: Service = Depends(Provide[Container.service])):
    result_data = data.copy()
    shikimori_id = data.get('shikimori_id')
    cache_shikimori = None
    if shikimori_id:
        cache_shikimori = await service.GetCache(shikimori_key.format(shikimori_id))
        if cache_shikimori:
            shikimori_data = json.loads(cache_shikimori)
    if not cache_shikimori:
        shikimori_data = (await shikimori_search_function(data) if shikimori_search_function else None) or await SearchOnShikimori(
            data.get('en_title') or data.get('ru_title'))
        if shikimori_data:
            await service.SetCache(shikimori_key.format(shikimori_data.get('id')), json.dumps(shikimori_data), 60*60*24)
            data['shikimori_id'] = shikimori_data.get('id')
    result_data['shikimori'] = shikimori_data
    return result_data, data
