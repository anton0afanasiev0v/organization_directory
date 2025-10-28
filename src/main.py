from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from .api.v1 import activities, buildings, fixtures, organizations
from .config import settings
from .database import Base, engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    print("Starting Organization Directory API...")
    # Используем асинхронное создание таблиц
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    print("Shutting down...")
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="REST API для справочника Организаций, Зданий и Деятельности",
    lifespan=lifespan,
)

# Include routers
app.include_router(organizations.router)
app.include_router(buildings.router)
app.include_router(activities.router)
app.include_router(fixtures.router)


@app.get("/")
async def root():
    return {
        "message": "Organization Directory API",
        "version": settings.PROJECT_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
