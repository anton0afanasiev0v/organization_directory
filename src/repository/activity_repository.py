from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..dto.activity import ActivityCreate
from ..model.activity import Activity
from .base import BaseRepository


class ActivityRepository(BaseRepository[Activity, ActivityCreate, ActivityCreate]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Activity)

    async def get(self, activity_id: int) -> Activity | None:
        """Получить деятельность по ID"""
        result = await self.db.execute(
            select(Activity).where(activity_id == Activity.id)
        )
        return result.scalar_one_or_none()

    async def get_with_relations(self, activity_id: int) -> Activity | None:
        """Получить деятельность со всеми связями"""
        result = await self.db.execute(
            select(Activity)
            .where(activity_id == Activity.id)
            .options(
                selectinload(Activity.parent),
                selectinload(Activity.children),
                selectinload(Activity.organizations),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_and_parent(
        self, name: str, parent_id: int | None
    ) -> Activity | None:
        """Получить деятельность по имени и родителю"""
        result = await self.db.execute(
            select(Activity).where(
                (name == Activity.name) & (parent_id == Activity.parent_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_children(self, parent_id: int | None) -> list[Activity]:
        """Получить дочерние деятельность"""
        result = await self.db.execute(
            select(Activity).where(parent_id == Activity.parent_id)
        )
        return result.scalars().all()

    async def get_all(self) -> list[Activity]:
        """Получить все деятельность"""
        result = await self.db.execute(select(Activity))
        return result.scalars().all()

    async def create(self, activity_data: ActivityCreate) -> Activity:
        """Создать новую деятельность"""
        activity = Activity(**activity_data.model_dump())
        self.db.add(activity)
        await self.db.flush()
        await self.db.refresh(activity)
        return activity

    async def update(
        self, activity_id: int, activity_data: ActivityCreate
    ) -> Activity | None:
        """Обновить деятельность"""
        activity = await self.get(activity_id)
        if not activity:
            return None

        for field, value in activity_data.model_dump().items():
            setattr(activity, field, value)

        await self.db.flush()
        await self.db.refresh(activity)
        return activity

    async def delete(self, activity_id: int) -> bool:
        """Удалить деятельность"""
        activity = await self.get(activity_id)
        if not activity:
            return False

        await self.db.delete(activity)
        await self.db.flush()
        return True
