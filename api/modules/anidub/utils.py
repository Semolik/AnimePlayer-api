import aiohttp
from bs4 import BeautifulSoup
import requests
from soupsieve import select
from ...settings import headers
from . import config
from ...utils import names


async def GetTitles(Url, html=None):
    if not html:
        response = requests.get(Url, headers=headers)
        response.encoding = 'utf8'
    if html or response:
        soup = BeautifulSoup(response.text if not html else html, 'lxml')
        data = soup.select('#dle-content')
        if not data:
            return 500
        data = data[0]
        outdata = list()
        titles = data.select('.th-item')
        if not titles:
            return 404
        for title in titles:
            th_in = title.select('.th-in')
            poster = th_in[0].select(
                '.th-img > img')[0].get('data-src').replace('thumbs/', '')
            title_info = {
                'poster': (poster if 'http' in poster else config.SiteLink+poster),
                'id': config.LinkSplitter.join(th_in[0].get('href').split('/')[3:]).split('.')[0],
            }
            try:
                title_info['rating'] = float(th_in[0].select('.th-rating')[0].text)
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
            if ru_title:
                title_info['ru_title'] = ru_title
            if en_title:
                title_info['en_title'] = en_title
            if series:
                title_info['series'] = series

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
                    title_info['genre'] = FormatLinkList(
                        short_info[0].select('a'), genre=True)
                    continue
                if 'Год:' == text[0]:
                    title_info['year'] = FormatLinkList(
                        short_info[0].select('a'), genre=True, one=True)
                    continue
                text[0] = text[0].replace(':', '')
                name = text.pop(0)
                value = ', '.join([i for i in text if i != ',']) if len(text) > 1 else text[0]
                info.append({'name': name, 'value': value})
            title_info['other_info'] = info
            th_tip_text = title.select('.th-tip-text')
            if th_tip_text:
                title_info['description'] = th_tip_text[0].text
            outdata.append(title_info)
        pages = data.select('.navigation *')
        return {
            'titles': outdata,
            'pages': int(pages[-1].text) if pages else 1,
        }
    else:
        return {
            'status': response.status_code if not html else 404,
            'message': "messages.get('not_response')",
        }


def FormatLinkList(a_tags, genre=False, one=False):
    array = [[i.text.lower(), i.get('href').split('/')] for i in a_tags]
    data = [{'name': i[0], 'link':i[1][-2]}
            for i in array] if genre else[[i[0], i[1][-1]] for i in array]
    return data[0] if one and data else data
