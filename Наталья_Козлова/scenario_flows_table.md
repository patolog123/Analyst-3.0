# Таблица потоков основного сценария (версия 2)

| Номер потока | Описание потока | Компонент |
|-------------|-----------------|-----------|
| 1 | Пользователь запускает бота командой /start | User → TG-app |
| 2 | Бот запрашивает URL канала для анализа | TG-app → User |
| 3 | Пользователь вводит URL канала | User → TG-app |
| 4 | Бот запрашивает параметры выборки (дата/период публикации, ключевые слова) | TG-app → User |
| 5 | Пользователь задает параметры выборки | User → TG-app |
| 6 | TG-app передает запрос с URL и параметрами в Backend | TG-app → Backend |
| 7 | Backend валидирует ввод пользователя | Backend (internal) |
| 8 | Backend запрашивает данные через Telegram API (список постов канала) | Backend → TG-server |
| 9 | Telegram Server получает данные канала | TG-server (internal) |
| 10 | Telegram Server возвращает сырые данные постов | TG-server → Backend |
| 11 | Backend отправляет данные и параметры в LLM для фильтрации | Backend → LLM |
| 12 | LLM анализирует и фильтрует посты по заданным параметрам | LLM (internal) |
| 13 | LLM возвращает отфильтрованный список постов | LLM → Backend |
| 14 | Backend сохраняет результаты анализа в базу данных | Backend → DB |
| 15 | База данных подтверждает сохранение результатов | DB → Backend |
| 16 | Backend формирует отчет в виде структурированного списка постов | Backend (internal) |
| 17 | Backend передает готовый отчет в TG-app | Backend → TG-app |
| 18 | TG-app отправляет готовый отчет пользователю | TG-app → User |

## Соответствие Use Case и Architecture

Таблица создана на основе:
- Основного потока из [`UC.md`](E:\работа\IDE-BAS\IDE-BAS\UC.md:15)
- Sequence diagram с автонумерацией из [`main_scenario_sequence_v2.plantuml`](E:\работа\IDE-BAS\IDE-BAS\main_scenario_sequence_v2.plantuml:1)
- Обновленной архитектуры системы (User, TG-app, Backend, TG-server, LLM, DB)