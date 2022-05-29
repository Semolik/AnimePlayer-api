
from fastapi import APIRouter
from ....modules.animevost import utils
from ....models import TitlesPage
from ....config import page_quantity
from ....responses import Message
from fastapi.responses import JSONResponse
from ....utils.messages import messages
router = APIRouter()


@router.get("/", response_model=TitlesPage, responses={404: {"model": Message}})
async def get_page(page: int | None = 1):
    response = await utils.ApiGet('last', {'page': page, 'quantity': page_quantity}, one=False, get_data=False)
    if not response:
        return JSONResponse(status_code=404, content={"message": messages[404]})
    data = response.get('data')
    if data is None:
        return JSONResponse(status_code=404, content={"message": messages[404]})
    return {
        'titles': [await utils.ResponseFormatting(title) for title in data],
        'pages': await utils.GetPageCount(response, page_quantity),
    }
