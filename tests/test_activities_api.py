from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.api.v1.activities import router
from src.dto import Activity, ActivityTree


class TestActivitiesAPI:
    """Тесты для API endpoints активностей"""

    @pytest.fixture
    def client(self):
        """Фикстура для тестового клиента"""
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        return TestClient(app)

    @pytest.fixture
    def sample_activity(self):
        """Фикстура для примера активности"""
        return Activity(id=1, name="Test Activity", description="Test Description")

    @pytest.fixture
    def sample_activity_tree(self):
        """Фикстура для примера дерева активностей"""
        return ActivityTree(
            id=1,
            name="Root Activity",
            children=[ActivityTree(id=2, name="Child Activity", children=[])],
        )

    @pytest.fixture
    def mock_api_key(self):
        """Фикстура для мок-API ключа"""
        return "test-api-key"

    def test_get_activities_success(self, client, sample_activity, mock_api_key):
        """Тест успешного получения списка активностей"""
        # Arrange
        with patch("src.api.v1.activities.get_activity_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_all_activities = AsyncMock(
                return_value=[sample_activity]
            )
            mock_service.return_value = mock_service_instance

            # Act
            response = client.get("/activities/", headers={"X-API-Key": mock_api_key})

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == sample_activity.id
            assert data[0]["name"] == sample_activity.name

    def test_get_activities_unauthorized(self, client):
        """Тест доступа без API ключа"""
        # Act
        response = client.get("/activities/")

        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_activity_tree_success(
        self, client, sample_activity_tree, mock_api_key
    ):
        """Тест успешного получения дерева активностей"""
        # Arrange
        with patch("src.api.v1.activities.get_activity_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_activity_tree = AsyncMock(
                return_value=[sample_activity_tree]
            )
            mock_service.return_value = mock_service_instance

            # Act
            response = client.get(
                "/activities/tree?max_level=3", headers={"X-API-Key": mock_api_key}
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data) == 1
            assert data[0]["id"] == sample_activity_tree.id
            assert data[0]["name"] == sample_activity_tree.name
            assert "children" in data[0]

    def test_get_activity_by_id_success(self, client, sample_activity, mock_api_key):
        """Тест успешного получения активности по ID"""
        # Arrange
        activity_id = 1
        with patch("src.api.v1.activities.get_activity_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_activity_by_id = AsyncMock(
                return_value=sample_activity
            )
            mock_service.return_value = mock_service_instance

            # Act
            response = client.get(
                f"/activities/{activity_id}", headers={"X-API-Key": mock_api_key}
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["id"] == sample_activity.id
            assert data["name"] == sample_activity.name

    def test_get_activity_by_id_not_found(self, client, mock_api_key):
        """Тест получения несуществующей активности"""
        # Arrange
        activity_id = 999
        with patch("src.api.v1.activities.get_activity_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_activity_by_id = AsyncMock(return_value=None)
            mock_service.return_value = mock_service_instance

            # Act
            response = client.get(
                f"/activities/{activity_id}", headers={"X-API-Key": mock_api_key}
            )

            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND
            data = response.json()
            assert data["detail"] == "Activity not found"

    def test_get_activity_tree_with_max_level(self, client, mock_api_key):
        """Тест получения дерева с указанием максимального уровня"""
        # Arrange
        max_level = 2
        with patch("src.api.v1.activities.get_activity_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_activity_tree = AsyncMock(return_value=[])
            mock_service.return_value = mock_service_instance

            # Act
            response = client.get(
                f"/activities/tree?max_level={max_level}",
                headers={"X-API-Key": mock_api_key},
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            mock_service_instance.get_activity_tree.assert_called_once_with(max_level)

    def test_get_activities_empty_list(self, client, mock_api_key):
        """Тест получения пустого списка активностей"""
        # Arrange
        with patch("src.api.v1.activities.get_activity_service") as mock_service:
            mock_service_instance = AsyncMock()
            mock_service_instance.get_all_activities = AsyncMock(return_value=[])
            mock_service.return_value = mock_service_instance

            # Act
            response = client.get("/activities/", headers={"X-API-Key": mock_api_key})

            # Assert
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
