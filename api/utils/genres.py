async def findInGenres(search_query: str, genres, name='', search_by_name=False, add_prelink=False):
    search_query_lower = search_query.lower()
    if genres:
        for genre in genres.get('genres'):
            for link in genre.get('links'):
                if (link.get('name') if search_by_name else link.get('link')) == search_query_lower:
                    if add_prelink:
                        link['prelink'] = genre.get('prelink')
                    return link
        for section in genres.get('sections'):
            if (section.get('name') if search_by_name else section.get('link')) == search_query_lower:
                return section
    return {
        'name': search_query_lower if search_by_name else name,
        'link': None,
    }
