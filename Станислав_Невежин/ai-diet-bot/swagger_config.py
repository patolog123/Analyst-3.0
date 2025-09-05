"""
Конфигурация Swagger документации для AI Diet Bot API
Интегрировано с общей конфигурацией приложения
"""

import os
from config import config

# Используем настройки из общей конфигурации
API_BASE_URL = config.API_BASE_URL

# Определяем hostname в зависимости от окружения
if "amvera.io" in API_BASE_URL:
    # Продакшн окружение на Amvera
    HOSTNAME = 'ai-diet-bot-snevezhin.amvera.io'
else:
    # Локальное окружение
    HOSTNAME = '0.0.0.0:8080'

SWAGGER_CONFIG = {
    "swagger": "2.0",
    "info": {
        "title": "AI Diet Bot API",
        "description": "REST API для AI Diet Bot 3.0 - системы генерации планов питания для спортсменов",
        "version": "1.0.0",
        "contact": {
            "name": "AI Diet Bot Team",
            "email": "support@aidietbot.com"
        }
    },
    "host": HOSTNAME,
    "basePath": "/api",
    "schemes": ["https", "http"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {
            "name": "Users",
            "description": "Управление пользователями"
        },
        {
            "name": "Meal Plans", 
            "description": "Генерация и управление планами питания"
        },
        {
            "name": "Workouts",
            "description": "Данные о тренировках"
        },
        {
            "name": "Activities",
            "description": "Данные о физической активности"
        },
        {
            "name": "Health",
            "description": "Проверка здоровья сервиса"
        }
    ],
    "securityDefinitions": {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "API ключ для доступа к сервису"
        }
    },
    "security": [{"ApiKeyAuth": []}]
}

# Пути к YAML спецификациям
SWAGGER_YAML_PATHS = {
    "main": "ai_diet_api.yaml",
    "simple": "ai_diet_api_simple.yaml"
}

def get_swagger_ui_template():
    """Возвращает кастомный шаблон для Swagger UI"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Diet Bot API - Swagger UI</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="//unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        html {
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }
        *,
        *:before,
        *:after {
            box-sizing: inherit;
        }
        body {
            margin: 0;
            background: #fafafa;
        }
        .swagger-ui .topbar {
            background-color: #2c3e50;
            padding: 10px 0;
        }
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
        .custom-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .custom-header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .custom-header p {
            margin: 10px 0 0;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <div class="custom-header">
        <h1>🍽️ AI Diet Bot API</h1>
        <p>REST API для генерации планов питания для спортсменов</p>
    </div>
    <div id="swagger-ui"></div>
    <script src="//unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: '/api/swagger.yaml',  # Путь к YAML спецификации остается прежним
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.presets.standalone
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                validatorUrl: null,
                docExpansion: 'none',
                tagsSorter: 'alpha',
                operationsSorter: 'alpha'
            });
        };
    </script>
</body>
</html>
"""