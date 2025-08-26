# Модель данных AI-агента Dota 2 Predictor

## Объект User (Пользователь Telegram)

**Основная сущность:** Хранит данные пользователей бота.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK, Уникальный идентификатор в системе | Auto Increment |
| telegram_id | BigInteger | Уникальный ID пользователя в Telegram | Not Null, Unique |
| username | String | Никнейм в Telegram (@username) | |
| first_name | String | Имя пользователя | Not Null |
| language_code | String | Язык пользователя (например, 'ru', 'en') | Default = 'en' |
| created_at | DateTime | Дата и время регистрации | Default = CURRENT_TIMESTAMP |
| last_activity | DateTime | Дата и время последнего запроса | Default = CURRENT_TIMESTAMP |
| request_count | Integer | Количество сделанных запросов | Default = 0 |

## Объект Team (Команда)

**Справочная сущность:** Хранит данные о командах Dota 2.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK, Уникальный идентификатор | Auto Increment |
| opendota_id | Integer | ID команды в OpenDota API | Unique |
| name | String | Официальное название команды | Not Null |
| tag | String | Тег команды (сокращение) | |
| matches_played | Integer | Количество сыгранных матчей | Default = 0 |
| wins | Integer | Количество побед | Default = 0 |
| losses | Integer | Количество поражений | Default = 0 |
| last_updated | DateTime | Дата последнего обновления данных | Default = CURRENT_TIMESTAMP |
| is_active | Boolean | Активна ли команда в текущем мета | Default = True |

## Объект Player (Игрок)

**Справочная сущность:** Хранит данные об игроках команд.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| opendota_id | Integer | ID игрока в OpenDota API | Unique |
| nickname | String | Никнейм игрока | Not Null |
| real_name | String | Реальное имя игрока | |
| team_id | Integer | FK → Team.id | Текущая команда |
| position | String | Позиция (1-5) | |
| last_updated | DateTime | Дата последнего обновления данных | Default = CURRENT_TIMESTAMP |

## Объект Patch (Патч Dota 2)

**Справочная сущность:** Информация о версиях игры.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| version | String | Версия патча (например, '7.35b') | Not Null, Unique |
| release_date | Date | Дата выхода патча | Not Null |
| end_date | Date | Дата окончания действия патча | |
| is_current | Boolean | Актуальный ли патч | Default = True |
| meta_description | Text | Описание мета-тенденций патча | |

## Объект Hero (Герой)

**Справочная сущность:** Данные о героях Dota 2.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| opendota_id | Integer | ID героя в OpenDota API | Unique |
| name | String | Локализованное имя героя | Not Null |
| roles | JSON | Роли героя (в JSON массиве) | |
| win_rate_patch | Decimal | Win rate героя в текущем патче | |

## Объект Match (Матч)

**Основная сущность:** Информация о матчах для анализа.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| opendota_id | BigInteger | ID матча в OpenDota API | Unique |
| radiant_team_id | Integer | FK → Team.id | Команда света |
| dire_team_id | Integer | FK → Team.id | Команда тьмы |
| patch_id | Integer | FK → Patch.id | Версия патча |
| start_time | DateTime | Время начала матча | |
| duration | Integer | Длительность матча в секундах | |
| radiant_win | Boolean | Победа сил света | |
| league_id | Integer | ID лиги/турнира | |
| league_name | String | Название лиги/турнира | |
| series_type | Integer | Тип серии (BO1, BO3, etc.) | |
| fetched_at | DateTime | Когда данные матча были получены | Default = CURRENT_TIMESTAMP |

## Объект Prediction (Прогноз)

**Основная сущность:** Хранит сделанные прогнозы.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| user_id | Integer | FK → User.id | Пользователь, запросивший прогноз | Not Null |
| team_a_id | Integer | FK → Team.id | Первая команда | Not Null |
| team_b_id | Integer | FK → Team.id | Вторая команда | Not Null |
| match_id  | Integer | FK → Match.id| Ссылка на матч, для которого сделан прогноз | Nullable |
| predicted_winner_id | Integer | FK → Team.id | Предсказанный победитель | |
| confidence_a | Decimal | Уверенность в победе команды A (0-1) | Not Null |
| confidence_b | Decimal | Уверенность в победе команды B (0-1) | Not Null |
| prediction_data | JSON | Сырые данные для прогноза (win rates, встречи и т.д.) | Not Null |
| llm_explanation | Text | Текст объяснения от LLM | |
| llm_model | String | Модель LLM, использованная для генерации | |
| created_at | DateTime | Дата и время создания прогноза | Default = CURRENT_TIMESTAMP |
| is_correct | Boolean | Был ли прогноз верным (заполняется post-factum) | |
| actual_winner_id | Integer | FK → Team.id | Фактический победитель (если матч уже состоялся) | |

## Объект TeamMatchStats (Статистика команды в матче)

