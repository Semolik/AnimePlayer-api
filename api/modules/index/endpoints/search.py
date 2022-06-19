import asyncio
from fastapi import APIRouter
from ....core.schemas.search import SearchPage, SearchAll, Search
from .. import config
from ....responses import Message
from ....utils.messages import messages
from fastapi.responses import JSONResponse
router = APIRouter()


@router.post("/search", response_model=SearchPage, responses={404: {"model": Message}})
async def search_for_titles_across_all_modules(search_data: SearchAll):
    search_query = Search(text=search_data.text)
    items = await asyncio.gather(*[call_search(module, search_query) for module in config.modules])
    if not list(filter(lambda _: _.get('titles'), items)):
        return JSONResponse(status_code=404, content={"message": messages['404_all']})
    return {'items': items}


async def call_search(module, search_query):
    search_result = await module.endpoints.search.search_titles(search_query)
    return {
        'module_name': module.config.ModuleTitle,
        'module_id': module.config.module_id,
        'titles': search_result.get('titles') if isinstance(search_result, dict) else []
    }
