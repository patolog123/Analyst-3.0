### Домашнее задание 2: User Case 
**Use Case: "Безопасные тренировки при грыже позвоночника"**
---
#### Как пользователь, Я хочу скорректировать тренировки при травме спины (грыжа позвоночника), чтобы не навредить себе.

###

| Элемент кейса           | Описание                                                                 |
|-------------------------|--------------------------------------------------------------------------|
| **Заголовок**           | Генерация персонализированной программы тренировок при межпозвонковой грыже |
| **Акторы**              | 1. Пользователь с диагнозом "грыжа"<br>2. Telegram-бот (AI-ассистент)<br>3. Врач (опционально) |
| **Предусловия**         | - Подтвержденный диагноз<br>- Наличие данных МРТ/заключения врача<br>- Режим "щадящие тренировки" активирован |
| **Триггер**             | Команда `/safe_spine_training`                                           |
| **Основной сценарий**   |                                                                          |
| 1                       | Пользователь: Вводит команду `/safe_spine_training`                      |
|                         | Система: Запрашивает локализацию грыжи (шейный/грудной/поясничный отдел) |
| 2                       | Пользователь: Указывает "поясничный отдел, L4-L5"                        |
|                         | Система: Уточняет стадию (1-4) и наличие острых симптомов                |
| 3                       | Пользователь: Вводит "2 стадия, периодические боли"                     |
|                         | Система: Генерирует план, исключая осевые нагрузки                      |
| **Альтернативные сценарии** |                                                                      |
| 3a                      | При острых симптомах:                                                    |
|                         | Система рекомендует полный покой и консультацию врача                    |
| 3b                      | Для шейного отдела:                                                      |
|                         | Исключает вращательные движения, предлагает изометрию                    |
| **Исключительные сценарии** |                                                                      |
| -                       | При отсутствии данных МРТ:                                               |
|                         | Дает общие рекомендации с пометкой "Требуется консультация специалиста"  |
| **Результат**           |                                                                          |
| -                       | Персонализированный план на 4 недели                                     |
| -                       | Чек-лист противопоказаний                                                |
| -                       | Система мониторинга состояния                                            |


