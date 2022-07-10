from typing import Dict, Optional
from .title import TitleBase
from .shikimori import ShikimoriShortInfo

class ShortInfoItem(TitleBase):
    shikimori: Optional[ShikimoriShortInfo | None]
    description: str
    

