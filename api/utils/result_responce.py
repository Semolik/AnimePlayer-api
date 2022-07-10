import json
from . import rule_34, shikimori
from .messages import messages

import aiohttp
from fastapi.responses import JSONResponse


async def GetResultResponce(key, service, data, horny, search_function=None):
    error = None
    try:
        result_data, data = await rule_34.addDataToResponse(data) if horny else await shikimori.addDataToResponse(data, search_function)
    except aiohttp.client_exceptions.ClientConnectorError:
        error = messages['rule34_connection_error'] if horny else messages['shikimori_connection_error']
    except:
        error = messages['rule34_error'] if horny else messages['shikimori_error']
    if not error:
        await service.SetCache(key, json.dumps(data))
        return result_data
    data['rule34' if horny else 'shikimori'] = {'error': {'message': error}}
    return data


async def GetResultResponceWithErrorIfNotLoaded(key, service, data, horny, search_function=None):
    try:
        result_data, data = await rule_34.addDataToResponse(data) if horny else await shikimori.addDataToResponse(data, search_function)
    except aiohttp.client_exceptions.ClientConnectorError:
        return JSONResponse(status_code=502, content={"message": messages['rule34_connection_error'] if horny else messages['shikimori_connection_error']})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": messages[500]})
    await service.SetCache(key, json.dumps(data))
    return result_data
