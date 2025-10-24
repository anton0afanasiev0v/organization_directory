import logging
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.declarative import declarative_base

from .config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

# Асинхронный движок БД
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db() -> AsyncSession:
    """Dependency для получения сессии БД с автоматическим управлением транзакциями"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back due to error: {str(e)}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def transaction():
    """Контекстный менеджер для явного управления транзакциями"""
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("Starting transaction")
            yield session
            await session.commit()
            logger.debug("Transaction committed successfully")
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction rolled back due to error: {str(e)}")
            raise
        finally:
            await session.close()


def with_transaction(func):
    """Декоратор для автоматического управления транзакциями"""

    async def wrapper(*args, **kwargs):
        async with transaction() as session:
            # Если функция ожидает сессию как параметр
            if "db" in kwargs:
                kwargs["db"] = session
            return await func(*args, **kwargs)

    return wrapper


async def check_db_connection():
    """Проверка подключения к БД"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return False
