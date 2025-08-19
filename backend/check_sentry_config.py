#!/usr/bin/env python3
"""
Sentry Configuration Checker
Проверяет настройки Sentry и тестирует подключение
"""

import os
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
import sentry_sdk

def check_sentry_config():
    """Проверка конфигурации Sentry"""
    print("🔍 Проверка конфигурации Sentry...")
    print("=" * 50)
    
    # Проверяем DSN
    if not settings.APP_SENTRY_DSN:
        print("❌ APP_SENTRY_DSN не настроен")
        print("💡 Добавьте APP_SENTRY_DSN в config/.env файл")
        return False
    
    print(f"✅ DSN настроен: {settings.APP_SENTRY_DSN[:30]}...")
    print(f"📍 Environment: {settings.APP_SENTRY_ENVIRONMENT}")
    print(f"🏷️  Release: {settings.APP_SENTRY_RELEASE}")
    print(f"📊 Traces Sample Rate: {settings.APP_SENTRY_TRACES_SAMPLE_RATE}")
    print(f"⚡ Profiles Sample Rate: {settings.APP_SENTRY_PROFILES_SAMPLE_RATE}")
    
    return True

def test_sentry_connection():
    """Тестирование подключения к Sentry"""
    print("\n🧪 Тестирование подключения...")
    print("=" * 50)
    
    try:
        # Инициализируем Sentry
        sentry_sdk.init(
            dsn=settings.APP_SENTRY_DSN,
            environment=settings.APP_SENTRY_ENVIRONMENT,
            release=settings.APP_SENTRY_RELEASE,
            traces_sample_rate=1.0,  # 100% для теста
        )
        
        print("✅ Sentry инициализирован успешно")
        
        # Отправляем тестовое сообщение
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("test", "config_check")
            scope.set_context("check_info", {
                "script": "check_sentry_config.py",
                "purpose": "Configuration validation"
            })
        
        sentry_sdk.capture_message("🧪 Тест конфигурации Sentry", level="info")
        print("✅ Тестовое сообщение отправлено")
        
        # Принудительно отправляем все события
        sentry_sdk.flush(timeout=5)
        print("✅ События отправлены в Sentry")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def main():
    """Главная функция"""
    print("🚀 AI Sentry Issues Explainer - Проверка конфигурации Sentry")
    print("=" * 60)
    
    # Проверяем конфигурацию
    if not check_sentry_config():
        print("\n📚 Инструкции по настройке см. в файле SENTRY_SETUP.md")
        sys.exit(1)
    
    # Тестируем подключение
    if test_sentry_connection():
        print("\n🎉 Sentry настроен правильно!")
        print("💡 Проверьте веб-интерфейс Sentry на наличие тестового сообщения")
    else:
        print("\n❌ Проблема с подключением к Sentry")
        print("📚 См. инструкции в SENTRY_SETUP.md")
        sys.exit(1)

if __name__ == "__main__":
    main()
