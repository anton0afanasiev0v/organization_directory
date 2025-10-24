import logging

from geopy.distance import geodesic
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import with_transaction
from ..dto.building import BuildingCreate, CoordinateRange, RadiusSearch
from ..repository.building_repository import BuildingRepository

logger = logging.getLogger(__name__)


class BuildingService:
    def __init__(self, db: AsyncSession):
        self.repository = BuildingRepository(db)

    async def get_building(self, building_id: int) -> BuildingCreate | None:
        """Получить здание по ID (бизнес-логика)"""
        building = await self.repository.get_with_organizations(building_id)
        if building:
            return BuildingCreate.model_validate(building)
        return None

    async def get_all_buildings(
        self, skip: int = 0, limit: int = 100
    ) -> list[BuildingCreate]:
        """Получить список зданий (бизнес-логика)"""
        buildings = await self.repository.get_multi(skip=skip, limit=limit)
        return [BuildingCreate.model_validate(building) for building in buildings]

    @with_transaction
    async def create_building(self, building_data: BuildingCreate) -> BuildingCreate:
        """Создать новое здание (бизнес-логика)"""
        # Проверяем бизнес-правила
        existing_building = await self.repository.get_by_address(building_data.address)
        if existing_building:
            raise ValueError("Здание с таким адресом уже существует")

        # Проверяем координаты
        if not (-90 <= building_data.latitude <= 90):
            raise ValueError("Широта должна быть в диапазоне от -90 до 90")
        if not (-180 <= building_data.longitude <= 180):
            raise ValueError("Долгота должна быть в диапазоне от -180 до 180")

        building = await self.repository.create(building_data)
        return BuildingCreate.model_validate(building)

    async def update_building(
        self, building_id: int, building_data: BuildingCreate
    ) -> BuildingCreate | None:
        """Обновить здание (бизнес-логика)"""
        existing_building = await self.repository.get(building_id)
        if not existing_building:
            return None

        # Проверяем уникальность адреса
        if building_data.address != existing_building.address:
            building_with_same_address = await self.repository.get_by_address(
                building_data.address
            )
            if (
                building_with_same_address
                and building_with_same_address.id != building_id
            ):
                raise ValueError("Здание с таким адресом уже существует")

        updated_building = await self.repository.update(building_id, building_data)
        if updated_building:
            return BuildingCreate.model_validate(updated_building)
        return None

    async def delete_building(self, building_id: int) -> bool:
        """Удалить здание (бизнес-логика)"""
        building = await self.repository.get_with_organizations(building_id)
        if not building:
            return False

        # Проверяем бизнес-правило: нельзя удалить здание с организациями
        if building.organizations:
            raise ValueError("Нельзя удалить здание с привязанными организациями")

        return await self.repository.delete(building_id)

    async def search_buildings_in_range(
        self, coord_range: CoordinateRange
    ) -> list[BuildingCreate]:
        """Поиск зданий в прямоугольной области (бизнес-логика)"""
        buildings = await self.repository.get_in_coordinate_range(
            coord_range.min_lat,
            coord_range.max_lat,
            coord_range.min_lng,
            coord_range.max_lng,
        )
        return [BuildingCreate.model_validate(building) for building in buildings]

    async def search_buildings_in_radius(
        self, search: RadiusSearch
    ) -> list[BuildingCreate]:
        """Поиск зданий в радиусе (бизнес-логика)"""
        all_buildings = await self.repository.get_all_with_organizations()

        center_point = (search.latitude, search.longitude)
        buildings_in_radius = []

        for building in all_buildings:
            building_point = (building.latitude, building.longitude)
            distance = geodesic(center_point, building_point).kilometers

            if distance <= search.radius_km:
                buildings_in_radius.append(BuildingCreate.model_validate(building))

        return buildings_in_radius
