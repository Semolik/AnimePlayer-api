import json
import aiohttp
from bs4 import BeautifulSoup
from ...settings import headers
from . import config
from ...utils import names
from ...utils.genres import findInGenres
from fastapi import Depends
from ...containers import Container
from ...services import Service
from dependency_injector.wiring import inject, Provide
from lxml import etree


async def GetTitles(Url, html=None):
    if not html:
        async with aiohttp.ClientSession() as session:
            response = await session.get(Url, headers=headers)
            if response.status != 200:
                return response.status
            html = await response.text()
    if html:
        soup = BeautifulSoup(html, 'lxml')
        data = soup.select('#dle-content')
        if not data:
            return 500
        data = data[0]
        outdata = list()
        titles = data.select('.th-item')
        if not titles:
            return 404
        for title in titles:
            th_in = title.select('a.th-in')
            if not th_in or '/anime/' not in th_in[0].get('href'):
                continue
            poster = th_in[0].select(
                '.th-img > img')[0].get('data-src').replace('thumbs/', '')
            title_info = {
                'poster': (poster if 'http' in poster else config.SiteLink+poster),
                'id': config.LinkSplitter.join(th_in[0].get('href').split('/')[3:]).split('.')[0],
            }
            try:
                title_info['rating'] = float(
                    th_in[0].select('.th-rating')[0].text)
            except ValueError:
                pass
            th_tip = title.select('.th-tip.hidden')
            if not th_tip:
                continue
            title_text_block = th_tip[0].select('.th-tip-header > .fx-1')[0]
            title_text = title_text_block.text
            ru_title = await names.GetTitle(title_text)
            en_title = await names.GetOriginalTitle(title_text)
            series = await names.GetSeriesFromTitle(title_text)
            title_info['ru_title'] = ru_title if ru_title else 'Ошибка получения названия'
            if en_title:
                title_info['en_title'] = en_title
            if series:
                title_info['series_info'] = series
            th_tip_list_elems = title.select('.th-tip-list > li')
            info = list()
            for li in th_tip_list_elems:
                short_info = li.select('.short-info')
                if not short_info:
                    continue
                text = list(
                    filter(None, [' '.join(i.text.split()) for i in short_info[0].children]))
                if not text or text[0] in ('Ссылка на трекер:', 'Количество серий:', 'День недели:'):
                    continue
                if 'Жанр:' == text[0]:
                    links, prelink = FormatLinkList(
                        short_info[0].select('a'), genre=True)
                    title_info['genre'] = links
                    continue
                if 'Год:' == text[0]:
                    links, prelink = FormatLinkList(
                        short_info[0].select('a'), genre=True, one=True)
                    title_info['year'] = links
                    continue
                text[0] = text[0].replace(':', '')
                name = text.pop(0)
                value = ', '.join([i for i in text if i != ',']) if len(
                    text) > 1 else text[0]
                info.append({'name': name, 'value': value})
            title_info['other_info'] = info
            th_tip_text = title.select('.th-tip-text')
            if th_tip_text:
                title_info['description'] = th_tip_text[0].text
            th_tip_category = title.select('.th-tip-btm > .th-tip-category')
            title_info['announce'] = th_tip_category[0].text == (await FindGenre('anime_ongoing')).get('name') if th_tip_category else False
            outdata.append(title_info)
        pages = data.select('.navigation *')
        return {
            'titles': outdata,
            'pages': int(pages[-1].text) if pages else 1,
        }
    else:
        return 500


def FormatLinkList(a_tags, genre=False, one=False):
    array = [[i.text.lower(), i.get('href').split('/')] for i in a_tags]
    data = [{'name': i[0], 'link':i[1][-2 if genre else -1]} for i in array]
    return data[0] if one and data else data, array[0][1][1] if data else None


@inject
async def GetGenres(html: str | None = None, service: Service = Depends(Provide[Container.service])):
    key = f'{config.module_id}-genres'
    value = await service.GetCache(key)
    if value:
        return json.loads(value)
    if not html:
        async with aiohttp.ClientSession() as session:
            response = await session.get(config.SiteLink, headers=headers)
            if response.status != 200:
                return
            html = await response.text()
    tree = etree.HTML(html)
    genre_xpath = '//*[@id="header"]/div/ul/li[2]'
    data = {
        'genres': [
            await get_genre_data(tree, genre_xpath, '/div/ul/li/a'),
            await get_genre_data(tree, genre_xpath, '/div/div/ul[1]/li/a', custom_name='Категория'),
        ],
        'sections': [
            {
                'name': 'Онгоинги',
                'prelink': 'anime',
                'link': 'anime_ongoing'
            },
            {
                'name': 'Дорамы',
                'prelink': '',
                'link': 'dorama'
            },
            {
                'name': 'Анонсы',
                'prelink': '',
                'link': 'anons_ongoing'
            },
        ]
    }
    await service.SetCache(key, json.dumps(data), 60*60*24)
    return data


async def get_genre_data(tree, xpath, end_path, custom_name=None):
    a = tree.xpath(xpath+'/a')[0]
    links, prelink = FormatLinkList(tree.xpath(xpath+end_path))
    data = {
        'name': custom_name or a.text,
        'prelink': prelink,
        'links': links,
    }
    return data


