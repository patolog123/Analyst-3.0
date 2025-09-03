# Модель данных финансового телеграм бота

## Объект User

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| User | ---- | Object | Пользователь телеграм бота |
|  | id | Integer | Уникальный идентификатор пользователя в Telegram (primary key) |
|  | chat_id | Integer | ID чата с пользователем |
|  | username | String | Имя пользователя в Telegram (опционально) |
|  | first_name | String | Имя пользователя |
|  | last_name | String | Фамилия пользователя (опционально) |
|  | language_code | String | Код языка пользователя (по умолчанию "ru") |
|  | registration_date | DateTime | Дата и время регистрации пользователя |
|  | default_currency | String | Валюта по умолчанию для операций (по умолчанию "RUB") |
|  | monthly_budget | Float | Месячный бюджет пользователя (опционально) |
|  | is_active | Boolean | Статус активности пользователя |
|  | last_activity | DateTime | Дата и время последней активности |

---

## Объект Category

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| Category | ---- | Object | Категория финансовой операции |
|  | id | Integer | Уникальный идентификатор категории (primary key) |
|  | user_id | Integer | ID пользователя (foreign key) |
|  | name | String | Название категории |
|  | type | Enum | Тип категории. **income** (доход), **expense** (расход) |
|  | emoji | String | Эмодзи для визуального обозначения категории (опционально) |
|  | color | String | Цвет категории в HEX формате |
|  | is_default | Boolean | Флаг системной категории по умолчанию |
|  | created_at | DateTime | Дата создания категории |

---

## Объект Transaction

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| Transaction | ---- | Object | Финансовая операция |
|  | id | Integer | Уникальный идентификатор транзакции (primary key) |
|  | user_id | Integer | ID пользователя (foreign key) |
|  | amount | Float | Сумма транзакции (≥ 0) |
|  | currency | String | Валюта транзакции |
|  | type | Enum | Тип транзакции. **income** (доход), **expense** (расход) |
|  | category_id | Integer | ID категории (foreign key) |
|  | description | String | Описание транзакции (опционально) |
|  | transaction_date | DateTime | Дата совершения транзакции |
|  | created_at | DateTime | Дата создания записи |
|  | updated_at | DateTime | Дата последнего обновления |
|  | is_recurring | Boolean | Флаг повторяющейся транзакции |
|  | recurring_id | Integer | ID родительской повторяющейся транзакции (опционально) |

---

## Объект Budget

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| Budget | ---- | Object | Бюджет пользователя |
|  | id | Integer | Уникальный идентификатор бюджета (primary key) |
|  | user_id | Integer | ID пользователя (foreign key) |
|  | category_id | Integer | ID категории (foreign key, опционально) |
|  | amount | Float | Сумма бюджета |
|  | currency | String | Валюта бюджета |
|  | period | Enum | Период бюджета. **daily**, **weekly**, **monthly**, **yearly** |
|  | start_date | DateTime | Дата начала действия бюджета |
|  | end_date | DateTime | Дата окончания действия бюджета (опционально) |
|  | is_active | Boolean | Флаг активности бюджета |
|  | created_at | DateTime | Дата создания бюджета |
|  | notifications_enabled | Boolean | Включены ли уведомления о превышении бюджета |

---

## Объект UserSettings

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| UserSettings | ---- | Object | Настройки пользователя |
|  | user_id | Integer | ID пользователя (primary key, foreign key) |
|  | notification_time | Time | Время отправки ежедневных уведомлений |
|  | report_frequency | Enum | Частота отчетов. **daily**, **weekly**, **monthly** |
|  | currency | String | Основная валюта |
|  | language | String | Язык интерфейса |
|  | is_notifications_enabled | Boolean | Включены ли уведомления |
|  | created_at | DateTime | Дата создания настроек |
|  | updated_at | DateTime | Дата обновления настроек |

---

## Объект SessionState

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| SessionState | ---- | Object | Состояние сессии пользователя |
|  | user_id | Integer | ID пользователя (primary key, foreign key) |
|  | current_state | Enum | Текущее состояние. **main_menu**, **adding_expense**, **adding_income**, **setting_category**, **viewing_report**, **setting_budget**, **setting_goal** |
|  | temp_data | JSON | Временные данные для текущей сессии |
|  | last_message_id | Integer | ID последнего сообщения бота |
|  | last_interaction | DateTime | Дата и время последнего взаимодействия |
|  | created_at | DateTime | Дата создания сессии |
|  | updated_at | DateTime | Дата обновления сессии |

---