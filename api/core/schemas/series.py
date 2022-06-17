from typing import List
from pydantic import BaseModel, conlist


class sourceItem(BaseModel):
    src: str
    size: int


class seriesItem(BaseModel):
    name: str
    sources: List[sourceItem]


class seriesItemWithoutName(BaseModel):
    sources: List[sourceItem]


class series(BaseModel):
    items: conlist(seriesItem, min_items=0)
    info: str
    request_required: bool
