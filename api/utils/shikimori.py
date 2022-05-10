import aiohttp
from ..config import ShikimoriLink
from requests.utils import requote_uri
from ..settings import headers
# import httpx
from lxml import etree
import ssl
import certifi
from ..config import ShikimoriLink, shikimori_api


async def SearchOnShikimori(name, kind=None):
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    conn = aiohttp.TCPConnector(ssl=ssl_context)
    async with aiohttp.ClientSession(connector=conn) as session:
        response = await session.get(f'https://shikimori.one/animes/autocomplete/v2?search={requote_uri(name)}', headers=headers)
        if response.status!=200:
            print(f'--- shikimori status {response.status} ---')
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
