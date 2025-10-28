import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..dto.activity import ActivityCreate
from ..dto.building import BuildingCreate
from ..dto.organization import OrganizationCreate, PhoneCreate
from ..service import ActivityService, BuildingService, OrganizationService

logger = logging.getLogger(__name__)


class FixtureService:
    def __init__(self, db: AsyncSession):
        self.activity_service = ActivityService(db)
        self.building_service = BuildingService(db)
        self.organization_service = OrganizationService(db)

    async def create_test_data(self) -> dict:
        """Создать тестовые данные"""
        try:
            # 1. Создаем виды деятельности
            activities = await self._create_activities()

            # 2. Создаем здания
            buildings = await self._create_buildings()

            # 3. Создаем организации
            organizations = await self._create_organizations(activities, buildings)

            return {
                "activities_created": len(activities),
                "buildings_created": len(buildings),
                "organizations_created": len(organizations),
                "total": len(activities) + len(buildings) + len(organizations)
            }
        except Exception as e:
            logger.error(f"Ошибка при создании тестовых данных: {str(e)}")
            raise

    async def has_test_data(self) -> bool:
        """Проверить, существуют ли тестовые данные"""
        try:
            activities = await self.activity_service.get_all_activities()
            buildings = await self.building_service.get_all_buildings()
            organizations = await self.organization_service.get_all_organizations()

            logger.info(f"Проверка тестовых данных: {len(activities)} активностей, {len(buildings)} зданий, {len(organizations)} организаций")

            return len(activities) > 0 and len(buildings) > 0 and len(organizations) > 0
        except Exception as e:
            logger.error(f"Ошибка при проверке тестовых данных: {str(e)}")
            return False

    async def get_test_data_status(self) -> dict:
        """Получить статус тестовых данных"""
        try:
            activities = await self.activity_service.get_all_activities()
            buildings = await self.building_service.get_all_buildings()
            organizations = await self.organization_service.get_all_organizations()

            return {
                "has_data": len(activities) > 0 and len(buildings) > 0 and len(organizations) > 0,
                "activity_count": len(activities),
                "building_count": len(buildings),
                "organization_count": len(organizations)
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статуса тестовых данных: {str(e)}")
            return {"has_data": False, "error": str(e)}

    async def _create_activities(self) -> list[ActivityCreate]:
        """Создать тестовые виды деятельности"""
        activities_data = [
            # Еда
            {"name": "Еда", "parent_id": None},
            {"name": "Мясная продукция", "parent_id": 1},
            {"name": "Молочная продукция", "parent_id": 1},
            {"name": "Рыба", "parent_id": 1},
            {"name": "Овощи и фрукты", "parent_id": 1},

            # Автомобили
            {"name": "Автомобили", "parent_id": None},
            {"name": "Грузовые", "parent_id": 6},
            {"name": "Легковые", "parent_id": 6},
            {"name": "Запчасти", "parent_id": 8},
            {"name": "Аксессуары", "parent_id": 8},

            # Услуги
            {"name": "Услуги", "parent_id": None},
            {"name": "Ремонт", "parent_id": 11},
            {"name": "Консультации", "parent_id": 11},
            {"name": "Образование", "parent_id": 11},
        ]

        created_activities = []
        for activity_data in activities_data:
            try:
                activity = await self.activity_service.create_activity(ActivityCreate(**activity_data))
                created_activities.append(activity)
            except Exception as e:
                logger.warning(f"Не удалось создать деятельность {activity_data['name']}: {str(e)}")

        return created_activities

    async def _create_buildings(self) -> list[BuildingCreate]:
        """Создать тестовые здания"""
        buildings_data = [
            {
                "address": "г. Москва, ул. Ленина, 1",
                "latitude": 55.7558,
                "longitude": 37.6176
            },
            {
                "address": "г. Москва, ул. Тверская, 10",
                "latitude": 55.7592,
                "longitude": 37.6215
            },
            {
                "address": "г. Санкт-Петербург, Невский проспект, 25",
                "latitude": 59.9343,
                "longitude": 30.3351
            },
            {
                "address": "г. Новосибирск, ул. Красный проспект, 100",
                "latitude": 55.0302,
                "longitude": 82.9204
            },
            {
                "address": "г. Екатеринбург, ул. Малышeva, 51",
                "latitude": 56.8389,
                "longitude": 60.6057
            }
        ]

        created_buildings = []
        for building_data in buildings_data:
            try:
                building = await self.building_service.create_building(BuildingCreate(**building_data))
                created_buildings.append(building)
            except Exception as e:
                logger.warning(f"Не удалось создать здание {building_data['address']}: {str(e)}")

        return created_buildings

    async def _create_organizations(self, activities: list[ActivityCreate], buildings: list[BuildingCreate]) -> list[OrganizationCreate]:
        """Создать тестовые организации"""
        organizations_data = [
            {
                "name": "ООО 'Мясной двор'",
                "building_id": buildings[0].id if buildings else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="2-222-222"),
                    PhoneCreate(phone_number="8-923-666-13-13")
                ],
                "activity_ids": [2]  # Мясная продукция
            },
            {
                "name": "ИП Петров 'Молочная ферма'",
                "building_id": buildings[1].id if len(buildings) > 1 else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="3-333-333"),
                    PhoneCreate(phone_number="8-923-777-14-14")
                ],
                "activity_ids": [3]  # Молочная продукция
            },
            {
                "name": "АО 'Авто-Груз'",
                "building_id": buildings[2].id if len(buildings) > 2 else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="4-444-444"),
                    PhoneCreate(phone_number="8-923-888-15-15")
                ],
                "activity_ids": [7]  # Грузовые
            },
            {
                "name": "ООО 'Легковые авто'",
                "building_id": buildings[3].id if len(buildings) > 3 else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="5-555-555"),
                    PhoneCreate(phone_number="8-923-999-16-16")
                ],
                "activity_ids": [8]  # Легковые
            },
            {
                "name": "Магазин 'Автозапчасти'",
                "building_id": buildings[4].id if len(buildings) > 4 else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="6-666-666"),
                    PhoneCreate(phone_number="8-923-000-17-17")
                ],
                "activity_ids": [9]  # Запчасти
            },
            {
                "name": "Сервисный центр 'Ремонт-Мастер'",
                "building_id": buildings[0].id if buildings else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="7-777-777"),
                    PhoneCreate(phone_number="8-923-111-18-18")
                ],
                "activity_ids": [12]  # Ремонт
            },
            {
                "name": "Консалтинговое агентство 'Эксперт'",
                "building_id": buildings[1].id if len(buildings) > 1 else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="8-888-888"),
                    PhoneCreate(phone_number="8-923-222-19-19")
                ],
                "activity_ids": [13]  # Консультации
            },
            {
                "name": "Образовательный центр 'Знание'",
                "building_id": buildings[2].id if len(buildings) > 2 else 1,
                "phone_numbers": [
                    PhoneCreate(phone_number="9-999-999"),
                    PhoneCreate(phone_number="8-923-333-20-20")
                ],
                "activity_ids": [14]  # Образование
            }
        ]

        created_organizations = []
        for org_data in organizations_data:
            try:
                organization = await self.organization_service.create_organization(OrganizationCreate(**org_data))
                created_organizations.append(organization)
            except Exception as e:
                logger.warning(f"Не удалось создать организацию {org_data['name']}: {str(e)}")

        return created_organizations
