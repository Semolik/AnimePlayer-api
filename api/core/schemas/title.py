from typing import Dict, List, Optional
from pydantic import BaseModel

from .rule34 import Rule34TitleInfo
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


class TitleBase(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str | None = None
    id: int
    genre:  List[genreItem]
    type: genreItem | None = None
    year: genreItem | None = None
    rating: float | None = None
    announce: bool

class Title(TitleBase):
    
    series: series
    description: str | None = None
    shikimori: Optional[Dict | None]
    rule34: Rule34TitleInfo  | None = None
    related: List[relatedItems] | None = None
    other_info: List[InfoItem] | None = None


class TitleStrId(Title):
    id: str
