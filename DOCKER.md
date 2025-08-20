# Docker Setup

## Быстрый старт

1. Скопируйте файл с переменными окружения:
```bash
cp .env.example .env
```

2. Отредактируйте `.env` файл, добавив необходимые API ключи:
```bash
nano .env
```

3. Запустите проект:
```bash
make build
make up
```

4. Проверьте, что все работает:
- Frontend: http://localhost:3001
- Backend API: http://localhost:8881
- MongoDB: localhost:27018

5. Войдите в систему с demo аккаунтом:
- **Username:** demo
- **Password:** demo123
- **Role:** admin

## Demo аккаунт

После первого запуска автоматически создается demo пользователь:

```
Username: demo
Password: demo123
Email: demo@example.com
Role: admin
```

Demo пользователь имеет полный доступ к системе и может:
- Управлять настройками Sentry
- Создавать и просматривать анализы
- Генерировать тестовые события
- Управлять workspace

## Команды

### Основные команды
```bash
make build    # Собрать все образы
make up       # Запустить все сервисы
make down     # Остановить все сервисы
make restart  # Перезапустить все сервисы
make logs     # Посмотреть логи всех сервисов
make clean    # Удалить все контейнеры, образы и volumes
```

### Логи отдельных сервисов
```bash
make logs-backend   # Логи backend
make logs-frontend  # Логи frontend
make logs-mongodb   # Логи MongoDB
```

### Режим разработки
```bash
make dev-up    # Запуск в режиме разработки (с hot reload)
make dev-down  # Остановка dev режима
```

## Сервисы

### MongoDB
- **Порт**: 27017
- **Пользователь**: admin
- **Пароль**: password123
- **База данных**: sentry_ai_explainer

### Backend (FastAPI)
- **Порт**: 8000
- **Health check**: http://localhost:8000/health
- **API docs**: http://localhost:8000/docs

### Frontend (React)
- **Порт**: 3000
- **URL**: http://localhost:3000

## Переменные окружения

Обязательные переменные в `.env`:
- `SECRET_KEY` - Секретный ключ для JWT
- `OPENAI_API_KEY` - API ключ OpenAI
- `SENTRY_API_TOKEN` - Токен для Sentry API
- `SENTRY_ORG_SLUG` - Slug организации в Sentry

Опциональные переменные (имеют значения по умолчанию):
- `APP_SENTRY_DSN` - DSN для мониторинга самого приложения
- `APP_SENTRY_ENVIRONMENT` - Окружение для Sentry (production/development)

## Troubleshooting

### Проблемы с подключением к MongoDB
```bash
docker-compose logs mongodb
```

### Проблемы с backend
```bash
docker-compose logs backend
# или войти в контейнер
docker-compose exec backend bash
```

### Проблемы с frontend
```bash
docker-compose logs frontend
# или войти в контейнер
docker-compose exec frontend sh
```

### Полная очистка
```bash
make clean
docker volume prune -f
```
