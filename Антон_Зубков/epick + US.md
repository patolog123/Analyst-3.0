# Epic: AI-агент "Помощник в карьерном развитии"

**Как** специалист, стремящийся к профессиональному росту,
**Я хочу** использовать интеллектуального помощника, который поможет мне оценить мои текущие навыки, спланировать карьерный путь и развивать необходимые компетенции,
**Чтобы** я мог целенаправленно двигаться к своим карьерным целям и оставаться конкурентоспособным на рынке труда.

---

## Feature Prioritization for MVP (MoSCoW Method)

Это Epic разбит на более мелкие User Stories, которые приоритизированы для итеративной разработки.

### Must-Have (Обязательно для MVP)

*Это ядро продукта, которое необходимо для первого релиза.*

---

#### User Story 1: Ручной ввод и оценка компетенций
*   **Как** пользователь, **я хочу** вручную добавлять свои навыки и оценивать свой уровень владения ими, **чтобы** создать основу для моей карты компетенций.

*   **Acceptance Criteria (AC):**
    *   **AC-1.1: Успешное добавление компетенции**
        *   **Дано:** Пользователь авторизован и находится на экране "Карта компетенций".
        *   **Когда:** Пользователь нажимает "Добавить компетенцию", вводит название "Python" и выбирает уровень "4" из 5.
        *   **И:** Нажимает "Сохранить".
        *   **Тогда:** В профиле пользователя сохраняется компетенция "Python" с уровнем 4.
        *   **И:** Карта компетенций обновляется, отображая новый навык.

    *   **AC-1.2: Обработка ошибки при добавлении дубликата**
        *   **Дано:** В профиле пользователя уже есть компетенция "Python".
        *   **Когда:** Пользователь пытается добавить компетенцию "python" (в любом регистре).
        *   **Тогда:** Система отображает ошибку "Такая компетенция уже существует" и не сохраняет дубликат.

    *   **AC-1.3: Валидация полей**
        *   **Дано:** Пользователь открыл форму добавления компетенции.
        *   **Когда:** Пытается сохранить форму с пустым названием или без выбранного уровня.
        *   **Тогда:** Система подсвечивает незаполненные поля и выводит сообщение "Заполните все обязательные поля".

---

#### User Story 2: Визуализация карты компетенций
*   **Как** пользователь, **я хочу** видеть свои компетенции в виде наглядной диаграммы, **чтобы** легко определять свои сильные и слабые стороны.

*   **Acceptance Criteria (AC):**
    *   **AC-2.1: Отображение диаграммы**
        *   **Дано:** У пользователя в профиле есть 5 сохраненных компетенций.
        *   **Когда:** Пользователь открывает главный экран.
        *   **Тогда:** Система отображает радиальную (или столбчатую) диаграмму, где каждый сектор/столбец соответствует одной компетенции, а его длина/высота — уровню владения.

    *   **AC-2.2: Интерактивность диаграммы**
        *   **Дано:** Диаграмма компетенций отображена.
        *   **Когда:** Пользователь наводит курсор на сектор "Java".
        *   **Тогда:** Появляется всплывающая подсказка с названием "Java" и уровнем "5/5".

---

#### User Story 3: Определение целевой роли
*   **Как** пользователь, **я хочу** указать свою целевую должность, **чтобы** система понимала, к какой цели я стремлюсь.

*   **Acceptance Criteria (AC):**
    *   **AC-3.1: Успешное сохранение целевой роли**
        *   **Дано:** Пользователь находится в настройках профиля.
        *   **Когда:** Вводит в поле "Целевая должность" значение "Senior Python Developer" и нажимает "Сохранить".
        *   **Тогда:** Система сохраняет эту информацию в профиле и отображает ее на главном экране.

---

#### User Story 4: Получение рекомендаций по обучению
*   **Как** пользователь, **я хочу** по запросу получать список учебных материалов для развития выбранного навыка, **чтобы** устранить пробелы в знаниях.

*   **Acceptance Criteria (AC):**
    *   **AC-4.1: Получение списка рекомендаций**
        *   **Дано:** Пользователь находится на карте компетенций.
        *   **Когда:** Нажимает на компетенцию "SQL" и выбирает "Получить рекомендации".
        *   **Тогда:** Система отображает список из 3-5 релевантных ссылок на внешние ресурсы (например, курсы на Stepik, статьи на Habr) с кратким описанием каждой ссылки.

### Should-Have (Желательно иметь)

*Если позволит время и ресурсы, эти функции должны быть в следующем релизе.*

