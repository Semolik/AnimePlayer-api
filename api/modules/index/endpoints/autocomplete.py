import asyncio
from fastapi import APIRouter, BackgroundTasks

from api.core.schemas.error import ErrorModel
from ....core.schemas.autocomplete import autocompleteAllSearch, autocompleteAllSearchBody
from .. import config
from ....utils.messages import messages
from fastapi.responses import JSONResponse
router = APIRouter()


@router.post("/autocomplete", response_model=autocompleteAllSearch, responses={404: {"model": ErrorModel}})
async def autocomplete_search_for_titles_across_all_modules(body: autocompleteAllSearchBody, background_tasks: BackgroundTasks):
    text = body.text
    items = list(filter(None, await asyncio.gather(*[call_autocomplete(module, background_tasks=background_tasks, text=text) for module in config.modules])))
    if not items:
        return JSONResponse(status_code=404, content={"message": messages['404_all']})
    return {'items': items}


async def call_autocomplete(module, text, background_tasks):
    search_result = await module.endpoints.autocomplete.autocomplete_search_titles(text=text, background_tasks=background_tasks)
    return {
        'module_name': module.config.ModuleTitle,
        'module_id': module.config.module_id,
        'titles': cut_array(search_result.get('titles'), 4)
    } if isinstance(search_result, dict) and search_result.get('titles') else None


def cut_array(array, length):
    if len(array) > length:
        return array[0:length]
    return array
