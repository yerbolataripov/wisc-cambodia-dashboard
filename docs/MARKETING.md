# Marketing Strategy Tab — guide для команды

Вкладка **«Маркетинговая стратегия»** (7-я вкладка) — операционный хаб для запуска приёмной комиссии AY 2026-2027. Открывается справа от Power BI.

## Структура

9 sub-tabs:

| # | Sub-tab | Что там |
|---|---|---|
| 1 | Обзор & Countdown | Hero + countdown-карточки по дедлайнам + статусы блоков работ + KPI targets |
| 2 | 🚀 Launch Playbook | **Чеклист для запуска**: 8-day sprint (день за днём), weekly playbook на май-август, growth hacks, risk register. Задачи с 💡 — стратегические добавки поверх исходного брифа |
| 3 | Аудитория & Позиционирование | 3 сегмента (Khmer / Chinese / Elite) + positioning + RTB |
| 4 | Funnel Model | Интерактивный калькулятор воронки + сценарии Conservative/Base/Aggressive |
| 5 | Каналы & Бюджет | Редактируемая таблица каналов (`st.data_editor`) + графики |
| 6 | Креативы & Контент | Production-чеклист (до 29 апр) + 6 content pillars |
| 7 | Admissions & Конверсия | SLA + Parent Journey + возражения + скрипты |
| 8 | Команда (RACI) | Матрица ответственности + ритм встреч |
| 9 | KPI Dashboard | Live-метрики из CSV + графики |

## Код

- [dashboard/marketing_tab.py](../dashboard/marketing_tab.py) — вся логика вкладки (bilingual RU/EN)
- [dashboard/app.py:1295](../dashboard/app.py#L1295) — 7-й `st.tabs()` и вызов `marketing_tab.render(lang)`

## Данные — что и как редактировать

Все файлы лежат в `project/data/`. Streamlit кэширует чтение через `@st.cache_data` — после правки файла на диске нужно **перезагрузить страницу** в браузере (кнопка "Rerun" в правом верхнем углу Streamlit или F5). Для некоторых статусов работает `st.cache_data.clear()` при нажатии Save.

### `marketing_launch_sprint.json`
**9 дней** launch-спринта (23 апр → 1 мая). Структура: `days[].items[]`. Поля item:
- `id` — уникальный ключ (для хранения статуса в session_state)
- `task_ru` / `task_en` — формулировка задачи
- `owner` — ответственный
- `bonus: true` — означает «добавка поверх исходного брифа» (в UI помечена как 💡)

Чтобы добавить задачу — допиши объект в `items` нужного дня. `id` должен быть уникальным.

### `marketing_timeline.json`
7 ключевых дедлайнов запуска. Поля:
- `date` (YYYY-MM-DD) — дата дедлайна
- `title_ru` / `title_en` — название
- `owner` — ответственный
- `deliverables_ru` / `deliverables_en` — результаты
- `status` — начальный статус: `not_started` | `in_progress` | `done`

Цветовая логика countdown-карточек:
- `< 0 дней` → серый (overdue)
- `0-7 дней` → красный
- `8-30 дней` → amber
- `> 30 дней` → navy

### `marketing_channels.csv`
Каналы, бюджеты, CPL-таргеты. Редактируется прямо в UI через `st.data_editor` → кнопка **«Сохранить в CSV»** перезаписывает файл. Можно также править руками в Excel/Numbers (UTF-8).

Столбцы: `channel, priority (P0/P1/P2), monthly_budget_usd, target_cpl_usd, expected_leads_month, owner, status`.

### `marketing_kpi.csv`
Еженедельная фактура. Команда обновляет каждый понедельник после weekly sync.

Столбцы:
- `week_start` (YYYY-MM-DD, понедельник)
- `leads_total`, `qualified_leads`
- `booked_tours`, `tours_completed`
- `applications`, `deposits`, `enrollments`
- `ad_spend_usd`, `cpl_usd`, `speed_to_lead_min`

Пока все строки — нули; дашборд покажет warning «Data source не настроен». После первой недели работы — заполните `2026-05-04` и вкладка оживёт.

### `marketing_enrollment_by_grade.csv`
Разбивка enrollments по grade bands. `current` — обновлять по мере поступления депозитов.

### `marketing_raci.json`
Матрица ответственности. Порядок в `team` строго соответствует позициям в `raci` (массив на каждую задачу). Чтобы добавить задачу — добавь объект в `tasks` с `task_ru`, `task_en`, `raci: ["R","A","C","I","C","I"]` (6 значений в порядке team).

Допустимые буквы: `R` / `A` / `C` / `I` / `""` (пусто).

## Персистентность статусов (важно)

Статусы **блоков работ** на вкладке 3.1 (креативы / скрипты / CRM / …) и deliverables на 3.8 хранятся в `st.session_state` — это значит:
- они **сохраняются пока открыта вкладка** браузера (перезагрузка страницы не теряет)
- они **сбрасываются при рестарте Streamlit-сервера** (деплой, падение процесса)
- они **не шарятся между пользователями**

Если нужна постоянная персистентность — правьте JSON напрямую. Для channels.csv есть кнопка **«Сохранить в CSV»** — она обновляет файл.

## Как добавить новый дедлайн / канал / задачу

1. Открой соответствующий JSON/CSV
2. Добавь запись (для timeline — сохрани формат ISO-даты; для RACI — 6 букв строго по порядку team)
3. Сохрани файл
4. В браузере нажми **Rerun** (или F5)

## Запуск

```bash
cd project
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Вкладка работает **оффлайн** — никаких внешних API-вызовов. Plotly и openpyxl уже в requirements.
