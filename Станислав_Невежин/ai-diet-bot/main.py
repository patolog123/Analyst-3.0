#!/usr/bin/env python3
"""
Главный исполняемый файл AI Diet Bot 3.0
Объединяет функциональность бота, инициализацию базы данных и HTTP API сервер
"""

import asyncio
import logging
import sys
import os
import json
import aiohttp
import signal
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple

from api_server import APIServer, start_api_server

from aiogram import Bot, Dispatcher, F, Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import config
from database import db
from llm_integration import llm

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

# Глобальные переменные для хранения данных интервью
user_interview_data = {}

# Состояния FSM согласно диаграмме последовательности
class Form(StatesGroup):
    main_menu = State()
    collecting_name = State()
    collecting_competition_date = State()
    collecting_gender = State()
    collecting_height = State()
    collecting_current_weight = State()
    collecting_target_weight = State()
    training_sessions = State()
    training_exercises = State()
    training_weight = State()
    training_reps = State()
    training_sets = State()
    activity_steps = State()
    activity_work_type = State()
    activity_extra = State()
    activity_hours = State()
    viewing_plan = State()
    viewing_saved_plans = State()
    finish_session = State()

# Функции инициализации базы данных
def execute_sql_file():
    """Выполнение SQL скрипта через psycopg2"""
    
    sql_file = 'ai_diet_physical_model_v1.7.sql'
    
    try:
        # Читаем содержимое SQL файла
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        logger.info(f"📖 Чтение SQL файла: {sql_file}")
        
        # Используем более умное разделение команд, учитывающее многострочные конструкции
        # Разделяем по точкам с запятой, но сохраняем конструкции с $$
        commands = []
        current_command = ""
        in_dollar_quote = False
        
        for line in sql_content.split('\n'):
            stripped_line = line.strip()
            
            # Проверяем начало/конец блока с $$
            if '$$' in stripped_line:
                in_dollar_quote = not in_dollar_quote
            
            current_command += line + '\n'
            
            # Если не внутри блока $$ и есть точка с запятой в конце строки
            if not in_dollar_quote and stripped_line.endswith(';'):
                commands.append(current_command.strip())
                current_command = ""
        
        # Добавляем последнюю команду, если она есть
        if current_command.strip():
            commands.append(current_command.strip())
        
        # Выполняем каждую команду
        for i, command in enumerate(commands):
            command = command.strip()
            if command:  # Пропускаем пустые команды
                logger.info(f"⚡ Выполнение команды {i+1}: {command.split()[0] if command.split() else 'unknown'}...")
                db.execute_query(command)
        
        logger.info("✅ SQL скрипт успешно выполнен")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении SQL скрипта: {e}")
        return False

def initialize_database():
    """Инициализация базы данных"""
    logger.info("🚀 Запуск инициализации базы данных...")
    
    # Проверяем существование SQL файла
    sql_file = 'ai_diet_physical_model_v1.7.sql'
    if not os.path.exists(sql_file):
        logger.error(f"❌ SQL файл {sql_file} не найден!")
        return False
    
    logger.info(f"✅ SQL файл найден: {sql_file}")
    
    try:
        # Подключаемся к базе данных
        db.connect()
        logger.info("✅ Подключение к базе данных установлено")
        
        # Выполняем SQL скрипт
        if execute_sql_file():
            logger.info("🎉 Инициализация базы данных завершена успешно!")
            logger.info("📋 База данных создана с правильным уникальным ограничением:")
            logger.info("   UNIQUE (athlete_id, plan_date, plan_name, meal_type)")
            return True
        else:
            logger.error("❌ Инициализация базы данных завершена с ошибками")
            return False
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при инициализации: {e}")
        return False
        
    finally:
        # Закрываем соединение с базой данных
        db.close()
        logger.info("✅ Соединение с базой данных закрыто")

