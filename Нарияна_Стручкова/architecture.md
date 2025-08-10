# Архитектура кино‑бота (просто и без опечаток)

```mermaid
graph TD
    %% --- Секции ---
    subgraph Клиент
        U[Пользователь в Telegram]
    end

    subgraph Telegram
        TB[Telegram‑бот]
        TAPI[Telegram Bot API]
    end

    subgraph Backend
        SVC[AI Agent (Python)]
    end

    subgraph Хранилища
        DB[(SQL Database)]
        KB[RAG Knowledge Base]
    end

    subgraph Внешние сервисы
        G[GigaChat LLM]
        CAT[Каталоги фильмов (Kinopoisk/IMDb)]
    end

    %% --- Потоки ---
    U -- MTProto/TCP --> TB
    TB -- Webhook HTTPS --> SVC

    SVC -- HTTPS REST --> G
    SVC -- HTTPS REST --> CAT
    SVC -- HTTPS REST --> KB

    SVC -- SQL over TCP --> DB

    SVC -- HTTPS Bot API --> TAPI
    TAPI -- HTTPS Bot API --> SVC
```
