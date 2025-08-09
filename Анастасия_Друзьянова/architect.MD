```mermaid
graph TD
    subgraph "Пользователь"
        A[Пользователь Telegram]
    end

    subgraph "Клиент (FE)"
        B[Telegram Bot App]
    end

    subgraph "BE"
        C[REST API]
        J[Брокер]
        F[Фоновые задачи.]
    end

    subgraph "Хранилища"
        G[(Реляционная БД <br><i>метаданные и структура дерева</i>)]
        I[(Векторная БД <br><i>векторный поиск и эмбеддинги базы знаний</i>)]
    end

    subgraph "Внешние сервисы"
        H{{LLM API}}
    end

    %% Связи между компонентами
    A -- Вопрос (query: txt) --> B
    B -- HTTPS --> C
    C -- Ставит задачи --> J
    J -- Передаёт задачи --> F
    F -- HTTPS --> H
    F -- Читает/пишет --> G
    F -- Читает/пишет --> I
    F -- Уведомляет о результате --> B
```
