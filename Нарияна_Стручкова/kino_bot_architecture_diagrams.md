# Архитектура Telegram-бота (Киносоветник)

## Блок-схема архитектуры
```mermaid
flowchart LR
    U[Пользователь в Telegram] -->|MTProto| TG[Telegram]
    TG -->|Webhook HTTPS| BOT[Telegram-бот (Python/FastAPI/aiogram)]

    BOT -->|HTTPS| GIGA[AI GigaChat]
    BOT -->|SQL over TCP| PG[(PostgreSQL)]
    BOT -->|HTTPS| IMDB[IMDb API]

    PG ---|хранит| PREFS[Предпочтения/оценки/избранное]
    PG ---|хранит| TITLES[Каталог фильмов]
```

## Последовательность запроса /recommend
```mermaid
sequenceDiagram
    participant U as Пользователь
    participant T as Telegram (Bot API)
    participant B as Telegram-бот
    participant DB as PostgreSQL
    participant G as GigaChat
    participant I as IMDb API

    U->>T: /recommend
    T->>B: Webhook update
    B->>DB: получить prefs/history
    B->>U: спросить настроение и время
    U->>B: mood + duration
    B->>I: (опционально) метаданные тайтлов
    B->>G: промпт на рекомендации/объяснения
    G-->>B: список кандидатов + причины
    B->>DB: сохранить выдачу/события
    B-->>U: до 5 карточек (смотреть/позже/не нравится)
```
