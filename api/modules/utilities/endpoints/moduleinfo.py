from ....core.schemas.moduleinfo import moduleInfoSchema
from fastapi import APIRouter
from ....modules.index import config 
from ....responses import Message
from fastapi.responses import JSONResponse
router = APIRouter()


@router.get("/moduleinfo", response_model=moduleInfoSchema,responses={404: {"model": Message}})
async def module_information_by_id(module_id: str):
    for module in config.modules:
        module_config = module.config
        if module_config.module_id == module_id:
            return {
                'module_title': module_config.ModuleTitle,
                'module_id': module_id
            }
    return JSONResponse(status_code=404, content={"message": "Такого модуля нет"})
