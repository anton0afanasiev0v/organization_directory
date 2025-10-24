from fastapi import APIRouter, Depends, HTTPException, status

from ...dto import Building, CoordinateRange, RadiusSearch
from ...security import verify_api_key
from ...service import BuildingService
from ..dependencies import get_building_service

router = APIRouter(
    prefix="/buildings", tags=["buildings"], dependencies=[Depends(verify_api_key)]
)


@router.get("/", response_model=list[Building])
async def get_buildings(
    skip: int = 0,
    limit: int = 100,
    service: BuildingService = Depends(get_building_service),
):
    buildings = await service.get_all_buildings()
    return buildings[skip : skip + limit]


@router.get("/{building_id}", response_model=Building)
async def get_building(
    building_id: int, service: BuildingService = Depends(get_building_service)
):
    building = await service.get_building_by_id(building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Building not found"
        )
    return building


@router.post("/search/range", response_model=list[Building])
async def search_buildings_in_range(
    coord_range: CoordinateRange,
    service: BuildingService = Depends(get_building_service),
):
    return await service.get_buildings_in_range(coord_range)


@router.post("/search/radius", response_model=list[Building])
async def search_buildings_in_radius(
    search: RadiusSearch, service: BuildingService = Depends(get_building_service)
):
    return await service.get_buildings_in_radius(search)
