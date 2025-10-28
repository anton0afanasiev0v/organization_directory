from fastapi import APIRouter, Depends, HTTPException, status

from ...security import verify_api_key
from ...service import FixtureService
from ..dependencies import get_fixture_service

router = APIRouter(
    prefix="/organizations/fixtures",
    tags=["fixtures"],
    dependencies=[Depends(verify_api_key)],
)


@router.post("/create")
async def create_test_data(
    service: FixtureService = Depends(get_fixture_service),
):
    """Создать тестовые данные"""
    try:
        result = await service.create_test_data()
        return {"message": "Тестовые данные успешно созданы", "data": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании тестовых данных: {str(e)}",
        )


@router.get("/status")
async def get_test_data_status(
    service: FixtureService = Depends(get_fixture_service),
):
    """Получить статус тестовых данных"""
    return await service.get_test_data_status()
