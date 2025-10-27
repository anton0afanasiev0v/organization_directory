from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dto.building import BuildingCreate
from ..model.building import Building


class BuildingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Building

    async def create(self, building_data: BuildingCreate) -> Building:
        """Создать новое здание"""
        db_building = Building(**building_data.model_dump())
        self.db.add(db_building)
        await self.db.commit()
        await self.db.refresh(db_building)
        return db_building

    async def get_multi(self, skip: int = 0, limit: int = 100) -> list[Building]:
        """Получить список зданий с пагинацией"""
        result = await self.db.execute(
            select(Building).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get(self, building_id: int) -> Building | None:
        """Получить здание по ID"""
        result = await self.db.execute(
            select(Building).where(building_id == Building.id)
        )
        return result.scalar_one_or_none()

    async def update(self, building_id: int, building_data: BuildingCreate) -> Building | None:
        """Обновить здание"""
        result = await self.db.execute(
            select(Building).where(building_id == Building.id)
        )
        building = result.scalar_one_or_none()
        
        if building:
            for field, value in building_data.model_dump().items():
                setattr(building, field, value)
            await self.db.commit()
            await self.db.refresh(building)
        
        return building

    async def delete(self, building_id: int) -> bool:
        """Удалить здание"""
        result = await self.db.execute(
            select(Building).where(building_id == Building.id)
        )
        building = result.scalar_one_or_none()
        
        if building:
            await self.db.delete(building)
            await self.db.commit()
            return True
        return False

    async def get_with_organizations(self, building_id: int) -> Building | None:
        """Получить здание с организациями"""
        result = await self.db.execute(
            select(Building)
            .where(building_id == Building.id)
            .options(selectinload(Building.organizations))
        )
        return result.scalar_one_or_none()

    async def get_by_address(self, address: str) -> Building | None:
        """Получить здание по адресу"""
        result = await self.db.execute(
            select(Building).where(address == Building.address)
        )
        return result.scalar_one_or_none()

    async def get_in_coordinate_range(
        self, min_lat: float, max_lat: float, min_lng: float, max_lng: float
    ) -> list[Building]:
        """Получить здания в прямоугольной области"""
        result = await self.db.execute(
            select(Building)
            .where(
                and_(
                    Building.latitude.between(min_lat, max_lat),
                    Building.longitude.between(min_lng, max_lng),
                )
            )
            .options(selectinload(Building.organizations))
        )
        return result.scalars().all()

    async def get_all_with_organizations(self) -> list[Building]:
        """Получить все здания с организациями"""
        result = await self.db.execute(
            select(Building).options(selectinload(Building.organizations))
        )
        return result.scalars().all()