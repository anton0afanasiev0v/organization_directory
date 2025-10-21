from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from ..repository.activity_repository import ActivityRepository
from ..dto.activity import ActivityCreate, ActivityTree
from ..database import with_transaction

logger = logging.getLogger(__name__)

class ActivityService:
    def __init__(self, db: AsyncSession):
        self.repository = ActivityRepository(db)

    async def get_activity(self, activity_id: int) -> Optional[ActivityCreate]:
        """Получить деятельность по ID (бизнес-логика)"""
        activity = await self.repository.get_with_relations(activity_id)
        if activity:
            return ActivityCreate.model_validate(activity)
        return None

    async def get_all_activities(self) -> List[ActivityCreate]:
        """Получить все деятельности (бизнес-логика)"""
        activities = await self.repository.get_all()
        return [ActivityCreate.model_validate(activity) for activity in activities]

    @with_transaction
    async def create_activity(self, activity_data: ActivityCreate) -> ActivityCreate:
        """Создать новую деятельность (бизнес-логика)"""
        # Проверяем бизнес-правила
        existing_activity = await self.repository.get_by_name_and_parent(
            activity_data.name,
            activity_data.parent_id
        )
        if existing_activity:
            raise ValueError("Деятельность с таким именем уже существует на этом уровне")

        # Проверяем максимальную вложенность (3 уровня)
        if activity_data.parent_id:
            parent_level = await self._get_activity_level(activity_data.parent_id)
            if parent_level >= 2:
                raise ValueError("Максимальная вложенность - 3 уровня")

        activity = await self.repository.create(activity_data)
        return ActivityCreate.model_validate(activity)

    async def update_activity(self, activity_id: int, activity_data: ActivityCreate) -> Optional[ActivityCreate]:
        """Обновить деятельность (бизнес-логика)"""
        existing_activity = await self.repository.get(activity_id)
        if not existing_activity:
            return None

        # Проверяем уникальность имени
        if activity_data.name != existing_activity.name or activity_data.parent_id != existing_activity.parent_id:
            activity_with_same_name = await self.repository.get_by_name_and_parent(
                activity_data.name,
                activity_data.parent_id
            )
            if activity_with_same_name and activity_with_same_name.id != activity_id:
                raise ValueError("Деятельность с таким именем уже существует на этом уровне")

        # Проверяем циклические зависимости
        if activity_data.parent_id:
            if await self._would_create_cycle(activity_id, activity_data.parent_id):
                raise ValueError("Нельзя создавать циклические зависимости в дереве деятельностей")

        updated_activity = await self.repository.update(activity_id, activity_data)
        if updated_activity:
            return ActivityCreate.model_validate(updated_activity)
        return None

    async def delete_activity(self, activity_id: int) -> bool:
        """Удалить деятельность (бизнес-логика)"""
        activity = await self.repository.get_with_relations(activity_id)
        if not activity:
            return False

        # Проверяем бизнес-правила
        if activity.children:
            raise ValueError("Нельзя удалить деятельность с дочерними элементами")

        if activity.organizations:
            raise ValueError("Нельзя удалить деятельность с привязанными организациями")

        return await self.repository.delete(activity_id)

    async def get_activity_tree(self, max_level: int = 3) -> List[ActivityTree]:
        """Получить дерево деятельностей (бизнес-логика)"""
        async def build_tree(parent_id: Optional[int] = None, level: int = 0) -> List[ActivityTree]:
            if level >= max_level:
                return []

            children = await self.repository.get_children(parent_id)

            tree = []
            for child in children:
                grandchildren = await build_tree(child.id, level + 1)
                tree.append(ActivityTree(
                    id=child.id,
                    name=child.name,
                    parent_id=child.parent_id,
                    level=level,
                    children=grandchildren
                ))

            return tree

        return await build_tree()

    async def get_descendant_activity_ids(self, activity_id: int) -> List[int]:
        """Получить ID всех потомков деятельности (бизнес-логика)"""
        async def get_children_ids(parent_id: int) -> List[int]:
            children = await self.repository.get_children(parent_id)
            all_ids = [parent_id]

            for child in children:
                all_ids.extend(await get_children_ids(child.id))

            return all_ids

        return await get_children_ids(activity_id)

    async def _get_activity_level(self, activity_id: int) -> int:
        """Получить уровень вложенности деятельности (вспомогательный метод)"""
        level = 0
        current_id = activity_id

        while current_id:
            activity = await self.repository.get(current_id)
            if not activity or not activity.parent_id:
                break
            level += 1
            current_id = activity.parent_id

        return level

    async def _would_create_cycle(self, activity_id: int, new_parent_id: int) -> bool:
        """Проверить циклические зависимости (вспомогательный метод)"""
        descendants = await self.get_descendant_activity_ids(activity_id)
        return new_parent_id in descendants