async def FindGenre(search_query: str, name='', search_by_name=False, add_prelink=False):
    genres = await GetGenres()
    return await findInGenres(search_query=search_query, name=name, genres=genres, search_by_name=search_by_name, add_prelink=add_prelink)


async def GetGenre(GenreUrl, page=None):
    Url = config.SiteLink+GenreUrl
    if page and page > 1:
        Url += f'/page/{page}/'
    return await GetTitles(Url)


async def GetTitleById(title_id: str):
    async with aiohttp.ClientSession() as session:
        response = await session.get(config.SiteLink+'/'.join(title_id.split(config.LinkSplitter))+'.html', headers=headers)
        if response.status != 200:
            return response.status
        html = await response.text()
    soup = BeautifulSoup(html, 'lxml')
    dle_content = soup.select('#dle-content')
    if not dle_content:
        return 500
    out = {
        'id': title_id
    }
    title = dle_content[0].select('.fright.fx-1 > h1')
    if not title:
        return
    raw_title = title[0].text
    title = raw_title.split('/')
    out['ru_title'] = title[0]
    if len(title) > 1:
        out['en_title'] = title[1].split(' [')[0]
    fleft = dle_content[0].select('.fleft')
    if not fleft:
        return
    poster = dle_content[0].select('.fposter > img')
    if poster:
        poster = poster[0].get('data-src')
    out['poster'] = (
        poster if 'http' in poster else config.SiteLink+poster) if poster else None
    fmeta_links = dle_content[0].select('.fmeta > span > a')
    if fmeta_links:
        for a in fmeta_links:
            href = a.get('href')
            if '/year/' in href:
                out['year'] = {
                    'name': a.text,
                    'link': href.split('/')[-2],
                }
            elif a == fmeta_links[-1]:
                link_parts = list(filter(None, a.get('href').split('/')))
                out['announce'] = link_parts and link_parts[-1] == 'anons_ongoing'
                out['type'] = await FindGenre(link_parts[-1], name=a.text)
    short_info = dle_content[0].select('ul.flist > li.short-info')
    if short_info:
        info = list()
        for info_item in short_info:
            if info_item:
                text = list(
                    filter(None, [' '.join(i.text.split()) for i in info_item.children]))
                if not text or text[0] in ('Ссылка на трекер:', 'Количество серий:'):
                    continue
                if 'Жанр:' == text[0]:
                    links, prelink = FormatLinkList(
                        info_item.select('a'), genre=True)
                    out['genre'] = links
                    continue
                if 'День недели:' == text[0]:
                    continue
                text[0] = text[0].replace(':', '')
                name = text.pop(0)
                value = ', '.join([i for i in text if i != ',']) if len(
                    text) > 1 else text[0]
                info.append({'name': name, 'value': value})
        out['other_info'] = info
    rating = dle_content[0].select(
        '.multirating-wrapper > .multirating-items-wrapper > .multirating-itog > span.multirating-itog-rateval')
    if rating:
        try:
            out['rating'] = float(rating[0].text)
        except ValueError:
            pass
    if not out.get('rating'):
        out['rating'] = 0
    series = list()
    series_elems = dle_content[0].select(
        '.fplayer.tabs-box > .tabs-b > .tabs-box > .tabs-sel')
    if len(series_elems) > 1:
        for link in [i for i in series_elems[1].select('span')]:
            series.append({
                'sources': [
                    {
                        'src': f'/utilities/sibnet?sibnet_id={link.get("data").split("=")[-1]}',
                        'size': 720,
                    }
                ],
                'name': link.text,
            })
    out['series'] = {
        'items': series,
        'request_required': True,
        'info': await names.GetSeriesFromTitle(raw_title),
    }
    related_items = dle_content[0].select('.related > .th-item')
    related = list()
    if related_items:
        related_list = list()
        for i in related_items:
            related_item = {}
            th_in = i.select('a.th-in')
            href = th_in[0].get('href')
            if not th_in or '/anime/' not in href:
                continue
            related_poster = i.select('img')
            if related_poster:
                related_poster = related_poster[0].get(
                    'data-src').replace('/small/', '/')
                related_item['poster'] = (
                    related_poster if 'http' in related_poster else config.SiteLink+related_poster)
            else:
                related_item['poster'] = None
            related_title = i.select('.th-title')
            if related_title:
                related_item['ru_title'] = related_title[0].text
            related_item['id'] = config.LinkSplitter.join(
                href.split('/')[3:]).split('.')[0]
            related_list.append(related_item)
        related.append({
            'name': 'Рекомендации',
            'items': related_list,
        })
    out['related'] = related
    return out


async def search(text, page):
    async with aiohttp.ClientSession() as session:
        response = await session.post(config.SiteLink+'index.php?do=search', params={'story': text, 'result_from': 1, 'full_search': 0, 'search_start': page or 1, 'subaction': 'search', 'do': 'search'}, headers=headers)
        if response.status != 200:
            return
        html = await response.text()
        return await GetTitles('', html)
