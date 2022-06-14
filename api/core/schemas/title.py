from typing import Dict, List, Optional
from pydantic import BaseModel, conlist
from .genres import genreItem


class relatedItem(BaseModel):
    ru_title: str
    poster: str | None = None
    id: str


class relatedItems(BaseModel):
    name: str
    items: List[relatedItem]


class InfoItem(BaseModel):
    name: str
    value: str


class sourceItem(BaseModel):
    src: str
    size: int


class seriesItem(BaseModel):
    name: str
    sources: List[sourceItem]


class series(BaseModel):
    items: conlist(seriesItem, min_items=0)
    info: str
    request_required: bool


class Title(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str | None = None
    id: int
    rating: float
    year: genreItem | None = None
    genre:  List[genreItem]
    type: genreItem
    announce: bool
    series: series
    description: str | None = None
    shikimori: Optional[Dict | None]
    rule34: List[Dict] | None = None
    related: List[relatedItems] | None = None
    other_info: List[InfoItem] | None = None


class TitleStrId(Title):
    id: str
