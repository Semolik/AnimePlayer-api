from typing import List
from pydantic import BaseModel


class autocompleteSearchItem(BaseModel):
    id: int
    name: str
    poster: str


class autocompleteSearchItemStrId(autocompleteSearchItem):
    id: str


class autocompleteSearch(BaseModel):
    titles: List[autocompleteSearchItem]


class autocompleteSearchStrIds(autocompleteSearch):
    titles: List[autocompleteSearchItemStrId]


class autocompleteModuleSearchItem(BaseModel):
    module_name: str
    module_id: str
    titles: List[autocompleteSearchItemStrId | autocompleteSearchItem]

class autocompleteModuleSearch(BaseModel):
    items: List[autocompleteModuleSearchItem]

