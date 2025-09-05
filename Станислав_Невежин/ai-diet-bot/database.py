"""
Модуль для работы с базой данных PostgreSQL на Amvera
Реализует все CRUD операции для AI диетолога 3.0 согласно физической модели v1.4
Оптимизирован для работы только с Amvera PostgreSQL через хардкодированный URL
"""

import logging
import json
import psycopg2
import subprocess
import socket
import time
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from config import config

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с базой данных PostgreSQL"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Установить соединение с базой данных через хардкодированный URL"""
        try:
            db_url = config.database_url
            logger.info(f"🔗 Попытка подключения с URL: {db_url}")
            self.connection = psycopg2.connect(
                db_url,
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            logger.info("✅ Успешное подключение к базе данных Amvera PostgreSQL")
            
            self.cursor = self.connection.cursor()
            
        except psycopg2.OperationalError as e:
            logger.error(f"❌ Ошибка подключения к базе данных (OperationalError): {e}")
            raise ConnectionError(f"Не удалось подключиться к БД Amvera: {e}") from e
        except psycopg2.ProgrammingError as e:
            logger.error(f"❌ Ошибка аутентификации (ProgrammingError): {e}")
            raise ConnectionError("Ошибка аутентификации. Проверьте хардкодированный URL базы данных в конфигурации.") from e
        except Exception as e:
            logger.error(f"❌ Неизвестная ошибка подключения: {e}")
            raise
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logger.info("✅ Соединение с базой данных закрыто")

    def check_database_availability(self, timeout: int = 5) -> bool:
        """Проверить доступность базы данных через хардкодированный URL"""
        try:
            # Пытаемся подключиться с коротким таймаутом
            test_conn = psycopg2.connect(config.database_url, connect_timeout=timeout)
            test_conn.close()
            logger.info("✅ База данных Amvera доступна")
            return True
        except Exception as e:
            logger.error(f"❌ База данных Amvera недоступна: {e}")
            return False

    def diagnose_connection_issues(self) -> Dict[str, Any]:
        """Диагностика проблем подключения к Amvera PostgreSQL"""
        diagnostics = {
            'database_available': False,
            'error_details': []
        }

        # Проверка доступности базы данных
        diagnostics['database_available'] = self.check_database_availability()

        if not diagnostics['database_available']:
            diagnostics['error_details'].append('База данных Amvera недоступна. Проверьте:')
            diagnostics['error_details'].append('1. Наличие базы данных PostgreSQL в панели Amvera')
            diagnostics['error_details'].append('2. Корректность хардкодированного URL базы данных')
            diagnostics['error_details'].append('3. Состояние кластера PostgreSQL в Amvera')
            diagnostics['error_details'].append('4. Подключение базы данных к приложению в настройках Amvera')

        return diagnostics

    def execute_query_with_retry(self, query: str, params: tuple = None, max_retries: int = 3,
                               retry_delay: int = 2) -> List[Dict]:
        """Выполнить запрос с повторными попытками при ошибках подключения"""
        for attempt in range(max_retries):
            try:
                return self.execute_query(query, params)
            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                if attempt == max_retries - 1:
                    raise
                
                logger.warning(f"⚠️ Попытка {attempt + 1}/{max_retries} не удалась: {e}")
                logger.info(f"⏳ Повторная попытка через {retry_delay} секунд...")
                time.sleep(retry_delay)
                
                # Принудительное переподключение
                self.close()
                self.connect()
        
        return []
    
    def ensure_connection(self):
        """Убедиться, что соединение с БД установлено, переподключиться при необходимости"""
        try:
            if self.connection is None or self.connection.closed:
                logger.warning("⚠️ Соединение с Amvera PostgreSQL разорвано, переподключаемся...")
                self.connect()
            elif self.cursor is None or self.cursor.closed:
                logger.warning("⚠️ Курсор БД закрыт, пересоздаем...")
                self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            logger.error(f"❌ Не удалось восстановить соединение с БД: {e}")
            return False
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Выполнить запрос и вернуть результаты"""
        try:
            # Убеждаемся, что соединение установлено
            if not self.ensure_connection():
                logger.error("❌ Невозможно выполнить запрос: нет соединения с Amvera PostgreSQL")
                return []
            
            logger.debug(f"📝 Выполнение SQL: {query}")
            logger.debug(f"🔢 Параметры: {params}")
            
            self.cursor.execute(query, params)
            
            # Проверяем, является ли запрос SELECT или содержит RETURNING
            query_upper = query.strip().upper()
            if query_upper.startswith('SELECT') or 'RETURNING' in query_upper:
                result = self.cursor.fetchall()
                logger.debug(f"📊 Результат запроса: {len(result)} записей")
                self.connection.commit()
                return result
            
            self.connection.commit()
            logger.debug("✅ Запрос выполнен успешно (без возвращаемых данных)")
            return []
            
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"❌ Ошибка выполнения запроса к Amvera PostgreSQL: {type(e).__name__}: {e}")
            logger.error(f"📋 SQL: {query}")
            logger.error(f"🔢 Параметры: {params}")
            
            # Детальная диагностика для PostgreSQL ошибок Amvera
            if hasattr(e, 'pgcode'):
                logger.error(f"📟 PostgreSQL код ошибки: {e.pgcode}")
            if hasattr(e, 'pgerror'):
                logger.error(f"📟 PostgreSQL сообщение: {e.pgerror}")
                
            # Пытаемся восстановить соединение с Amvera PostgreSQL после ошибки
            try:
                self.ensure_connection()
            except Exception as reconnect_error:
                logger.error(f"❌ Не удалось восстановить соединение с Amvera PostgreSQL: {reconnect_error}")
                
            raise
    
    def get_user(self, telegram_id: int) -> Optional[Dict]:
        """Получить пользователя по Telegram ID"""
        query = "SELECT * FROM athletes WHERE telegram_id = %s"
        result = self.execute_query(query, (telegram_id,))
        return result[0] if result else None
    
    def create_user(self, user_data: Dict) -> int:
        """Создать нового пользователя согласно v1.7 с telegram_id"""
        query = """
        INSERT INTO athletes (
            telegram_id, name, gender, height, current_weight,
            target_weight, competition_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING athlete_id
        """
        params = (
            user_data['telegram_id'],
            user_data.get('name', ''),
            user_data.get('gender'),
            user_data.get('height'),
            user_data.get('current_weight'),
            user_data.get('target_weight'),
            user_data.get('competition_date')
        )
        try:
            result = self.execute_query(query, params)
            if result and len(result) > 0:
                athlete_id = result[0]['athlete_id']
                logger.info(f"✅ Пользователь создан с athlete_id: {athlete_id}")
                return athlete_id
            else:
                logger.error("❌ Не удалось создать пользователя: запрос не вернул athlete_id")
                logger.error(f"📋 Параметры запроса: {params}")
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка создания пользователя: {e}")
            logger.error(f"📋 Параметры запроса: {params}")
            import traceback
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            return None
    
    def update_user(self, athlete_id: int, update_data: Dict) -> bool:
        """Обновить данные пользователя"""
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(athlete_id)
        
        query = f"UPDATE athletes SET {set_clause} WHERE athlete_id = %s"
        self.execute_query(query, values)
        return True
    
    def save_workout_info(self, athlete_id: int, workout_data: Dict) -> int:
        """Сохранить информацию о тренировках"""
        query = """
        INSERT INTO workouts (
            athlete_id, sessions_per_week, exercises,
            equipment_weight, reps, sets
        ) VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING workout_id
        """
        params = (
            athlete_id,
            workout_data.get('sessions_per_week'),
            workout_data.get('exercises'),
            workout_data.get('equipment_weight'),
            workout_data.get('reps'),
            workout_data.get('sets')
        )
        try:
            result = self.execute_query(query, params)
            if result and len(result) > 0:
                workout_id = result[0]['workout_id']
                logger.info(f"✅ Данные тренировок сохранены с workout_id: {workout_id}")
                return workout_id
            else:
                logger.error("❌ Не удалось сохранить данные тренировок: запрос не вернул workout_id")
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения тренировок: {e}")
            import traceback
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            return None
    
    def save_activity_info(self, athlete_id: int, activity_data: Dict) -> int:
        """Сохранить информацию о физической активности согласно v1.7"""
        query = """
        INSERT INTO activities (
            athlete_id, steps_per_day, work_type, additional_activity, activity_hours
        ) VALUES (%s, %s, %s, %s, %s)
        RETURNING activity_id
        """
        params = (
            athlete_id,
            activity_data.get('steps_per_day'),
            activity_data.get('work_type'),
            activity_data.get('additional_activity'),
            activity_data.get('activity_hours')
        )
        try:
            result = self.execute_query(query, params)
            if result and len(result) > 0:
                activity_id = result[0]['activity_id']
                logger.info(f"✅ Данные активности сохранены с activity_id: {activity_id}")
                return activity_id
            else:
                logger.error("❌ Не удалось сохранить данные активности: запрос не вернул activity_id")
                return None
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения активности: {e}")
            import traceback
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            return None
    
    def save_meal_plan(self, athlete_id: int, plan_data: Dict) -> int:
        """Сохранить план питания согласно v1.7 (объединенная таблица)"""
        logger.info(f"💾 Попытка сохранения плана питания для athlete_id {athlete_id}")
        logger.debug(f"📋 Данные плана: {json.dumps(plan_data, indent=2, default=str)}")
        
        # Получаем дату плана из данных или используем следующий день
        plan_date = plan_data.get('plan_date')
        if isinstance(plan_date, str):
            from datetime import datetime
            plan_date = datetime.strptime(plan_date, '%Y-%m-%d').date()
        elif plan_date is None:
            from datetime import date, timedelta
            plan_date = date.today() + timedelta(days=1)
        
        # Получаем название плана или используем значение по умолчанию
        plan_name = plan_data.get('plan_name', 'Основной план')
        
        meal_ids = []
        
        try:
            # Сначала удаляем существующий план на эту дату с таким названием
            delete_query = """
            DELETE FROM meal_plans
            WHERE athlete_id = %s AND plan_date = %s AND plan_name = %s
            """
            delete_params = (athlete_id, plan_date, plan_name)
            
            logger.info(f"🗑️ Удаление существующего плана для athlete_id {athlete_id}, даты {plan_date}, названия '{plan_name}'")
            self.execute_query(delete_query, delete_params)
            logger.info("✅ Существующий план удален")
            
            # Проверяем наличие приемов пищи в данных плана
            meals = plan_data.get('meals', [])
            if not meals:
                logger.error("❌ В данных плана отсутствуют приемы пищи")
                return None
            
            # Используем один запрос для всех приемов пищи для атомарности
            for i, meal in enumerate(meals):
                query = """
                INSERT INTO meal_plans (
                    athlete_id, meal_type, calories, proteins,
                    fats, carbs, description, plan_date, plan_name
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING meal_id
                """
                
                # Получаем значения с проверкой на None
                meal_type = meal.get('meal_type', '')
                calories = meal.get('calories', 0) or 0
                proteins = meal.get('proteins', 0) or 0
                fats = meal.get('fats', 0) or 0
                carbs = meal.get('carbs', 0) or 0
                description = meal.get('description', '') or ''
                
                params = (
                    athlete_id,
                    meal_type,
                    calories,
                    proteins,
                    fats,
                    carbs,
                    description,
                    plan_date,
                    plan_name
                )
                
                logger.info(f"🍽 [{i+1}/{len(meals)}] Сохранение: {meal_type}")
                logger.debug(f"📅 Дата плана: {plan_date}, Название: {plan_name}")
                logger.debug(f"🔢 Параметры: {params}")
                
                result = self.execute_query(query, params)
                logger.debug(f"📊 Результат execute_query: {result}")
                
                if result and len(result) > 0:
                    meal_id = result[0]['meal_id']
                    meal_ids.append(meal_id)
                    logger.info(f"✅ Прием пищи {meal_type} сохранен с ID {meal_id}")
                else:
                    logger.error(f"❌ Запрос выполнен, но не вернул meal_id для {meal_type}")
                    logger.error(f"📋 Параметры запроса: {params}")
                    # Если один из запросов не вернул ID, откатываем всю транзакцию
                    raise Exception(f"Не удалось сохранить прием пищи {meal_type}")
            
            if meal_ids:
                logger.info(f"✅ План питания '{plan_name}' успешно сохранен. Сохранено приемов пищи: {len(meal_ids)}, первый meal_id: {meal_ids[0]}")
                return meal_ids[0]
            else:
                logger.error("❌ Не удалось сохранить ни одного приема пищи")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения плана питания: {e}")
            import traceback
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            # Откатываем транзакцию при любой ошибке
            if self.connection:
                self.connection.rollback()
            return None

    def save_meals(self, plan_id: int, meals_data: List[Dict]) -> bool:
        """Сохранить приемы пищи для плана (совместимость со старой структурой)"""
        # Метод оставлен для совместимости, но теперь используется объединенная таблица
        # Фактическое сохранение происходит в save_meal_plan
        logger.warning("⚠️ Метод save_meals устарел, используется объединенная таблица meal_plans")
        return True
    
    def get_user_plans(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Получить все планы питания пользователя согласно v1.7 (несколько планов на день)"""
        query = """
        SELECT
            mp.plan_date,
            mp.plan_name,
            SUM(mp.calories) as total_calories,
            SUM(mp.proteins) as total_proteins,
            SUM(mp.fats) as total_fats,
            SUM(mp.carbs) as total_carbs,
            MAX(mp.created_at) as created_at,
            COUNT(DISTINCT mp.meal_type) as meal_count
        FROM meal_plans mp
        JOIN athletes a ON mp.athlete_id = a.athlete_id
        WHERE a.telegram_id = %s
        GROUP BY mp.plan_date, mp.plan_name
        ORDER BY mp.plan_date DESC, mp.plan_name
        LIMIT %s
        """
        return self.execute_query(query, (user_id, limit))

    def get_plan_by_date(self, athlete_id: int, plan_date: date) -> List[Dict]:
        """Получить план питания на конкретную дату согласно v1.7"""
        query = """
        SELECT * FROM meal_plans
        WHERE athlete_id = %s AND plan_date = %s
        ORDER BY meal_type
        """
        return self.execute_query(query, (athlete_id, plan_date))

    def get_meals_for_plan(self, plan_date: date, athlete_id: int, plan_name: str = 'Основной план') -> List[Dict]:
        """Получить приемы пищи для плана на дату с указанным названием"""
        query = """
        SELECT * FROM meal_plans
        WHERE athlete_id = %s AND plan_date = %s AND plan_name = %s
        ORDER BY meal_type
        """
        return self.execute_query(query, (athlete_id, plan_date, plan_name))
    
    def validate_competition_date(self, competition_date: date) -> bool:
        """Проверить валидность даты соревнований (≥ 7 дней от сегодня)"""
        if competition_date <= date.today() + timedelta(days=6):
            return False
        return True
    
    def validate_weight_difference(self, current_weight: float, target_weight: float) -> bool:
        """Проверить разницу весов (≤ 5%)"""
        if current_weight <= 0 or target_weight <= 0:
            return False
        
        difference = abs(current_weight - target_weight) / current_weight
        return difference <= 0.05  # 5% максимальная разница
    
    def get_athlete_id_by_telegram(self, telegram_id: int) -> Optional[int]:
        """Получить athlete_id по telegram_id"""
        query = "SELECT athlete_id FROM athletes WHERE telegram_id = %s"
        result = self.execute_query(query, (telegram_id,))
        if result and len(result) > 0:
            return result[0]['athlete_id']
        else:
            logger.warning(f"⚠️ Пользователь с telegram_id {telegram_id} не найден")
            return None

    def get_next_athlete_id(self) -> int:
        """Получить следующий athlete_id (максимальный + 1)"""
        query = "SELECT COALESCE(MAX(athlete_id), 0) + 1 as next_id FROM athletes"
        result = self.execute_query(query)
        if result and len(result) > 0:
            return result[0]['next_id']
        else:
            logger.warning("⚠️ Не удалось получить следующий athlete_id, используем 1")
            return 1

# Глобальный экземпляр базы данных
db = Database()