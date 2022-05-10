import json
import re
from typing import Dict
import aiohttp
from lxml import etree
from .config import ApiLink, SiteLink, ModuleTitle, hentai, module_id
from ...config import ShikimoriLink, shikimori_api
from ...settings import headers
from ...utils.shikimori import SearchOnShikimori
from ...utils.rule_34 import SearchOnRule34
from fastapi import Depends
from ...containers import Container
from ...services import Service
from dependency_injector.wiring import inject, Provide


async def ApiPost(method, data={}, get_data=True, session=None, not_close_session=False, one=True):
    session = session or aiohttp.ClientSession()
    response = await session.post(ApiLink+method, data=data)
    if response.status!=200:
        return
    response_json = await response.json()
    if not not_close_session:
        await session.close()
    if get_data is not True:
        return response_json
    data = response_json.get('data')
    if data:
        return  data[0] if one else data


async def ApiGet(method, params={}, get_data=True, session=None, not_close_session=False, one=True):
    session = session or aiohttp.ClientSession()
    response = await session.get(ApiLink+method, params=params)
    if response.status!=200:
        return
    response_json = await response.json()
    if not not_close_session:
        await session.close()
    state = response_json.get('state')
    if state and state.get('status') != 'ok':
        return
    if get_data is not True:
        return response_json
    data = response_json.get('data')
    if data:
        return data[0] if one else data


async def ResponseFormatting(response, full=False):
    text = response.get('title')
    title = text.replace('\\"', '"').replace("\\'", "'")
    data = {
        'ru_title': await GetTitle(title),
        'en_title': await GetOriginalTitle(title),
        'poster': response.get('urlImagePreview'),
        'id': response.get('id'),
        'rating': round(response.get('rating')/response.get('votes')*2, 1),
        'year': response.get('year'),
        'genre': response.get('genre').split(', '),
        'announce': response.get('series') == '',
        'type': response.get('type'),
    }
    description = response.get('description')
    if description:
        data['description'] = ' '.join(description.replace(
            '\\', '').replace('<br />', '\n').split())
    if not full:
        if response.get('series'):
            series = text.split(" /")
            if len(series) > 1:
                series = series[1].split("] [")
                if len(series) == 1:
                    series = series[0].split(' [')
                    if len(series) > 1:
                        data['series'] = series[1][:-1]
                elif series:
                    series = series[0].split(' [')
                    if len(series) > 1:
                        data['series'] = series[1]
        return data

    out_genre = list()
    for genre in data.get('genre'):
        found_genre = await FindGenre(genre.lower())
        if found_genre:
            out_genre.append(found_genre)
        else:
            out_genre.append([genre])
    data['genre'] = out_genre
    year = await FindGenre(response.get('year'))
    if year:
        data['year'] = year
    else:
        data['year'] = [response.get('year')]
    series = await ApiPost('playlist', {'id': response.get('id')}, get_data=False)
    if series:
        series_ = await SortPlaylist(series)
        data['series'] = {
            'info': re.findall('\[(.*?)\]', response.get('title')),
            'data': series_,
            'direct_link': True,
        }
    else:
        data['series'] = None
    data_title_type = data.get('type')
    if data_title_type:
        title_type = await FindGenre(data_title_type)
        if title_type:
            data['type'] = title_type
        else:
            data['type'] = [data.get('type')]
    data['service_title'] = ModuleTitle
    # data['horny'] = hentai
    return data


async def shikimori_search(data):
    title_types = {
        "ТВ": 'tv',
        "OVA": 'ova',
        "ONA": 'ona',
        "ТВ-спэшл": 'special',
        "полнометражный фильм": 'movie'
    }
    title = data.get('en_title') or data.get('ru_title')
    title_type = data.get('type')
    if title_type and title:
        return await SearchOnShikimori(title, title_types.get(title_type[0]))


async def rule34_search(data):
    title = data.get('en_title')
    if title:
        print('en_title есть')
        return await SearchOnRule34(title)
    print('en_title нету')


async def GetTitle(fullTitle):
    return ' '.join(fullTitle.split('/',  maxsplit=1)[0].split())


async def GetOriginalTitle(fullTitle):
    splitedFullTitle = fullTitle.split('/',  maxsplit=1)
    if len(splitedFullTitle) == 2:
        return ' '.join(splitedFullTitle[1].split('[')[0].split())


async def FindGenre(name: str):
    name_lower = name.lower()
    genres = await GetGenres()
    if genres:
        for key, value in genres.items():
            for j in value.get('links'):
                if j[0] == name_lower:
                    return [name, j[1]]


async def fix_year(year: Dict):
    year['links'] = year['links'][::-1]
    return year


@inject
async def GetGenres(html=None, service: Service = Depends(Provide[Container.service])):
    key = f'{module_id}-genres'
    value = await service.GetCache(key)
    if value:
        return json.loads(value)
    if not html:
        async with aiohttp.ClientSession() as session:
            response = await session.get(SiteLink, headers=headers)
            if response.status!=200:
                return
            html = await response.text()
    tree = etree.HTML(html)
    genre_xpath = '/html/body/div/div[2]/div[1]/ul/li[2]'
    category_xpath = '/html/body/div/div[2]/div[1]/ul/li[3]'
    year_xpath = '/html/body/div/div[2]/div[1]/ul/li[4]'
    data = {
        'genre': await get_genre_data(tree, genre_xpath, '/div/span/a'),
        'category': await get_genre_data(tree, category_xpath, '/span/span/a'),
        'year': await fix_year(await get_genre_data(tree, year_xpath, '/span/span/a')),
    }
    await service.SetCache(key, json.dumps(data), 60*60*24)
    return data


async def get_genre_data(tree, xpath, end_path):
    a = tree.xpath(xpath+'/a')[0]
    return {
        'name': a.text,
        'prelink': a.attrib.get('href').replace('/', ''),
        'links': await FormatLinkList(tree.xpath(xpath+end_path)),
    }


async def FormatLinkList(a_tags):
    return [[i.text.lower(), i.attrib.get('href').split('/')[-2]] for i in a_tags]


def Sorting(item: Dict) -> int:
    name = item.get('name')
    numbers = re.findall('[0-9]+', name)
    if numbers:
        return int(numbers[0])
    return -1


async def PlyrSource(source):
    return {
        'type': "video",
        'sources': [
                {
                    'src': source['hd'],
                    'size': 720,
                },
            {
                    'src': source['std'],
                    'size': 480,
                    }
        ],
        'poster': source['preview'],
        'name': source['name'],
    }


async def SortPlaylist(playlist):
    series = list()
    other = list()
    for i in playlist:
        if 'серия' in i.get('name').lower():
            series.append(i)
        else:
            other.append(i)
    if series:
        series = sorted(series, key=Sorting)
    other = sorted(other, key=lambda _: _.get('name'))
    return [await PlyrSource(i) for i in series+other]
