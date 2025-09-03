# Модель данных финансового телеграм бота

## Объект User

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| User | ---- | Object | Пользователь телеграм бота |
|  | id | Integer | Уникальный идентификатор пользователя в Telegram (primary key) |
|  | username | String | Имя пользователя в Telegram |
|  | first_name | String | Имя пользователя |
|  | default_currency | String | Валюта по умолчанию для операций (по умолчанию "RUB") |
---

## Объект Category

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| Category | ---- | Object | Категория финансовой операции |
|  | id | Integer | Уникальный идентификатор категории (primary key) |
|  | user_id | Integer | ID пользователя (foreign key) |
|  | name | String | Название категории |
|  | type | Enum | Тип категории. **income** (доход), **expense** (расход) |

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

---

## Объект Budget

| Родительская сущность | Атрибут | Тип | Описание |
|------------------------|---------|------|----------|
| Budget | ---- | Object | Бюджет пользователя |
|  | id | Integer | Уникальный идентификатор бюджета (primary key) |
|  | user_id | Integer | ID пользователя (foreign key) |
|  | amount | Float | Сумма бюджета |
|  | currency | String | Валюта бюджета |
|  | period | Enum | Период бюджета. **daily**, **weekly**, **monthly**, **yearly** |
|  | start_date | DateTime | Дата начала действия бюджета |
|  | notifications_enabled | Boolean | Включены ли уведомления о превышении бюджета |

---