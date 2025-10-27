import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..database import with_transaction
from ..dto import ActivityCreate, BuildingCreate, OrganizationCreate
from ..service import ActivityService, BuildingService, OrganizationService

logger = logging.getLogger(__name__)

class FixtureService:
    def __init__(self, db: AsyncSession):
        self.activity_service = ActivityService(db)
        self.building_service = BuildingService(db)
        self.organization_service = OrganizationService(db)

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

    @with_transaction
    async def create_test_data(self) -> dict:
        """Создать тестовые данные (бизнес-логика)"""
        logger.info("Начало создания тестовых данных")
        
        # Проверяем, существуют ли уже тестовые данные
        if await self.has_test_data():
            logger.info("Тестовые данные уже существуют")
            return {"status": "exists", "message": "Тестовые данные уже существуют"}

        try:
            # Создаем здания с географическими координатами
            buildings_data = [
                BuildingCreate(
                    name="Главный офис", 
                    address="ул. Центральная, 1",
                    latitude=55.7558,
                    longitude=37.6173
                ),
                BuildingCreate(
                    name="Филиал №1", 
                    address="пр. Победы, 42",
                    latitude=55.7520,
                    longitude=37.6250
                ),
                BuildingCreate(
                    name="Склад", 
                    address="промзона Северная, 5",
                    latitude=55.7480,
                    longitude=37.6080
                ),
                BuildingCreate(
                    name="Торговый центр", 
                    address="ул. Тверская, 15",
                    latitude=55.7600,
                    longitude=37.6100
                ),
                BuildingCreate(
                    name="Бизнес-центр", 
                    address="ул. Садовая, 8",
                    latitude=55.7500,
                    longitude=37.6200
                )
            ]
            
            buildings = []
            for building_data in buildings_data:
                building = await self.building_service.create_building(building_data)
                buildings.append(building)
                logger.info(f"Создано здание: {building.name}")
            
            # Создаем иерархическую структуру деятельностей (3 уровня)
            activities_data = [
                # Корневые категории (уровень 1)
                ActivityCreate(name="Еда", description="Продукты питания и напитки"),
                ActivityCreate(name="Автомобили", description="Автомобильная промышленность"),
                ActivityCreate(name="Розничная торговля", description="Продажа товаров в магазинах"),
                ActivityCreate(name="Общественное питание", description="Кафе, рестораны, бары"),
                ActivityCreate(name="Строительство", description="Строительные работы"),
            ]
            
            # Сначала создаем корневые категории
            root_activities = []
            for activity_data in activities_data:
                activity = await self.activity_service.create_activity(activity_data)
                root_activities.append(activity)
                logger.info(f"Создана корневая деятельность: {activity.name}")
            
            # Создаем дочерние категории (уровень 2)
            # Для категории "Еда"
            meat_activity = await self.activity_service.create_activity(
                ActivityCreate(name="Мясная продукция", description="Мясо и мясные изделия", parent_id=root_activities[0].id)
            )
            dairy_activity = await self.activity_service.create_activity(
                ActivityCreate(name="Молочная продукция", description="Молочные продукты", parent_id=root_activities[0].id)
            )
            
            # Для категории "Автомобили"
            truck_activity = await self.activity_service.create_activity(
                ActivityCreate(name="Грузовые", description="Грузовые автомобили", parent_id=root_activities[1].id)
            )
            car_activity = await self.activity_service.create_activity(
                ActivityCreate(name="Легковые", description="Легковые автомобили", parent_id=root_activities[1].id)
            )
            
            # Создаем подкатегории (уровень 3)
            # Для "Легковые"
            parts_activity = await self.activity_service.create_activity(
                ActivityCreate(name="Запчасти", description="Автомобильные запчасти", parent_id=car_activity.id)
            )
            accessories_activity = await self.activity_service.create_activity(
                ActivityCreate(name="Аксессуары", description="Автомобильные аксессуары", parent_id=car_activity.id)
            )
            
            # Собираем все активности
            all_activities = root_activities + [meat_activity, dairy_activity, truck_activity, car_activity, parts_activity, accessories_activity]
            
            # Создаем организации с различными комбинациями деятельностей
            organizations_data = [
                OrganizationCreate(
                    name="Магазин Уют",
                    building_id=buildings[0].id,
                    activity_ids=[root_activities[2].id],
                    phones=["+7 (999) 123-45-67", "+7 (999) 123-45-68"]
                ),
                OrganizationCreate(
                    name="Кафе Солнце",
                    building_id=buildings[1].id,
                    activity_ids=[root_activities[3].id],  
                    phones=["+7 (888) 765-43-21"]
                ),
                OrganizationCreate(
                    name="СтройГрупп",
                    building_id=buildings[2].id,
                    activity_ids=[root_activities[4].id],
                    phones=["+7 (777) 111-22-33", "+7 (777) 111-22-34"]
                ),
                OrganizationCreate(
                    name="Мясной двор",
                    building_id=buildings[3].id,
                    activity_ids=[meat_activity.id], 
                    phones=["+7 (555) 222-33-44"]
                ),
                OrganizationCreate(
                    name="Молочная ферма",
                    building_id=buildings[4].id,
                    activity_ids=[dairy_activity.id], 
                    phones=["+7 (444) 333-22-11"]
                ),
                OrganizationCreate(
                    name="ГрузАвто",
                    building_id=buildings[0].id,
                    activity_ids=[truck_activity.id],  
                    phones=["+7 (333) 444-55-66"]
                ),
                OrganizationCreate(
                    name="ЛегкоДрайв",
                    building_id=buildings[1].id,
                    activity_ids=[car_activity.id],  
                    phones=["+7 (222) 555-66-77"]
                ),
                OrganizationCreate(
                    name="АвтоЗапчасти",
                    building_id=buildings[2].id,
                    activity_ids=[parts_activity.id], 
                    phones=["+7 (111) 666-77-88", "+7 (111) 666-77-89"]
                ),
                OrganizationCreate(
                    name="АвтоСтиль",
                    building_id=buildings[3].id,
                    activity_ids=[accessories_activity.id],  
                    phones=["+7 (900) 777-88-99"]
                ),
                OrganizationCreate(
                    name="Супермаркет Еда",
                    building_id=buildings[4].id,
                    activity_ids=[root_activities[0].id, root_activities[2].id],
                    phones=["+7 (800) 999-00-11"]
                )
            ]
            
            organizations = []
            for org_data in organizations_data:
                organization = await self.organization_service.create_organization(org_data)
                organizations.append(organization)
                logger.info(f"Создана организация: {organization.name}")

            logger.info("Тестовые данные успешно созданы!")
            return {
                "status": "created",
                "message": "Тестовые данные успешно созданы",
                "buildings": len(buildings),
                "activities": len(all_activities),
                "organizations": len(organizations)
            }

        except Exception as e:
            logger.error(f"Ошибка при создании тестовых данных: {str(e)}")
            raise

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
