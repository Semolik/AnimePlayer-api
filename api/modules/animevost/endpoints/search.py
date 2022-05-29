
from fastapi import APIRouter, Depends
from ....modules.animevost import utils
from ....containers import Container
from ....services import Service
from dependency_injector.wiring import inject, Provide
from ....models import TitlesPage
from ....schemas import Search
from ....modules.animevost import config
import json

from ....responses import Message
from ....utils.messages import messages
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/search", response_model=TitlesPage, responses={404: {"model": Message}})
@inject
async def search_titles(search_data: Search, service: Service = Depends(Provide[Container.service])):
    key = f'search_{config.module_id}_{"_".join(search_data.text.split(" "))}_{search_data.page}'
    cache_data = await service.GetCache(key)
    if cache_data:
        return json.loads(cache_data)
    titles = await utils.search(text=search_data.text, page=search_data.page)
    if not titles:
        return JSONResponse(status_code=404, content={"message": messages[404]})
    await service.SetCache(key, json.dumps(titles))
    return titles
