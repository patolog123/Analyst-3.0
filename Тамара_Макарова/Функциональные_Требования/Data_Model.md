# Модель данных AI-агента SocioMind (текущая реализация)

## Таблица users (Пользователи)

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| user_id | INTEGER | PK, ID пользователя в Telegram | Primary Key |
| username | TEXT | Никнейм в Telegram | |
| personality_type | TEXT | Код типа (e.g., "INTJ", "ESFP") | |
| test_date | TEXT | Дата прохождения теста | |

## Таблица chat_messages (Сообщения чата)

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | INTEGER | PK | Auto Increment |
| chat_id | INTEGER | ID чата в Telegram | |
| user_id | INTEGER | ID пользователя | |
| message_text | TEXT | Текст сообщения | |
| timestamp | DATETIME | Время сообщения | Default = CURRENT_TIMESTAMP |

## Таблица chat_members (Участники чата)

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| chat_id | INTEGER | ID чата в Telegram | Composite PK |
| user_id | INTEGER | ID пользователя | Composite PK |
| username | TEXT | Никнейм пользователя | |
| first_name | TEXT | Имя пользователя | |
| last_name | TEXT | Фамилия пользователя | |
| first_seen | DATETIME | Первое появление | Default = CURRENT_TIMESTAMP |
| last_seen | DATETIME | Последняя активность | Default = CURRENT_TIMESTAMP |

## Таблица reports (Отчеты)

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| chat_id | INTEGER | ID чата в Telegram | Composite PK |
| report_date | DATE | Дата отчета | Composite PK |
| report_data | TEXT | Текст отчета | |

## Google Sheets Integration
**Лист "PersonalityTypes":**
- User ID | Telegram username | Тип личности | Дата тестирования

## Бизнес-правила

1. **Автоочистка данных:**
   - Сообщения чата автоматически удаляются через 7 дней
   - Очистка выполняется ежедневно

2. **Ограничения тестирования:**
   - Команда `/test` доступна только в личных сообщениях
   - В групповых чатах - перенаправление в личный чат

3. **Ограничения отчетов:**
   - Один отчет в день на чат
   - Требуется >70% протестированных участников
   - Бот должен быть администратором