---

#### User Story 5: Автоматический анализ резюме
*   **Как** пользователь, **я хочу** загрузить свое резюме, **чтобы** система автоматически определила мои навыки и сэкономила мне время на ручном вводе.

*   **Acceptance Criteria (AC):**
    *   **AC-5.1: Успешный парсинг резюме**
        *   **Дано:** Пользователь выбирает опцию "Загрузить резюме".
        *   **Когда:** Загружает файл в формате .pdf или .docx.
        *   **Тогда:** Система анализирует файл и через 10-15 секунд отображает список найденных компетенций (например, "Git, Docker, SQL").

    *   **AC-5.2: Подтверждение и добавление компетенций**
        *   **Дано:** Система предложила список компетенций из резюме.
        *   **Когда:** Пользователь выбирает "Git" и "SQL", снимает галочку с "Docker" и нажимает "Добавить".
        *   **Тогда:** Компетенции "Git" и "SQL" добавляются в его профиль (с уровнем по умолчанию "1" для последующей оценки).

---

#### User Story 6: Отслеживание прогресса
*   **Как** пользователь, **я хочу** отмечать пройденные курсы и видеть, как обновляется моя карта компетенций, **чтобы** отслеживать свой прогресс.

*   **Acceptance Criteria (AC):**
    *   **AC-6.1: Завершение рекомендованного курса**
        *   **Дано:** Пользователь получил рекомендации для навыка "SQL".
        *   **Когда:** Он отмечает один из курсов как "Пройден".
        *   **Тогда:** Система предлагает ему обновить оценку навыка "SQL" (например, с 3 до 4).
        *   **И:** После подтверждения, карта компетенций визуально обновляется.

### Could-Have (Возможно включить)

*Менее важные функции, которые могут быть реализованы, если останется время.*

---

#### User Story 7: Детальное тестирование и оценка
*   **Как** пользователь, **я хочу** проходить тесты для объективной оценки своих навыков, **чтобы** получить точное представление о своем уровне.

*   **Acceptance Criteria (AC):**
    *   **AC-7.1: Прохождение теста**
        *   **Дано:** Пользователь выбирает компетенцию "JavaScript".
        *   **Когда:** Нажимает "Пройти тест".
        *   **Тогда:** Система запускает тест из 10 вопросов с вариантами ответов.
        *   **И:** После завершения теста система показывает результат (например, "8/10 правильных ответов") и автоматически обновляет уровень навыка в профиле.

### Won't-Have (Не будет в этой версии)

*Функции, которые сознательно исключены из скоупа текущего проекта.*

*   Интеграция с HR-системами компаний.
*   Подбор наставников и менторская программа.
*   Социальные функции и сравнение профилей с другими пользователями.

---

## Нефункциональные требования (Non-Functional Requirements, NFR)

*   **NFR-PERF-001: Производительность интерфейса**
    *   **Описание:** Система должна обеспечивать быстрый отклик для комфортной работы пользователя.
    *   **Критерии измерения:**
        *   Время загрузки карты компетенций: не более 2 секунд при наличии до 50 навыков.
        *   Время ответа на действия пользователя (клик, ввод): не более 200 мс.
        *   Время анализа резюме: не более 20 секунд для файлов до 5 МБ.

*   **NFR-SEC-001: Защита данных пользователя**
    *   **Описание:** Персональные данные и информация о компетенциях должны быть надежно защищены.
    *   **Критерии измерения:**
        *   Все данные пользователя, хранящиеся в базе данных, должны быть зашифрованы.
        *   Взаимодействие с сервером должно происходить только по протоколу HTTPS.
        *   Система должна иметь защиту от базовых веб-уязвимостей (OWASP Top 10).

*   **NFR-USAB-001: Удобство использования**
    *   **Описание:** Интерфейс должен быть интуитивно понятным для новых пользователей.
    *   **Критерии измерения:**
        *   Добавление новой компетенции должно занимать не более 3 кликов с главного экрана.
        *   Процесс загрузки резюме и подтверждения навыков должен быть понятен без дополнительной инструкции.

*   **NFR-COMP-001: Совместимость**
    *   **Описание:** Система должна корректно работать в современных браузерах и поддерживать основные форматы файлов.
    *   **Критерии измерения:**
        *   Веб-приложение корректно отображается и функционирует в последних версиях Chrome, Firefox, Safari.
        *   Система успешно обрабатывает файлы резюме в форматах `.pdf` и `.docx`.
