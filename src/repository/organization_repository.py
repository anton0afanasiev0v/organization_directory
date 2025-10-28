from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dto.organization import OrganizationCreate, OrganizationUpdate
from ..model import Activity, Organization, OrganizationPhone


class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = Organization

    async def get(self, organization_id: int) -> Organization | None:
        """Получить организацию по ID"""
        result = await self.db.execute(
            select(Organization).where(organization_id == Organization.id)
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, organization_id: int) -> Organization | None:
        """Получить организацию со всеми связями"""
        result = await self.db.execute(
            select(Organization)
            .where(organization_id == Organization.id)
            .options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Organization | None:
        """Получить организацию по имени"""
        result = await self.db.execute(
            select(Organization).where(name == Organization.name)
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Organization]:
        """Получить все организации"""
        result = await self.db.execute(
            select(Organization)
            .offset(skip)
            .limit(limit)
            .options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
        )
        return result.scalars().all()

    async def get_all_with_buildings(self) -> list[Organization]:
        """Получить все организации со зданиями"""
        result = await self.db.execute(
            select(Organization).options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
        )
        return result.scalars().all()

    async def get_by_building(self, building_id: int) -> list[Organization]:
        """Получить организации в здании"""
        result = await self.db.execute(
            select(Organization)
            .where(building_id == Organization.building_id)
            .options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
        )
        return result.scalars().all()

    async def get_by_activities(self, activity_ids: list[int]) -> list[Organization]:
        """Получить организации по видам деятельности"""
        result = await self.db.execute(
            select(Organization)
            .join(Organization.activities)
            .where(Activity.id.in_(activity_ids))
            .options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
            .distinct()
        )
        return result.scalars().all()

    async def get_in_coordinate_range(
        self, min_lat: float, max_lat: float, min_lng: float, max_lng: float
    ) -> list[Organization]:
        """Получить организации в прямоугольной области"""
        from ..model.building import Building

        result = await self.db.execute(
            select(Organization)
            .join(Building)
            .where(
                and_(
                    Building.latitude.between(min_lat, max_lat),
                    Building.longitude.between(min_lng, max_lng),
                )
            )
            .options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
        )
        return result.scalars().all()

    async def search_by_name(self, name: str) -> list[Organization]:
        """Поиск организаций по названию"""
        result = await self.db.execute(
            select(Organization)
            .where(Organization.name.ilike(f"%{name}%"))
            .options(
                selectinload(Organization.phone_numbers),
                selectinload(Organization.activities),
                selectinload(Organization.building),
            )
        )
        return result.scalars().all()

    async def create(self, organization_data: OrganizationCreate) -> Organization:
        """Создать новую организацию"""
        organization = Organization(
            name=organization_data.name, building_id=organization_data.building_id
        )
        self.db.add(organization)
        await self.db.flush()

        # Добавляем телефоны
        for phone_data in organization_data.phone_numbers:
            phone = OrganizationPhone(
                phone_number=phone_data.phone_number, organization_id=organization.id
            )
            self.db.add(phone)

        # Добавляем деятельность
        if organization_data.activity_ids:
            activities_result = await self.db.execute(
                select(Activity).where(Activity.id.in_(organization_data.activity_ids))
            )
            activities = activities_result.scalars().all()
            organization.activities.extend(activities)

        await self.db.flush()
        await self.db.refresh(organization)
        return organization

    async def update(
        self, organization_id: int, update_data: OrganizationUpdate
    ) -> Organization | None:
        """Обновить организацию"""
        organization = await self.get_with_relations(organization_id)
        if not organization:
            return None

        # Обновляем базовые поля
        if update_data.name is not None:
            organization.name = update_data.name
        if update_data.building_id is not None:
            organization.building_id = update_data.building_id

        # Обновляем телефоны
        if update_data.phone_numbers is not None:
            # Удаляем старые телефоны
            await self.db.execute(
                delete(OrganizationPhone).where(
                    organization_id == OrganizationPhone.organization_id
                )
            )
            # Добавляем новые
            for phone_data in update_data.phone_numbers:
                phone = OrganizationPhone(
                    phone_number=phone_data.phone_number,
                    organization_id=organization_id,
                )
                self.db.add(phone)

        # Обновляем деятельность
        if update_data.activity_ids is not None:
            organization.activities.clear()
            activities_result = await self.db.execute(
                select(Activity).where(Activity.id.in_(update_data.activity_ids))
            )
            activities = activities_result.scalars().all()
            organization.activities.extend(activities)

        await self.db.flush()
        await self.db.refresh(organization)
        return organization

    async def delete(self, organization_id: int) -> bool:
        """Удалить организацию"""
        organization = await self.get(organization_id)
        if not organization:
            return False

        await self.db.delete(organization)
        await self.db.flush()
        return True