def check_database_tables():
    """Проверить существование таблиц в базе данных"""
    try:
        db.connect()
        
        # Проверяем существование основных таблиц
        tables_to_check = ['athletes', 'meal_plans', 'workouts', 'activities']
        
        for table in tables_to_check:
            check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table}'
            );
            """
            result = db.execute_query(check_query)
            if not result or not result[0]['exists']:
                logger.warning(f"⚠️ Таблица {table} не существует")
                return False
        
        logger.info("✅ Все необходимые таблицы существуют в базе данных")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке таблиц: {e}")
        return False
        
    finally:
        db.close()


# Вспомогательные функции для клавиатур
def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура главного меню согласно диаграмме"""
    buttons = [
        [InlineKeyboardButton(text="🎯 Составить план", callback_data="create_plan")],
        [InlineKeyboardButton(text="📋 Сохраненные планы", callback_data="saved_plans")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def view_plan_keyboard(plan_id: int, day_number: int) -> InlineKeyboardMarkup:
    """Клавиатура для просмотра плана питания с навигацией по дням"""
    total_days = 7
    
    buttons = []
    
    # Кнопки навигации по дням
    nav_buttons = []
    if day_number > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Предыдущий", callback_data=f"day_{plan_id}_{day_number-1}"))
    
    nav_buttons.append(InlineKeyboardButton(text=f"День {day_number}", callback_data=f"day_{plan_id}_{day_number}"))
    
    if day_number < total_days:
        nav_buttons.append(InlineKeyboardButton(text="Следующий ➡️", callback_data=f"day_{plan_id}_{day_number+1}"))
    
    buttons.append(nav_buttons)
    
    # Кнопки действий
    action_buttons = [
        InlineKeyboardButton(text="💾 Сохранить план", callback_data=f"save_plan_{plan_id}"),
        InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu"),
        InlineKeyboardButton(text="✅ Завершить просмотр плана", callback_data="finish_session")
    ]
    buttons.append(action_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def view_generated_plan_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для просмотра сгенерированного плана согласно диаграмме (только 2 кнопки)"""
    buttons = [
        [InlineKeyboardButton(text="✅ Завершить просмотр плана", callback_data="finish_session")],
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Обработчики команд бота
@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик команды /start согласно диаграмме последовательности"""
    user = message.from_user
    logger.info(f"👤 Пользователь {user.id} начал работу с ботом")
    
    # Проверяем, есть ли пользователь в базе согласно диаграмме
    existing_user = db.get_user(user.id)
    
    if existing_user:
        welcome_text = (
            f"С возвращением, {user.first_name}! 🏋️‍♂️\n\n"
            "Готовы продолжить работу над вашим питанием?"
        )
        await message.answer(welcome_text, reply_markup=main_menu_keyboard())
        await state.set_state(Form.main_menu)
    else:
        welcome_text = (
            f"Привет! 👋\n\n"
            "Я - AI диетолог 3.0, твой персональный помощник в создании "
            "идеального плана питания для подготовки к соревнованиям! 🥇\n\n"
            "Для начала, давай познакомимся поближе. Ответь на несколько вопросов о себе:"
        )
        await message.answer(welcome_text)
        await message.answer("👤 Как тебя зовут? (укажи свое имя)")
        await state.set_state(Form.collecting_name)

@dp.message(Form.collecting_name)
async def collect_name_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора имени пользователя"""
    user = message.from_user
    name = message.text.strip()
    
    if not name or len(name) < 2:
        await message.answer("❌ Имя должно содержать хотя бы 2 символа. Пожалуйста, введи свое имя:")
        return
    
    await state.update_data(name=name)
    await message.answer("📅 Когда у тебя соревнования? (в формате ДД.ММ.ГГГГ)")
    await state.set_state(Form.collecting_competition_date)

@dp.message(Form.collecting_competition_date)
async def collect_competition_date_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора даты соревнований"""
    user = message.from_user
    
    try:
        comp_date = datetime.strptime(message.text, '%d.%m.%Y').date()
        
        # Валидация даты соревнований согласно диаграмме
        if not db.validate_competition_date(comp_date):
            await message.answer(
                "❌ Ошибка: До начала соревнований должно оставаться не меньше недели.\n"
                "💡 Рекомендую выступить на следующих соревнованиях!\n\n"
                "Пожалуйста, укажи другую дату:"
            )
            return
        
        await state.update_data(competition_date=comp_date)
        await message.answer("👫 Укажи свой пол (М/Ж):")
        await state.set_state(Form.collecting_gender)
        
    except ValueError:
        await message.answer("❌ Неверный формат даты. Пожалуйста, используй формат ДД.ММ.ГГГГ:")

@dp.message(Form.collecting_gender)
async def collect_gender_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора пола пользователя"""
    gender = message.text.upper()
    
    if gender in ['М', 'M', 'МУЖ', 'МУЖСКОЙ']:
        await state.update_data(gender='M')
        await message.answer("📏 Какой у тебя рост (в см)?")
        await state.set_state(Form.collecting_height)
    elif gender in ['Ж', 'F', 'ЖЕН', 'ЖЕНСКИЙ']:
        await state.update_data(gender='F')
        await message.answer("📏 Какой у тебя рост (в см)?")
        await state.set_state(Form.collecting_height)
    else:
        await message.answer("❌ Неверный формат данных. Пожалуйста, укажи свой пол (М/Ж):")

@dp.message(Form.collecting_height)
async def collect_height_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора роста пользователя"""
    try:
        height = float(message.text.replace(',', '.'))
        if 100 <= height <= 250:
            await state.update_data(height=height)
            await message.answer("⚖️ Какой у тебя текущий вес (в кг)?")
            await state.set_state(Form.collecting_current_weight)
        else:
            await message.answer("❌ Рост должен быть от 100 до 250 см. Пожалуйста, проверь введенные значения:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи рост числом (в см):")

@dp.message(Form.collecting_current_weight)
async def collect_current_weight_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора текущего веса пользователя"""
    try:
        current_weight = float(message.text.replace(',', '.'))
        if 30 <= current_weight <= 200:
            await state.update_data(current_weight=current_weight)
            await message.answer("🎯 Какой у тебя целевой вес (в кг)?")
            await state.set_state(Form.collecting_target_weight)
        else:
            await message.answer("❌ Вес должен быть от 30 до 200 кг. Пожалуйста, проверь введенные значения:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи вес числом (в кг):")

@dp.message(Form.collecting_target_weight)
async def collect_target_weight_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора целевого веса пользователя"""
    try:
        target_weight = float(message.text.replace(',', '.'))
        user_data = await state.get_data()
        current_weight = user_data.get('current_weight')
        
        # Валидация разницы весов согласно диаграмме
        if not db.validate_weight_difference(current_weight, target_weight):
            await message.answer(
                "❌ Ошибка: Разница между текуным и целевым весом не должна превышать 5%.\n"
                "Пожалуйста, укажи реалистичный целевой вес:"
            )
            return
        
        await state.update_data(target_weight=target_weight)
        await finish_parameter_collection(message, state, message.from_user)
        
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи вес числом (в кг):")

async def finish_parameter_collection(message: types.Message, state: FSMContext, user: types.User) -> None:
    """Завершение сбора параметров и сохранение пользователя согласно диаграмме"""
    user_data = await state.get_data()
    
    # Формируем имя пользователя
    name = f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
    
    # Сохраняем пользователя в базу
    user_data['telegram_id'] = user.id
    user_data['name'] = name
    
    try:
        athlete_id = db.create_user(user_data)
        
        if athlete_id is None:
            logger.error(f"❌ Не удалось сохранить пользователя {user.id}: athlete_id = None")
            await message.answer(
                "❌ Произошла ошибка при сохранении данных. Попробуй позже или обратись в поддержку."
            )
            await state.clear()
    
        logger.info(f"✅ Пользователь {user.id} сохранен с athlete_id {athlete_id}")
        
        await message.answer(
            "✅ Параметры сохранены! Переходим к вопросам о тренировок 🏋️‍♂️",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Начать интервью 💪", callback_data="start_interview")
            ]])
        )
        
        await state.set_state(Form.main_menu)
        
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения пользователя: {e}")
        import traceback
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        await message.answer(
            "❌ Произошла ошибка при сохранении данных. Попробуй позже или обратись в поддержку."
        )
        await state.clear()

