# Модель данных AI-агента SocioMind

## Объект User (Пользователь)

**Основная сущность:** Хранит данные пользователя Telegram.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK, Уникальный идентификатор в системе | Auto Increment |
| telegram_id | BigInteger | Уникальный ID пользователя в Telegram | Not Null, Unique |
| username | String | Никнейм в Telegram (@username) | |
| first_name | String | Имя пользователя | Not Null |
| created_at | DateTime | Дата и время регистрации | Default = CURRENT_TIMESTAMP |

## Объект PersonalityType (Тип личности)

**Справочная сущность:** Содержит описание соционических типов.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK, Уникальный идентификатор | Auto Increment |
| code | String | Код типа (e.g., "INTJ", "ESFP") | Not Null, Unique, Length=4 |
| psycho_name | String | Психологическое название (e.g., "Аналитик") | Not Null |
| socio_name | String | Соционическое название (e.g., "Робеспьер") | Not Null |
| full_name | String | Полное описание (e.g., "Логико-интуитивный интроверт") | Not Null |
| description | Text | Развернутое описание типа | |
| strengths | Text | Сильные стороны типа | |
| weaknesses | Text | Зоны развития типа | |

## Объект UserPersonality (Тип пользователя)

**Связующая сущность:** Связывает пользователя с его типом и хранит данные теста.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| user_id | Integer | FK → User.id | Not Null |
| personality_type_id | Integer | FK → PersonalityType.id | Not Null |
| determined_at | DateTime | Дата и время определения типа | Default = CURRENT_TIMESTAMP |
| test_answers | JSON/Text | JSON-структура или текст с ответами пользователя на вопросы теста | |
| is_active | Boolean | Актуальность данного типирования | Default = True |

## Объект Chat (Чат/Группа)

**Основная сущность:** Хранит данные о групповых чатах.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| telegram_chat_id | BigInteger | Уникальный ID чата в Telegram | Not Null, Unique |
| title | String | Название чата | Not Null |
| type | String | Тип чата ("group", "supergroup") | Not Null |
| bot_is_admin | Boolean | Является ли бот администратором | Default = False |
| created_at | DateTime | Дата добавления чата в систему | Default = CURRENT_TIMESTAMP |

## Объект ChatMember (Участник чата)

**Связующая сущность:** Отслеживает участников групп и их статус.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| chat_id | Integer | FK → Chat.id | Not Null |
| user_id | Integer | FK → User.id | Not Null |
| first_detected | DateTime | Когда пользователь был впервые обнаружен в чате | Default = CURRENT_TIMESTAMP |
| last_checked | DateTime | Когда статус пользователя проверялся в последний раз | Default = CURRENT_TIMESTAMP |
| is_member | Boolean | Является ли пользователь участником на данный момент | Default = True |

## Объект GroupReport (Отчет по группе)

**Сущность отчетности:** Хранит сгенерированные отчеты по чатам.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| chat_id | Integer | FK → Chat.id | Not Null |
| generated_at | DateTime | Дата и время генерации отчета | Default = CURRENT_TIMESTAMP |
| period_start | Date | Начало анализируемого периода (e.g., 2025-08-01) | |
| period_end | Date | Конец анализируемого периода (e.g., 2025-08-07) | |
| report_data | JSON/Text | Данные отчета (структурированный JSON или готовый текст) | Not Null |
| message_id | Integer | ID сообщения с отчетом в Telegram (для избежания дублирования) | |

## Объект TestQuestion (Вопрос теста)

**Справочная сущность:** Вопросы для тестирования.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| number | Integer | Порядковый номер вопроса | Not Null, Unique |
| text | Text | Текст вопроса | Not Null |
| socio_function | String | Соционическая функция, которую оценивает вопрос (e.g., "Базовая") | Not Null |

## Объект UserTestSession (Сессия тестирования)

**Сущность процесса:** Для хранения состояния прохождения теста.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| user_id | Integer | FK → User.id | Not Null |
| current_question_id | Integer | FK → TestQuestion.id | Текущий вопрос |
| answers | JSON | JSON с сохраненными ответами {question_id: "answer"} | |
| started_at | DateTime | Время начала теста | Default = CURRENT_TIMESTAMP |
| expires_at | DateTime | Время, когда сессия станет неактивной (started_at + 5 мин на вопрос * 10) | |
| status | String | Статус сессии ("in_progress", "completed", "expired", "cancelled") | Default = "in_progress" |

---

## Бизнес-правила (Ограничения уровня данных)

1.  **UserPersonality:**
    *   У одного пользователя (`user_id`) может быть только одна запись с `is_active = True`.
    *   `determined_at` не может быть раньше, чем `User.created_at`.

2.  **GroupReport:**
    *   Для одного чата (`chat_id`) можно создать не более одного отчета в день (`generated_at::date`).
    *   `period_end` не может быть больше текущей даты.

3.  **ChatMember:**
    *   Комбинация `chat_id` и `user_id` должна быть уникальной.

4.  **UserTestSession:**
    *   У пользователя может быть только одна активная сессия (`status = 'in_progress'`) в один момент времени.
    *   `expires_at` вычисляется автоматически при создании.

## Связи (Relations)

*   **User** `1 → ∞` **UserPersonality** (Один пользователь может иметь несколько типирований, но только одно активное)
*   **User** `1 → ∞` **UserTestSession** (Один пользователь может иметь несколько сессий тестирования)
*   **User** `∞ → ∞` **Chat** (через **ChatMember**) (Пользователь может состоять во многих чатах, чат имеет много пользователей)
*   **Chat** `1 → ∞` **GroupReport** (Для одного чата может быть сгенерировано много отчетов)
*   **PersonalityType** `1 → ∞` **UserPersonality** (Один тип может быть присвоен многим пользователям)