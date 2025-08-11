```mermaid
graph TD
    subgraph "Клиент"
        A[Пользователь/Беседа]
    end

    subgraph "Telegram"
        B[Frontend Bot]
        I[Telegram API]
    end

    subgraph "Backend"
        D[AI Agent <i>Python</i>]
    end

    subgraph "Хранилища"
        E[(Google Sheets <i>User Types</i>)]
        F[(SQLite <i>Group Reports</i>)]
        J[RAG Knowledge Base]
    end

    subgraph "Внешние сервисы"
        G{{LLM <i>Gemini</i>}}
    end

    A -- MTProto/TCP --> B
    B -- Webhook по HTTPS --> D
    D -- Чтение/запись по HTTPS --> E
    D -- Чтение/запись по SQL --> F
    D -- Запрос шаблонов по HTTPS --> J
    D -- Анализ типов по HTTPS --> G
    D -- Получение данных чата по HTTPS --> I
    G -- Использует контекст по HTTPS --> J
    I -- История сообщений <i>Состав группы</i> (API Telegram-бота, HTTPS) --> D
```
