from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional

from ..model.building import Building
from ..dto.building import BuildingCreate
from .base import BaseRepository

class BuildingRepository(BaseRepository[Building, BuildingCreate, BuildingCreate]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Building)

    async def get_with_organizations(self, building_id: int) -> Optional[Building]:
        """Получить здание с организациями"""
        result = await self.db.execute(
            select(Building)
            .where(building_id == Building.id)
            .options(selectinload(Building.organizations))
        )
        return result.scalar_one_or_none()

    async def get_by_address(self, address: str) -> Optional[Building]:
        """Получить здание по адресу"""
        result = await self.db.execute(
            select(Building).where(address == Building.address)
        )
        return result.scalar_one_or_none()

    async def get_in_coordinate_range(
            self,
            min_lat: float,
            max_lat: float,
            min_lng: float,
            max_lng: float
    ) -> List[Building]:
        """Получить здания в прямоугольной области"""
        result = await self.db.execute(
            select(Building)
            .where(
                and_(
                    Building.latitude.between(min_lat, max_lat),
                    Building.longitude.between(min_lng, max_lng)
                )
            )
            .options(selectinload(Building.organizations))
        )
        return result.scalars().all()

    async def get_all_with_organizations(self) -> List[Building]:
        """Получить все здания с организациями"""
        result = await self.db.execute(
            select(Building).options(selectinload(Building.organizations))
        )
        return result.scalars().all()