**Связующая сущность:** Детальная статистика команд в матчах.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| match_id | Integer | FK → Match.id | Not Null |
| team_id | Integer | FK → Team.id | Not Null |
| is_radiant | Boolean | Играла ли команда за Radiant | Not Null |
| heroes | JSON | Массив ID героев команды | |
| bans | JSON | Массив ID забаненных героев | |
| kills | Integer | Количество убийств | |
| deaths | Integer | Количество смертей | |
| assists | Integer | Количество assists | |
| net_worth | Integer | Общая net worth команды | |
| experience | Integer | Общий опыт команды | |
| first_blood | Boolean | Забрала ли команда first blood | |

## Объект TeamPatchStats (Статистика команды в патче)

**Агрегированная сущность:** Статистика команд по патчам.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| team_id | Integer | FK → Team.id | Not Null |
| patch_id | Integer | FK → Patch.id | Not Null |
| matches_played | Integer | Количество матчей | Default = 0 |
| wins | Integer | Количество побед | Default = 0 |
| win_rate | Decimal | Процент побед | |
| favorite_heroes | JSON | Чаще всего выбираемые герои | |
| ban_rate | Decimal | Процент банов против команды | |
| average_match_duration | Integer | Средняя длительность матчей | |
| updated_at | DateTime | Дата последнего обновления | Default = CURRENT_TIMESTAMP |

## Объект HeadToHead (Личные встречи)

**Агрегированная сущность:** Статистика личных встреч между командами.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| team_a_id | Integer | FK → Team.id | Not Null |
| team_b_id | Integer | FK → Team.id | Not Null |
| total_matches | Integer | Всего матчей между командами | Default = 0 |
| team_a_wins | Integer | Победы первой команды | Default = 0 |
| team_b_wins | Integer | Победы второй команды | Default = 0 |
| last_meeting_date | DateTime | Дата последней встречи | |
| streak | Integer | Текущая серия побед (положительная для team_a, отрицательная для team_b) | Default = 0 |
| updated_at | DateTime | Дата последнего обновления | Default = CURRENT_TIMESTAMP |

## Объект APILog (Лог API запросов)

**Сущность мониторинга:** Для отслеживания запросов к внешним API.

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| id | Integer | PK | Auto Increment |
| api_name | String | Название API (OpenDota, OpenAI и т.д.) | Not Null |
| endpoint | String | Конечная точка API | Not Null |
| request_data | JSON | Данные запроса | |
| response_status | Integer | HTTP статус ответа | |
| response_data | JSON | Данные ответа (усеченные) | |
| response_time_ms | Integer | Время ответа в миллисекундах | |
| timestamp | DateTime | Время запроса | Default = CURRENT_TIMESTAMP |
| success | Boolean | Успешен ли запрос | Not Null |

---

## Бизнес-правила (Ограничения уровня данных)

1.  **Prediction:**
    *   `confidence_a + confidence_b = 1.0`
    *   `team_a_id != team_b_id`
    *   Один пользователь не может делать более 5 прогнозов в минуту (проверка по `user_id` и `created_at`)

2.  **TeamPatchStats:**
    *   `win_rate` вычисляется как `wins / matches_played`
    *   Комбинация `team_id` и `patch_id` должна быть уникальной

3.  **HeadToHead:**
    *   Комбинация `team_a_id` и `team_b_id` должна быть уникальной (с учетом порядка)
    *   `team_a_wins + team_b_wins <= total_matches`

4.  **Team:**
    *   `matches_played >= wins + losses`
    *   Команда должна иметь минимум 10 матчей для включения в прогнозы (`matches_played >= 10`)

5.  **User:**
    *   `request_count` сбрасывается через определенные интервалы (реализуется на уровне приложения)

## Связи (Relations)

*   **User** `1 → ∞` **Prediction** (Один пользователь может запросить много прогнозов)
*   **Team** `1 → ∞` **Prediction** (as team_a) (Команда может участвовать во многих прогнозах как team_a)
*   **Team** `1 → ∞` **Prediction** (as team_b) (Команда может участвовать во многих прогнозах как team_b)
*   **Team** `1 → ∞` **Player** (Одна команда может иметь много игроков)
*   **Team** `1 → ∞` **TeamPatchStats** (Одна команда имеет статистику по многим патчам)
*   **Team** `∞ → ∞` **Team** (через **HeadToHead**) (Команды имеют истории встреч друг с другом)
*   **Patch** `1 → ∞` **TeamPatchStats** (Один патч содержит статистику многих команд)
*   **Patch** `1 → ∞` **Match** (В одном патче сыграно много матчей)
*   **Match** `1 → 2` **TeamMatchStats** (Один матч имеет две записи статистики - по команде)
*   **Prediction** `0..1 → 1` **Match** (Прогноз может быть связан с фактическим матчем post-factum)


