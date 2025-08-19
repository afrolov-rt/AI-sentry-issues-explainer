# 🔧 Настройка Sentry DSN через интерфейс

Мы успешно добавили возможность настройки Sentry DSN через веб-интерфейс приложения!

## 🚀 Что было добавлено

### Backend:
1. **Модель Workspace** - добавлено поле `sentry_dsn` в схему `Workspace`
2. **API Endpoint** - обновлен `PUT /api/v1/workspaces/current` для поддержки `sentry_dsn`
3. **Валидация** - добавлена схема `WorkspaceUpdate` с поддержкой всех Sentry настроек

### Frontend:
1. **Страница настроек** - создана `SettingsPage.tsx` с формой для настройки Sentry
2. **Типы** - обновлены интерфейсы `Workspace` и `UpdateWorkspaceRequest`
3. **API сервис** - добавлен метод `testSentryConnection`
4. **Hook** - добавлена функция `refreshWorkspace` в `useWorkspace`

## 🎯 Как использовать

1. **Войдите в приложение** с учетными данными demo/demo123
2. **Перейдите в Settings** через боковое меню
3. **Заполните Sentry настройки**:
   - **Sentry API Token** - ваш API токен из Sentry
   - **Sentry Organization Slug** - идентификатор организации
   - **Sentry DSN** - Data Source Name для отправки событий

4. **Протестируйте подключение** - нажмите "Test Connection"
5. **Сохраните настройки** - нажмите "Save Settings"

## 📋 Поля настроек Sentry

### Sentry API Token
- Используется для **чтения** issues из Sentry
- Получить можно в: Settings → Auth Tokens в Sentry
- Права: `project:read`, `org:read`

### Sentry Organization Slug  
- Идентификатор вашей организации в Sentry
- Найти можно в URL: `https://sentry.io/organizations/[ORG_SLUG]/`

### Sentry DSN
- Используется для **отправки** событий в ваш Sentry проект
- Получить можно в: Settings → Projects → [Project] → Client Keys (DSN)
- Формат: `https://key@organization.ingest.sentry.io/project-id`

## 🔐 Безопасность

- Токены и DSN скрыты в интерфейсе (показываются как пароли)
- Можно показать/скрыть через иконку глаза
- Данные передаются через защищенное API с JWT авторизацией

## ✅ Функциональность

- ✅ Добавление/редактирование Sentry настроек
- ✅ Тестирование подключения к Sentry API
- ✅ Скрытие чувствительных данных в интерфейсе
- ✅ Валидация полей и обработка ошибок
- ✅ Автоматическое обновление workspace после сохранения

## 🎨 UI/UX особенности

- Современный дизайн с Material-UI компонентами
- Группировка настроек по разделам
- Индикаторы загрузки для операций
- Информативные сообщения об ошибках и успехе
- Подсказки (helper text) для каждого поля

Теперь ваше приложение готово для полноценной интеграции с Sentry! 🎉
