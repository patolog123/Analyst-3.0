``` mermaid
sequenceDiagram
  autonumber
  actor A as Аналитик
  participant UI as Интерфейс
  participant S as Сервер
  participant AI as ИИ-сервис
  participant DB as База данных

  A->>UI: Открыть артефакт → «Метки»
  UI->>S: Запрос рекомендаций (artifact_id)
  S->>AI: Сгенерировать теги
  AI-->>S: Теги + уверенность
  S-->>UI: Показать предложения
  A->>UI: Отметить теги + добавить свои
  UI->>S: Сохранить выбранные теги
  S->>DB: Обновить artifact_tags (итоговое состояние)
  S->>DB: Записать tag_events (кто/когда/что сделал)
  S-->>UI: «Сохранено»
```
