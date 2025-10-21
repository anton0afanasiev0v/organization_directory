from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...database import get_db
from ...security import verify_api_key
from ...service import OrganizationService, ActivityService, BuildingService
from ...dto import Organization, OrganizationCreate, OrganizationUpdate

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/", response_model=List[Organization])
async def get_organizations(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    organizations = await service.get_all_organizations()
    return organizations[skip:skip + limit]

@router.get("/{organization_id}", response_model=Organization)
async def get_organization(organization_id: int, db: AsyncSession = Depends(get_db)):
    service = OrganizationService(db)
    organization = await service.get_organization_by_id(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization

@router.get("/building/{building_id}", response_model=List[Organization])
async def get_organizations_by_building(building_id: int, db: AsyncSession = Depends(get_db)):
    # Сначала проверяем существование здания
    building_service = BuildingService(db)
    building = await building_service.get_building_by_id(building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )

    service = OrganizationService(db)
    return await service.get_organizations_by_building(building_id)

@router.get("/activity/{activity_id}", response_model=List[Organization])
async def get_organizations_by_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    # Сначала проверяем существование деятельности
    activity_service = ActivityService(db)
    activity = await activity_service.get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    service = OrganizationService(db)
    return await service.get_organizations_by_activity(activity_id)

@router.get("/search/name", response_model=List[Organization])
async def search_organizations_by_name(
        name: str = Query(..., description="Organization name to search"),
        db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    return await service.search_organizations_by_name(name)

@router.post("/", response_model=Organization, status_code=status.HTTP_201_CREATED)
async def create_organization(
        organization_data: OrganizationCreate,
        db: AsyncSession = Depends(get_db)
):
    service = OrganizationService(db)
    return await service.create_organization(organization_data)