```mermaid
flowchart TD
    title Процесс работы с AI-Индексатором артефактов

    %% Начало
    Start([Начало])

    %% Выбор действия аналитика
    Start --> DecisionAction{Что делает аналитик?}
    DecisionAction --> |Присвоить метки| AssignLabels
    DecisionAction --> |Фильтровать по меткам| FilterTags

    %% Присвоение меток
    subgraph UI1 [Интерфейс Пользователя]
      AssignLabels --> SelectArtifacts[Выбрать один или несколько артефактов]
      SelectArtifacts --> ClickAssign[Нажать "Присвоить метки"]
      ClickAssign --> DecisionBulk{Выбрано ≥ N артефактов?}
      DecisionBulk --> |Да| StartBackground([Запустить фоновую задачу])
      StartBackground --> NotifyBG[Показать уведомление о старте фоновой задачи]
      NotifyBG --> End1([Конец])
      DecisionBulk --> |Нет| ToAI
    end

    subgraph AI [Система / AI-Индексатор]
      ToAI[Отправить запрос в AI-Индексатор] --> DecisionAI{Сбой или низкая уверенность?}
      DecisionAI --> |Да| AIServerDown[Сервис недоступен или таймаут]
      AIServerDown --> UIFallback
      DecisionAI --> |Нет| AISuccess[AI вернул рекомендации с confidence]
      AISuccess --> DecisionConf{confidence < порог?}
      DecisionConf --> |Да| WarnLowConf[Показать предупреждение о низкой уверенности]
      DecisionConf --> |Нет| ShowRecs[Отобразить рекомендации AI]
      WarnLowConf --> UIFallback
      ShowRecs --> UIFallback
    end

    subgraph UIFallback [Интерфейс Пользователя]
      UIFallback --> ManualInput[Предложить ввод меток вручную]
      ManualInput --> UIReview
    end

    subgraph UIReview [Интерфейс Пользователя]
      UIReview[Взаимодействие с UI] --> AcceptReject[Принять/отклонить рекомендации]
      AcceptReject --> AddCustom[Добавить собственные метки]
      AddCustom --> DecisionLimit{Превышен лимит меток?}
      DecisionLimit --> |Да| WarnLimit[Показать предупреждение о лимите]
      WarnLimit --> WaitRemoval[Дождаться удаления лишних меток]
      WaitRemoval --> ClickSave
      DecisionLimit --> |Нет| ClickSave[Нажать "Сохранить"]
      ClickSave --> DB
    end

    subgraph DB [Система / БД]
      DB --> SaveTags[Сохранить метки в БД]
      DB --> EnqueueFeedback[Отправить метки и фидбэк в очередь дообучения]
      EnqueueFeedback --> UpdateUI[Обновить интерфейс с новыми метками]
      UpdateUI --> End1
    end

    %% Фильтрация по меткам
    subgraph UI2 [Интерфейс Пользователя]
      FilterTags --> ClickFilter[Нажать "Фильтровать"]
      ClickFilter --> SelectTags[Выбрать до 5 меток]
      SelectTags --> ApplyFilter[Применить фильтр]
    end

    subgraph DB2 [Система / БД]
      ApplyFilter --> QueryArtifacts[Выполнить запрос к хранилищу артефактов]
    end

    subgraph UI3 [Интерфейс Пользователя]
      QueryArtifacts --> DecisionEmpty{Результат пуст?}
      DecisionEmpty --> |Да| ShowNoResults[Показать "Ничего не найдено"]
      ShowNoResults --> SuggestChange[Предложить изменить фильтр]
      SuggestChange --> End1
      DecisionEmpty --> |Нет| ShowResults[Отобразить список артефактов]
      ShowResults --> End1
    end
```