# Обработчики callback запросов
@dp.callback_query(F.data == "start_interview")
async def start_interview_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик начала интервью о тренировках согласно диаграмме"""
    await callback.answer()
    user = callback.from_user
    
    # Задаем первый фиксированный вопрос о тренировках согласно диаграмме
    await callback.message.edit_text("💪 Опиши свой режим тренировок. Какое количество тренировок у тебя в неделю (укажи числом)?")
    await state.set_state(Form.training_sessions)

# Обработчики состояний тренировок и активности
@dp.message(Form.training_sessions)
async def training_sessions_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о количестве тренировок"""
    user = message.from_user
    answer = message.text
    
    try:
        # Валидация: должно быть число от 1 до 14
        sessions = int(answer)
        if 1 <= sessions <= 14:
            await state.update_data(sessions_per_week=sessions)
            await message.answer("🏋️‍♂️ Какие упражнения ты делаешь на тренировках?")
            await state.set_state(Form.training_exercises)
        else:
            await message.answer("❌ Количество тренировок должно быть от 1 до 14 в неделю. Пожалуйста, укажи корректное число:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи количество тренировок числом:")

@dp.message(Form.training_exercises)
async def training_exercises_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа об упражнениях"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем упражнения
    await state.update_data(exercises=answer)
    await message.answer("⚖️ Какой вес снарядов ты используешь (в кг)?")
    await state.set_state(Form.training_weight)

@dp.message(Form.training_weight)
async def training_weight_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о весе снарядов"""
    user = message.from_user
    answer = message.text
    
    try:
        # Валидация: вес должен быть положительным числом
        weight = float(answer.replace(',', '.'))
        if weight > 0:
            await state.update_data(equipment_weight=weight)
            await message.answer("🔄 Сколько повторов ты делаешь (укажи числом)?")
            await state.set_state(Form.training_reps)
        else:
            await message.answer("❌ Вес снарядов должен быть положительным числом. Пожалуйста, укажи корректное значение:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи вес числом (в кг):")

@dp.message(Form.training_reps)
async def training_reps_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о повторениях"""
    user = message.from_user
    answer = message.text
    
    try:
        # Валидация: повторения должны быть положительным целым числом
        reps = int(answer)
        if reps > 0:
            await state.update_data(reps=reps)
            await message.answer("🔄 Сколько подходов ты делаешь (укажи числом)?")
            await state.set_state(Form.training_sets)
        else:
            await message.answer("❌ Количество повторений должно быть положительным числом. Пожалуйста, укажи корректное значение:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи количество повторений целым числом:")

@dp.message(Form.training_sets)
async def training_sets_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о подходах"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем все данные о тренировках
    user_data = await state.get_data()
    athlete_id = db.get_athlete_id_by_telegram(user.id)
    
    if athlete_id:
        workout_data = {
            'sessions_per_week': user_data.get('sessions_per_week', ''),
            'exercises': user_data.get('exercises', ''),
            'equipment_weight': user_data.get('equipment_weight', ''),
            'reps': user_data.get('reps', ''),
            'sets': answer
        }
        logger.info(f"💾 Сохранение данных тренировок для athlete_id {athlete_id}: {workout_data}")
        try:
            workout_id = db.save_workout_info(athlete_id, workout_data)
            if workout_id:
                logger.info(f"✅ Данные тренировок сохранены с workout_id {workout_id}")
            else:
                logger.error("❌ Не удалось сохранить данные тренировок (workout_id = None)")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения тренировок: {e}")
            import traceback
            logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
    
    # Переходим к вопросам о физической активности согласно диаграмме
    await message.answer("✅ Данные о тренировках сохранены! Переходим к вопросам о физической активности!")
    await message.answer("🚶‍♂️ Сколько шагов в день ты делаешь (укажи числом)?")
    await state.set_state(Form.activity_steps)

