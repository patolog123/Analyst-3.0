# Модель данных AI-агента SocioMind

## Объект User (Пользователь)

**Основная сущность:** Хранит данные пользователя Telegram

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK, Уникальный идентификатор в системе | Auto Increment |
| telegram_id | BigInteger | Уникальный ID пользователя в Telegram | Not Null, Unique |
| username | String | Никнейм в Telegram (@username) | |
| first_name | String | Имя пользователя | Not Null |

## Объект PersonalityType (Тип личности)

**Справочная сущность:** Содержит описание соционических типов

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK, Уникальный идентификатор | Auto Increment |
| code | String | Код типа (e.g., "INTJ", "ESFP") | Not Null, Unique, Length=4 |
| psycho_name | String | Психологическое название (e.g., "Аналитик") | Not Null |

## Объект UserPersonality (Тип пользователя)

**Связующая сущность:** Связующая сущность: Связывает пользователя с его типом и хранит данные теста. Данные из этой сущности синхронизируются с Google Sheets

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| user_id | Integer | FK → User.id | Not Null |
| personality_type_id | Integer | FK → PersonalityType.id | Not Null |
| determined_at | DateTime | Дата и время определения типа | Default = CURRENT_TIMESTAMP |

## Объект Chat (Чат/Группа)

**Основная сущность:** Хранит данные о групповых чатах

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| telegram_chat_id | BigInteger | Уникальный ID чата в Telegram | Not Null, Unique |
| title | String | Название чата | Not Null |

## Объект ChatMember (Участник чата)

**Связующая сущность:** Отслеживает участников групп

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| chat_id | Integer | FK → Chat.id | Not Null |
| user_id | Integer | FK → User.id | Not Null |

## Объект GroupReport (Отчет по группе)

**Сущность отчетности:** Хранит сгенерированные отчеты по чатам

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| chat_id | Integer | FK → Chat.id | Not Null |
| generated_at | DateTime | Дата и время генерации отчета | Default = CURRENT_TIMESTAMP |
| report_data | JSON/Text | Данные отчета (структурированный JSON или готовый текст) | Not Null |

## Объект UserTestSession (Сессия тестирования)

**Сущность процесса:** Для хранения состояния прохождения теста

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| user_id | Integer | FK → User.id | Not Null |
| current_question_id | Integer | FK → TestQuestion.id | Текущий вопрос |
| status | String | Статус сессии ("in_progress", "completed", "expired", "cancelled") | Default = "in_progress" |

---

## Бизнес-правила (Ограничения уровня данных)

1.  **UserPersonality:**
    *   У одного пользователя (`user_id`) может быть только одна активная запись типа личности

2.  **GroupReport:**
    *   Для одного чата (`chat_id`) можно создать не более одного отчета в день (`DATE(generated_at)`)

3.  **ChatMember:**
    *   Комбинация `chat_id` и `user_id` должна быть уникальной

4.  **UserTestSession:**
    *   У пользователя может быть только одна активная сессия (`status = 'in_progress'`) в один момент времени

## Связи (Relations)

*   **User** `1 → ∞` **UserPersonality** (Один пользователь может иметь один тип личности)
*   **User** `∞ → ∞` **Chat** (через **ChatMember**) (Пользователь может состоять во многих чатах, чат имеет много пользователей)
*   **Chat** `1 → ∞` **GroupReport** (Для одного чата может быть сгенерировано много отчетов)
*   **PersonalityType** `1 → ∞` **UserPersonality** (Один тип может быть присвоен многим пользователям)