```mermaid
sequenceDiagram
    actor User as Пользователь
    participant Bot as Telegram-бот
    sequenceDiagram
    actor User as Пользователь
    participant Bot as Telegram-бот
    participant State as BotState
    participant Profile as UserProfile
    participant DB as База данных
    participant API as API рекомендаций
    participant KP as Kinopoisk API

    User->>Bot: /start
    Bot->>DB: Проверка существования пользователя
    DB-->>Bot: Пользователь найден/не найден
    Bot->>User: Приветственное сообщение

    loop Основной сценарий
        User->>Bot: /recommend или "Подобрать кино"
        Bot->>State: Сохранить состояние: awaiting_mood
        Bot->>User: "Какое настроение?" (кнопки жанров)

        User->>Bot: Выбор настроения (например, "комедия")
        Bot->>State: Сохранить состояние: awaiting_duration
        Bot->>User: "Сколько времени есть?" (кнопки времени)

        User->>Bot: Выбор длительности (например, "90-120 мин")
        Bot->>State: Сохранить состояние: processing
        
        alt Новый пользователь?
            Bot->>Profile: Проверить experience_level
            Profile-->>Bot: experience_level = 'new'
            Bot->>User: "Давайте узнаем ваши вкусы!"
            Bot->>User: "Любимый жанр?" (кнопки)
            User->>Bot: Выбор жанра
            Bot->>User: "Любимый актер/режиссер?"
            User->>Bot: Текстовый ввод
            Bot->>User: "Последний понравившийся фильм?"
            User->>Bot: Текстовый ввод
            Bot->>Profile: Сохранить предпочтения
        end

        Bot->>API: Запрос рекомендаций (настроение, время, предпочтения)
        API->>KP: Поиск фильмов с русской локализацией
        KP-->>API: Список фильмов (макс. 5)
        API-->>Bot: Рекомендации с обоснованием

        alt Нет результатов
            Bot->>User: "Ничего не найдено. Попробуйте: /broaden или /popular"
        else Есть результаты
            Bot->>DB: Сохранить сессию рекомендаций
            Bot->>User: Показать карусель карточек (постер, название, рейтинг, обоснование)
            Bot->>User: Кнопки: "смотреть" | "позже" | "не нравится"
        end
    end

    loop Обработка действий пользователя
        User->>Bot: Выбор действия (например, "смотреть")
        Bot->>DB: Сохранить взаимодействие (UserInteraction)
        Bot->>KP: Запрос ссылок на стриминги
        KP-->>Bot: Ссылки на платформы
        Bot->>User: Показать ссылки для просмотра
    end

    alt Обработка ошибок
        API--xBot: Таймаут API
        Bot->>User: "Кинотеатр на перерыве. Попробуйте через пару минут!"
        
        DB--xBot: Ошибка чтения данных
        Bot->>User: "Не могу прочитать предпочтения. Обновите профиль /profile"
    end
