import logging
from abc import ABC
from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый репозиторий с CRUD операциями"""

    def __init__(self, db: AsyncSession, model: type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, id: int) -> ModelType | None:
        """Получить объект по ID"""
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} {id}: {str(e)}")
            raise

    async def get_multi(
        self, skip: int = 0, limit: int = 100, **filters
    ) -> list[ModelType]:
        """Получить список объектов с фильтрацией"""
        try:
            query = select(self.model)

            # Применяем фильтры
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)

            query = query.offset(skip).limit(limit)
            result = await self.db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} list: {str(e)}")
            raise

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Создать новый объект"""
        try:
            obj_data = obj_in.model_dump()
            db_obj = self.model(**obj_data)
            self.db.add(db_obj)
            await self.db.flush()
            await self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise

    async def update(self, id: int, obj_in: UpdateSchemaType) -> ModelType | None:
        """Обновить объект"""
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return None

            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_obj, field, value)

            await self.db.flush()
            await self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {str(e)}")
            raise

    async def delete(self, id: int) -> bool:
        """Удалить объект"""
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return False

            await self.db.delete(db_obj)
            await self.db.flush()
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} {id}: {str(e)}")
            raise
