from fastapi import Query
from pydantic import BaseModel

class Search(BaseModel):
    text: str = Query(default=None, min_length=4)
    page: int | None = 1
