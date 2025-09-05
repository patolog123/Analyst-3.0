## REST Таблица: Запрос прогноза матча 

### **Endpoint:** `POST /api/predict`

| **Request** |  |  |  |  |
|---|---|---|---|---|
| **Название параметра** | **Тип данных** | **Находится в** | **Описание** | **Обязательность параметра** |
| `telegram_user_id` | integer | body | ID пользователя в Telegram | да |
| `team_a_name` | string | body | Название первой команды | да |
| `team_b_name` | string | body | Название второй команды | да |
| `language` | string | body | Язык для ответа (напр., 'ru', 'en') | нет |

---

| **Response** |  |  |  |  |
|---|---|---|---|---|
| **Название параметра** | **Тип данных** | **Находится в** | **Описание** | **Обязательность параметра** |
| `team_a` | string | body | Название первой команды | да |
| `team_b` | string | body | Название второй команды | да |
| `confidence_team_a` | number | body | Уверенность в победе команды A (в процентах 0-100) | да |
| `confidence_team_b` | number | body | Уверенность в победе команды B (в процентах 0-100) | да |
| `predicted_winner` | string | body | Название предсказанного победителя | да |
| `explanation` | string | body | Текстовое объяснение прогноза | да |

**Response code:** <200> (Успех)

---

### **Endpoint:** `GET /api/predictions/{user_id}`

| **Request** |  |  |  |  |
|---|---|---|---|---|
| **Название параметра** | **Тип данных** | **Находится в** | **Описание** | **Обязательность параметра** |
| `user_id` | integer | path | ID пользователя | да |

---

| **Response** |  |  |  |  |
|---|---|---|---|---|
| **Название параметра** | **Тип данных** | **Находится в** | **Описание** | **Обязательность параметра** |
| `predictions` | array | body | Список прогнозов | да |
| &nbsp;&nbsp;↳ `prediction_id` | integer | body | ID прогноза | да |
| &nbsp;&nbsp;↳ `team_a` | string | body | Команда A | да |
| &nbsp;&nbsp;↳ `team_b` | string | body | Команда B | да |
| &nbsp;&nbsp;↳ `predicted_winner` | string | body | Предсказанный победитель | да |
| &nbsp;&nbsp;↳ `created_at` | string | body | Дата создания | да |
| &nbsp;&nbsp;↳ `is_correct` | boolean | body | Был ли прогноз верен | нет |