@dp.message(Form.activity_steps)
async def activity_steps_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о количестве шагов"""
    user = message.from_user
    answer = message.text
    
    try:
        # Валидация: шаги должны быть положительным целым числом
        steps = int(answer)
        if steps >= 0:
            await state.update_data(steps_per_day=steps)
            await message.answer("💼 Характер работы (сидячая, подвижная)?")
            await state.set_state(Form.activity_work_type)
        else:
            await message.answer("❌ Количество шагов не может быть отрицательным. Пожалуйста, укажи корректное значение:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи количество шагов целым числом:")

@dp.message(Form.activity_work_type)
async def activity_work_type_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о характере работы"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем характер работы
    await state.update_data(work_type=answer)
    await message.answer("🏊‍♂️ Дополнительная активность - плавание, бег, велосипед (укажи текстом один вариант)?")
    await state.set_state(Form.activity_extra)

@dp.message(Form.activity_extra)
async def activity_extra_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о дополнительной активности"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем дополнительную активность
    await state.update_data(extra_activity=answer)
    await message.answer("⏰ Сколько часов в неделю занимает дополнительная активность (укажи числом)?")
    await state.set_state(Form.activity_hours)

@dp.message(Form.activity_hours)
async def activity_hours_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о часах активности"""
    user = message.from_user
    answer = message.text
    
    try:
        # Валидация: часы активности должны быть положительным числом
        hours = float(answer.replace(',', '.'))
        if hours >= 0:
            # Сохраняем все данные о физической активности согласно v1.7
            user_data = await state.get_data()
            athlete_id = db.get_athlete_id_by_telegram(user.id)

            if athlete_id:
                activity_data = {
                    'steps_per_day': user_data.get('steps_per_day'),
                    'work_type': user_data.get('work_type'),
                    'additional_activity': user_data.get('extra_activity'),
                    'activity_hours': hours
                }
                logger.info(f"💾 Сохранение данных активности для athlete_id {athlete_id}: {activity_data}")
                try:
                    activity_id = db.save_activity_info(athlete_id, activity_data)
                    if activity_id:
                        logger.info(f"✅ Данные активности сохранены с activity_id {activity_id}")
                    else:
                        logger.error("❌ Не удалось сохранить данные активности (activity_id = None)")
                except Exception as e:
                    logger.error(f"❌ Ошибка сохранения активности: {e}")
                    import traceback
                    logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
            
            # Генерируем план питания согласно диаграмме
            await message.answer("✅ Все данные сохранены! Начинаем генерацию плана питания 🍽️")
            
            try:
                # Получаем данные пользователя
                athlete_id = db.get_athlete_id_by_telegram(user.id)
                user_data = db.get_user(user.id)
                
                # Проверяем наличие всех необходимых данных
                required_fields = ['gender', 'height', 'current_weight', 'target_weight', 'competition_date']
                missing_fields = [field for field in required_fields if not user_data.get(field)]
                
                if missing_fields:
                    logger.error(f"❌ Отсутствуют обязательные поля: {missing_fields}")
                    await message.answer(
                        "❌ Недостаточно данных для генерации плана. Пожалуйста, начни заново с /start",
                        reply_markup=main_menu_keyboard()
                    )
                    await state.set_state(Form.main_menu)
                    return
                
                # Генерируем план через LLM
                logger.info(f"🔄 Генерация плана питания для пользователя {user.id}")
                meal_plan = await llm.generate_meal_plan(user_data)
                
                if not meal_plan:
                    logger.error("❌ LLM вернул пустой план питания")
                    # Согласно диаграмме: обработка ошибки генерации плана
                    await message.answer(
                        "❌ Произошла ошибка при генерации плана питания. Попробуй позже или обратись в поддержку.",
                        reply_markup=main_menu_keyboard()
                    )
                    await state.set_state(Form.main_menu)
                    return
                
                # Согласно диаграмме: проверка на ошибку сохранения плана
                if 'error' in meal_plan:
                    logger.error(f"❌ Ошибка генерации плана: {meal_plan.get('error')}")
                    await message.answer(
                        "❌ Произошла ошибка при генерации плана питания. Попробуй позже или обратись в поддержку.",
                        reply_markup=main_menu_keyboard()
                    )
                    await state.set_state(Form.main_menu)
                    return
                
                # Временно отключаем проверку для отладки
                logger.debug(f"📋 Полученный план от LLM: {json.dumps(meal_plan, indent=2, default=str)}")
                
                # Проверяем наличие необходимых данных в плане
                if 'meals' not in meal_plan or not meal_plan['meals']:
                    logger.error("❌ План питания не содержит приемов пищи")
                    logger.error(f"📊 Структура плана: {list(meal_plan.keys())}")
                    # Временно используем fallback план для отладки
                    fallback_plan = llm._create_fallback_plan(user_data)
                    logger.info("🔄 Используем fallback план")
                    meal_plan = fallback_plan
                
                # Генерируем уникальное название для плана согласно требованиям
                # План должен быть на следующий день после генерации
                from datetime import datetime, timedelta
                plan_date = datetime.now().date() + timedelta(days=1)
                plan_name = f"План на {plan_date.strftime('%d.%m.%Y')}"
                
                # Сохраняем план в базу с названием
                try:
                    logger.info(f"💾 Попытка сохранения плана питания для athlete_id {athlete_id}")
                    logger.debug(f"📋 Данные плана: {json.dumps(meal_plan, indent=2, default=str)}")
                    
                    # Добавляем название плана в данные плана
                    meal_plan['plan_name'] = plan_name
                    plan_id = db.save_meal_plan(athlete_id, meal_plan)
                    
                    if plan_id is not None:
                        logger.info(f"✅ План питания сохранен с plan_id {plan_id}, названием: {plan_name}")
                        
                        # Согласно диаграмме: отправляем сообщение о готовности с кнопками
                        await message.answer(
                            "🎉 План питания готов! Выбери действие:",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="📋 Просмотреть план", callback_data=f"view_plan_{plan_id}")],
                                [InlineKeyboardButton(text="🏠 Вернуться в главное меню", callback_data="back_to_menu")]
                            ])
                        )
                        await state.set_state(Form.viewing_plan)
                        logger.info(f"✅ План питания успешно создан и сохранен (ID: {plan_id}, название: {plan_name})")
                    else:
                        logger.error("❌ Не удалось сохранить план питания в базу данных (plan_id = None)")
                        await message.answer(
                            "❌ Ошибка сохранения плана питания. Попробуй позже или обратись в поддержку.",
                            reply_markup=main_menu_keyboard()
                        )
                        await state.set_state(Form.main_menu)
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка сохранения плана в базу: {type(e).__name__}: {e}")
                    import traceback
                    logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
                    await message.answer(
                        "❌ Ошибка сохранения плана питания. Попробуй позже или обратись в поддержку.",
                        reply_markup=main_menu_keyboard()
                    )
                    await state.set_state(Form.main_menu)
                
            except Exception as e:
                logger.error(f"❌ Ошибка генерации плана: {type(e).__name__}: {e}")
                await message.answer(
                    "❌ Ошибка генерации плана питания. Проверьте настройки API ключа DeepSeek и попробуйте позже.",
                    reply_markup=main_menu_keyboard()
                )
                await state.set_state(Form.main_menu)
        else:
            await message.answer("❌ Количество часов активности не может быть отрицательным. Пожалуйста, укажи корректное значение:")
    except ValueError:
        await message.answer("❌ Неверный формат данных. Пожалуйста, введи количество часов числом:")

