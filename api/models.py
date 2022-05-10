from typing import Dict, List, Optional

from pydantic import BaseModel


class Title(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str
    id: int
    rating: float
    year: List[str]
    genre: List[List[str]]
    announce: bool
    series: Dict
    description: str | None = None
    shikimori: Optional[Dict | None]
    rule34: List | None = None


class TitleInfo(BaseModel):
    ru_title: str
    en_title: str | None = None
    poster: str
    id: int
    rating: float
    year: str
    genre: List[str]
    announce: bool
    series: str
    description: str
