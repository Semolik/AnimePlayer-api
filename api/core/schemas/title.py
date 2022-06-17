from typing import Dict, List, Optional
from pydantic import BaseModel
from .genres import genreItem
from .series import series


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
