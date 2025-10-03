# REST API (табличный вид) — Wellness AI Bot

Версия: **v1**  
Тип бота: **текстовый Telegram‑бот** (генерация плана питания и плана тренировок).  
Аутентификация: не требуется — идентификация по `telegram_id`, приходящему от Telegram через Backend.

---

## 0. Конвенции
- Все ответы — JSON.
- Даты/время — `timestamptz` (ISO 8601, UTC).
- Ошибки возвращаются в формате: `{ "error": "<code>", "message": "..." }`.

---

## 1) POST `/v1/users`
**Назначение:** регистрация пользователя (по `telegram_id`).

### Request (body)
| Название параметра | Тип данных | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | body | Telegram ID пользователя | да |
| name | string | body | Имя/ник | нет |

### Response `201 Created`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| user_id | bigint | body | Внутренний ID пользователя |
| telegram_id | bigint | body | Telegram ID |
| name | string | body | Имя |
| created_at | timestamptz | body | Дата регистрации |
| created | boolean | body | true — если создан, false — уже существовал |

---

## 2) PUT `/v1/profile`
**Назначение:** создать/обновить профиль пользователя.

### Request (body)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | body | Telegram ID | да |
| sex | string | body | Пол (`male` \| `female` \| `other`) | нет |
| birth_date | date | body | Дата рождения | нет |
| height_cm | int | body | Рост | нет |
| weight_kg | numeric | body | Вес | нет |
| activity_level | string | body | `low` \| `medium` \| `high` | нет |
| dietary_restrictions | string | body | Ограничения в питании | нет |
| allergens | string | body | Аллергены | нет |
| timezone | string | body | Часовой пояс (например, `Europe/Moscow`) | нет |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| user_id | bigint | body | ID пользователя |
| updated | boolean | body | true — профиль создан/обновлён |
| profile | object | body | Снимок профиля (все атрибуты) |

---

## 3) GET `/v1/profile`
**Назначение:** получить профиль пользователя.

### Request (query)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | query | Telegram ID | да |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| user_id | bigint | body | ID пользователя |
| profile | object | body | Профиль (или `null`, если не найден) |

---

## 4) GET `/v1/menu`
**Назначение:** вернуть доступные пункты меню (для Telegram‑клиента).

### Request (query)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | query | Telegram ID | да |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| items | array<string> | body | Доступные кнопки, например: `["План питания","План тренировок"]` |
| active_profile | boolean | body | Есть ли сохранённый профиль |
| active_plans | object | body | `{ "nutrition": plan_id \| null, "workout": plan_id \| null }` |

---

## 5) POST `/v1/plans/generate`
**Назначение:** сгенерировать план (питание или тренировки) с помощью LLM и сохранить в БД.

### Request (body)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | body | Telegram ID | да |
| plan_type | string | body | `nutrition` \| `workout` | да |
| goal_hint | string | body | Необязательная подсказка цели на один запуск | нет |
| preferences | object | body | Переопределение предпочтений на один запуск | нет |

### Response `201 Created`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| plan_id | bigint | body | ID созданного плана |
| user_id | bigint | body | ID пользователя |
| plan_type | string | body | Тип |
| title | string | body | Заголовок |
| content | string | body | Текст плана (сгенерированный LLM) |
| is_active | bool | body | Флаг активного |
| created_at | timestamptz | body | Дата создания |

---

## 6) GET `/v1/users/{telegram_id}/plans`
**Назначение:** получить список планов пользователя.

### Request (path + query)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | path | Telegram ID | да |
| type | string | query | Фильтр: `nutrition` \| `workout` | нет |
| active | boolean | query | Только активные | нет |
| limit | int | query | Количество на страницу | нет |
| offset | int | query | Смещение | нет |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| items | array<object> | body | Массив: `[{ plan_id, plan_type, title, created_at, is_active }]` |
| total | int | body | Общее количество |

---

## 7) GET `/v1/plans/{plan_id}`
**Назначение:** получить конкретный план.

### Request (path)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| plan_id | bigint | path | ID плана | да |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| plan_id | bigint | body | ID |
| user_id | bigint | body | Пользователь |
| plan_type | string | body | Тип |
| title | string | body | Заголовок |
| content | string | body | Полный текст плана |
| is_active | bool | body | Активен |
| created_at | timestamptz | body | Дата создания |

---

## 8) PATCH `/v1/plans/{plan_id}/activate`
**Назначение:** сделать план активным (сбрасывает предыдущий активный того же типа).

### Request (path)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| plan_id | bigint | path | ID плана | да |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| plan_id | bigint | body | Активированный план |
| plan_type | string | body | Тип |
| is_active | bool | body | true |
| replaced | boolean | body | Был ли деактивирован предыдущий активный |

---

## 9) DELETE `/v1/plans/{plan_id}`
**Назначение:** удалить план.

### Request (path)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| plan_id | bigint | path | ID плана | да |

### Response `200 OK`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| success | boolean | body | Удалено |
| deleted_id | bigint | body | ID удалённого |

---

## 10) POST `/v1/debug/llm`
**Назначение:** логировать запрос/ответ LLM (для отладки).

### Request (body)
| Параметр | Тип | Где | Описание | Обязателен |
|---|---|---|---|---|
| telegram_id | bigint | body | Telegram ID | да |
| prompt | string | body | Текст запроса в LLM | да |
| response | string | body | Ответ LLM | да |
| plan_type | string | body | `nutrition` \| `workout` | нет |

### Response `201 Created`
| Параметр | Тип | Где | Описание |
|---|---|---|---|
| log_id | bigint | body | ID лога |
| created_at | timestamptz | body | Когда зафиксирован лог |
| saved | bool | body | Признак успешного сохранения |

---

## 11) Коды ошибок (общие)
| Код | Когда | Тело |
|---|---|---|
| 400 | Неверные параметры запроса | `{ "error": "bad_request", "message": "..." }` |
| 401 | Не авторизован (если включите токен) | `{ "error": "unauthorized" }` |
| 404 | Объект не найден | `{ "error": "not_found" }` |
| 409 | Конфликт бизнес‑правил | `{ "error": "conflict", "details": "..." }` |
| 500 | Внутренняя ошибка сервера/LLM | `{ "error": "server_error" }` |

---

### Примечания к реализации
- Все операции идентифицируют пользователя по `telegram_id` (из Telegram webhook).  
- Для уникальности активного плана по типу рекомендуем индекс:  
  `create unique index plans_one_active_per_type on plans(user_id, plan_type) where is_active = true;`
- Параметр `content` может хранить текст плана; альтернативно структуру можно положить в `meta JSONB`.
