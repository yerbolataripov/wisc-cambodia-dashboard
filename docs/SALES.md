# Sales Strategy Tab — guide для команды

Вкладка **«Стратегия продаж»** (8-я вкладка, справа от «Маркетинговой стратегии») — операционный хаб для Admissions Officer и команды продаж. Разделение зон:

| Вкладка | Зона |
|---|---|
| Маркетинговая стратегия (7) | Привлечение: каналы, креативы, бюджет — **генерация лида** |
| **Стратегия продаж (8)** | Конверсия: **что делать после лида** — скрипты, возражения, туры, обучение, CRM |

## Структура — 10 sub-tabs

| # | Sub-tab | Что там |
|---|---|---|
| 1 | Overview & Performance | Hero с active leads / tours / applications / deposits + enrollment pacing chart + team action items на неделю |
| 2 | Funnel & Pipeline | Live funnel-chart по 9 стадиям + SLA-таблица переходов + редактируемая pipeline-таблица (18 mock-лидов) |
| 3 | Response Playbook | Правила реагирования < 5 мин + auto-reply на 3 языках + разделение мессенджеров по сегментам |
| 4 | Message Scripts | **12 скриптов × 3 языка** (RU/EN/KM) — expandable cards с «когда», «цель», «чего НЕ делать» |
| 5 | Objections Matrix | **15 возражений × 3 языка** + 6-шаговое правило работы + фильтр по категории |
| 6 | Tour Playbook | 60-минутный timeline (от подготовки до close) + 6 правил «никогда не делай» |
| 7 | Training Course | **10 модулей** (3-дневный интенсив 28-30 апреля) с теорией + упражнениями + quiz. Passing score 80% |
| 8 | Product Deep-Dive | Pricing calculator (grade × discounts), program comparison by grade, 10 infrastructure cards с selling lines |
| 9 | Competitor Battle Cards | 7 конкурентов (ISPP, Northbridge, iCAN, CIS, EWIS, Mengly, TBD) — placeholder для Айжан |
| 10 | Sales KPIs | Individual scorecard для ПК (speed-to-lead, show-up, conversions) + recording cadence + incentives proposal |

## Код

- [dashboard/sales_tab.py](../dashboard/sales_tab.py) — вся логика Sales-вкладки
- [dashboard/app.py](../dashboard/app.py) — 8-я вкладка подключена через `sales_tab.render(lang)`
- **Переиспользует** design-system из `marketing_tab.py` (PALETTE + `_inject_styles` + `_divider`) — через import. Визуальная консистентность гарантирована.

## Data-файлы — что править

Все в `project/data/`. Streamlit кэширует через `@st.cache_data` — после правки JSON/CSV обнови страницу в браузере.

### `sales_scripts.json` — **главный файл для команды**
12 скриптов × 3 языка. ПК / Айжан правит тексты напрямую — UI подхватит.

Структура:
```json
{
  "scripts": [
    {
      "id": "s1_first_reply",
      "title": "First reply to inbound lead (within 5 min)",
      "when": "когда использовать",
      "goal": "цель",
      "dont": "чего НЕ делать",
      "en": "английский текст",
      "ru": "русский текст",
      "km": "кхмерский текст"
    }
  ],
  "auto_reply_off_hours": { "en": ..., "ru": ..., "km": ... }
}
```

**Айжан проверяет все кхмерские блоки** — они помечены в UI как `[AIJAN-REVIEW]`.

### `objections_matrix.json`
15 возражений по категориям (Цена / Английский / Язык / Китайский / Репутация / Локация / Время / Сомнения / Документы / Конкурент / Тест / Сертификаты / Оплата / SEN). Поля `objection_ru/en/km`, `answer_ru/en/km`, `rule`, `category`.

В UI — фильтр по категории.

### `sales_pipeline.csv`
Mock-данные pipeline на 18 лидов. В проде команда заменит на реальные данные или подключит CRM-экспорт.

Столбцы: `lead_id, name, phone, grade, source, stage, last_contact, next_action, owner, priority, notes`.

**Stages**: New → Contacted → Qualified → Tour Booked → Tour Done → Application → Entrance Test → Deposit → Enrolled → Lost.

### `training_modules.json`
10 модулей курса для ПК. Каждый модуль:
```json
{
  "id": "m1_product",
  "title": "Module 1: ...",
  "goal": "цель модуля",
  "theory": ["bullet 1", "bullet 2"],
  "video": "placeholder / URL",
  "exercises": ["упражнение 1"],
  "quiz": [
    {
      "q": "вопрос",
      "options": ["A", "B", "C", "D"],
      "correct_idx": 1,
      "explain": "почему B правильный"
    }
  ]
}
```

Quiz интерактивен — ПК выбирает ответ, сразу видит correct/incorrect + объяснение. Пройденные модули отмечаются чекбоксом (session_state).

### `competitor_battle_cards.json`
7 карточек конкурентов (6 заполнены placeholder'ами + 1 TBD). Структура:
```json
{
  "competitors": [
    {
      "id": "ispp",
      "name": "ISPP (International School of Phnom Penh)",
      "tuition_g1": "~$18,000",
      "tuition_g6": "~$22,000",
      "tuition_g10": "~$28,000",
      "strengths": "...",
      "weaknesses": "...",
      "our_edge": "...",
      "pitch": "готовая фраза для родителя"
    }
  ]
}
```

**Айжан финализирует после secret shopping** (задача уже закрыта). Поля tuition можно оставить примерными.

### `sales_kpis.csv`
KPI-рубрика для индивидуального scorecard. Обновляется еженедельно.

Столбцы: `kpi, target, current, unit (pct/min/count), tier (top/mid/bottom/quality/activity), tip`.

Как обновлять: раз в пятницу команда вписывает `current` значения — дашборд показывает цветовые лампочки 🟢🟡🔴.

## Персистентность

Как и в Marketing-вкладке:
- **Статусы модулей курса**, quiz-ответы, редактирование pipeline — в `st.session_state` (живут пока открыт браузер)
- **Сохранение pipeline.csv** — кнопка «💾 Сохранить» перезаписывает файл на диске (действует для всех пользователей)
- Остальные правки — напрямую в JSON/CSV файлы

## Курс обучения — быстрый путь

1. **28 апреля** (T-3): Modules 1-3 (продукт / сегменты / психология) — теория + quiz
2. **29 апреля** (T-2): Modules 4-6 (CRM дисциплина / мессенджеры / phone skills) — теория + role-play
3. **30 апреля** (T-1): Modules 7-10 (tour / objections / closing / excellence) + финальный exam
4. **1 мая**: Go-live

**Passing score** 80%. Retake допускается.

## Запуск

```bash
cd project
pip install -r requirements.txt
streamlit run dashboard/app.py
```

Открой `http://localhost:8501` → Marketing Strategy → Sales Strategy — рядом справа.
