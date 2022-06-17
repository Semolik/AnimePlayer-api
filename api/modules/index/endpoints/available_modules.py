from typing import List
from fastapi import APIRouter
from .. import config
router = APIRouter()


@router.get("/available_modules", response_model=List[str])
async def available_modules_ids():
    return [module.config.module_id for module in config.modules]
