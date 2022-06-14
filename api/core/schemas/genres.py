from typing import List
from pydantic import BaseModel


class genreItem(BaseModel):
    name: str
    link: str | None = None


class Genre(BaseModel):
    name: str
    prelink: str
    links: List[genreItem]


class Section(BaseModel):
    name: str
    prelink: str
    link: str


class Genres(BaseModel):
    genres: List[Genre]
    sections: List[Section]
