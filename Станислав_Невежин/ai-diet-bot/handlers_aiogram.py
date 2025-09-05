"""
Обработчики команд и состояний для Telegram бота AI диетолога с aiogram 3.x
Реализует всю логику согласно Sequence Diagram v1.4
"""

import logging
import json
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import CommandStart

from config import config
from database import db
from llm_integration import llm

logger = logging.getLogger(__name__)

# Состояния FSM согласно диаграмме последовательности
class Form(StatesGroup):
    main_menu = State()
    collecting_name = State()  # Добавлено состояние для сбора имени
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

# Глобальные переменные для хранения данных интервью
user_interview_data = {}

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

async def collect_target_weight_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик сбора целевого веса пользователя"""
    try:
        target_weight = float(message.text.replace(',', '.'))
        user_data = await state.get_data()
        current_weight = user_data.get('current_weight')
        
        # Валидация разницы весов согласно диаграмме
        if not db.validate_weight_difference(current_weight, target_weight):
            await message.answer(
                "❌ Ошибка: Разница между текущим и целевым весом не должна превышать 5%.\n"
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
            return
            
        logger.info(f"✅ Пользователь {user.id} сохранен с athlete_id {athlete_id}")
        
        await message.answer(
            "✅ Параметры сохранены! Переходим к вопросам о тренировках 🏋️‍♂️",
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

async def start_interview_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик начала интервью о тренировках согласно диаграмме"""
    await callback.answer()
    user = callback.from_user
    
    # Задаем первый фиксированный вопрос о тренировках согласно диаграмме
    await callback.message.edit_text("💪 Опиши свой режим тренировок. Какое количество тренировок у тебя в неделю (укажи числом)?")
    await state.set_state(Form.training_sessions)

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

async def training_exercises_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа об упражнениях"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем упражнения
    await state.update_data(exercises=answer)
    await message.answer("⚖️ Какой вес снарядов ты используешь (в кг)?")
    await state.set_state(Form.training_weight)

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

async def activity_work_type_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о характере работы"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем характер работы
    await state.update_data(work_type=answer)
    await message.answer("🏊‍♂️ Дополнительная активность - плавание, бег, велосипед (укажи текстом один вариант)?")
    await state.set_state(Form.activity_extra)

async def activity_extra_handler(message: types.Message, state: FSMContext) -> None:
    """Обработчик ответа о дополнительной активности"""
    user = message.from_user
    answer = message.text
    
    # Сохраняем дополнительную активность
    await state.update_data(extra_activity=answer)
    await message.answer("⏰ Сколько часов в неделю занимает дополнительная активность (укажи числом)?")
    await state.set_state(Form.activity_hours)

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

async def show_plan(message: types.Message, athlete_id: int, plan_date: date, day_number: int, plan_name: str = 'Без названия') -> None:
    """Показать план питания на выбранный день согласно v1.7"""
    meals = db.get_meals_for_plan(plan_date, athlete_id, plan_name)
    
    if not meals:
        await message.answer("План питания не найден.")
        return
    
    # Формируем сообщение с планом
    day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    day_name = day_names[min(day_number - 1, 6)]
    
    plan_text = f"📋 {day_name} ({plan_date.strftime('%d.%m.%Y')})"
    if plan_name != 'Без названия':
        plan_text += f" - {plan_name}"
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
    
    await message.answer(plan_text, reply_markup=view_plan_keyboard(athlete_id, day_number))

async def create_plan_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик создания плана питания согласно диаграмме"""
    await callback.answer()
    await callback.message.edit_text(
        "🔍 Для создания идеального плана питания мне нужно узнать немного больше о твоих тренировках.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Начать интервью 🏋️‍♂️", callback_data="start_interview")
        ]])
    )

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

async def cancel_handler(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик отмены"""
    try:
        await callback.answer()
        user = callback.from_user
        logger.info(f"❌ Пользователь {user.id} отменил операцию")
        
        # Очищаем временные данные
        await state.clear()
        user_interview_data.pop(user.id, None)
        
        await callback.message.edit_text(
            "Операция отменена. Если захочешь начать заново - напиши /start",
            reply_markup=main_menu_keyboard()
        )
    except Exception as e:
        # Игнорируем ошибки устаревших callback запросов
        if "query is too old" in str(e) or "query ID is invalid" in str(e):
            logger.warning(f"⚠️ Игнорируем устаревший callback запрос: {e}")
        else:
            logger.error(f"❌ Ошибка обработки cancel: {e}")
            raise

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

