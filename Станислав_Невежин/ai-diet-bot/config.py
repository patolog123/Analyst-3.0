"""
Конфигурация приложения для AI диетолога 3.0 с HTTP API
Оптимизировано для развертывания на Amvera (ai-diet-bot-snevezhin.amvera.io)
"""

import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Config:
    """Конфигурация приложения для Amvera с поддержкой HTTP API"""
    
    # Основные настройки (обязательные)
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', 'your_telegram_bot_token_here')
    DEEPSEEK_API_KEY: str = os.getenv('DEEPSEEK_API_KEY', 'your_deepseek_api_key_here')
    
    # Настройки HTTP API сервера
    HOST: str = os.getenv('HOST', '0.0.0.0')
    PORT: int = int(os.getenv('PORT', '8080'))
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'http://0.0.0.0:8080')
    
    # CORS настройки для локальной разработки
    CORS_ORIGINS: list = field(default_factory=lambda: os.getenv('CORS_ORIGINS', 'http://0.0.0.0:8080').split(','))
    CORS_ALLOW_CREDENTIALS: bool = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'
    CORS_ALLOW_METHODS: list = field(default_factory=lambda: os.getenv('CORS_ALLOW_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','))
    CORS_ALLOW_HEADERS: list = field(default_factory=lambda: os.getenv('CORS_ALLOW_HEADERS', 'Content-Type,Authorization,X-Requested-With').split(','))
    
    # Флаги окружения
    IS_PRODUCTION: bool = os.getenv('ENVIRONMENT', 'production').lower() == 'production'
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # Настройки LLM
    DEEPSEEK_MODEL: str = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
    DEEPSEEK_BASE_URL: str = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    DEEPSEEK_TEMPERATURE: float = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.7'))
    DEEPSEEK_MAX_TOKENS: int = int(os.getenv('DEEPSEEK_MAX_TOKENS', '4000'))
    
    # Настройки бота
    ADMIN_USER_ID: int = int(os.getenv('ADMIN_USER_ID', '0'))
    SUPPORT_CHAT_ID: str = os.getenv('SUPPORT_CHAT_ID', '')
    
    # Настройки логирования
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def api_urls(self) -> dict:
        """URLs API endpoints для Amvera"""
        base_url = self.API_BASE_URL.rstrip('/')
        return {
            'health': f"{base_url}/health",
            'users': f"{base_url}/api/users",
            'user_detail': f"{base_url}/api/users/{{telegram_id}}",
            'meal_plans': f"{base_url}/api/meal-plans",
            'meal_plan_detail': f"{base_url}/api/meal-plans/{{plan_id}}",
            'workouts': f"{base_url}/api/workouts",
            'activities': f"{base_url}/api/activities",
            'swagger_ui': f"{base_url}/api/docs"
        }
    
    @property
    def database_url(self) -> str:
        """Получить URL подключения к базе данных"""
        # Используем DATABASE_URL от Amvera или fallback на хардкод
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            print(f"DEBUG: Используется DATABASE_URL от Amvera: {db_url}")
            return db_url
        else:
            # Fallback для локальной разработки или если Amvera не предоставила URL
            url = "postgresql://postgres:postgres@postgres-db-snevezhin.db-msk0.amvera.tech:5432/ai-diet-bot"
            print(f"DEBUG: Используется fallback URL базы данных: {url}")
            return url
    
    @property
    def swagger_config(self) -> dict:
        """Конфигурация для Swagger UI"""
        return {
            'title': 'AI Diet Bot API',
            'version': '1.0.0',
            'description': 'HTTP API для Telegram бота AI диетолога',
            'contact': {
                'name': 'Support',
                'url': self.API_BASE_URL,
                'email': 'support@example.com'
            },
            'license': {
                'name': 'MIT',
                'url': 'https://opensource.org/licenses/MIT'
            }
        }
    
    @property
    def is_valid(self) -> bool:
        """Проверить валидность конфигурации"""
        return bool(self.BOT_TOKEN and self.DEEPSEEK_API_KEY and self.API_BASE_URL)
    
    def validate(self) -> None:
        """Валидация конфигурации"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен")
        if not self.DEEPSEEK_API_KEY:
            raise ValueError("DEEPSEEK_API_KEY не установлен")
        if not self.API_BASE_URL:
            raise ValueError("API_BASE_URL не установлен")
        if not self.API_BASE_URL.startswith(('http://', 'https://')):
            raise ValueError("API_BASE_URL должен начинаться с http:// или https://")
        

# Глобальный экземпляр конфигурации
config = Config()

# Автоматическая валидация отключена для Amvera с хардкодированным URL
# Валидация выполняется принудительно в main_aiogram_v3.py при запуске
if __name__ == "__main__":
    # Только для тестирования при прямом запуске config.py
    try:
        config.validate()
        print("✅ Конфигурация успешно загружена и валидирована")
    except ValueError as e:
        print(f"❌ Ошибка конфигурации: {e}")