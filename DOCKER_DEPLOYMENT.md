# Развертывание приложения с помощью Docker

## Требования

- Docker
- Docker Compose

## Быстрый старт

1. **Клонируйте репозиторий:**
   ```bash
   git clone <repository-url>
   cd organization_directory
   ```

2. **Запустите приложение:**
   ```bash
   docker-compose up --build
   ```

3. **Проверьте работу приложения:**
   - API: http://localhost
   - Swagger документация: http://localhost/docs
   - Health check: http://localhost/health
   - PostgreSQL: localhost:5432
   - pgAdmin: http://localhost:28080

## Подробная инструкция

### 1. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/organization_db
SECRET_KEY=your-secret-key-here
PROJECT_NAME=Organization Directory
PROJECT_VERSION=1.0.0
PORT=8000
```

### 2. Запуск в фоновом режиме

```bash
docker-compose up -d --build
```

### 3. Остановка приложения

```bash
docker-compose down
```

### 4. Просмотр логов

```bash
# Логи всех сервисов
docker-compose logs

# Логи конкретного сервиса
docker-compose logs web
docker-compose logs postgres
```

### 5. Доступ к базе данных

**Через pgAdmin:**
- URL: http://localhost:28080
- Email: pgadmin@email.com
- Пароль: 9tkgWIxz3nknyoIlBQYL

**Через командную строку:**
```bash
docker-compose exec postgres psql -U user -d organization_db
```

### 6. Создание тестовых данных

После запуска приложения вы можете создать тестовые данные через API:

```bash
curl -X POST "http://localhost/organizations/fixtures/create" \
  -H "X-API-Key: your-api-key"
```

### 7. Проверка статуса тестовых данных

```bash
curl -X GET "http://localhost/organizations/fixtures/status" \
  -H "X-API-Key: your-api-key"
```

## Структура контейнеров

- **web**: FastAPI приложение (порт 8000, пробрасывается на 80)
- **postgres**: PostgreSQL база данных (порт 5432)
- **pgadmin**: Веб-интерфейс для управления PostgreSQL (порт 28080)

## Проблемы и решения

### Проблема: Порт уже занят
```bash
# Измените порт в docker-compose.yml
ports:
  - "8080:8000"  # Вместо "80:8000"
```

### Проблема: Права доступа к директории data
```bash
sudo chown -R $USER:$USER data/
```

### Проблема: База данных не запускается
```bash
# Очистите тома данных
docker-compose down -v
docker-compose up --build
```

## Разработка

### Запуск в режиме разработки
```bash
docker-compose up --build --force-recreate
```

### Пересборка после изменений
```bash
docker-compose up --build --no-cache
```

## Резервное копирование

### Создание бэкапа базы данных
```bash
docker-compose exec postgres pg_dump -U user organization_db > backup.sql
```

### Восстановление из бэкапа
```bash
docker-compose exec -T postgres psql -U user organization_db < backup.sql
```

## Мониторинг

### Проверка состояния контейнеров
```bash
docker-compose ps
```

### Использование ресурсов
```bash
docker stats
```