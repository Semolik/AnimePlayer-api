import string
import aiohttp
from requests.utils import requote_uri
from ..settings import headers
from pygelbooru import Gelbooru, API_RULE34

gelbooru = Gelbooru(api=API_RULE34)


async def SearchOnRule34(name='', tag=None):
    try:
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
                                    print('--- result ---')
                                    print(result)
                                    print('--- result ---')
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
