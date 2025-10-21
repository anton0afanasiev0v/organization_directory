from ..database import get_db
from ..service import BuildingService, ActivityService, OrganizationService
from fastapi import Depends

async def get_building_service(db=Depends(get_db)) -> BuildingService:
    return BuildingService(db)

async def get_activity_service(db=Depends(get_db)) -> ActivityService:
    return ActivityService(db)

async def get_organization_service(db=Depends(get_db)) -> OrganizationService:
    return OrganizationService(db)