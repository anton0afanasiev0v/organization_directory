# organization_directory

# Тестовое задание "Создание REST API приложения"

## Описание проекта

REST API приложение для справочника Организаций, Зданий и Деятельности с использованием FastAPI, SQLAlchemy, Alembic и Pydantic.

## Структура проекта

```
organization_directory/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── api/
│       ├── __init__.py
│       ├── organizations.py
│       ├── buildings.py
│       └── activities.py
├── migrations/
├── tests/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Модели базы данных

### 1. Activity (Деятельность)
```python
class Activity(Base):
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    level = Column(Integer, nullable=False)  # Уровень вложенности (1-3)
    
    # Связи
    parent = relationship("Activity", remote_side=[id], back_populates="children")
    children = relationship("Activity", back_populates="parent")
    organizations = relationship("OrganizationActivity", back_populates="activity")
```

### 2. Building (Здание)
```python
class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)  # Широта
    longitude = Column(Float, nullable=False)  # Долгота
    
    # Связи
    organizations = relationship("Organization", back_populates="building")
```

### 3. Organization (Организация)
```python
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    
    # Связи
    building = relationship("Building", back_populates="organizations")
    phone_numbers = relationship("PhoneNumber", back_populates="organization")
    activities = relationship("OrganizationActivity", back_populates="organization")
```

### 4. PhoneNumber (Телефонные номера)
```python
class PhoneNumber(Base):
    __tablename__ = "phone_numbers"
    
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Связи
    organization = relationship("Organization", back_populates="phone_numbers")
```

### 5. OrganizationActivity (Связь многие-ко-многим)
```python
class OrganizationActivity(Base):
    __tablename__ = "organization_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    # Связи
    organization = relationship("Organization", back_populates="activities")
    activity = relationship("Activity", back_populates="organizations")
```

## API Endpoints

### Организации

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/organizations/` | Список всех организаций |
| GET | `/api/organizations/{id}` | Информация об организации по ID |
| GET | `/api/organizations/building/{building_id}` | Организации в конкретном здании |
| GET | `/api/organizations/activity/{activity_id}` | Организации по виду деятельности |
| GET | `/api/organizations/search/` | Поиск организаций по названию |
| GET | `/api/organizations/activity-tree/{activity_id}` | Организации по дереву деятельности |
| GET | `/api/organizations/nearby/` | Организации в радиусе/области |

### Здания

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/buildings/` | Список всех зданий |
| GET | `/api/buildings/{id}` | Информация о здании по ID |

### Деятельности

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/activities/` | Список всех видов деятельности |
| GET | `/api/activities/{id}` | Информация о виде деятельности по ID |
| GET | `/api/activities/tree/` | Дерево видов деятельности |

## Установка и запуск

### Локальная установка

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd organization_directory
```

2. Создать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Настроить переменные окружения:
```bash
cp .env.example .env
# Отредактировать .env файл
```

5. Запустить миграции:
```bash
alembic upgrade head
```

6. Запустить приложение:
```bash
uvicorn app.main:app --reload
```

### Запуск через Docker

1. Клонировать репозиторий:
```bash
git clone <repository-url>
cd organization_directory
```

2. Запустить контейнеры:
```bash
docker-compose up -d
```

3. Приложение будет доступно по адресу: `http://localhost:8000`

## Документация API

После запуска приложения документация доступна по адресам:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Аутентификация

Все запросы к API требуют статический API ключ в заголовке:
```
X-API-Key: your-static-api-key
```

## Примеры запросов

### Получить организации в здании
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/organizations/building/1"
```

### Поиск организаций по деятельности
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/organizations/activity-tree/1"
```

### Организации в радиусе
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/organizations/nearby?lat=55.7558&lon=37.6173&radius=1000"
```

### Поиск по названию
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8000/api/organizations/search?name=Рога"
```

## Тестовые данные

База данных автоматически заполняется тестовыми данными при первом запуске, включая:
- 10 видов деятельности с древовидной структурой
- 5 зданий с координатами
- 15 организаций с телефонами и связями с деятельностями

## Особенности реализации

- Ограничение уровня вложенности деятельностей до 3 уровней
- Геопоиск организаций по радиусу и прямоугольной области
- Рекурсивный поиск по дереву деятельностей
- Валидация данных через Pydantic
- Автоматическая документация API
- Готовность к развертыванию в Docker