# Обработчики callback запросов главного меню
@dp.callback_query(F.data == "create_plan", Form.main_menu)
async def create_plan_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик создания плана питания согласно диаграмме"""
    await callback.answer()
    await callback.message.edit_text(
        "🔍 Для создания идеального плана питания мне нужно узнать немного больше о твоих тренировках.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Начать интервью 🏋️‍♂️", callback_data="start_interview")
        ]])
    )

@dp.callback_query(F.data == "saved_plans", Form.main_menu)
async def saved_plans_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик просмотра сохраненных планов согласно диаграмме"""
    await callback.answer()
    user = callback.from_user
    logger.info(f"📋 Запрос сохраненных планов для пользователя {user.id}")
    
    try:
        plans = db.get_user_plans(user.id)
        logger.info(f"📊 Получено планов: {len(plans)}")
        logger.debug(f"📋 Данные планов: {plans}")
        
        if plans:
            buttons = []
            for plan in plans[:10]:  # Увеличиваем лимит для отображения нескольких планов на день
                plan_date = plan['plan_date'].strftime('%d.%m.%Y')
                plan_name = plan.get('plan_name', 'Без названия')
                buttons.append([InlineKeyboardButton(
                    text=f"{plan_name} ({plan['total_calories']} ккал)",
                    callback_data=f"view_saved_plan_{plan['plan_date']}_{plan_name}"
                )])
            buttons.append([InlineKeyboardButton(text="← Назад", callback_data="back_to_menu")])
            
            await callback.message.edit_text(
                "📅 Твои сохраненные планы питания:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
            )
            await state.set_state(Form.viewing_saved_plans)
        else:
            logger.info("📭 У пользователя нет сохраненных планов")
            await callback.message.edit_text(
                "📭 У тебя пока нет сохраненных планов питания. Создай первый план!",
                reply_markup=main_menu_keyboard()
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка получения сохраненных планов: {e}")
        import traceback
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        await callback.message.edit_text(
            "❌ Ошибка загрузки планов. Попробуй позже или обратись в поддержку.",
            reply_markup=main_menu_keyboard()
        )

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик возврата в главное меню"""
    try:
        await callback.answer()
        await callback.message.edit_text(
            "Главное меню 🏠\n\nВыбери действие:",
            reply_markup=main_menu_keyboard()
        )
        await state.set_state(Form.main_menu)
    except Exception as e:
        # Игнорируем ошибки устаревших callback запросов
        if "query is too old" in str(e) or "query ID is invalid" in str(e):
            logger.warning(f"⚠️ Игнорируем устаревший callback запрос: {e}")
        else:
            logger.error(f"❌ Ошибка обработки back_to_menu: {e}")
            raise

@dp.callback_query(F.data.startswith("view_plan_"))
async def view_plan_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик просмотра сгенерированного плана согласно диаграмме"""
    await callback.answer()
    plan_id = int(callback.data.split('_')[2])  # view_plan_{plan_id}
    user = callback.from_user
    
    try:
        # Получаем информацию о плане из базы данных
        plan_info = db.execute_query(
            "SELECT plan_date, plan_name FROM meal_plans WHERE meal_id = %s LIMIT 1",
            (plan_id,)
        )
        
        if plan_info:
            plan_date = plan_info[0]['plan_date']
            plan_name = plan_info[0].get('plan_name', 'Без названия')
            athlete_id = db.get_athlete_id_by_telegram(user.id)
            
            if athlete_id:
                # Получаем детали плана для отображения с учетом названия
                meals = db.get_meals_for_plan(plan_date, athlete_id, plan_name)
                
                if not meals:
                    await callback.message.answer("❌ План питания не найден")
                    return
                
                # Формируем сообщение с планом - только название плана, без дублирования даты
                plan_text = f"📋 {plan_name}"
                plan_text += ":\n\n"
                
                total_calories = 0
                total_proteins = 0
                total_fats = 0
                total_carbs = 0
                
                for meal in meals:
                    plan_text += f"🍽 {meal['meal_type'].capitalize()}: {meal['description']}\n"
                    plan_text += f"   📊 {meal['calories']} ккал (Б:{meal['proteins']}г, Ж:{meal['fats']}г, У:{meal['carbs']}г)\n\n"
                    
                    total_calories += meal['calories']
                    total_proteins += meal['proteins']
                    total_fats += meal['fats']
                    total_carbs += meal['carbs']
                
                plan_text += f"📈 Итого за день: {total_calories} ккал "
                plan_text += f"(Б:{total_proteins:.1f}г, Ж:{total_fats:.1f}г, У:{total_carbs:.1f}г)"
                
                # Отправляем план с клавиатурой из 2 кнопок согласно диаграмме
                await callback.message.answer(plan_text, reply_markup=view_generated_plan_keyboard())
                await state.set_state(Form.viewing_plan)
            else:
                await callback.message.answer("❌ Ошибка: Пользователь не найден")
        else:
            await callback.message.answer("❌ План не найден")
            
    except (ValueError, IndexError) as e:
        logger.error(f"❌ Ошибка обработки callback view_plan: {e}")
        await callback.message.answer("❌ Ошибка: Неверный формат данных плана")

@dp.callback_query(F.data.startswith("view_saved_plan_"))
async def handle_view_saved_plan(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик просмотра конкретного плана согласно диаграмме"""
    await callback.answer()
    # view_saved_plan_YYYY-MM-DD_plan_name
    parts = callback.data.split('_')
    plan_date_str = parts[3]
    plan_name = '_'.join(parts[4:]) if len(parts) > 4 else 'Без названия'
    
    user = callback.from_user
    
    try:
        # Парсим дату из строки формата YYYY-MM-DD
        plan_date = datetime.strptime(plan_date_str, '%Y-%m-%d').date()
        logger.info(f"📅 Запрос плана на дату: {plan_date}, название: {plan_name}")
        
        athlete_id = db.get_athlete_id_by_telegram(user.id)
        logger.info(f"👤 Athlete ID пользователя {user.id}: {athlete_id}")
        
        if athlete_id:
            # Получаем детали плана для отображения с учетом названия
            meals = db.get_meals_for_plan(plan_date, athlete_id, plan_name)
            logger.info(f"🍽 Получено приемов пищи: {len(meals)}")
            logger.debug(f"📋 Данные приемов пищи: {meals}")
            
            if not meals:
                logger.warning(f"⚠️ План питания не найден для даты {plan_date}, названия {plan_name}")
                await callback.message.answer("❌ План питания не найден")
                return
            
            # Формируем сообщение с планом - только название плана
            plan_text = f"📋 {plan_name}"
            plan_text += ":\n\n"
            
            total_calories = 0
            total_proteins = 0
            total_fats = 0
            total_carbs = 0
            
            for meal in meals:
                plan_text += f"🍽 {meal['meal_type'].capitalize()}: {meal['description']}\n"
                plan_text += f"   📊 {meal['calories']} ккал (Б:{meal['proteins']}г, Ж:{meal['fats']}г, У:{meal['carbs']}г)\n\n"
                
                total_calories += meal['calories']
                total_proteins += meal['proteins']
                total_fats += meal['fats']
                total_carbs += meal['carbs']
            
            plan_text += f"📈 Итого за день: {total_calories} ккал "
            plan_text += f"(Б:{total_proteins:.1f}г, Ж:{total_fats:.1f}г, У:{total_carbs:.1f}г)"
            
            # Отправляем план с клавиатура из 2 кнопок согласно диаграмме
            await callback.message.answer(plan_text, reply_markup=view_generated_plan_keyboard())
            await state.set_state(Form.viewing_plan)
            logger.info(f"✅ План успешно отображен для пользователя {user.id}")
        else:
            logger.error(f"❌ Athlete ID не найден для пользователя {user.id}")
            await callback.message.answer("❌ Ошибка: Пользователь не найден")
            
    except ValueError:
        logger.error(f"❌ Неверный формат даты плана: {plan_date_str}")
        await callback.message.answer("❌ Ошибка: Неверный формат даты плана")
    except Exception as e:
        logger.error(f"❌ Ошибка при получении плана: {e}")
        import traceback
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        await callback.message.answer(
            "❌ Ошибка загрузки плана. Попробуй позже или обратись в поддержку."
        )

@dp.callback_query(F.data == "finish_session")
async def finish_session_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик завершения сессии согласно диаграмме"""
    await callback.answer()
    user = callback.from_user
    logger.info(f"🏁 Пользователь {user.id} завершил сессию")
    
    # Очищаем временные данные сессии согласно диаграмме
    await state.clear()
    user_interview_data.pop(user.id, None)
    
    # Отправляем сообщение о завершении сессии
    await callback.message.edit_text(
        "🏁 Сессия завершена. Удачи на соревнованиях! 🏆\n\n"
        "Если понадобится новая консультация - напиши /start",
        reply_markup=None
    )

# Основная функция запуска
async def main() -> None:
    """Главная функция запуска бота и API сервера"""
    logger.info("🚀 Запуск AI Diet Bot 3.0 с HTTP API...")
    
    # Проверяем и инициализируем базу данных
    if not check_database_tables():
        logger.info("🔄 База данных не инициализирована, запускаем инициализацию...")
        if not initialize_database():
            logger.error("❌ Не удалось инициализировать базу данных")
            return
    
    # Запускаем API сервер в фоновой задаче
    api_task = asyncio.create_task(start_api_server())
    logger.info("🌐 HTTP API сервер запущен в фоновом режиме")
    
    # Принудительно удаляем вебхук ПЕРЕД запуском бота
    logger.info("🔄 Принудительное удаление вебхука...")
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info(f"✅ Вебхук успешно удален (попытка {attempt + 1})")
            break
        except Exception as e:
            logger.warning(f"⚠️ Не удалось удалить вебхук (попытка {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                logger.error("❌ Все попытки удалить вебхук провалились")
    
    # Дополнительная проверка статуса вебхука
    try:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url:
            logger.warning(f"⚠️ ВНИМАНИЕ: Вебхук все еще активен: {webhook_info.url}")
            logger.warning("🔄 Пытаемся удалить вебхук еще раз...")
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info("✅ Вебхук окончательно удален после дополнительной проверки")
        else:
            logger.info("✅ Вебхук не активен, можно запускать polling")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось проверить статус вебхука: {e}")
    
    # Запускаем бота
    try:
        logger.info("🤖 Запуск polling режима бота...")
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("🤖 Polling остановлен по сигналу")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        import traceback
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
    finally:
        # Отменяем API задачу при завершении
        api_task.cancel()
        try:
            await api_task
        except asyncio.CancelledError:
            logger.info("🌐 HTTP API сервер остановлен")
        await bot.session.close()

async def run_main():
    """Запуск основной функции с обработкой сигналов"""
    # Создаем основную задачу
    main_task = asyncio.create_task(main())
    
    # Настраиваем обработку сигналов
    loop = asyncio.get_running_loop()
    
    # Обработчик для SIGTERM
    def handle_sigterm():
        logger.info("📋 Получен SIGTERM сигнал, начинаем graceful shutdown...")
        main_task.cancel()
    
    # Обработчик для SIGINT (Ctrl+C)
    def handle_sigint():
        logger.info("📋 Получен SIGINT сигнал, начинаем graceful shutdown...")
        main_task.cancel()
    
    # Регистрируем обработчики сигналов
    try:
        loop.add_signal_handler(signal.SIGTERM, handle_sigterm)
        loop.add_signal_handler(signal.Signal.SIGTERM, handle_sigterm)  # Для Windows
    except (AttributeError, NotImplementedError):
        logger.warning("⚠️ SIGTERM обработка не поддерживается на этой платформе")
    
    try:
        loop.add_signal_handler(signal.SIGINT, handle_sigint)
        loop.add_signal_handler(signal.Signal.SIGINT, handle_sigint)  # Для Windows
    except (AttributeError, NotImplementedError):
        logger.warning("⚠️ SIGINT обработка не поддерживается на этой платформе")
    
    # Ожидаем завершения основной задачи
    try:
        await main_task
    except asyncio.CancelledError:
        logger.info("✅ Graceful shutdown завершен")
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка в main: {e}")
        raise

# Функции для работы с YAML и тестирования
def open_yaml_file():
    """Открытие и проверка YAML файла спецификации"""
    yaml_file = 'ai_diet_api.yaml'
    try:
        if os.path.exists(yaml_file):
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"✅ YAML файл найден: {yaml_file}")
                logger.info(f"📄 Размер файла: {len(content)} символов")
                
                # Проверяем основные элементы спецификации
                has_info = "info:" in content
                has_paths = "paths:" in content
                has_components = "components:" in content
                
                logger.info(f"📋 Структура YAML: info={has_info}, paths={has_paths}, components={has_components}")
                
                if has_info and has_paths:
                    logger.info("🎯 YAML файл корректно структурирован")
                    return True
                else:
                    logger.warning("⚠️ YAML файл может быть неполным или поврежденным")
                    return False
        else:
            logger.error(f"❌ YAML файл не найден: {yaml_file}")
            return False
    except Exception as e:
        logger.error(f"❌ Ошибка чтения YAML файла: {e}")
        return False

async def test_all_endpoints():
    """Тестирование всех эндпоинтов API сервера"""
    logger.info("🧪 Запуск тестирования всех эндпоинтов API...")
    
    # Явный импорт aiohttp внутри функции для гарантии доступности
    try:
        import aiohttp
        logger.info(f"✅ Модуль aiohttp успешно импортирован, версия: {aiohttp.__version__}")
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта aiohttp: {e}")
        logger.error("📦 Проверьте, что aiohttp установлен: pip install aiohttp")
        
        # Попробуем проверить доступные модули
        import sys
        logger.info(f"📦 Доступные модули: {sorted(sys.modules.keys())}")
        return False
    
    # Используем единый telegram_id для всех тестов
    test_telegram_id = 999888777
    
    endpoints = [
        ("GET", "/health"),
        ("GET", "/api/swagger/"),
        ("GET", "/api/swagger.yaml"),
        ("POST", "/api/users"),
        ("GET", f"/api/users/{test_telegram_id}"),
        ("POST", "/api/meal-plans"),
        ("GET", f"/api/meal-plans?telegram_id={test_telegram_id}")
    ]
    
    results = []
    base_url = config.API_BASE_URL
    logger.info(f"🌐 Тестирование эндпоинтов на базовом URL: {base_url}")
    logger.info(f"🔧 Конфигурация API_BASE_URL: {config.API_BASE_URL}")
    logger.info(f"🔧 Конфигурация HOST: {config.HOST}")
    logger.info(f"🔧 Конфигурация PORT: {config.PORT}")
    
    # Проверяем, совпадает ли base_url с ожидаемым URL Amvera
    expected_amvera_url = "https://ai-diet-bot-snevezhin.amvera.io"
    if base_url != expected_amvera_url:
        logger.warning(f"⚠️ ВНИМАНИЕ: base_url ({base_url}) не совпадает с ожидаемым Amvera URL ({expected_amvera_url})")
        logger.warning("⚠️ Тестирование может идти на неправильный сервер!")
        logger.warning("⚠️ Проверьте переменные окружения API_BASE_URL")
    
    # Переменная для хранения созданного athlete_id
    created_athlete_id = None
    # Дата плана питания: сегодня + 1 день
    from datetime import datetime, timedelta
    plan_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    for method, endpoint in endpoints:
        try:
            full_url = f"{base_url}{endpoint}"
            logger.info(f"🔍 Тестирование: {method} {full_url}")
            
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(full_url) as response:
                        status = response.status
                        response_text = await response.text()
                        logger.info(f"{method} {endpoint}: {status} - Response: {response_text[:200]}")
                        results.append((method, endpoint, status, status < 500))
                elif method == "POST" and endpoint == "/api/users":
                    # Получаем следующий athlete_id из базы данных
                    db.connect()
                    next_athlete_id = db.get_next_athlete_id()
                    db.close()
                    
                    user_data = {
                        "telegram_id": test_telegram_id,
                        "name": "Тест Эндпоинт",
                        "gender": "M",
                        "height": 175,
                        "current_weight": 70,
                        "target_weight": 68,
                        "competition_date": "2025-09-29"
                    }
                    async with session.post(
                        full_url,
                        json=user_data,
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        status = response.status
                        response_text = await response.text()
                        logger.info(f"{method} {endpoint}: {status} - Response: {response_text[:200]}")
                        
                        # Сохраняем athlete_id из ответа для использования в последующих запросах
                        if status == 201:
                            try:
                                response_data = await response.json()
                                created_athlete_id = response_data.get('athlete_id')
                                logger.info(f"✅ Создан пользователь с athlete_id: {created_athlete_id}")
                            except:
                                logger.warning("⚠️ Не удалось получить athlete_id из ответа")
                        
                        results.append((method, endpoint, status, status in [201, 409]))
                elif method == "POST" and endpoint == "/api/meal-plans":
                    if created_athlete_id is None:
                        logger.warning("⚠️ athlete_id не создан, пропускаем тест POST /api/meal-plans")
                        results.append((method, endpoint, 0, False))
                        continue
                    
                    # Используем athlete_id созданного пользователя
                    async with session.post(
                        full_url,
                        json={
                            "telegram_id": test_telegram_id,
                            "athlete_id": created_athlete_id,
                            "plan_date": plan_date,
                            "plan_name": f"Тестовый план на {plan_date}"
                        },
                        headers={'Content-Type': 'application/json'}
                    ) as response:
                        status = response.status
                        response_text = await response.text()
                        logger.info(f"{method} {endpoint}: {status} - Response: {response_text[:200]}")
                        results.append((method, endpoint, status, status < 500))
        except Exception as e:
            # Детальное логирование ошибки для отладки
            logger.error(f"❌ Ошибка тестирования {method} {endpoint}: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"🔍 Трассировка ошибки: {traceback.format_exc()}")
            results.append((method, endpoint, 0, False))
        
        await asyncio.sleep(0.5)
    
    # Вывод результатов
    logger.info("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ ЭНДПОИНТОВ:")
    logger.info("=" * 50)
    
    successful_tests = sum(1 for _, _, _, success in results if success)
    total_tests = len(results)
    
    for method, endpoint, status, success in results:
        status_icon = "✅" if success else "❌"
        logger.info(f"{status_icon} {method} {endpoint}: {status}")
    
    logger.info("=" * 50)
    logger.info(f"Итого: {successful_tests}/{total_tests} эндпоинтов работают")
    
    return successful_tests == total_tests

async def run_with_features():
    """Запуск с дополнительными функциями: YAML проверка и тестирование эндпоинтов"""
    logger.info("🚀 Запуск AI Diet Bot с дополнительными функциями...")
    
    # 1. Проверяем YAML файл
    logger.info("📄 Проверка YAML файла спецификации...")
    yaml_ok = open_yaml_file()
    
    if not yaml_ok:
        logger.warning("⚠️ Проблемы с YAML файлом, но продолжаем запуск")
    
    # 2. Запускаем основной сервер и бота
    main_task = asyncio.create_task(run_main())
    
    # 3. После запуска сервера тестируем эндпоинты
    await asyncio.sleep(3)  # Даем серверу время на запуск
    
    logger.info("🔍 Тестирование эндпоинтов после запуска сервера...")
    endpoints_ok = await test_all_endpoints()
    
    if endpoints_ok:
        logger.info("🎉 Все эндпоинты работают корректно!")
    else:
        logger.warning("⚠️ Некоторые эндпоинты могут иметь проблемы")
    
    # Ждем завершения основной задачи
    try:
        await main_task
    except asyncio.CancelledError:
        logger.info("✅ Приложение завершено")

if __name__ == "__main__":
    import signal
    try:
        # Проверяем, запущен ли на Amvera
        is_amvera = "amvera.io" in config.API_BASE_URL
        if is_amvera:
            logger.info(f"🌐 Запуск на Amvera: {config.API_BASE_URL}")
            logger.info("📋 Доступные функции:")
            logger.info("   - Основной бот AI Diet Bot")
            logger.info("   - HTTP API сервер")
            logger.info("   - Swagger документация")
            logger.info("   - OpenAPI YAML спецификация")
            logger.info("   - Автоматическое тестирование эндпоинтов")
        
        # Запускаем с дополнительными функциями
        asyncio.run(run_with_features())
        
        # После завершения основного запуска, если на Amvera, запускаем тестирование эндпоинтов
        if is_amvera:
            logger.info("🔍 Запуск тестирования эндпоинтов после основного сервера...")
            # Тестирование эндпоинтов осуществляется только в main.py
            test_result = asyncio.run(test_all_endpoints())
            if test_result:
                logger.info("🎉 Все эндпоинты API работают корректно на Amvera!")
            else:
                logger.warning("⚠️ Некоторые эндпоинты требуют внимания на Amvera")
        
    except KeyboardInterrupt:
        logger.info("✅ Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        logger.error(f"🔍 Трассировка: {traceback.format_exc()}")
        sys.exit(1)