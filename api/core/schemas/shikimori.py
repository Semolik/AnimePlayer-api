from typing import Dict, List
from pydantic import BaseModel

class ShikimoriShortInfo(BaseModel):
    score: float
    status: str
    studios: List[Dict]
    kind: str