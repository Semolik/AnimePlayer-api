from typing import List
from pydantic import BaseModel
from .genres import genreItem
from .title import InfoItem, TitleBase


class TitleInfo(TitleBase):
    genre:  List[genreItem] | None = None
    series_info: str | None = None
    description: str | None = None
    other_info: List[InfoItem] | None = None


class TitleInfoStrId(TitleInfo):
    id: str


class TitlesPage(BaseModel):
    titles: List[TitleInfo]
    pages: int


class TitlesPageStrId(BaseModel):
    titles: List[TitleInfoStrId]
    pages: int
