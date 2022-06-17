from typing import List
from fastapi import Query
from pydantic import BaseModel

from api.core.schemas.titles import TitleInfo, TitleInfoStrId


class SearchAll(BaseModel):
    text: str = Query(default=None, min_length=4)


class Search(SearchAll):
    page: int | None = 1


class SearchItem(BaseModel):
    module_name: str
    module_id: str
    titles: List[TitleInfo | TitleInfoStrId]


class SearchPage(BaseModel):
    items: List[SearchItem]
