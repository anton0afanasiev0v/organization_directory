from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...security import verify_api_key
from ...service import OrganizationService, BuildingService, ActivityService
from ...dto import Organization, OrganizationCreate
from ..dependencies import get_organization_service, get_building_service, get_activity_service

router = APIRouter(
    prefix="/organizations",
    tags=["organizations"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/", response_model=List[Organization])
async def get_organizations(
    skip: int = 0,
    limit: int = 100,
    service: OrganizationService = Depends(get_organization_service)
):
    organizations = await service.get_all_organizations()
    return organizations[skip:skip + limit]

@router.get("/{organization_id}", response_model=Organization)
async def get_organization(
    organization_id: int, 
    service: OrganizationService = Depends(get_organization_service)
):
    organization = await service.get_organization_by_id(organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    return organization

@router.post("/", response_model=Organization)
async def create_organization(
    organization_data: OrganizationCreate,
    service: OrganizationService = Depends(get_organization_service)
):
    return await service.create_organization(organization_data)

@router.get("/search/name", response_model=List[Organization])
async def search_organizations_by_name(
    name: str = Query(..., description="Organization name to search"),
    service: OrganizationService = Depends(get_organization_service)
):
    return await service.search_organizations_by_name(name)

@router.get("/building/{building_id}", response_model=List[Organization])
async def get_organizations_by_building(
    building_id: int, 
    organization_service: OrganizationService = Depends(get_organization_service),
    building_service: BuildingService = Depends(get_building_service)
):
    building = await building_service.get_building_by_id(building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    return await organization_service.get_organizations_by_building(building_id)

@router.get("/activity/{activity_id}", response_model=List[Organization])
async def get_organizations_by_activity(
    activity_id: int,
    organization_service: OrganizationService = Depends(get_organization_service),
    activity_service: ActivityService = Depends(get_activity_service)
):
    activity = await activity_service.get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )
    return await organization_service.get_organizations_by_activity(activity_id)