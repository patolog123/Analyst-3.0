АИ-телеграм бот
Use Case: выбрать посты из канала
Главный актор: блогер
Предусловия: блогер авторизован в телеграмм
Ограничения: 
1. в одном запросе должен быть указан 1 канал
2. в одном запросе должна быть указана одна тема поиска. Тема поиска может задаваться одним словом или словосочетанием.
Триггер: Блогер открывает бот и выбирает команду "Выбрать посты из канала"
Основной сценарий:
1. Бот предлагает ввести ссылку на канал, задать тему поиска, задать временной интервал поиска, задать опцию строгого/нестрогого поиска.
2. Блогер вводит требуемые параметры
3. Бот контролирует параметры:
    - доступность канала;
    - правильность временного периода.
4. Если блогер правильно ввел параметры, то переход на следующий шаг
5. Если блогер указал опцию строгого поиска, то бот выбирает посты, в которых есть указанное слово или словосочетание
6. Бот возвращает список ссылок на посты.

Альтернативные сценарии

4а. Если блогер вел неправильные параметры, то 
4а1. Бот оповещает об ошибке параметров
4а2. Выполняется основной сценарий, начиная с шага 1

5а. Если блогер указал опцию несторого поиска, то бот выбирает посты, в которых рассматривается указанная тема
5а1. Выполняется основной сценарий, начиная с шага 6