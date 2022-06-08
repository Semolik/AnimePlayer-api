async def GetSeriesFromTitle(title):
    series = title.split(" /")
    if len(series) > 1:
        series = series[1].split("] [")
        if len(series) == 1:
            series = series[0].split(' [')
            if len(series) > 1:
                return series[1][:-1]
        elif series:
            series = series[0].split(' [')
            if len(series) > 1:
                return series[1]


async def GetTitle(fullTitle):
    return ' '.join(fullTitle.split('/',  maxsplit=1)[0].split())


async def GetOriginalTitle(fullTitle):
    splitedFullTitle = fullTitle.split('/',  maxsplit=1)
    if len(splitedFullTitle) == 2:
        return ' '.join(splitedFullTitle[1].split('[')[0].split())
