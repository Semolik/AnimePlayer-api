from typing import List
from pydantic import BaseModel
from .genres import genreItem
from .title import InfoItem


class TitleInfo(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str
    id: int
    rating: float | None = None
    year: genreItem
    genre: List[genreItem]
    announce: bool
    series_info: str | None = None
    description: str
    other_info: List[InfoItem] | None = None


class TitleInfoStrId(TitleInfo):
    id: str


class TitlesPage(BaseModel):
    titles: List[TitleInfo]
    pages: int


class TitlesPageStrId(BaseModel):
    titles: List[TitleInfoStrId]
    pages: int
