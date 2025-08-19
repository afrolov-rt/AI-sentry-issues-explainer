# 📈 Настройка Sentry DSN

Это руководство поможет вам настроить Sentry DSN для мониторинга приложения AI Sentry Issues Explainer.

## 🎯 Что такое Sentry DSN?

DSN (Data Source Name) - это уникальный URL, который Sentry использует для определения куда отправлять данные о событиях и ошибках из вашего приложения.

## 🚀 Пошаговая настройка

### Шаг 1: Создание аккаунта в Sentry

1. Перейдите на [sentry.io](https://sentry.io)
2. Нажмите "Get Started" или "Sign Up"
3. Создайте аккаунт (можно использовать GitHub, Google или email)
4. Подтвердите email, если требуется

### Шаг 2: Создание организации

1. После входа создайте организацию или используйте существующую
2. Выберите подходящее имя (например, "MyCompany" или ваше имя)

### Шаг 3: Создание проекта

1. Нажмите "Create Project"
2. Выберите платформу: **Python**
3. Выберите фреймворк: **FastAPI** (или просто Python)
4. Введите название проекта: `ai-sentry-explainer`
5. Нажмите "Create Project"

### Шаг 4: Получение DSN

После создания проекта вы увидите страницу с инструкциями по настройке. DSN будет выглядеть примерно так:

```
https://1234567890abcdef1234567890abcdef@o1234567.ingest.sentry.io/1234567
```

### Шаг 5: Настройка в приложении

1. Скопируйте ваш DSN
2. Откройте файл `config/.env`
3. Найдите строку `APP_SENTRY_DSN=`
4. Вставьте ваш DSN:
   ```env
   APP_SENTRY_DSN=https://1234567890abcdef1234567890abcdef@o1234567.ingest.sentry.io/1234567
   ```

### Шаг 6: Тестирование интеграции

1. Запустите приложение:
   ```bash
   python main.py
   ```

2. Проверьте статус Sentry:
   ```bash
   curl http://localhost:8000/api/v1/debug/sentry-status
   ```

3. Отправьте тестовую ошибку:
   ```bash
   curl -X POST http://localhost:8000/api/v1/debug/test-error
   ```

4. Проверьте в веб-интерфейсе Sentry, что ошибка появилась в Issues

## 🔧 Дополнительные настройки

### Environment (Среда)
Укажите среду выполнения:
```env
APP_SENTRY_ENVIRONMENT=development  # или production, staging
```

### Release (Версия)
Укажите версию приложения:
```env
APP_SENTRY_RELEASE=1.0.0
```

### Sample Rates (Частота сэмплирования)
Настройте частоту отправки данных (от 0.0 до 1.0):
```env
APP_SENTRY_TRACES_SAMPLE_RATE=0.1      # 10% транзакций
APP_SENTRY_PROFILES_SAMPLE_RATE=0.1    # 10% профилей производительности
```

## 📊 Что будет отслеживаться?

После настройки Sentry будет автоматически отслеживать:

- ✅ **Ошибки и исключения** в приложении
- ✅ **Производительность** API эндпоинтов
- ✅ **Контекст пользователей** и workspace
- ✅ **Логи** уровня ERROR и выше
- ✅ **Интеграции** с MongoDB, HTTP запросами
- ✅ **Кастомные события** для AI анализа

## 🛠️ Debug эндпоинты

Для тестирования интеграции доступны эндпоинты (только в development режиме):

```bash
# Проверить статус Sentry
GET /api/v1/debug/sentry-status

# Отправить тестовую ошибку
POST /api/v1/debug/test-error

# Отправить тестовое сообщение
POST /api/v1/debug/test-message
```

## 🔒 Безопасность

- DSN содержит публичный ключ и безопасно использовать в коде
- Не передавайте секретные данные через Sentry события
- В production отключите debug эндпоинты (DEBUG=False)

## ❓ Troubleshooting

### Sentry не инициализируется
- Проверьте, что `APP_SENTRY_DSN` не пустой
- Убедитесь, что DSN корректный (начинается с https://)
- Проверьте логи приложения на ошибки инициализации

### События не появляются в Sentry
- Проверьте интернет соединение
- Убедитесь, что sample rates не равны 0.0
- Проверьте, что проект активен в Sentry

### Слишком много событий
- Уменьшите sample rates
- Настройте фильтрацию в before_send функциях
- Используйте Sentry Filters в веб-интерфейсе

## 📚 Дополнительные ресурсы

- [Sentry Python Documentation](https://docs.sentry.io/platforms/python/)
- [FastAPI Integration](https://docs.sentry.io/platforms/python/guides/fastapi/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
