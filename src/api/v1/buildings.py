from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...database import get_db
from ...security import verify_api_key
from ...service import BuildingService
from ...dto import Building, BuildingCreate, CoordinateRange, RadiusSearch

router = APIRouter(
    prefix="/buildings",
    tags=["buildings"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/", response_model=List[Building])
async def get_buildings(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db)
):
    service = BuildingService(db)
    buildings = await service.get_all_buildings()
    return buildings[skip:skip + limit]

@router.get("/{building_id}", response_model=Building)
async def get_building(building_id: int, db: AsyncSession = Depends(get_db)):
    service = BuildingService(db)
    building = await service.get_building_by_id(building_id)
    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )
    return building

@router.post("/search/range", response_model=List[Building])
async def search_buildings_in_range(
        coord_range: CoordinateRange,
        db: AsyncSession = Depends(get_db)
):
    service = BuildingService(db)
    return await service.get_buildings_in_range(coord_range)

@router.post("/search/radius", response_model=List[Building])
async def search_buildings_in_radius(
        search: RadiusSearch,
        db: AsyncSession = Depends(get_db)
):
    service = BuildingService(db)
    return await service.get_buildings_in_radius(search)