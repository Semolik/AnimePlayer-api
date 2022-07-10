from pydantic import BaseModel


class moduleInfoSchema(BaseModel):
    module_title: str
    module_id: str
