## Объект users (Пользователь)

**Основная сущность:** Хранит данные пользователя Telegram

| Атрибут             | Тип          | Описание                                    | Ограничения                     |
|---------------------|--------------|---------------------------------------------|---------------------------------|
| id                  | Integer      | Уникальный идентификатор в системе           | Primary Key, Auto Increment     |
| telegram_id         | BigInteger   | Уникальный ID пользователя в Telegram       | Not Null, Unique                |
| username            | String(255)  | Никнейм в Telegram                          |                                 |
| full_name           | String(255)  | Полное имя пользователя                     |                                 |
| specialization      | String(100)  | Специализация пользователя                  | e.g., 'история языка', 'синтаксис' |
| subscription_tier   | String(50)   | Уровень подписки                            | Default = 'basic' (basic, premium) |
| created_at          | DateTime     | Дата и время создания записи                | Default = CURRENT_TIMESTAMP     |
| last_active         | DateTime     | Дата и время последней активности           |                                 |

## Объект queries (Запрос)

**Основная сущность:** Хранит историю запросов пользователей для анализа текста

| Атрибут            | Тип          | Описание                                    | Ограничения                     |
|--------------------|--------------|---------------------------------------------|---------------------------------|
| id                 | Integer      | Уникальный идентификатор запроса            | Primary Key, Auto Increment     |
| user_id            | Integer      | FK → users.id                               | Not Null                        |
| original_text      | Text         | Исходный текст запроса                      | Not Null (e.g., "зеленеть")     |
| processed_text     | Text         | Нормализованная версия текста               |                                 |
| type               | String(50)   | Тип запроса                                 | Not Null ('word', 'sentence', 'phrase') |
| analysis_mode      | String(50)   | Режим анализа                               | Not Null ('quick', 'full_analysis', 'etymology_only') |
| parameters         | JSON         | Параметры анализа                           |                                 |
| created_at         | DateTime     | Дата и время создания запроса               | Default = CURRENT_TIMESTAMP     |

## Объект analyses (Анализ)

**Основная сущность:** Хранит результаты анализа запросов

| Атрибут                   | Тип          | Описание                                    | Ограничения                     |
|---------------------------|--------------|---------------------------------------------|---------------------------------|
| id                        | Integer      | Уникальный идентификатор анализа            | Primary Key, Auto Increment     |
| query_id                  | Integer      | FK → queries.id                             | Not Null, Unique                |
| morphological_analysis     | JSON         | Морфологический анализ                      | e.g., { "token": "зеленеть", "pos": "глагол", ... } |
| etymological_analysis     | JSON         | Этимологический анализ                      | e.g., { "origin": "праслав. *zeleněti", ... } |
| syntactic_analysis        | JSON         | Синтаксический анализ                       | Для предложений                 |
| stylistic_recommendations  | Text         | Стилистические рекомендации                 |                                 |
| confidence_score          | Float        | Уровень уверенности анализа                 | e.g., 0.9 (90% уверенности)     |
| generated_report          | Text         | Полный текст отчета для пользователя        |                                 |
| created_at                | DateTime     | Дата и время создания анализа               | Default = CURRENT_TIMESTAMP     |

## Объект analysis_conflicts (Конфликты анализа)

**Связующая сущность:** Хранит альтернативные интерпретации и конфликты анализа

| Атрибут            | Тип          | Описание                                    | Ограничения                     |
|--------------------|--------------|---------------------------------------------|---------------------------------|
| id                 | Integer      | Уникальный идентификатор конфликта          | Primary Key, Auto Increment     |
| analysis_id        | Integer      | FK → analyses.id                            | Not Null                        |
| conflicting_field  | String(100)  | Поле с конфликтом                           | 'etymology', 'morphology'       |
| alternative_value  | JSON         | Альтернативное значение                     | Not Null                        |
| source             | String(255)  | Источник альтернативной интерпретации       | e.g., 'Исправный словарь X', 'Гипотеза пользователя Y' |
| resolved           | Boolean      | Статус разрешения конфликта                 | Default = false                 |

## Объект exports (Экспорт)

**Сущность отчетности:** Хранит результаты экспортированного анализа

| Атрибут            | Тип          | Описание                                    | Ограничения                     |
|--------------------|--------------|---------------------------------------------|---------------------------------|
| id                 | Integer      | Уникальный идентификатор экспорта           | Primary Key, Auto Increment     |
| analysis_id        | Integer      | FK → analyses.id                            | Not Null                        |
| user_id            | Integer      | FK → users.id                               | Not Null                        |
| format             | String(10)   | Формат экспорта                             | Not Null ('json', 'pdf')        |
| file_id            | String(255)  | ID файла в Telegram                         |                                 |
| storage_path       | Text         | Путь в файловом хранилище                   | e.g., S3, локально              |
| created_at         | DateTime     | Дата и время создания экспорта              | Default = CURRENT_TIMESTAMP     |

## Объект user_hypotheses (Гипотезы пользователей)

**Сущность краудсорсинга:** Хранит гипотезы пользователей для анализа слов

| Атрибут            | Тип          | Описание                                    | Ограничения                     |
|--------------------|--------------|---------------------------------------------|---------------------------------|
| id                 | Integer      | Уникальный идентификатор гипотезы           | Primary Key, Auto Increment     |
| user_id            | Integer      | FK → users.id                               | Not Null                        |
| word               | String(255)  | Слово, к которому относится гипотеза        | Not Null                        |
| hypothesis_text    | Text         | Текст гипотезы                              | Not Null                        |
| status             | String(50)   | Статус гипотезы                             | Default = 'pending' (pending, accepted, rejected) |
| reviewed_by        | Integer      | FK → users.id                               | Модератор (админ)               |
| created_at         | DateTime     | Дата и время создания гипотезы              | Default = CURRENT_TIMESTAMP     |

---

## Бизнес-правила (Ограничения уровня данных)

1. **queries**:
   * Каждый запрос (`id`) связан с одним пользователем (`user_id`).
   * Поле `original_text` не может быть пустым.

2. **analyses**:
   * Каждый анализ (`id`) соответствует ровно одному запросу (`query_id`) (1:1 отношение).
   * Поле `query_id` уникально.

3. **analysis_conflicts**:
   * Конфликт (`id`) связан с одним анализом (`analysis_id`).
   * Поле `alternative_value` не может быть пустым.

4. **exports**:
   * Экспорт (`id`) связан с одним анализом (`analysis_id`) и пользователем (`user_id`).
   * Поле `format` обязательно и ограничено значениями 'json' или 'pdf'.

5. **user_hypotheses**:
   * Гипотеза (`id`) связана с одним пользователем (`user_id`) и может быть проверена другим пользователем (`reviewed_by`).
   * Поля `word` и `hypothesis_text` не могут быть пустыми.
   * Комбинация `user_id` и `word` должна быть уникальной, чтобы избежать дублирования гипотез для одного слова от одного пользователя.

## Связи (Relations)

* **users** `1 → ∞` **queries** (Один пользователь может создать много запросов)
* **queries** `1 → 1` **analyses** (Один запрос имеет ровно один анализ)
* **analyses** `1 → ∞` **analysis_conflicts** (Один анализ может иметь много конфликтов)
* **analyses** `1 → ∞` **exports** (Один анализ может быть экспортирован несколько раз)
* **users** `1 → ∞` **exports** (Один пользователь может иметь много экспортов)
* **users** `1 → ∞` **user_hypotheses** (Один пользователь может предложить много гипотез)
* **users** `1 → ∞` **user_hypotheses** (через `reviewed_by`) (Один пользователь может проверить много гипотез)

