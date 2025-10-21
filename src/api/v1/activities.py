from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...security import verify_api_key
from ...service import ActivityService
from ...dto import Activity, ActivityCreate, ActivityTree
from ..dependencies import get_activity_service

router = APIRouter(
    prefix="/activities",
    tags=["activities"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/", response_model=List[Activity])
async def get_activities(service: ActivityService = Depends(get_activity_service)):
    return await service.get_all_activities()

@router.get("/tree", response_model=List[ActivityTree])
async def get_activity_tree(
    max_level: int = 3, 
    service: ActivityService = Depends(get_activity_service)
):
    return await service.get_activity_tree(max_level)

@router.get("/{activity_id}", response_model=Activity)
async def get_activity(
    activity_id: int, 
    service: ActivityService = Depends(get_activity_service)
):
    activity = await service.get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    return activity