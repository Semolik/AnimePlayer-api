from typing import List
from fastapi import APIRouter
from ....modules.animevost import utils
from ....models import TitleInfo
from ....config import page_quantity
from ....responses import Message
from fastapi.responses import JSONResponse
router = APIRouter()


@router.get("/", response_model=List[TitleInfo], responses={404: {"model": Message}})
async def get_page(page: int | None = 1):
    response = await utils.ApiGet('last', {'page': page, 'quantity': page_quantity}, one=False)
    if not response:
        return JSONResponse(status_code=404, content={"message": "Item not found"})
    return [await utils.ResponseFormatting(title) for title in response]
