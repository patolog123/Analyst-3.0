# AI Diet Bot 3.0 🤖🥗

Telegram бот для создания персонализированных планов питания для спортсменов с использованием AI (DeepSeek).

## 🎯 Возможности

- 📊 Сбор антропометрических данных спортсмена
- 🏋️‍♂️ Интервью о тренировочном режиме
- 🚶‍♂️ Анализ физической активности
- 🧠 Генерация планов питания через DeepSeek AI
- 💾 Сохранение и просмотр предыдущих планов
- ✅ Валидация данных (дата соревнований, разница весов)

## 🏗️ Архитектура

### Технологический стек
- **Python 3.13+** - основной язык разработки
- **Aiogram 3.x** - фреймворк для Telegram ботов
- **PostgreSQL** - база данных
- **DeepSeek API** - генерация контента через LLM
- **Aiohttp** - асинхронные HTTP запросы

### Структура базы данных (v1.7)
```sql
athletes (спортсмены)
├── athlete_id (SERIAL PRIMARY KEY)
├── telegram_id (BIGINT UNIQUE)
├── name (VARCHAR)
├── gender (CHAR(1))
├── height (DECIMAL)
├── current_weight (DECIMAL)
├── target_weight_category (DECIMAL)
├── competition_date (DATE)
└── created_at (TIMESTAMP)

meal_plans (планы питания - объединенная таблица v1.7)
├── meal_id (SERIAL PRIMARY KEY)
├── athlete_id (FOREIGN KEY)
├── meal_type (VARCHAR) -- завтрак/обед/ужин
├── calories (INTEGER)
├── proteins (DECIMAL)
├── fats (DECIMAL)
├── carbs (DECIMAL)
├── description (TEXT)
├── plan_date (DATE)
└── created_at (TIMESTAMP)

workouts (тренировки)
├── workout_id (SERIAL PRIMARY KEY)
├── athlete_id (FOREIGN KEY)
├── sessions_per_week (INTEGER)
├── exercises (VARCHAR)
├── equipment_weight (DECIMAL)
├── reps (INTEGER)
├── sets (INTEGER)
└── created_at (TIMESTAMP)

activities (активность)
├── activity_id (SERIAL PRIMARY KEY)
├── athlete_id (FOREIGN KEY)
├── activity_type (VARCHAR)
├── duration_minutes (INTEGER)
├── frequency_per_week (INTEGER)
└── created_at (TIMESTAMP)
```

## 🚀 Установка и запуск

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd ai-diet-bot
```

### 2. Установка зависимостей
```bash
pip install -r requirements_aiogram.txt
```

### 3. Настройка окружения для Amvera
Для развертывания на Amvera используйте файл `.env` из репозитория. В панели управления Amvera установите:

**Обязательные переменные окружения:**
```env
BOT_TOKEN=your_telegram_bot_token
DEEPSEEK_API_KEY=your_deepseek_api_key
DATABASE_PASSWORD=your_postgres_password  # Пароль от базы данных Amvera PostgreSQL
```

**Опциональные настройки:**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
```

> **Важно:** URL базы данных хардкодирован в конфигурации для Amvera. Не используйте локальные настройки DB_HOST, DB_PORT, DB_NAME.

### 4. Инициализация базы данных
```bash
python init_db.py
```

### 5. Запуск бота
```bash
python main_aiogram_v3.py
```

## 📋 Sequence Diagram

Бот работает согласно следующей диаграмме последовательности:

1. **Инициализация** - команда `/start`, проверка существующего пользователя
2. **Сбор параметров** - дата соревнований, пол, рост, текущий и целевой вес
3. **Валидация** - проверка даты (≥7 дней) и разницы весов (≤5%)
4. **Интервью о тренировках** - вопросы о режиме тренировок
5. **Интервью об активности** - вопросы о физической активности
6. **Генерация плана** - создание плана питания через DeepSeek AI
7. **Просмотр плана** - навигация по дням недели
8. **Сохранение плана** - запись в базу данных

## 🔧 Конфигурация

Основные настройки в `config.py`:

- `BOT_TOKEN` - токен Telegram бота
- `DEEPSEEK_API_KEY` - ключ API DeepSeek
- Настройки базы данных PostgreSQL
- Параметры LLM (температура, максимальное количество токенов)

## 📊 Валидация данных

### Проверка даты соревнований
```python
def validate_competition_date(competition_date: date) -> bool:
    """Проверить что до соревнований ≥ 7 дней"""
    return competition_date > date.today() + timedelta(days=6)
```

### Проверка разницы весов
```python
def validate_weight_difference(current_weight: float, target_weight: float) -> bool:
    """Проверить разницу весов ≤ 5%"""
    difference = abs(current_weight - target_weight) / current_weight
    return difference <= 0.05
```

## 🤖 Команды бота

- `/start` - начать работу с ботом
- Главное меню:
  - 🎯 Создать план питания
  - 📋 Мои сохраненные планы
  - ❌ Отмена

## 🐛 Отладка

Включите debug режим в `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

Логи будут содержать подробную информацию о работе бота и запросах к API.

## 📝 Лицензия

MIT License - подробности в файле LICENSE.

## 🤝 Поддержка

Для вопросов и предложений создавайте issue в репозитории или обращайтесь к разработчикам.

---

**Версия:** 3.0
**Последнее обновление:** 2025-08-30
**Соответствует:** ai_diet_physical_model_v1.7.sql и ai_diet_sequence_diagram.plantuml
