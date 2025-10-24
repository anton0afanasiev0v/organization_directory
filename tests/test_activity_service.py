from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.dto import Activity, ActivityCreate, ActivityTree
from src.service import ActivityService


class TestActivityService:
    """Тесты для ActivityService"""

    @pytest.fixture
    def mock_session(self):
        """Фикстура для мок-сессии базы данных"""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def activity_service(self, mock_session):
        """Фикстура для сервиса с мок-сессией"""
        return ActivityService(mock_session)

    @pytest.fixture
    def sample_activity(self):
        """Фикстура для примера активности"""
        return Activity(
            id=1,
            name="Test Activity",
            description="Test Description",
            # ... другие поля Activity
        )

    @pytest.fixture
    def sample_activity_tree(self):
        """Фикстура для примера дерева активностей"""
        return ActivityTree(
            id=1,
            name="Root Activity",
            children=[ActivityTree(id=2, name="Child Activity", children=[])],
        )

    @pytest.mark.asyncio
    async def test_get_all_activities_success(self, activity_service, mock_session):
        """Тест успешного получения всех активностей"""
        # Arrange
        expected_activities = [
            Activity(id=1, name="Activity 1"),
            Activity(id=2, name="Activity 2"),
        ]

        # Мокируем вызов к базе данных
        activity_service._get_activities_query = AsyncMock(
            return_value=expected_activities
        )

        # Act
        result = await activity_service.get_all_activities()

        # Assert
        assert result == expected_activities
        activity_service._get_activities_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_activities_empty(self, activity_service):
        """Тест получения пустого списка активностей"""
        # Arrange
        activity_service._get_activities_query = AsyncMock(return_value=[])

        # Act
        result = await activity_service.get_all_activities()

        # Assert
        assert result == []
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_activity_by_id_found(self, activity_service, sample_activity):
        """Тест успешного поиска активности по ID"""
        # Arrange
        activity_id = 1
        activity_service._get_activity_by_id_query = AsyncMock(
            return_value=sample_activity
        )

        # Act
        result = await activity_service.get_activity_by_id(activity_id)

        # Assert
        assert result == sample_activity
        activity_service._get_activity_by_id_query.assert_called_once_with(activity_id)

    @pytest.mark.asyncio
    async def test_get_activity_by_id_not_found(self, activity_service):
        """Тест поиска несуществующей активности"""
        # Arrange
        activity_id = 999
        activity_service._get_activity_by_id_query = AsyncMock(return_value=None)

        # Act
        result = await activity_service.get_activity_by_id(activity_id)

        # Assert
        assert result is None
        activity_service._get_activity_by_id_query.assert_called_once_with(activity_id)

    @pytest.mark.asyncio
    async def test_get_activity_tree_success(
        self, activity_service, sample_activity_tree
    ):
        """Тест успешного получения дерева активностей"""
        # Arrange
        max_level = 3
        activity_service._build_activity_tree = AsyncMock(
            return_value=[sample_activity_tree]
        )

        # Act
        result = await activity_service.get_activity_tree(max_level)

        # Assert
        assert result == [sample_activity_tree]
        activity_service._build_activity_tree.assert_called_once_with(max_level)

    @pytest.mark.asyncio
    async def test_get_activity_tree_empty(self, activity_service):
        """Тест получения пустого дерева активностей"""
        # Arrange
        max_level = 2
        activity_service._build_activity_tree = AsyncMock(return_value=[])

        # Act
        result = await activity_service.get_activity_tree(max_level)

        # Assert
        assert result == []
        activity_service._build_activity_tree.assert_called_once_with(max_level)

    @pytest.mark.asyncio
    async def test_get_activity_tree_max_level_validation(self, activity_service):
        """Тест валидации максимального уровня глубины"""
        # Arrange
        max_level = 0  # Некорректное значение
        activity_service._build_activity_tree = AsyncMock(return_value=[])

        # Act & Assert
        with pytest.raises(ValueError):
            await activity_service.get_activity_tree(max_level)

    @pytest.mark.asyncio
    async def test_create_activity_success(self, activity_service, mock_session):
        """Тест успешного создания активности"""
        # Arrange
        activity_data = ActivityCreate(
            name="New Activity", description="New Description"
        )

        created_activity = Activity(
            id=1, name="New Activity", description="New Description"
        )
        activity_service._create_activity_query = AsyncMock(
            return_value=created_activity
        )

        # Act
        result = await activity_service.create_activity(activity_data)

        # Assert
        assert result == created_activity
        activity_service._create_activity_query.assert_called_once_with(activity_data)


class TestActivityServiceIntegration:
    """Интеграционные тесты для ActivityService"""

    @pytest.mark.asyncio
    async def test_service_dependencies_injection(self):
        """Тест корректности инъекции зависимостей"""
        # Arrange
        mock_session = AsyncMock(spec=AsyncSession)

        # Act
        service = ActivityService(mock_session)

        # Assert
        assert service.session is mock_session
        assert hasattr(service, "get_all_activities")
        assert hasattr(service, "get_activity_by_id")
        assert hasattr(service, "get_activity_tree")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
