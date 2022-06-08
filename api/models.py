from typing import Dict, List, Optional
from pydantic import BaseModel


class genreItem(BaseModel):
    name: str
    link: str | None = None


class Title(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str
    id: int
    rating: float
    year: genreItem
    genre:  List[genreItem]
    type: genreItem
    announce: bool
    series: Dict
    description: str | None = None
    shikimori: Optional[Dict | None]
    rule34: List[Dict] | None = None


class InfoItem(BaseModel):
    name: str
    value: str


class TitleInfo(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str
    id: int
    rating: float | None = None
    year: genreItem
    genre: List[genreItem]
    announce: bool | None = None
    series: str | None = None
    description: str
    other_info: List[InfoItem]


class TitleStrId(TitleInfo):
    id: str


class TitlesPage(BaseModel):
    titles: List[TitleInfo]
    pages: int


class TitlesPageStrId(BaseModel):
    titles: List[TitleStrId]
    pages: int


class Genre(BaseModel):
    name: str
    prelink: str
    links: List[genreItem]
