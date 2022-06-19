import asyncio
from fastapi import APIRouter
from ....core.schemas.autocomplete import autocompleteModuleSearch
from .. import config
from ....responses import Message
from ....utils.messages import messages
from fastapi.responses import JSONResponse
router = APIRouter()


@router.post("/autocomplete", response_model=autocompleteModuleSearch, responses={404: {"model": Message}})
async def autocomplete_search_for_titles_across_all_modules(text: str):
    items = list(filter(None, await asyncio.gather(*[call_autocomplete(module, text) for module in config.modules])))
    if not items:
        return JSONResponse(status_code=404, content={"message": messages['404_all']})
    return {'items': items}


async def call_autocomplete(module, text):
    search_result = await module.endpoints.autocomplete.autocomplete_search_titles(text)
    return {
        'module_name': module.config.ModuleTitle,
        'module_id': module.config.module_id,
        'titles': search_result.get('titles')
    } if isinstance(search_result, dict) and search_result.get('titles') else None
