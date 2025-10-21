from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from ..repository import OrganizationRepository, BuildingRepository, ActivityRepository
from ..dto.organization import OrganizationCreate, OrganizationUpdate, Organization
from ..service import ActivityService
from ..database import with_transaction

logger = logging.getLogger(__name__)

class OrganizationService:
    def __init__(self, db: AsyncSession):
        self.organization_repo = OrganizationRepository(db)
        self.building_repo = BuildingRepository(db)
        self.activity_repo = ActivityRepository(db)
        self.activity_service = ActivityService(db)

    async def get_organization(self, organization_id: int) -> Optional[Organization]:
        """Получить организацию по ID (бизнес-логика)"""
        organization = await self.organization_repo.get_with_relations(organization_id)
        if organization:
            return Organization.model_validate(organization)
        return None

    async def get_all_organizations(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """Получить все организации (бизнес-логика)"""
        organizations = await self.organization_repo.get_all(skip=skip, limit=limit)
        return [Organization.model_validate(org) for org in organizations]

    @with_transaction
    async def create_organization(self, organization_data: OrganizationCreate) -> Organization:
        """Создать новую организацию (бизнес-логика)"""
        # Проверяем бизнес-правила

        # 1. Проверяем уникальность имени
        existing_organization = await self.organization_repo.get_by_name(organization_data.name)
        if existing_organization:
            raise ValueError("Организация с таким названием уже существует")

        # 2. Проверяем существование здания
        building = await self.building_repo.get(organization_data.building_id)
        if not building:
            raise ValueError("Указанное здание не существует")

        # 3. Проверяем существование деятельностей
        if organization_data.activity_ids:
            for activity_id in organization_data.activity_ids:
                activity = await self.activity_repo.get(activity_id)
                if not activity:
                    raise ValueError(f"Деятельность с ID {activity_id} не существует")

        # 4. Проверяем формат телефонов
        for phone in organization_data.phone_numbers:
            if not self._validate_phone_format(phone.phone_number):
                raise ValueError(f"Неверный формат телефона: {phone.phone_number}")

        organization = await self.organization_repo.create(organization_data)
        return Organization.model_validate(organization)

    async def update_organization(self, organization_id: int, update_data: OrganizationUpdate) -> Optional[Organization]:
        """Обновить организацию (бизнес-логика)"""
        existing_organization = await self.organization_repo.get(organization_id)
        if not existing_organization:
            return None

        # Проверяем бизнес-правила

        # 1. Проверяем уникальность имени
        if update_data.name and update_data.name != existing_organization.name:
            organization_with_same_name = await self.organization_repo.get_by_name(update_data.name)
            if organization_with_same_name and organization_with_same_name.id != organization_id:
                raise ValueError("Организация с таким названием уже существует")

        # 2. Проверяем существование здания
        if update_data.building_id:
            building = await self.building_repo.get(update_data.building_id)
            if not building:
                raise ValueError("Указанное здание не существует")

        # 3. Проверяем существование деятельностей
        if update_data.activity_ids:
            for activity_id in update_data.activity_ids:
                activity = await self.activity_repo.get(activity_id)
                if not activity:
                    raise ValueError(f"Деятельность с ID {activity_id} не существует")

        # 4. Проверяем формат телефонов
        if update_data.phone_numbers:
            for phone in update_data.phone_numbers:
                if not self._validate_phone_format(phone.phone_number):
                    raise ValueError(f"Неверный формат телефона: {phone.phone_number}")

        updated_organization = await self.organization_repo.update(organization_id, update_data)
        if updated_organization:
            return Organization.model_validate(updated_organization)
        return None

    async def delete_organization(self, organization_id: int) -> bool:
        """Удалить организацию (бизнес-логика)"""
        organization = await self.organization_repo.get(organization_id)
        if not organization:
            return False

        # Дополнительные бизнес-правила при удалении могут быть добавлены здесь

        return await self.organization_repo.delete(organization_id)

    async def get_organizations_by_building(self, building_id: int) -> List[Organization]:
        """Получить организации в здании (бизнес-логика)"""
        # Проверяем существование здания
        building = await self.building_repo.get(building_id)
        if not building:
            raise ValueError("Здание не существует")

        organizations = await self.organization_repo.get_by_building(building_id)
        return [Organization.model_validate(org) for org in organizations]

    async def get_organizations_by_activity(self, activity_id: int) -> List[Organization]:
        """Получить организации по виду деятельности (бизнес-логика)"""
        # Проверяем существование деятельности
        activity = await self.activity_repo.get(activity_id)
        if not activity:
            raise ValueError("Деятельность не существует")

        # Получаем всех потомков деятельности
        activity_ids = await self.activity_service.get_descendant_activity_ids(activity_id)

        organizations = await self.organization_repo.get_by_activities(activity_ids)
        return [Organization.model_validate(org) for org in organizations]

    async def search_organizations_by_name(self, name: str) -> List[Organization]:
        """Поиск организаций по названию (бизнес-логика)"""
        if len(name) < 2:
            raise ValueError("Поисковый запрос должен содержать минимум 2 символа")

        organizations = await self.organization_repo.search_by_name(name)
        return [Organization.model_validate(org) for org in organizations]

    def _validate_phone_format(self, phone: str) -> bool:
        """Валидация формата телефона (вспомогательный метод)"""
        # Простая валидация - можно заменить на более сложную логику
        import re
        phone_pattern = re.compile(r'^[\d\s\-\+\(\)]+$')
        return bool(phone_pattern.match(phone)) and len(phone) >= 5