# AI agent documentation

## 1. Концепция

Этот AI-агент для системных аналитиков, которым нужно сформировать UML-диаграмму любого вида (последовательности, use case и др.) с использованием текстового промпта, в отличие от других ИИ-агентов, предоставляет пользователю возможность вручную взаимодействовать с кодом диаграммы на PlantUML.

## 2. Стейкхолдеры

| id | Стейкхолдер | Тип | Ожидания | Риски | Роль в проекте |
|-------------|-------------|-------------|-------------| ------------- |  ------------- |
| ai001    |  Проектная команда  | Внутренние | Получить прибыль | Уйти в убыток, не окупить вложения  |  Владелец | 
| ai002    | Команда разработчиков    | Внутренние | Получить конкретно ТЗ для реализации  | Некачественно реализовать ТЗ | Разработка  | 
| ai003    | Инвесторы    | Внешние  | Получить прибыль | Уйти в убыток, не окупить вложения  | Наблюдение, консультация  | 
| ai004    | Команда маркетинга    | Внутренние  | Обеспечить ожидаемый поток клиентов | Выбор неудачной маркетинговой стратегии |  Продвижение  |
| ai005    | Служба поддержки  | Внутренние  | Обеспечить пользователям качественный сервис | Недостаток информации о системе для оказания качественной поддержки  |  Сопровождение   |
| ai006    | Отдел продаж    | Внутренние  | Обеспечить ожидаемый объём продаж | Невыполнение плановых показателей по продажам  |  Продажи  | 
| ai007    | Бухгалтер    | Внутренние  | Сформировать корректную бухгалтерскую отчетность | Неккоректность расчетов |  Бухгалтерия   | 
| ai008    | Пользователь неплатящий    | Внешние  | Получить возможность отрисовки UML-диаграммы | Баги ИИ-агента |  Пользователь    | 
| ai009    | Пользователь премиум    | Внешние  | Получить возможность отрисовки UML-диаграммы в неограниченном количестве | Баги ИИ-агента  |  Пользователь    |
| ai010    | Роскомнадзор   | Внешние  | Соблюдение законодательства в сфере защиты персональных данных | Штрафные санкции за несоблюдение законодательства в сфере защиты персональных данных |  Регулятор  | 
| ai011    | Конкуренты   | Внешние  | Наблюдение за развитием | Выпуск новых функций  |  Конкурент |
| ai012    | СМИ   | Внешние  | Формирование позитивного образа продукта | Формирование негативного образа продукта |  Освещение  |
| ai013    | Общественность   | Внешние  | Позитивные отзывы в соцсетях | Негативные отзывы в соцсетях  |  Освещение  | 



## 3. USER STORY

**Неплатящий / премиум пользователь:**

| id | Вариант использования | User story | 
|-------------|-------------|-------------|
| us001    |  Отправить запрос | Как пользователь, я хочу иметь возможность отправить письменный промпт, чтобы получить нужную мне UML-диаграмму.|
| us002    |  Увидеть диаграмму | Как пользователь, я хочу видеть графическое представление полученной UML-диаграммы, чтобы избежать ошибов в UML-диаграмме.|
| us003    |  Изменить диаграмму | Как пользователь, я хочу иметь возможность менять диграмму, чтобы исправлять недочеты и получить в точности небходимую мне диаграмму.|
| us004    |  Сохранить диаграмму | Как пользователь, я хочу иметь возможность сохранить диаграмму, чтобы при возвращении к работе над диаграммой, не писать промпт заново.|
| us005    |  Масштабировать диаграмму | Как пользователь, я хочу иметь возможность масштабировать диаграмму, чтобы изучить как отдельные её части, так и всю диаграмму целиком.|
| us006    |  Работать над другой диаграммой | Как пользователь, я хочу иметь возможность создания дополнительного листа, чтобы строить несколько диаграмм одновременно.|
| us007    |  Экспортировать диаграмму | Как пользователь, я хочу иметь возможность экспортировать полученную UML-диаграмму, чтобы делиться ей с коллегами.|
| us008    |  Написать в поддержку | Как пользователь, я хочу писать в службу поддержки, чтобы получить ответ на вопрос о функционале или сообщить о проблеме.|

**Команда разработчиков:**

| id | Вариант использования | User story | 
|-------------|-------------|-------------|
| dev001    | Получить ТЗ | Как разработчик, я хочу получить четкое ТЗ, чтобы не делать лишнюю работу.|
| dev002    | Узнать причину возникновения проблемы | Как разработчик, я хочу сохранять логи, чтобы понять причину возникновения ошибки.|

**Проектная команда / инвесторы:**

| id | Вариант использования | User story | 
|-------------|-------------|-------------|
| pm001    | Получить прибыль | Как владелец проекта, я хочу внедрить способ монетизации, чтобы окупить вложенные инвестиции и заработать |

**Отдел маркетинга:**

| id | Вариант использования | User story | 
|-------------|-------------|-------------|
| ad001    | Определить ЦА | Как маркетолог, я хочу получать информацию о возрасте, поле и роде занятий пользователей, чтобы применить эти данные при продумывании маркетинговой стратегии |