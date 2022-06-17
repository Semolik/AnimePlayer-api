from fastapi import APIRouter, Depends
from .. import utils, config
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....core.schemas.titles import TitlesPageStrId
from ....core.schemas.search import Search
import json

from ....responses import Message
from ....utils.messages import messages
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/search", response_model=TitlesPageStrId, responses={404: {"model": Message}})
@inject
async def search_titles(search_data: Search, service: Service = Depends(Provide[Container.service])):
    key = f'search_{config.module_id}_{"_".join(search_data.text.split(" "))}_{search_data.page}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    titles = await utils.search(text=search_data.text, page=search_data.page)
    if isinstance(titles, int):
        return JSONResponse(status_code=titles, content={"message": messages[{500: 'not_response', 404: 404}[titles]]})
    await service.SetCache(key, json.dumps(titles))
    return titles
