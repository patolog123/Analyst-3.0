"""
Модуль интеграции с LLM (DeepSeek) для генерации вопросов и планов питания
Согласно диаграмме последовательности AI диетолога 3.0
"""

import logging
import json
import aiohttp
import asyncio
from datetime import date, timedelta
from typing import Dict, List, Optional, Any
from config import config

logger = logging.getLogger(__name__)

class LLMIntegration:
    """Класс для работы с DeepSeek API"""
    
    def __init__(self):
        self.api_key = config.DEEPSEEK_API_KEY
        self.base_url = config.DEEPSEEK_BASE_URL
        self.model = config.DEEPSEEK_MODEL
        self.temperature = config.DEEPSEEK_TEMPERATURE
        self.max_tokens = config.DEEPSEEK_MAX_TOKENS
        # Увеличиваем timeout для генерации плана питания (сложный запрос)
        self.plan_timeout = aiohttp.ClientTimeout(total=240, connect=60, sock_connect=60, sock_read=120)  # 240 секунд для сложных запросов
    
    async def _make_request(self, messages: List[Dict], timeout: aiohttp.ClientTimeout = None) -> Optional[Dict]:
        """Выполнить запрос к DeepSeek API"""
        if not self.api_key:
            logger.error("❌ DEEPSEEK_API_KEY не установлен")
            logger.error("💡 Установите действительный API ключ через переменную окружения DEEPSEEK_API_KEY")
            return None
        
        # Проверяем базовый URL (более гибкая проверка)
        if not self.base_url:
            logger.error(f"❌ Базовый URL DeepSeek не установлен")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # Используем переданный timeout или стандартный 45 секунд
        request_timeout = timeout or aiohttp.ClientTimeout(total=45, connect=15, sock_connect=15, sock_read=30)
        
        try:
            logger.info(f"🔗 Отправка запроса к DeepSeek API: {self.base_url}")
            logger.debug(f"📝 Промпт: {messages[-1]['content'][:100]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=request_timeout
                ) as response:
                    
                    response_text = await response.text()
                    logger.debug(f"📨 Ответ DeepSeek: Status {response.status}, Body: {response_text[:200]}...")
                    
                    if response.status == 200:
                        data = await response.json()
                        logger.info("✅ Успешный ответ от DeepSeek API")
                        return data
                    else:
                        logger.error(f"❌ Ошибка DeepSeek API: {response.status}")
                        logger.error(f"📋 Тело ошибки: {response_text}")
                        
                        # Анализ распространенных ошибок
                        if response.status == 401:
                            logger.error("🔑 Ошибка 401: Неверный API ключ или ключ истек")
                        elif response.status == 429:
                            logger.error("⏰ Ошибка 429: Превышен лимит запросов")
                        elif response.status == 500:
                            logger.error("⚡ Ошибка 500: Внутренняя ошибка сервера DeepSeek")
                        elif response.status == 503:
                            logger.error("🌐 Ошибка 503: Сервис временно недоступен")
                            
                        return None
                        
        except aiohttp.ClientConnectorError as e:
            logger.error(f"❌ Ошибка соединения с DeepSeek: {e}")
            logger.error("🌐 Проверьте интернет-соединение и доступность api.deepseek.com")
            return None
        except aiohttp.ServerTimeoutError as e:
            logger.error(f"⏰ Таймаут сервера DeepSeek: {e}")
            logger.error("💡 Сервер не ответил в течение установленного времени")
            return None
        except aiohttp.ClientResponseError as e:
            logger.error(f"❌ Ошибка ответа DeepSeek: {e.status} - {e.message}")
            if e.status == 429:
                logger.error("🚫 Превышен лимит запросов. Попробуйте позже.")
            elif e.status == 401:
                logger.error("🔑 Неверный API ключ. Проверьте DEEPSEEK_API_KEY.")
            elif e.status >= 500:
                logger.error("⚡ Ошибка сервера DeepSeek. Попробуйте позже.")
            return None
        except aiohttp.ClientError as e:
            logger.error(f"🌐 Сетевая ошибка DeepSeek: {e}")
            logger.error("💡 Проверьте интернет-соединение и доступность api.deepseek.com")
            return None
        except TimeoutError as e:
            logger.error(f"⏰ Общий таймаут операции DeepSeek: {e}")
            logger.error("💡 Операция заняла слишком много времени. Увеличьте timeout или проверьте сеть.")
            return None
        except asyncio.TimeoutError as e:
            logger.error(f"⏰ Asyncio таймаут DeepSeek: {e}")
            logger.error("💡 Асинхронная операция превысила лимит времени.")
            return None
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка DeepSeek: {type(e).__name__}: {e}")
            logger.error("💡 Проверьте настройки API и корректность запроса")
            return None
    
    async def generate_training_question(self) -> str:
        """Сгенерировать первый вопрос о тренировках (количество тренировок)"""
        messages = [
            {
                "role": "system",
                "content": "Ты - AI диетолог, помогающий спортсменам готовиться к соревнованиям. "
                          "Задай естественный вопрос о количестве тренировок в неделю."
            },
            {
                "role": "user",
                "content": "Сгенерируй естественный вопрос о количестве тренировок в неделю. "
                          "Вопрос должен быть дружелюбным и побуждать к ответу."
            }
        ]
        
        response = await self._make_request(messages)
        if response and 'choices' in response and response['choices']:
            return response['choices'][0]['message']['content']
        
        # Fallback вопрос
        return "💪 Сколько тренировок в неделю ты делаешь?"
    
    async def generate_activity_question(self) -> str:
        """Сгенерировать вопрос о физической активности"""
        messages = [
            {
                "role": "system",
                "content": "Ты - AI диетолог, помогающий спортсменам готовиться к соревнованиям. "
                          "Задай естественный вопрос о физической активности спортсмена вне тренировок."
            },
            {
                "role": "user",
                "content": "Сгенерируй вопрос о физической активности спортсмена в повседневной жизни. "
                          "Вопрос должен быть естественным и побуждать к подробному ответу. "
                          "Спроси о шагах в день, характере работы, дополнительной активности и часах активности."
            }
        ]
        
        response = await self._make_request(messages)
        if response and 'choices' in response and response['choices']:
            return response['choices'][0]['message']['content']
        
        # Fallback вопрос
        return "🚶‍♂️ Опиши свою физическую активность:\n• Шаги в день\n• Характер работы\n• Дополнительная активность\n• Часы активности"
    
    async def generate_meal_plan(self, user_data: Dict) -> Dict:
        """Сгенерировать дневный план питания"""
        # Конвертируем decimal значения в float для избежания ошибок типов
        processed_data = {}
        for key, value in user_data.items():
            if hasattr(value, '__float__'):
                processed_data[key] = float(value)
            else:
                processed_data[key] = value
        
        # Формируем промпт на основе данных пользователя
        prompt = self._create_meal_plan_prompt(processed_data)
        
        messages = [
            {
                "role": "system",
                "content": "Ты - профессиональный диетолог, специализирующийся на спортивном питании. "
                          "Создай детальный дневный план питания для спортсмена на основе его данных."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = await self._make_request(messages, timeout=self.plan_timeout)
        
        if response and 'choices' in response and response['choices']:
            plan_text = response['choices'][0]['message']['content']
            return self._parse_meal_plan(plan_text, processed_data)
        
        # Fallback план
        return self._create_fallback_plan(processed_data)
    
    def _create_meal_plan_prompt(self, user_data: Dict) -> str:
        """Создать промпт для генерации плана питания"""
        return f"""
Ты - профессиональный диетолог, специализирующийся на спортивном питании.
Создай детальный дневный план питания для спортсмена на основе следующих данных:

Основные данные спортсмена:
- Пол: {user_data.get('gender', 'не указан')}
- Рост: {user_data.get('height', 0)} см
- Текущий вес: {user_data.get('current_weight', 0)} кг
- Целевой вес: {user_data.get('target_weight', 0)} кг
- Дата соревнований: {user_data.get('competition_date', 'не указана')}

ТРЕБОВАНИЯ К ПЛАНУ ПИТАНИЯ:
1. План должен быть на ОДИН день (сегодняшний день)
2. Укажи 3 основных приема пищи: завтрак, обед, ужин
3. Для каждого приема пищи укажи:
   - Подробное описание блюд (названия продуктов и их количество)
   - Калорийность (ккал)
   - Белки (г)
   - Жиры (г)
   - Углеводы (г)
4. Общая калорийность дня должна соответствовать цели спортсмена
5. Баланс БЖУ: белки 30-40%, жиры 20-30%, углеводы 30-50%
6. Учитывай разницу между текущим и целевым весом
7. План должен быть разнообразным и сбалансированным

ВАЖНО: Верни ответ ТОЛЬКО в формате JSON без дополнительного текста.

Структура JSON ответа:
{{
    "total_calories": 2500,
    "total_proteins": 180.0,
    "total_fats": 70.0,
    "total_carbs": 250.0,
    "plan_date": "2025-09-02",
    "meals": [
        {{
            "meal_type": "завтрак",
            "calories": 600,
            "proteins": 40.0,
            "fats": 20.0,
            "carbs": 70.0,
            "description": "Овсянка с ягодами и орехами, 2 вареных яйца"
        }},
        {{
            "meal_type": "обед",
            "calories": 800,
            "proteins": 60.0,
            "fats": 30.0,
            "carbs": 80.0,
            "description": "Гречка с куриной грудкой, овощной салат"
        }},
        {{
            "meal_type": "ужин",
            "calories": 600,
            "proteins": 50.0,
            "fats": 20.0,
            "carbs": 60.0,
            "description": "Творог 5% с грецкими орехами, кефир 1%"
        }}
    ]
}}
"""
    
    def _parse_meal_plan(self, plan_text: str, user_data: Dict) -> Dict:
        """Парсинг сгенерированного плана питания"""
        try:
            logger.debug(f"📝 Сырой ответ от LLM: {plan_text[:500]}...")
            
            # Пытаемся извлечь JSON из ответа
            json_str = None
            if '```json' in plan_text:
                json_str = plan_text.split('```json')[1].split('```')[0].strip()
            elif '```' in plan_text:
                json_str = plan_text.split('```')[1].split('```')[0].strip()
            else:
                # Пытаемся найти JSON в тексте
                import re
                json_match = re.search(r'\{.*\}', plan_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0).strip()
                else:
                    json_str = plan_text
            
            logger.debug(f"📋 Извлеченный JSON: {json_str[:300]}...")
            
            plan_data = json.loads(json_str)
            logger.debug(f"✅ Успешно распарсен план: {json.dumps(plan_data, indent=2, default=str)[:200]}...")
            return plan_data
            
        except (json.JSONDecodeError, IndexError, AttributeError) as e:
            logger.error(f"❌ Ошибка парсинга плана питания: {e}")
            logger.error(f"📋 Текст для парсинга: {plan_text[:200]}...")
            import traceback
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            return self._create_fallback_plan(user_data)
    
    def _create_fallback_plan(self, user_data: Dict) -> Dict:
        """Создать fallback план питания"""
        gender = user_data.get('gender', 'M')
        current_weight = float(user_data.get('current_weight', 70))
        target_weight = float(user_data.get('target_weight_category', 65))
        
        # Расчет базовой калорийности
        if gender == 'M':
            base_calories = 2500.0
        else:
            base_calories = 2000.0
        
        # Корректировка на разницу весов
        weight_diff = float(current_weight - target_weight)
        if weight_diff > 0:
            base_calories -= weight_diff * 100.0  # Дефицит для снижения веса
        else:
            base_calories += abs(weight_diff) * 100.0  # Профицит для набора веса
        
        return {
            "total_calories": int(base_calories),
            "total_proteins": round(float(base_calories) * 0.35 / 4, 1),
            "total_fats": round(float(base_calories) * 0.25 / 9, 1),
            "total_carbs": round(float(base_calories) * 0.4 / 4, 1),
            "plan_date": (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
            "meals": [
                {
                    "meal_type": "завтрак",
                    "calories": int(float(base_calories) * 0.3),
                    "proteins": round(float(base_calories) * 0.3 * 0.35 / 4, 1),
                    "fats": round(float(base_calories) * 0.3 * 0.25 / 9, 1),
                    "carbs": round(float(base_calories) * 0.3 * 0.4 / 4, 1),
                    "description": "Овсянка с ягодами и орехами, 2 вареных яйца"
                },
                {
                    "meal_type": "обед",
                    "calories": int(float(base_calories) * 0.4),
                    "proteins": round(float(base_calories) * 0.4 * 0.35 / 4, 1),
                    "fats": round(float(base_calories) * 0.4 * 0.25 / 9, 1),
                    "carbs": round(float(base_calories) * 0.4 * 0.4 / 4, 1),
                    "description": "Гречка с куриной грудкой, овощной салат"
                },
                {
                    "meal_type": "ужин",
                    "calories": int(float(base_calories) * 0.3),
                    "proteins": round(float(base_calories) * 0.3 * 0.35 / 4, 1),
                    "fats": round(float(base_calories) * 0.3 * 0.25 / 9, 1),
                    "carbs": round(float(base_calories) * 0.3 * 0.4 / 4, 1),
                    "description": "Творог 5% с грецкими орехами, кефир 1%"
                }
            ]
        }

# Глобальный экземпляр LLM интеграции
llm = LLMIntegration()