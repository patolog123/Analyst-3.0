#!/usr/bin/env python3
"""
HTTP API сервер для AI Diet Bot 3.0
Интеграция aiohttp с существующим aiogram ботом
"""

import asyncio
import logging
import json
import os
from datetime import datetime, date
from typing import Dict, Any, Optional
from decimal import Decimal

from aiohttp import web
import aiohttp_cors

from swagger_config import get_swagger_ui_template
from config import config

from database import db
from llm_integration import llm

# Настройка логирования
logger = logging.getLogger(__name__)

class APIServer:
    """HTTP API сервер для AI Diet Bot"""
    
    def __init__(self):
        # Используем конфигурацию из config.py
        self.host = config.HOST
        self.port = config.PORT
        self.api_base_url = config.API_BASE_URL
        self.app = web.Application()
        self.setup_routes()
        
    def setup_routes(self):
        """Настройка маршрутов API с проверкой на дублирование"""
        
        # Получаем список уже зарегистрированных маршрутов
        existing_routes = [str(route) for route in self.app.router.routes()]
        
        # Функция для безопасной регистрации маршрутов
        def safe_add_route(method, path, handler):
            route_str = f"{method} {path}"
            if route_str not in existing_routes:
                if method == 'GET':
                    self.app.router.add_get(path, handler)
                elif method == 'POST':
                    self.app.router.add_post(path, handler)
                # Изменяем формат логирования чтобы избежать интерпретации как команды
                logger.info(f"✅ Зарегистрирован маршрут: {method} {path}")
            else:
                logger.warning(f"⚠️ Маршрут уже существует: {route_str}")
        
        # Health check - добавляем оба метода для CORS
        safe_add_route('GET', '/health', self.health_check)
        safe_add_route('OPTIONS', '/health', self.health_check_options)
        
        # Users endpoints
        safe_add_route('POST', '/api/users', self.create_user)
        safe_add_route('GET', '/api/users', self.get_users)
        safe_add_route('GET', '/api/users/{telegram_id}', self.get_user)
        
        # Meal plans endpoints
        safe_add_route('POST', '/api/meal-plans', self.generate_meal_plan)
        safe_add_route('GET', '/api/meal-plans', self.get_user_plans)
        safe_add_route('GET', '/api/meal-plans/{plan_id}', self.get_meal_plan)
        
        # Workouts endpoints
        safe_add_route('POST', '/api/workouts', self.save_workout_data)
        
        # Activities endpoints
        safe_add_route('POST', '/api/activities', self.save_activity_data)
        
        # Swagger documentation будет настроена в setup_swagger_docs()
        # Убрали ручной маршрут чтобы избежать конфликта
        
        # Логируем все зарегистрированные маршруты для отладки
        logger.info("📋 Все зарегистрированные маршруты:")
        for route in self.app.router.routes():
            logger.info(f"   - {route}")
        
        # Настройка CORS
        self.setup_cors()
        
    def setup_cors(self):
        """Настройка CORS для кросс-доменных запросов"""
        cors = aiohttp_cors.setup(self.app, defaults={
            origin: aiohttp_cors.ResourceOptions(
                allow_credentials=config.CORS_ALLOW_CREDENTIALS,
                expose_headers="*",
                allow_headers=config.CORS_ALLOW_HEADERS,
                allow_methods=config.CORS_ALLOW_METHODS,
            ) for origin in config.CORS_ORIGINS
        })
        
        # Применяем CORS ко всем маршрутам
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Проверка здоровья сервиса"""
        logger.info(f"🔍 Получен запрос health check: {request.method} {request.path}")
        logger.info(f"🌐 Заголовки запроса: {dict(request.headers)}")
        logger.info(f"🔗 URL запроса: {request.url}")
        
        # Добавляем CORS заголовки вручную для health check
        response = web.json_response({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "service": "AI Diet Bot API",
            "endpoint": "/health"
        })
        
        # Добавляем CORS заголовки
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        
        return response
    
    async def health_check_options(self, request: web.Request) -> web.Response:
        """Обработчик OPTIONS запросов для health check (CORS)"""
        logger.info(f"🔍 Получен OPTIONS запрос health check: {request.method} {request.path}")
        
        response = web.Response(status=200)
        # Добавляем CORS заголовки для OPTIONS
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Max-Age'] = '3600'
        
        return response
    
    async def create_user(self, request: web.Request) -> web.Response:
        """Создание нового пользователя"""
        try:
            data = await request.json()
            
            # Валидация обязательных полей
            required_fields = ['telegram_id', 'name', 'gender', 'height', 
                             'current_weight', 'target_weight', 'competition_date']
            for field in required_fields:
                if field not in data:
                    return web.json_response(
                        {"error": f"Missing required field: {field}"},
                        status=400
                    )
            
            # Проверяем, существует ли пользователь
            existing_user = db.get_user(data['telegram_id'])
            if existing_user:
                return web.json_response(
                    {"error": "User already exists"},
                    status=409
                )
            
            # Сохраняем пользователя
            athlete_id = db.create_user(data)
            
            if athlete_id is None:
                return web.json_response(
                    {"error": "Failed to create user"},
                    status=500
                )
            
            return web.json_response(
                {
                    "message": "User created successfully",
                    "athlete_id": int(athlete_id) if athlete_id is not None else None,
                    "telegram_id": data['telegram_id']
                },
                status=201
            )
            
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def get_users(self, request: web.Request) -> web.Response:
        """Получение списка пользователей"""
        try:
            limit = int(request.query.get('limit', 10))
            offset = int(request.query.get('offset', 0))
            
            # Здесь должна быть реализация получения пользователей из БД
            # Временно возвращаем заглушку
            users = []
            
            return web.json_response({
                "users": [self._convert_decimals_to_float(user) for user in users if user is not None],
                "total": len(users),
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def get_user(self, request: web.Request) -> web.Response:
        """Получение пользователя по Telegram ID"""
        try:
            telegram_id = int(request.match_info['telegram_id'])
            user = db.get_user(telegram_id)
            
            if not user:
                return web.json_response(
                    {"error": "User not found"},
                    status=404
                )
            
            # Преобразование Decimal и datetime для JSON сериализации
            user_serializable = self._convert_decimals_to_float(user) if user is not None else {}
            
            return web.json_response(user_serializable)
            
        except ValueError:
            return web.json_response(
                {"error": "Invalid telegram_id format"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def generate_meal_plan(self, request: web.Request) -> web.Response:
        """Генерация плана питания"""
        logger.info(f"🔍 Получен запрос на генерацию плана питания: {request.method} {request.path}")
        try:
            data = await request.json()
            logger.info(f"📦 Данные запроса: {data}")
            telegram_id = data.get('telegram_id')
            athlete_id = data.get('athlete_id')
            
            if not telegram_id and not athlete_id:
                return web.json_response(
                    {"error": "telegram_id or athlete_id is required"},
                    status=400
                )
            
            # Получаем данные пользователя
            if athlete_id:
                # Используем переданный athlete_id для получения данных пользователя
                user_data = self._get_user_by_athlete_id(athlete_id)
            else:
                # Используем telegram_id для обратной совместимости
                user_data = db.get_user(telegram_id)
            
            if not user_data:
                return web.json_response(
                    {"error": "User not found"},
                    status=404
                )
            
            # Генерируем план питания через LLM
            meal_plan = await llm.generate_meal_plan(user_data)
            
            if not meal_plan or 'error' in meal_plan:
                return web.json_response(
                    {"error": "Failed to generate meal plan"},
                    status=500
                )
            
            # Добавляем plan_date и plan_name из запроса в данные плана
            if 'plan_date' in data:
                meal_plan['plan_date'] = data['plan_date']
            if 'plan_name' in data:
                meal_plan['plan_name'] = data['plan_name']
            
            # Сохраняем план в базу
            if not athlete_id:
                # Если athlete_id не передан, получаем его из telegram_id
                athlete_id = db.get_athlete_id_by_telegram(telegram_id)
            
            plan_id = db.save_meal_plan(athlete_id, meal_plan)
            
            if plan_id is None:
                return web.json_response(
                    {"error": "Failed to save meal plan"},
                    status=500
                )
            
            return web.json_response({
                "message": "Meal plan generated successfully",
                "plan_id": int(plan_id) if plan_id is not None else None,
                "plan_data": self._convert_decimals_to_float(meal_plan)
            }, status=201)
            
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error generating meal plan: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def get_user_plans(self, request: web.Request) -> web.Response:
        """Получение планов питания пользователя"""
        try:
            telegram_id = request.query.get('telegram_id')
            
            if not telegram_id:
                return web.json_response(
                    {"error": "telegram_id is required"},
                    status=400
                )
            
            plans = db.get_user_plans(int(telegram_id))
            
            # Преобразуем данные для JSON сериализации
            serializable_plans = [self._convert_decimals_to_float(plan) for plan in plans if plan is not None]
            
            return web.json_response({
                "plans": serializable_plans,
                "total": len(plans)
            })
            
        except Exception as e:
            logger.error(f"Error getting user plans: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def get_meal_plan(self, request: web.Request) -> web.Response:
        """Получение детальной информации о плане питания"""
        try:
            plan_id = int(request.match_info['plan_id'])
            
            # Здесь должна быть реализация получения плана из БД
            # Временно возвращаем заглушку
            plan = None
            
            if not plan:
                return web.json_response(
                    {"error": "Meal plan not found"},
                    status=404
                )
            
            return web.json_response(self._convert_decimals_to_float(plan) if plan is not None else {})
            
        except ValueError:
            return web.json_response(
                {"error": "Invalid plan_id format"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error getting meal plan: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def save_workout_data(self, request: web.Request) -> web.Response:
        """Сохранение данных о тренировках"""
        try:
            data = await request.json()
            telegram_id = data.get('telegram_id')
            
            if not telegram_id:
                return web.json_response(
                    {"error": "telegram_id is required"},
                    status=400
                )
            
            athlete_id = db.get_athlete_id_by_telegram(telegram_id)
            if not athlete_id:
                return web.json_response(
                    {"error": "User not found"},
                    status=404
                )
            
            workout_id = db.save_workout_info(athlete_id, data)
            
            if workout_id is None:
                return web.json_response(
                    {"error": "Failed to save workout data"},
                    status=500
                )
            
            return web.json_response({
                "message": "Workout data saved successfully",
                "workout_id": int(workout_id) if workout_id is not None else None
            }, status=201)
            
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error saving workout data: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def save_activity_data(self, request: web.Request) -> web.Response:
        """Сохранение данных о физической активности"""
        try:
            data = await request.json()
            telegram_id = data.get('telegram_id')
            
            if not telegram_id:
                return web.json_response(
                    {"error": "telegram_id is required"},
                    status=400
                )
            
            athlete_id = db.get_athlete_id_by_telegram(telegram_id)
            if not athlete_id:
                return web.json_response(
                    {"error": "User not found"},
                    status=404
                )
            
            activity_id = db.save_activity_info(athlete_id, data)
            
            if activity_id is None:
                return web.json_response(
                    {"error": "Failed to save activity data"},
                    status=500
                )
            
            return web.json_response({
                "message": "Activity data saved successfully",
                "activity_id": int(activity_id) if activity_id is not None else None
            }, status=201)
            
        except json.JSONDecodeError:
            return web.json_response(
                {"error": "Invalid JSON"},
                status=400
            )
        except Exception as e:
            logger.error(f"Error saving activity data: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def setup_swagger_docs(self):
        """Настройка Swagger документации"""
        
        # Полностью отключаем автоматическую настройку aiohttp-swagger
        # и настраиваем Swagger UI вручную чтобы избежать конфликтов
        
        # Создаем маршрут для Swagger UI
        async def swagger_ui_handler(request):
            return web.Response(
                text=get_swagger_ui_template(),
                content_type='text/html'
            )
        
        # Создаем маршрут для YAML спецификации
        async def swagger_yaml_handler(request):
            try:
                # Загружаем основной YAML файл спецификации
                with open('ai_diet_api.yaml', 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                return web.Response(
                    text=yaml_content,
                    content_type='application/yaml'
                )
            except FileNotFoundError:
                logger.error("YAML файл спецификации не найден")
                return web.Response(
                    text="swagger: '2.0'\ninfo:\n  title: AI Diet Bot API\n  version: 1.0.0\n  description: YAML файл не найден",
                    content_type='application/yaml',
                    status=404
                )
        
        # Регистрируем маршруты только если они еще не зарегистрированы
        # Это предотвращает конфликт "method GET is already registered"
        routes = [str(route) for route in self.app.router.routes()]
        
        if '/api/swagger/' not in routes:
            self.app.router.add_get('/api/swagger/', swagger_ui_handler)
            logger.info("✅ Маршрут /api/swagger/ зарегистрирован")
        
        if '/api/swagger.yaml' not in routes:
            self.app.router.add_get('/api/swagger.yaml', swagger_yaml_handler)
            logger.info("✅ Маршрут /api/swagger.yaml зарегистрирован")
        
        logger.info("📚 Swagger UI настроен вручную по пути /api/swagger/")
    
    def _get_user_by_athlete_id(self, athlete_id: int) -> Optional[Dict]:
        """Получить данные пользователя по athlete_id"""
        query = "SELECT * FROM athletes WHERE athlete_id = %s"
        result = db.execute_query(query, (athlete_id,))
        return result[0] if result else None

    def _convert_decimals_to_float(self, data):
        """Рекурсивно преобразует Decimal, datetime и date значения для JSON сериализации"""
        if data is None:
            return None
        elif isinstance(data, (Decimal, float)):
            return float(data)
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        elif isinstance(data, dict):
            return {k: self._convert_decimals_to_float(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_decimals_to_float(item) for item in data]
        else:
            return data

    async def start(self):
        """Запуск сервера"""
        await self.setup_swagger_docs()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"API server started on {self.host}:{self.port}")
        logger.info(f"🌐 Базовый URL API: {self.api_base_url}")
        logger.info(f"📚 Swagger docs available at {self.api_base_url}/api/swagger/")
        
        # Бесконечный цикл для работы сервера
        await asyncio.Future()

async def start_api_server():
    """Запуск API сервера"""
    server = APIServer()
    logger.info(f"🚀 Запуск API сервера на {server.host}:{server.port}")
    logger.info(f"🌐 Базовый URL API: {server.api_base_url}")
    logger.info(f"🔧 CORS origins: {config.CORS_ORIGINS}")
    await server.start()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(start_api_server())