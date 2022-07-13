from pydantic import BaseModel


class Image(BaseModel):
    url: str
    blurhash: str | None = None