# Функция для регистрации обработчиков
def register_handlers(dp: Dispatcher) -> None:
    """Регистрация всех обработчиков для aiogram 3.x"""
    dp.message.register(start_handler, CommandStart())
    # Новые обработчики сбора параметров
    dp.message.register(collect_name_handler, Form.collecting_name)
    dp.message.register(collect_competition_date_handler, Form.collecting_competition_date)
    dp.message.register(collect_gender_handler, Form.collecting_gender)
    dp.message.register(collect_height_handler, Form.collecting_height)
    dp.message.register(collect_current_weight_handler, Form.collecting_current_weight)
    dp.message.register(collect_target_weight_handler, Form.collecting_target_weight)
    # Обработчики тренировок и активности
    dp.message.register(training_sessions_handler, Form.training_sessions)
    dp.message.register(training_exercises_handler, Form.training_exercises)
    dp.message.register(training_weight_handler, Form.training_weight)
    dp.message.register(training_reps_handler, Form.training_reps)
    dp.message.register(training_sets_handler, Form.training_sets)
    dp.message.register(activity_steps_handler, Form.activity_steps)
    dp.message.register(activity_work_type_handler, Form.activity_work_type)
    dp.message.register(activity_extra_handler, Form.activity_extra)
    dp.message.register(activity_hours_handler, Form.activity_hours)
    
    dp.callback_query.register(create_plan_handler, F.data == "create_plan", Form.main_menu)
    dp.callback_query.register(saved_plans_handler, F.data == "saved_plans", Form.main_menu)
    dp.callback_query.register(back_to_menu_handler, F.data == "back_to_menu")
    dp.callback_query.register(cancel_handler, F.data == "cancel")
    dp.callback_query.register(start_interview_handler, F.data == "start_interview")
    
    # Обработчики для навигации по планам согласно диаграмме
    dp.callback_query.register(lambda callback, state: handle_day_navigation(callback, state), F.data.startswith("day_"))
    dp.callback_query.register(lambda callback, state: handle_save_plan(callback, state), F.data.startswith("save_plan_"))
    dp.callback_query.register(handle_view_saved_plan, F.data.startswith("view_saved_plan_"))
    dp.callback_query.register(view_plan_handler, F.data.startswith("view_plan_"))
    dp.callback_query.register(finish_session_handler, F.data == "finish_session")

async def handle_day_navigation(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик навигации по дням плана"""
    await callback.answer()
    data = callback.data.split('_')
    plan_id = int(data[1])
    day_number = int(data[2])
    
    # Получаем athlete_id пользователя
    user = callback.from_user
    athlete_id = db.get_athlete_id_by_telegram(user.id)
    
    if athlete_id:
        # Получаем дату и название плана из базы данных
        plan_info = db.execute_query(
            "SELECT plan_date, plan_name FROM meal_plans WHERE meal_id = %s LIMIT 1",
            (plan_id,)
        )
        if plan_info:
            plan_date = plan_info[0]['plan_date']
            plan_name = plan_info[0].get('plan_name', 'Без названия')
            await show_plan(callback.message, athlete_id, plan_date, day_number, plan_name)
        else:
            await callback.message.answer("❌ План не найден")
    else:
        await callback.message.answer("❌ Пользователь не найден")

async def handle_save_plan(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Обработчик сохранения плана"""
    await callback.answer()
    await callback.message.answer("✅ План успешно сохранен!", reply_markup=main_menu_keyboard())
    await state.set_state(Form.main_menu)

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