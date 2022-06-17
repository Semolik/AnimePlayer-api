import json
import re
from typing import Dict
import aiohttp
from lxml import etree
from .config import ApiLink, SiteLink, ModuleTitle, module_id
from ...settings import headers
from ...utils.shikimori import SearchOnShikimori
from ...utils.rule_34 import SearchOnRule34
from ...utils import names
from ...utils.genres import findInGenres
from fastapi import Depends
from ...containers import Container
from ...services import Service
from dependency_injector.wiring import inject, Provide
from bs4 import BeautifulSoup


async def ApiPost(method, data={}, get_data=True, session=None, not_close_session=False, one=True):
    session = session or aiohttp.ClientSession()
    response = await session.post(ApiLink+method, data=data)
    if response.status != 200:
        return
    response_json = await response.json()
    if not not_close_session:
        await session.close()
    if get_data is not True:
        return response_json
    data = response_json.get('data')
    if data:
        return data[0] if one else data


async def ApiGet(method, params={}, get_data=True, session=None, not_close_session=False, one=True):
    session = session or aiohttp.ClientSession()
    response = await session.get(ApiLink+method, params=params)
    if response.status != 200:
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


@inject
async def GetMirror(service: Service = Depends(Provide[Container.service])):
    key = f'{module_id}-mirror'
    value = await service.GetCache(key)
    if value:
        return value
    async with aiohttp.ClientSession() as session:
        response = await session.get(SiteLink, headers=headers)
        if response.status != 200:
            return
        html = await response.text()
    soup = BeautifulSoup(html, 'lxml')
    block = soup.select('#moduleLeft-1 > .interDub > a')
    if not block:
        return
    url = block[0].get('href')
    await service.SetCache(key, url, 60*60*5)
    return url


async def ClearDescription(description):
    return' '.join(description.replace(
        '\\', '').replace('<br />', '\n').split())


async def FormatGenres(genres):
    return [await FindGenre(genre.lower(), True) for genre in genres]


async def search(text, page):
    async with aiohttp.ClientSession() as session:
        form = aiohttp.FormData()
        form.add_field('subaction', 'search')
        form.add_field('story', text)
        form.add_field('search_start', page-1)
        response = await session.post(SiteLink+'index.php?do=search', data=form)
        if response.status != 200:
            return response.status
        html = await response.text()
    return await GetTitles('', html=html)


async def ResponseFormatting(response, full=False):
    text = response.get('title')
    title = text.replace('\\"', '"').replace("\\'", "'")
    data = {
        'ru_title': await names.GetTitle(title),
        'en_title': await names.GetOriginalTitle(title),
        'poster': response.get('urlImagePreview'),
        'id': response.get('id'),
        'rating': round(response.get('rating')/response.get('votes')*2, 1),
        'year': await FindGenre(response.get('year')),
        'genre': await FormatGenres(response.get('genre').split(', ')),
        'announce': response.get('series') == '',
        'type': response.get('type'),
    }
    description = response.get('description')
    if description:
        data['description'] = await ClearDescription(description)
    if not full:
        if response.get('series'):
            data['series_info'] = await names.GetSeriesFromTitle(text)
        return data

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
        data['type'] = await FindGenre(data_title_type, search_by_name=True)

    # data['service_title'] = ModuleTitle
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
        return await SearchOnShikimori(title, title_types.get(title_type.get('name')))


async def FindGenre(name: str, search_by_name=False, add_prelink=False):
    genres = await GetGenres()
    return await findInGenres(search_query=name, genres=genres, search_by_name=search_by_name, add_prelink=add_prelink)


def GetGenre(GenreUrl, page=None):
    Url = SiteLink+GenreUrl
    if page:
        Url += f'/page/{page}/'
    return GetTitles(Url)


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
            if response.status != 200:
                return
            html = await response.text()
    tree = etree.HTML(html)
    genre_xpath = '/html/body/div/div[2]/div[1]/ul/li[2]'
    category_xpath = '/html/body/div/div[2]/div[1]/ul/li[3]'
    year_xpath = '/html/body/div/div[2]/div[1]/ul/li[4]'
    data = {
        'genres': [
            await get_genre_data(tree, genre_xpath, '/div/span/a'),
            await get_genre_data(tree, category_xpath, '/span/span/a'),
            await fix_year(await get_genre_data(tree, year_xpath, '/span/span/a')),
        ],
        'sections': [
            {
                'name': 'Онгоинги',
                'prelink': '',
                'link': 'ongoing'
            },
        ]
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
    return [{'name': i.text.lower(), 'link': i.attrib.get('href').split('/')[-2]} for i in a_tags]


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
            },
        ],
        'poster': source['preview'],
        'name': source['name'],
    }


async def GetTitles(Url, html=None):
    if not html:
        async with aiohttp.ClientSession() as session:
            response = await session.get(Url, headers=headers)
            if response.status != 200:
                return response.status
            html = await response.text()
    soup = BeautifulSoup(html, 'lxml')
    titles = soup.find_all('div', class_='shortstory')
    if not titles:
        return
    output = list()
    mirror = await GetMirror()
    for i in titles:
        a = i.select(".shortstoryHead > h2 > a")[0]
        shortstoryContent = i.select(
            ".shortstoryContent > table > tr > td > p")
        text = a.text
        title = {
            'ru_title': await names.GetTitle(text),
            'en_title': await names.GetOriginalTitle(text),
            'poster': mirror+i.select(".shortstoryContent > table > tr > td > div > a > img")[0].get('src'),
            'id': await IdFromLink(a.get('href')),
            'rating': None,
            'announce': '[анонс]' in text.lower(),
        }
        if shortstoryContent:
            for i in shortstoryContent:
                name = i.find('strong')
                if not name:
                    continue
                value = name.nextSibling
                if name.text == 'Год выхода: ':
                    title['year'] = await FindGenre(value)
                if name.text == 'Описание: ':
                    title['description'] = await ClearDescription(value)
                if name.text == 'Жанр: ':
                    title['genre'] = await FormatGenres(value.split(', '))
        title['series'] = await names.GetSeriesFromTitle(text)
        output.append(title)
    NavBar = soup.find(class_='block_4')
    page = int([i for i in NavBar.select('span')
                if i.text.isdigit()][0].text) if NavBar else 1
    pages = int(NavBar.select('a')[-1].text) if NavBar else 1
    data = {
        'titles': output,
        'pages': pages if pages >= page else page,
    }
    return data


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


async def IdFromLink(url):
    return int(url.split('/')[-1].split('-')[0])


async def GetPageCount(response, page_quantity):
    count = response.get('state').get('count')
    return (count // page_quantity) + 1 if count % page_quantity > 1 else 0
