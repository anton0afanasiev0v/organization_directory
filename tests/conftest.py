import os
import sys

import pytest

# Добавляем путь к src для импорта модулей
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Фикстуры для тестов


@pytest.fixture
def sample_activity_data():
    """Фикстура с тестовыми данными активности"""
    return {"id": 1, "name": "Test Activity", "description": "Test Description"}


@pytest.fixture
def sample_activity_tree_data():
    """Фикстура с тестовыми данными дерева активностей"""
    return {
        "id": 1,
        "name": "Root Activity",
        "children": [{"id": 2, "name": "Child Activity", "children": []}],
    }
