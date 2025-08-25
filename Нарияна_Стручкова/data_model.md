# Модель данных AI-киносоветник

## 📊 Обзор сущностей

### 🎯 Основные сущности пользователей

#### **User** (Пользователь)
*Основная сущность: Хранит данные пользователя Telegram*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK, Уникальный идентификатор | Auto Increment |
| `telegram_id` | BigInteger | ID пользователя в Telegram | Not Null, Unique |
| `username` | String | Никнейм в Telegram | |
| `first_name` | String | Имя пользователя | Not Null |
| `created_at` | DateTime | Дата регистрации | Default = CURRENT_TIMESTAMP |
| `state` | String | Текущее состояние бота | Enum: 'idle', 'awaiting_mood', 'awaiting_duration', 'awaiting_genre', 'awaiting_actor', 'awaiting_last_movie' |

#### **UserProfile** (Профиль пользователя)
*Профильная сущность: Хранит предпочтения и историю*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | Not Null, Unique |
| `experience_level` | String | Уровень опыта | Enum: 'new', 'returning', 'active' |
| `favorite_genre` | String | Любимый жанр | |
| `favorite_actor_director` | String | Любимый актер/режиссер | |
| `last_liked_movie` | String | Последний понравившийся фильм | |
| `preferred_duration` | String | Предпочтение по времени | Enum: 'short', 'medium', 'long' |
| `last_recommendation_at` | DateTime | Последняя рекомендация | |

---

### 🎬 Сущности контента

#### **Movie** (Фильм)
*Справочная сущность: Информация о фильмах*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `external_id` | String | ID в внешней API (Kinopoisk/IMDb) | Unique |
| `title_ru` | String | Русское название | Not Null |
| `title_original` | String | Оригинальное название | |
| `year` | Integer | Год выпуска | |
| `duration` | Integer | Длительность в минутах | |
| `rating` | Float | Рейтинг | |
| `genres` | JSON | Жанры (массив) | Default = '[]' |
| `poster_url` | String | URL постера | |
| `description` | Text | Описание | |
| `age_rating` | String | Возрастной рейтинг | |
| `country` | String | Страна производства | |
| `is_russian` | Boolean | Русская локализация | Default = true |

#### **StreamingLink** (Ссылки на стриминги)
*Связующая сущность: Доступность фильма на платформах*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `movie_id` | Integer | FK → Movie.id | Not Null |
| `service_name` | String | Название сервиса | |
| `url` | String | Ссылка для просмотра | |
| `price` | Decimal | Стоимость | |
| `available` | Boolean | Доступность | Default = true |

---

### ⭐ Сущности взаимодействий

#### **UserRating** (Оценки пользователя)
*Оценочная сущность: История оценок*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | Not Null |
| `movie_id` | Integer | FK → Movie.id | Not Null |
| `rating` | Integer | Оценка (1-5) | Check: 1-5 |
| `rated_at` | DateTime | Время оценки | Default = CURRENT_TIMESTAMP |

#### **UserFavorite** (Избранное)
*Коллекционная сущность: Любимые фильмы*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | Not Null |
| `movie_id` | Integer | FK → Movie.id | Not Null |
| `added_at` | DateTime | Время добавления | Default = CURRENT_TIMESTAMP |

#### **UserInteraction** (Взаимодействия)
*Аналитическая сущность: Действия пользователя*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | Not Null |
| `movie_id` | Integer | FK → Movie.id | |
| `action_type` | String | Тип действия | Enum: 'watch', 'watch_later', 'dislike', 'click', 'view', 'rate', 'favorite' |
| `interaction_data` | JSON | Дополнительные данные | |
| `created_at` | DateTime | Время действия | Default = CURRENT_TIMESTAMP |

---

### 🎯 Сущности рекомендаций

#### **RecommendationSession** (Сессия рекомендаций)
*Процессная сущность: Сессия подбора фильмов*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | Not Null |
| `mood` | String | Настроение | Enum: 'comedy', 'drama', 'thriller', 'romance', 'action', 'fantasy', 'horror', 'sci-fi', 'adventure', 'detective' |
| `duration_preference` | String | Время просмотра | Enum: 'short', 'medium', 'long' |
| `session_type` | String | Тип сессии | Enum: 'personalized', 'popular', 'broad' |
| `created_at` | DateTime | Время создания | Default = CURRENT_TIMESTAMP |
| `completed_at` | DateTime | Время завершения | |

#### **Recommendation** (Рекомендация)
*Результатная сущность: Конкретная рекомендация*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `session_id` | Integer | FK → RecommendationSession.id | Not Null |
| `movie_id` | Integer | FK → Movie.id | Not Null |
| `position` | Integer | Позиция в выдаче | Check: 1-5 |
| `reason` | Text | Обоснование рекомендации | |
| `shown_at` | DateTime | Время показа | Default = CURRENT_TIMESTAMP |
| `user_response` | String | Ответ пользователя | Enum: 'watched', 'watch_later', 'disliked', 'no_response' |

---

### 🔧 Сервисные сущности

#### **BotState** (Состояние бота)
*Техническая сущность: Управление состоянием*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | Not Null, Unique |
| `current_state` | String | Текущее состояние | Enum: 'idle', 'awaiting_mood', 'awaiting_duration', 'awaiting_genre', 'awaiting_actor', 'awaiting_last_movie' |
| `state_data` | JSON | Данные состояния | |
| `updated_at` | DateTime | Время обновления | Default = CURRENT_TIMESTAMP |

#### **APIRequestLog** (Лог запросов)
*Мониторинговая сущность: Логирование API*

| Атрибут | Тип | Описание | Ограничения |
|---------|------|----------|-------------|
| `id` | Integer | PK | Auto Increment |
| `user_id` | Integer | FK → User.id | |
| `endpoint` | String | API endpoint | |
| `request_data` | JSON | Данные запроса | |
| `response_status` | Integer | HTTP статус | |
| `response_data` | JSON | Данные ответа | |
| `created_at` | DateTime | Время запроса | Default = CURRENT_TIMESTAMP |

---

## 🔗 Схема связей

```mermaid
erDiagram
    User ||--o{ UserProfile : has
    User ||--o{ UserRating : rates
    User ||--o{ UserFavorite : favorites
    User ||--o{ RecommendationSession : requests
    User ||--o{ UserInteraction : interacts
    User ||--o{ BotState : maintains
    
    Movie ||--o{ UserRating : rated_by
    Movie ||--o{ UserFavorite : favorited_by
    Movie ||--o{ Recommendation : recommended_in
    Movie ||--o{ StreamingLink : available_on
    
    RecommendationSession ||--o{ Recommendation : contains
    
    APIRequestLog }o--|| User : made_by

