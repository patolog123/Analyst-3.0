-- SQL скрипт создания физической модели базы данных AI Diet Bot
-- Для СУБД PostgreSQL
-- Версия 1.7 (добавлено поле telegram_id)
-- Дата создания: 2025-09-01
-- Обновлено: 2025-09-04 - убрано удаление таблиц и тестовые данные

-- Создание таблицы спортсменов (только если не существует)
CREATE TABLE IF NOT EXISTS athletes (
    athlete_id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE, -- Добавлено поле для идентификации пользователей Telegram
    name VARCHAR(100) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')) NOT NULL,
    height DECIMAL(5,2) NOT NULL CHECK (height > 0),
    current_weight DECIMAL(5,2) NOT NULL CHECK (current_weight > 0),
    target_weight DECIMAL(5,2) NOT NULL CHECK (target_weight > 0),
    competition_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT weight_check CHECK (ABS(current_weight - target_weight) <= current_weight * 0.05)
);

-- Создание объединенной таблицы планов питания и приемов пищи (только если не существует)
CREATE TABLE IF NOT EXISTS meal_plans (
    meal_id SERIAL PRIMARY KEY,
    athlete_id INTEGER NOT NULL REFERENCES athletes(athlete_id) ON DELETE CASCADE,
    meal_type VARCHAR(10) NOT NULL CHECK (meal_type IN ('завтрак', 'обед', 'ужин')),
    calories INTEGER NOT NULL CHECK (calories > 0),
    proteins DECIMAL(5,2) NOT NULL CHECK (proteins >= 0),
    fats DECIMAL(5,2) NOT NULL CHECK (fats >= 0),
    carbs DECIMAL(5,2) NOT NULL CHECK (carbs >= 0),
    description TEXT,
    plan_date DATE NOT NULL,
    plan_name VARCHAR(50) DEFAULT 'Основной план',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Уникальное ограничение для предотвращения дублирования планов
    UNIQUE (athlete_id, plan_date, plan_name, meal_type)
);

-- Создание триггерной функции для проверки даты соревнований (только если не существует)
CREATE OR REPLACE FUNCTION check_competition_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.plan_date > (SELECT competition_date FROM athletes WHERE athlete_id = NEW.athlete_id) - INTERVAL '7 days' THEN
        RAISE EXCEPTION 'План должен начинаться не позднее чем за неделю до соревнований';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера (только если не существует)
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'meal_plan_date_check') THEN
        CREATE TRIGGER meal_plan_date_check
        BEFORE INSERT OR UPDATE ON meal_plans
        FOR EACH ROW EXECUTE FUNCTION check_competition_date();
    END IF;
END $$;

-- Создание таблицы тренировок (только если не существует)
CREATE TABLE IF NOT EXISTS workouts (
    workout_id SERIAL PRIMARY KEY,
    athlete_id INTEGER NOT NULL REFERENCES athletes(athlete_id) ON DELETE CASCADE,
    sessions_per_week INTEGER NOT NULL CHECK (sessions_per_week BETWEEN 1 AND 14),
    exercises VARCHAR(100) NOT NULL,
    equipment_weight DECIMAL(5,2) CHECK (equipment_weight >= 0),
    reps INTEGER CHECK (reps > 0),
    sets INTEGER CHECK (sets > 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы физической активности (только если не существует)
CREATE TABLE IF NOT EXISTS activities (
    activity_id SERIAL PRIMARY KEY,
    athlete_id INTEGER NOT NULL REFERENCES athletes(athlete_id) ON DELETE CASCADE,
    steps_per_day INTEGER CHECK (steps_per_day > 0),
    work_type VARCHAR(50),
    additional_activity VARCHAR(100),
    activity_hours DECIMAL(4,2) CHECK (activity_hours >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Сообщение об успешном выполнении скрипта
SELECT 'Физическая модель базы данных создана (версия 1.7 с telegram_id). Тестовые данные не добавлены.' AS message;