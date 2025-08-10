```mermaid
graph TD
    subgraph "Пользователь"
        A[Пользователь Telegram]
    end

    subgraph "Frontend"
        B[Telegram Bot]
    end
    
    subgraph "tg server"
        C[...]
    end

    subgraph "Backend"
        D[REST API]
    end

    subgraph "Хранилища"
        E[(БД)]
    end

    subgraph "Внешние сервисы"
        F{{LLM API}}
    end

    %% Связи между компонентами
    A -- ... --> B
    B <-- HTTPS --> C
    C -- HTTPS --> D
    D -- TCP --> E
    D -- TCP --> F
```
