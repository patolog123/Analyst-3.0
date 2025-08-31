``` mermaid
sequenceDiagram
  autonumber
  actor A as Аналитик
  participant UI as Интерфейс
  participant S as Сервер
  participant DB as База данных

  A->>UI: Выбрать до 5 меток → «Фильтровать»
  UI->>S: GET /artifacts?tags=...
  S->>DB: Найти артефакты с ВСЕМИ метками (AND)
  DB-->>S: Список результатов
  S-->>UI: Возврат артефактов
  UI-->>A: Показать результаты или «ничего не найдено»
```
