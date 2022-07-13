from typing import List
from fastapi import Query
from pydantic import BaseModel
from .image import Image


class autocompleteSearchItem(BaseModel):
    id: int
    name: str
    poster: Image


class autocompleteSearchItemStrId(autocompleteSearchItem):
    id: str


class autocompleteSearch(BaseModel):
    titles: List[autocompleteSearchItem]


class autocompleteSearchStrIds(autocompleteSearch):
    titles: List[autocompleteSearchItemStrId]


class autocompleteModuleItem(BaseModel):
    module_name: str
    module_id: str
    titles: List[autocompleteSearchItemStrId | autocompleteSearchItem]


class autocompleteAllSearch(BaseModel):
    items: List[autocompleteModuleItem]


class autocompleteAllSearchBody(BaseModel):
    text: str = Query(default=None, min_length=1)
