from typing import Dict, List
from pydantic import BaseModel
from .error import ErrorModel


class Rule34TitleInfo(BaseModel):
    content: List[Dict] | None = None
    error: ErrorModel
