"""
Streamlit Dashboard — WISC Cambodia
Bilingual (RU/EN) with adjustable projection years
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import io
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.financial_model import FinancialModel
from agents.revenue_agent import RevenueAgent
from agents.expense_agent import ExpenseAgent
from agents.growth_agent import GrowthAgent
from agents.risk_agent import RiskAgent
from exports.powerbi_export import PowerBIExporter
from dashboard import marketing_tab
from dashboard import sales_tab

st.set_page_config(page_title="WISC", page_icon="🏫", layout="wide")

# ============================================================
# TRANSLATIONS
# ============================================================
LANG = {
    "ru": {
        "page_title": "WISC — Финансовая модель",
        "title": "WISC Cambodia — Финансовая и маркетинговая стратегия",
        "subtitle_tpl": "{n}-летний финансовый прогноз со сценарным анализом",
        # Sidebar
        "params": "Параметры",
        "language": "Язык / Language",
        "years": "Горизонт (лет)",
        "tuition": "Стоимость обучения ($/год)",
        "enrollment_fee": "Вступительный взнос ($/ученик)",
        "jsm_fee": "Взнос JSM (% от выручки)",
        "jsm_years": "Срок JSM (лет)",
        "salary_tax": "Налог на ЗП (%)",
        "scenario": "Сценарий",
        "scenarios": {"base": "Базовый", "optimistic": "Оптимистичный", "pessimistic": "Пессимистичный"},
        # Tabs
        "tabs": ["Обзор", "Доходы", "Расходы", "Сценарии", "Исследование рынка", "Power BI", "Маркетинговая стратегия", "Стратегия продаж"],
        # Tab 1
        "total_revenue": "Выручка",
        "total_profit": "Прибыль",
        "npv": "NPV (10%)",
        "roi": "ROI",
        "breakeven": "Окупаемость",
        "year_n": "Год {n}",
        "na": "Н/Д",
        "annual_pnl": "Годовой P&L",
        "revenue": "Выручка",
        "expenses": "Расходы",
        "profit": "Прибыль",
        "cum_profit_margin": "Накопленная прибыль и маржа",
        "cum_profit": "Накопленная прибыль",
        "margin_pct": "Маржа %",
        "year": "Год",
        "usd": "USD ($)",
        "margin": "Маржа",
        "y1_monthly": "Год 1 — Помесячный денежный поток",
        "month": "Месяц",
        "pnl_table": "Сводная таблица P&L",
        "students": "Ученики",
        "cum_profit_col": "Накопл. прибыль",
        # Tab 2
        "total_rev_label": "Общая выручка",
        "avg_annual_rev": "Средняя годовая выручка",
        "monthly_tuition": "Ежемесячная плата",
        "rev_by_year": "Выручка по годам",
        "rev_growth": "Темп роста выручки",
        "growth_pct": "Рост (%)",
        "rev_summary": "Сводка по доходам (годовая)",
        "rev_monthly": "Помесячная таблица доходов (Год 1)",
        "rev_monthly_cols": {"month_name": "Месяц", "academic_year": "Уч. год", "period": "Период", "students": "Ученики", "tuition_revenue": "Плата за обучение", "enrollment_fee_revenue": "Вступит. взнос", "total_revenue": "Итого доходы"},
        "rev_monthly_title": "Помесячная таблица доходов",
        "rev_monthly_note": """
**Методика расчёта (Май 2026 — Июль 2027, 15 мес.):**
- **Май-Июль 2026** (набор): собираются вступительные взносы ($350/ученик ÷ 3 мес.) + маркетинг
- **Авг 2026 — Май 2027** (учёба, 10 мес.): плата за обучение (ученики × $4,000 ÷ 10 мес.)
- **Июн-Июль 2027** (каникулы): доходов нет, но ЗП учителям и админ. платится
- Кол-во учеников **одинаково** каждый учебный месяц
""",
        # Tab 3
        "total_exp": "Расходы",
        "cost_student_y1": "Расход/ученик (Г1)",
        "cost_student_last": "Расход/ученик (Г{n})",
        "exp_structure": "Структура расходов (Год 1)",
        "exp_by_cat": "Расходы по категориям (по годам)",
        "exp_table": "Детальная таблица расходов (годовая)",
        "exp_monthly": "Помесячная таблица расходов (Год 1)",
        "exp_monthly_cols": {"month_name": "Месяц", "academic_year": "Уч. год", "period": "Период", "students": "Ученики", "teacher_cost": "ЗП учителей", "admin_cost": "ЗП админ.", "salary_taxes": "Налоги на ЗП", "building": "Содержание здания", "operating": "Операционные", "marketing": "Маркетинг", "jsm_fee": "Взнос JSM", "total_expenses": "Итого расходы", "profit": "Прибыль"},
        "exp_monthly_title": "Помесячная таблица расходов",
        "exp_monthly_note": """
**Методика расчёта расходов:**
- **ЗП учителей** — **авг 2026 — июл 2027** (12 мес., включая каникулы). Годовая ÷ 12.
- **ЗП администрации** — **все 15 мес.** (май 2026 — июл 2027). Годовая ÷ 12.
- **Налоги на ЗП** — 5% от текущего ФОТ за каждый месяц.
- **Содержание здания** — **все 15 мес.** Аренда + коммунальные + ремонт. Годовое ÷ 12.
- **Операционные** — **все 15 мес.** Интернет, канцтовары. Годовые ÷ 12.
- **Маркетинг** — только **май-июль 2026** (весь бюджет ÷ 3 мес.).
- **Взнос JSM** — 10% от платы за обучение, только **авг 2026 — май 2027**.
""",
        "cat_labels": {
            "teacher_cost": "Зарплата учителей",
            "admin_cost": "Зарплата админ.",
            "salary_taxes": "Налоги на ЗП",
            "building": "Содержание здания",
            "operating": "Операционные",
            "marketing": "Маркетинг",
            "jsm_fee": "Взнос JSM"
        },
        # Tab 4
        "scenario_compare": "Сравнение сценариев",
        "profit_by_scenario": "Прибыль по сценариям",
        "cum_by_scenario": "Накопленная прибыль по сценариям",
        "annual_profit": "Годовая прибыль ($)",
        "enrollment_forecast": "Прогноз набора учеников",
        "max_cap": "Макс. вместимость",
        "utilization": "Загрузка %",
        "sensitivity": "Анализ чувствительности — Стоимость обучения",
        "current": "Текущая",
        "tuition_year": "Стоимость обучения ($/год)",
        "stress_tests": "Стресс-тесты",
        # Tab 5
        "market_title": "Рынок образования Камбоджи — Глубокое исследование",
        "market_source": "Источник: World Bank API (2024), Wikipedia, проверено март 2026",
        "macro_overview": "Макроэкономический обзор (World Bank 2024)",
        "population": "Население",
        "gdp": "ВВП",
        "gdp_capita": "ВВП/душу",
        "urbanization": "Урбанизация",
        "gdp_growth": "Рост ВВП",
        "private_ed_growth": "Рост частного образования",
        "secondary_growth": "Рост среднего образования",
        "private_share_axis": "Доля частного нач. образования (%)",
        "private_title": "Рост в 4 раза за 9 лет (CAGR ~17%)",
        "secondary_axis": "Охват средним образованием (%)",
        "secondary_title": "Растущий рынок: +2 п.п./год",
        "school_age": "Школьный возраст (6-18)",
        "private_share": "Доля частных (оц.)",
        "edu_spend": "Расходы на обр.",
        "gni_capita": "ВНД/душу",
        "demographics": "Демография и спрос (World Bank 2024)",
        "demo_text": """
    - **Население**: 17.64 млн, медианный возраст 26 лет — очень молодая страна
    - **Дети школьного возраста (6-18)**: ~4.2 млн
    - **Урбанизация**: **40.9%** — крупный городской рынок
    - **ВНД на душу**: $2,550 — растущий средний класс
    - **Рост ВВП**: 5.5%/год — один из самых быстрых в ASEAN
    - **Коэффициент рождаемости**: 2.58""",
        "edu_system": """
    ### Система образования
    - **Структура**: 6+3+3 (Начальная 1-6, Средняя 7-9, Старшая 10-12)
    - **Учебный год**: октябрь — август (каникулы авг-сен)
    - **Программа**: национальная программа MoEYS (обязательна)
    - **Экзамены**: 9 класс, Бакалавриат 12 класса (BAC II)
    - **Начальное**: 109% охват — полное покрытие
    - **Среднее**: 58.8% — **растущая возможность** (+2 п.п./год)""",
        "competition": "Конкурентная среда",
        "comp_cols": ["Сегмент", "Стоимость ($/год)", "Кол-во школ", "Размер класса"],
        "comp_segments": ["Бюджетный\n$200-800", "Средний\n$800-2,500", "Премиум\n$2,500-5,000", "Международный\n$5,000-20,000"],
        "your_school": "ВАША ШКОЛА\n$4,000/год",
        "num_schools": "Примерное кол-во школ",
        "market_pos_title": "Ваша позиция: верхний премиум-сегмент",
        "your_position": """
    ### Ваша позиция: Премиум ($4,000/год)
    - Верхний сегмент премиум-класса
    - Конкуренция: ~100-200 школ
    - Ключевые отличия: качество преподавания, оснащение, английский, результаты экзаменов
    - **Попутный ветер**: рост частного образования ~17% CAGR""",
        "competitors_title": "Прямые конкуренты WISC",
        "comp_name": "Школа",
        "comp_tuition": "Стоимость ($/год)",
        "comp_grades": "Классы",
        "comp_curriculum": "Программа",
        "comp_strengths": "Сильные стороны",
        "comp_students": "Учеников",
        "comp_direct_data": [
            ["East-West International (EWIS)", "4,320-7,040", "K-12", "Cambridge + MoEYS", "Лидер билингвал. сегмента, WASC аккредитация", 465],
            ["Footprints International", "2,706-6,250", "K-12", "Cambridge + MoEYS", "Билингвал Khmer/English, 2 кампуса, WASC", "1,000+"],
            ["Paragon International", "4,650-13,620", "K-12", "Cambridge (CAIE)", "Крупный бренд, CIS аккредитация, бывш. Zaman", "1,100+"],
            ["The Westline School", "~1,000", "K-12", "MoEYS + англ. + кит.", "19 кампусов (WEG), 13,000+ учеников", "13,000+"],
            ["BELTEI International", "300-800", "K-12", "MoEYS + ESL (амер.)", "26 кампусов в ПП, ISO 9001, самая крупная сеть", "10,000+"],
            ["Home of English", "4,611-4,862", "K-12", "Американская + MoEYS", "IB аккредитация, 40+ нац-стей, 4 кампуса", 500],
            ["CIA First International", "3,950-7,550", "K-12", "Американская (AP)", "WASC, AP Capstone, 4 кампуса, 5,500 учеников", "5,500+"],
        ],
        "comp_details": [
            {
                "name": "East-West International School (EWIS)",
                "founded": "2006",
                "website": "ewiscambodia.edu.kh",
                "campuses": "1 кампус, BKK3",
                "students": "~465 учеников, 25+ национальностей",
                "staff": "88 учителей",
                "accreditation": "WASC, Cambridge International, MoEYS",
                "curriculum": "IPC / IMYC / Cambridge IGCSE / AS / A Levels + кхмерская нац. программа",
                "languages": "Английский, Кхмерский (билингвал)",
                "fees": "Nursery $4,320 · K $5,800 · 1-3 $5,970 · 4-5 $6,320 · 6-8 $6,630 · 9-12 $7,040",
                "features": "95% выпускников поступают в вузы, 11+ партнёрств с университетами, скидка 5-20% для сиблингов",
                "source": "ewiscambodia.edu.kh, international-schools-database.com",
            },
            {
                "name": "Footprints International School",
                "founded": "2007",
                "website": "footprintsschool.edu.kh",
                "campuses": "2 кампуса: Toul Kork, Toul Tom Poung",
                "students": "1,000+ учеников, 15+ национальностей",
                "staff": "329 сотрудников и учителей",
                "accreditation": "WASC, Cambridge (CAIE), MoEYS",
                "curriculum": "IEYC / IPC / Cambridge + кхмерская нац. программа",
                "languages": "Английский, Кхмерский, Мандаринский",
                "fees": "Nursery $2,706 · K $4,563 · 1-5 $5,106 · 6-8 ~$5,500 · 9-12 $6,250",
                "features": "95% кхмерских / 5% международных учеников, скидки 15-20% для сиблингов, медцентр на кампусе",
                "source": "footprintsschool.edu.kh, international-schools-database.com",
            },
            {
                "name": "Paragon International School (бывш. Zaman)",
                "founded": "1997",
                "website": "paragonisc.edu.kh",
                "campuses": "1 новый объединённый кампус (2025), Svay Pak",
                "students": "1,100+ учеников",
                "staff": "Учителя из 9+ стран",
                "accreditation": "CIS (Council of International Schools), Cambridge (CAIE), MoEYS",
                "curriculum": "Билингвальная (Khmer + Cambridge) и Международная (полный CAIE: IGCSE, AS/A Levels)",
                "languages": "Английский, Кхмерский",
                "fees": "$4,650-13,620 (зависит от класса и программы), скидки 15-20% сиблингам",
                "features": "Одна из старейших международных школ Камбоджи, CIS аккредитация (редкость), новый современный кампус 2025",
                "source": "paragonisc.edu.kh, wikipedia.org, schoolscambodia.com",
            },
            {
                "name": "The Westline School (WEG)",
                "founded": "2008",
                "website": "wegcambodia.com",
                "campuses": "19 кампусов (Westline Education Group)",
                "students": "13,000+ учеников (группа WEG)",
                "staff": "1,000+ сотрудников",
                "accreditation": "MoEYS",
                "curriculum": "Кхмерская нац. программа + ESL (американский стандарт) + китайский",
                "languages": "Английский, Кхмерский, Китайский",
                "fees": "~$1,000/год — одна из самых доступных",
                "features": "Крупнейшая сеть по числу учеников, рост с 600 до 13,000+ за 15 лет, собственный институт подготовки учителей (EDI)",
                "source": "wegcambodia.com, schoolscambodia.com, phnompenhpost.com",
            },
            {
                "name": "BELTEI International School",
                "founded": "2002",
                "website": "beltei.edu.kh",
                "campuses": "26 кампусов в Пном Пене",
                "students": "10,000+ (оценка, 26 кампусов × 30-40 в классе)",
                "staff": "Не раскрывается",
                "accreditation": "MoEYS, ISO 9001:2008, TAYO ASEAN Award",
                "curriculum": "Кхмерская нац. программа + ESL (американский стандарт), IT, бизнес",
                "languages": "Английский, Кхмерский",
                "fees": "$300-800/год (оценка) — бюджетный сегмент",
                "features": "BELTEI = Business, Economics, Law, Tourism, English, IT. Самая крупная сеть кампусов, есть собственный университет (BIU)",
                "source": "beltei.edu.kh, educationcambodia.org, schoolscambodia.com",
            },
            {
                "name": "Home of English International School",
                "founded": "1997 (начат в 1993 в Индонезии)",
                "website": "homeofenglish.edu.kh",
                "campuses": "4 кампуса: BKK3 (главный), BKK3 (детсад), Toul Kork/Sen Sok, Prek Eng/Mean Chey",
                "students": "Не раскрывается, 40+ национальностей",
                "staff": "Низкое соотношение ученик/учитель",
                "accreditation": "IB (International Baccalaureate), MoEYS, CIS, AISA",
                "curriculum": "Американская + кхмерская, диплом US, критическое мышление",
                "languages": "Английский (основной), Кхмерский",
                "fees": "1-4 класс $4,611 · 5-8 $4,862 · 9-12 $4,847 · регистрация $244",
                "features": "IB аккредитация (редкость в Камбодже), международное сообщество, фокус на благотворительность",
                "source": "homeofenglish.edu.kh, international-schools-database.com, educationcambodia.org",
            },
            {
                "name": "CIA First International School",
                "founded": "2004 (начали с 17 детей)",
                "website": "ciaschool.edu.kh",
                "campuses": "4 кампуса: Sen Sok 1 (K-8), Sen Sok 2 (9-12), Chbar Ampov (K-12), Russey Keo (K-8)",
                "students": "5,500+ учеников, 20+ национальностей",
                "staff": "398 учителей, 1,100+ персонала",
                "accreditation": "WASC, AP (College Board), MoEYS",
                "curriculum": "Американская (Common Core, AERO, NGSS), 20+ предметов AP, AP Capstone Diploma (первая в Камбодже)",
                "languages": "Английский (основной), Кхмерский (FTC трек)",
                "fees": "K3-K5 $3,950-5,950 · 1-5 $6,600 · 6-8 $7,550 · 9-12 выше · регистрация $850",
                "features": "Крупнейшая премиум международная школа Камбоджи, первая AP Capstone, куплена Navis Capital (2020), рост с 17 до 5,500",
                "source": "ciaschool.edu.kh, international-schools-database.com, schrole.com",
            },
        ],
        "comp_intl_data": [
            ["ISPP", "9,500-29,000", "IB", "#1 международная, nonprofit, семьи дипломатов"],
            ["Northbridge (Nord Anglia)", "8,000-22,000", "Британская", "Глобальная сеть, премиум оснащение"],
            ["iCAN British", "5,000-13,000", "Британская", "Растущая школа"],
            ["Canadian International (CIS)", "6,600-19,400", "Канадская (Alberta)", "3 кампуса, сильная репутация"],
            ["Logos International", "4,000-8,000", "Американская", "Христианская школа, сообщество"],
        ],
        "competitors_intl_title": "Международные школы (верхний сегмент)",
        "comp_wisc_title": "Позиционирование WISC",
        "comp_wisc_text": """
- **Цена WISC ($4,000/год)** — верхние 30% прямых конкурентов
- Дороже чем EWIS ($1,680-3,500) и BELTEI ($1,500-3,000)
- На уровне CIA First ($4,000-6,000) и Home of English ($4,600-4,900)
- Значительно дешевле международных (ISPP $9,500-29,000)
- **Отстройка**: билингвал + малые классы + STEM + русский язык""",
        "regulations": "Нормативные требования (MoEYS)",
        "reg_cols": ["Требование", "Детали"],
        "reg_rows": [
            ["Лицензия", "Одобрение MoEYS — заявка + инспекция"],
            ["Программа", "Обязательное следование национальной программе"],
            ["Учителя", "Минимум степень бакалавра, педсертификат желательно"],
            ["Помещения", "Стандарты площади, требования безопасности"],
            ["Размер класса", "Макс. 45 (гос.), частные обычно 25-35"],
            ["Регистрация", "Мин. торговли + MoEYS"],
            ["Отчётность", "Ежегодно: ученики и результаты экзаменов"]
        ],
        "pp_private_title": "Частные школы Пном Пеня",
        "pp_schools": "Частных школ",
        "pp_public_schools": "Государственных школ",
        "pp_nationwide": "Частных по стране",
        "pp_share": "Доля Пном Пеня",
        "pp_students_est": "Учеников (оц. 2024)",
        "pp_students_nationwide": "По стране (оц.)",
        "pp_text": """
- **519 частных школ** в Пном Пене vs 251 государственных — частный сектор доминирует (67%)
- По стране: **2,295 частных школ** (2024-2025, MoEYS)
- Пном Пень = **22.6%** всех частных школ страны
- Оценка учеников в частных школах Пном Пеня: **~120,000** (2024)
- Рост с 2019: тогда было 218,357 учеников в 1,222 школах по стране — сейчас ~450,000 в 2,295 школах""",
        "pp_by_level_title": "Ученики частных школ Пном Пеня по классам",
        "pp_level": "Уровень",
        "pp_schools_count": "Школ",
        "pp_students_count": "Учеников",
        "pp_grade": "Класс",
        "pp_level_data": [
            ["Детский сад", 120, "12,000"],
            ["Начальная (1-6)", 195, "55,000"],
            ["Средняя (7-9)", 120, "32,000"],
            ["Старшая (10-12)", 84, "21,000"],
            ["Итого", 519, "120,000"],
        ],
        "pp_enrollment_rates": "Охват по уровням (MoEYS 2023-2024)",
        "pp_nationwide_title": "Школы по стране (MoEYS 2022-2023)",
        "salary_title": "Зарплаты учителей в частных школах",
        "salary_cols": ["Тип школы", "Мин ($/мес)", "Макс ($/мес)", "Примечание"],
        "salary_text": """
- **Гос. школы**: $250-350/мес — базовая ставка MoEYS
- **Бюджетные частные**: $200-400/мес — локальные школы с низкой стоимостью
- **Средний сегмент**: $350-700/мес — конкурентоспособная оплата
- **Премиум школы**: $500-1,200/мес — высокие требования к квалификации
- **Иностранные учителя (ESL)**: $800-1,200/мес — языковые академии
- **Международные школы**: $1,500-2,500/мес — полный пакет (жильё, страховка, перелёт)""",
        "salary_note": "💡 Для WISC (премиум, $4,000/год) ожидаемая ЗП учителей: **$500-1,200/мес**",
        "moeys_title": "Стандарт MoEYS — Национальная программа",
        "moeys_overview": "Общая информация",
        "moeys_structure_label": "Структура",
        "moeys_year_label": "Учебный год",
        "moeys_weeks_label": "Уч. недель",
        "moeys_lesson_label": "Урок (мин)",
        "moeys_lang_label": "Язык обучения",
        "moeys_primary_title": "Начальная школа (1-6 класс)",
        "moeys_secondary_title": "Средняя школа (7-9 класс)",
        "moeys_upper_title": "Старшая школа (10-12 класс)",
        "moeys_subject": "Предмет",
        "moeys_lessons_week": "Уроков/нед",
        "moeys_notes": "Примечание",
        "moeys_grades_1_3": "1-3 класс",
        "moeys_grades_4_6": "4-6 класс",
        "moeys_exams_title": "Ключевые экзамены",
        "moeys_exam_name": "Экзамен",
        "moeys_exam_desc": "Описание",
        "moeys_teacher_req_title": "Требования к учителям (MoEYS)",
        "moeys_private_rules_title": "Правила для частных школ",
        "moeys_private_rules_text": """
- **Обязательно**: следовать национальной программе MoEYS
- **Кхмерский язык** — обязательный предмет во всех частных школах
- **Можно добавлять**: билингвальные программы, международные учебные планы (Cambridge, IB)
- **Лицензия MoEYS** обязательна + ежегодная инспекция помещений
- **Ежегодная отчётность**: кол-во учеников и результаты экзаменов
- **Реформа 2025**: переход на 4-летнюю подготовку учителей (или 1 год для бакалавров)""",
        "moeys_seasons_note": "💡 WISC может расширять программу сверх MoEYS: добавить углублённый English, STEM, русский язык — при условии сохранения обязательных предметов",
        "social_title": "Охват социальных сетей в Камбодже",
        "social_users": "Пользователей (млн)",
        "social_penetration": "Охват %",
        "social_platform": "Платформа",
        "social_best_for": "Применение для школы",
        "social_total": "Всего в соц. сетях",
        "social_population": "от населения",
        "fb_ads_title": "Facebook Ads — Камбоджа",
        "fb_cpc": "CPC (клик)",
        "fb_cpm": "CPM (1000 показов)",
        "fb_cpl": "CPL (лид, обр.)",
        "fb_discount": "Дешевле чем US",
        "acq_title": "Каналы привлечения учеников",
        "acq_channel": "Канал",
        "acq_share": "Доля %",
        "acq_cost": "Стоимость",
        "acq_note": "Примечание",
        "recruit_title": "Каналы найма учителей",
        "recruit_channel": "Канал",
        "recruit_target": "Аудитория",
        "recruit_cost": "Стоимость",
        "recruit_note": "Примечание",
        "recruit_best_months": "Лучшее время найма: июнь-август",
        "persona_title": "Портрет родителей — целевые сегменты",
        "persona_segment": "Сегмент",
        "persona_share": "Доля %",
        "persona_income": "Доход семьи ($/мес)",
        "persona_profile": "Профиль",
        "persona_priority": "Приоритет в обр.",
        "persona_channels": "Каналы",
        "persona_location": "Районы",
        "persona_common_title": "Общие черты целевых родителей",
        "persona_decision": "Решение принимает",
        "persona_research": "Период выбора школы",
        "persona_touches": "Касаний до записи",
        "persona_concern": "Главный запрос",
        "persona_breaker": "Стоп-фактор",
        "persona_children": "Среднее кол-во детей",
        "weeks_label": "нед.",
        "social_platforms_data": {
            "Parent communities, school pages, ads, groups": "Родительские сообщества, страницы школ, реклама, группы",
            "Short video, school life, young parents 25-35": "Короткие видео, жизнь школы, молодые родители 25-35",
            "Parent groups, announcements, enrollment comms": "Родительские группы, объявления, коммуникация о наборе",
            "Direct parent communication, rural areas": "Прямая связь с родителями, сельские районы",
            "Visual branding, premium positioning, expat parents": "Визуальный бренд, премиум-позиция, экспат-родители",
            "School tours, teacher intros, long-form content": "Туры по школе, знакомство с учителями, длинный контент",
            "Teacher recruitment, B2B partnerships": "Найм учителей, B2B-партнёрства",
        },
        "acq_channels_data": [
            ["Сарафанное радио", "40%", "Низкая"],
            ["Facebook (орг. + реклама)", "25%", "Низкая-Средняя"],
            ["День открытых дверей", "15%", "Средняя"],
            ["TikTok / YouTube контент", "8%", "Низкая"],
            ["Онлайн-каталоги", "5%", "Низкая"],
            ["Билборды / Печать", "4%", "Высокая"],
            ["Партнёрства / Посольства", "3%", "Низкая"],
        ],
        "acq_chart_labels": ["Сараф. радио", "Facebook", "Open House", "TikTok", "Каталоги", "Билборды", "Партнёрства"],
        "recruit_channels_data": [
            ["Facebook-группы", "Местные + Иностр.", "Бесплатно"],
            ["Khmer24.com", "Местные кхмеры", "Бесплатно"],
            ["BongThom.com", "Местные кхмеры", "Бесплатно"],
            ["CamHR.com", "Местные + Иностр.", "Средняя"],
            ["LinkedIn", "Иностр. + Управл.", "Средне-Высокая"],
            ["Teach Away / Schrole", "Иностранные", "Высокая"],
            ["Приход в школу / Реферал", "Местные", "Бесплатно"],
            ["Партнёрства с вузами", "Местные начинающие", "Низкая"],
        ],
        "persona_segments_data": [
            {
                "name": "Кхмерский верхний средний",
                "profile": "Семья с двумя доходами, владельцы бизнеса или специалисты, 30-45 лет",
                "priority": "Билингвальное (кхмер+английский), результаты экзаменов, подготовка к вузу",
                "channels": "Facebook, Сарафанное радио, Telegram-группы",
                "factors": "Качество обучения | Уровень английского | Репутация школы | Результаты экзаменов",
            },
            {
                "name": "Кхмерский состоятельный",
                "profile": "Владельцы бизнеса, чиновники, 35-50 лет",
                "priority": "Международная программа, путь в зарубежный вуз, престиж",
                "channels": "Instagram, Сарафанное радио, Прямой контакт",
                "factors": "Бренд/престиж | Международная аккредитация | Оснащение | Нетворкинг",
            },
            {
                "name": "Семьи экспатов",
                "profile": "Сотрудники НКО, дипломаты, предприниматели, 30-50 лет",
                "priority": "Обучение на англ., признанная программа (Cambridge/IB), мобильность",
                "channels": "Экспат-форумы, Facebook-группы, Сети посольств, Онлайн-каталоги",
                "factors": "Признание программы | Качество англ. | Сообщество | Безопасность",
            },
            {
                "name": "Кхмерский амбициозный",
                "profile": "Один доход, квалифиц. работники, первое поколение в частной школе, 28-40 лет",
                "priority": "Лучше чем гос. школа, навыки английского, безопасная среда",
                "channels": "Facebook, TikTok, Соседи/родственники",
                "factors": "Доступность | Расположение/транспорт | Программа англ. | Безопасность",
            },
        ],
        "persona_common_data": {
            "decision_maker": "Мать (70-80%), отец консультирует",
            "research_period": "4 нед.",
            "top_concern": "Качество обучения английскому",
            "deal_breaker": "Безопасность, расстояние, скрытые платежи",
        },
        "mktg_title": "Рекомендации по маркетинговым кампаниям",
        "mktg_funnel_title": "Воронка набора учеников",
        "mktg_funnel_stages": ["Охват", "Интерес", "Рассмотрение", "Заявка", "Зачисление"],
        "mktg_budget_title": "Рекомендуемое распределение бюджета",
        "mktg_channel": "Канал",
        "mktg_budget_pct": "Доля %",
        "mktg_budget_usd": "Бюджет $",
        "mktg_leads": "Ожид. лидов",
        "mktg_campaigns_title": "Рекомендуемые кампании",
        "mktg_timing": "Период",
        "mktg_goal": "Цель",
        "mktg_tactics": "Тактики",
        "mktg_kpi": "KPI",
        "mktg_calendar_title": "Маркетинговый календарь",
        "mktg_period": "Период",
        "mktg_activity": "Активность",
        "mktg_monthly_budget": "Рекомендуемый бюджет/мес",
        "mktg_cost_per_enroll": "Стоимость зачисления",
        "mktg_enrollments_mo": "Зачислений/мес",
        "mktg_total_leads": "Лидов/мес",
        "mktg_campaigns_data": [
            {
                "name": "Ранняя запись",
                "goal": "Обеспечить ранние зачисления со скидкой на обучение",
                "tactics": "Скидка 5-10% за раннюю запись | Обратный отсчёт в рекламе | Видео-отзывы родителей | Ограниченные места",
                "kpi": "100+ зачислений",
            },
            {
                "name": "День открытых дверей",
                "goal": "Привлечь семьи на кампус, 25-30% конверсия визит→заявка",
                "tactics": "Трансляция тура в Facebook | Студенческие TikTok-туры | Угощения/подарки | Ответ по email за 24ч",
                "kpi": "100+ семей на событие",
            },
            {
                "name": "Реферальная волна",
                "goal": "Задействовать текущих родителей, конверсия 4x vs холодные лиды",
                "tactics": "Кредит $300 за зачисленного реферала | Бейджи амбассадоров | Таблица лидеров с призами | Эксклюзивные мероприятия",
                "kpi": "60+ реферальных зачислений/год",
            },
            {
                "name": "TikTok — Жизнь школы",
                "goal": "Узнаваемость среди молодых родителей 25-35",
                "tactics": "Видео «День ученика» | Серия об учителях | Уроки английского | Прогресс учеников до/после",
                "kpi": "300K+ просмотров/мес, 1500+ подписчиков/мес",
            },
            {
                "name": "Назад в школу",
                "goal": "Поздние зачисления + узнаваемость на следующий год",
                "tactics": "Контент «первый день» | Родительское сообщество | Витрина достижений | Билборды у школ",
                "kpi": "50+ поздних зачислений",
            },
            {
                "name": "Витрина результатов",
                "goal": "Укрепить доверие через результаты экзаменов 9/12 класс",
                "tactics": "Истории успеха учеников | Инфографика сравнения | Поступления в вузы | Видео-отзывы родителей",
                "kpi": "Доверие к бренду, 500+ запросов",
            },
        ],
        "mktg_calendar_data": [
            ["Янв-Фев", "Создание контента, SEO-оптимизация"],
            ["Мар-Май", "Кампания «Ранняя запись», серия Open House"],
            ["Май-Июл", "Пиковый набор, Реферальная волна"],
            ["Авг-Сен", "Кампания «Назад в школу», поздний набор"],
            ["Окт-Ноя", "Витрина результатов экзаменов, имидж"],
            ["Дек", "Итоги года, планирование следующего"],
        ],
        "launch_title": "План набора 180 учеников (Апрель — Июль)",
        "launch_subtitle": "Пошаговый план запуска WISC — от 0 до 180 учеников за 4 месяца",
        "launch_total_budget": "Общий бюджет",
        "launch_target": "Цель",
        "launch_period": "Период",
        "launch_cost_per": "За ученика",
        "launch_month": "Месяц",
        "launch_phase": "Фаза",
        "launch_budget": "Бюджет",
        "launch_enrollments": "Зачисления",
        "launch_cumulative": "Накоплено",
        "launch_channels": "Каналы",
        "launch_actions": "Ключевые действия",
        "launch_kpis_title": "Целевые KPI за 4 месяца",
        "launch_leads": "Лидов всего",
        "launch_oh_attendees": "Посетителей Open House",
        "launch_referrals": "Реферальных зачислений",
        "launch_fb_reach": "Охват Facebook",
        "launch_tiktok_views": "Просмотров TikTok",
        "launch_website": "Визитов на сайт",
        "launch_conversion": "Конверсия",
        "launch_months_data": [
            {"month": "Апрель", "phase": "Запуск и узнаваемость"},
            {"month": "Май", "phase": "Пиковый набор"},
            {"month": "Июнь", "phase": "Конверсия лидов"},
            {"month": "Июль", "phase": "Срочность и финальное закрытие"},
        ],
        "launch_actions_data": [
            ["Грандиозное открытие", "Видео-туры по школе", "Скидка -10% Early Bird", "Билборды в 5 районах", "Пресс-релиз + СМИ"],
            ["3 Open House (по выходным)", "Запуск реферала: кредит $300", "Кампания отзывов родителей", "Таргет по районам", "Telegram-группа родителей"],
            ["Ретаргетинг тёплых лидов", "Последний шанс Early Bird", "Индивидуальные туры 1-на-1", "Реферальный буст с призами", "Мероприятия для экспатов"],
            ["Обратный отсчёт мест", "Личные звонки всем тёплым лидам", "Финальный Open House", "Работа амбассадоров", "Предпоказ формы/материалов"],
        ],
        "launch_risks_title": "Риски набора 180 учеников",
        "launch_risk": "Риск",
        "launch_risk_impact": "Влияние",
        "launch_risk_prob": "Вероятность",
        "launch_risk_desc": "Описание",
        "launch_risk_mitig": "Как снизить",
        "launch_risks_data": [
            {"risk": "Нет бренда / репутации", "impact": "Критический", "prob": "Высокая", "desc": "Новая школа без выпускников, результатов экзаменов, отзывов — родители колеблются", "mitig": "Open House, пробные уроки, профили учителей, партнёрство с известными брендами, ранние отзывы"},
            {"risk": "Короткое окно набора", "impact": "Высокое", "prob": "Высокая", "desc": "4 месяца — агрессивно, большинство школ набирают 6-12 мес., родителям нужно 4+ нед. на решение", "mitig": "Основной бюджет в апрель-май, пре-маркетинг с марта, тактика срочности, отклик за 24ч"},
            {"risk": "Конкуренция устоявшихся школ", "impact": "Высокое", "prob": "Высокая", "desc": "519 частных школ в Пном Пене с лояльной базой, связями, проверенными результатами", "mitig": "Уникальные отличия (билингвал, малые классы, современное оснащение), фокус на недообслуженные районы"},
            {"risk": "Задержка лицензии MoEYS", "impact": "Критический", "prob": "Средняя", "desc": "Одобрение лицензии может занять 2-6 мес., без неё нельзя легально зачислять учеников", "mitig": "Начать процесс немедленно, нанять консультанта, подготовить все документы заранее"},
            {"risk": "Учителя не наняты вовремя", "impact": "Высокое", "prob": "Средняя", "desc": "Родители приходят — учителей нет. Нужно 15-20 учителей для 180 учеников", "mitig": "Нанять ядро (5-8 учителей) до начала маркетинга, показывать профили в рекламе"},
            {"risk": "Помещения не готовы", "impact": "Критический", "prob": "Средняя", "desc": "Задержки стройки/ремонта → Open House в незаконченном здании → потеря доверия", "mitig": "Подготовить 3-4 показательных класса к апрелю, 3D-рендеры для остальных зон"},
            {"risk": "Сопротивление цене $4,000/год", "impact": "Среднее", "prob": "Высокая", "desc": "Премиум цена в рынке где средний сегмент $800-2,500 — ограничивает аудиторию до 10-15% семей", "mitig": "Чётко объяснять ценность, рассрочка (помесячно), скидка Early Bird, скидки на 2-го ребёнка, 2-3 стипендии"},
            {"risk": "Усталость от рекламы", "impact": "Среднее", "prob": "Средняя", "desc": "Массированная реклама за 4 мес. → усталость аудитории, рост CPL, падение CTR", "mitig": "Ротация креативов каждые 2 нед., диверсификация каналов, органический контент, сарафанное радио"},
            {"risk": "Сезонный конфликт", "impact": "Среднее", "prob": "Средняя", "desc": "Апрель = Кхмерский Новый год (1 нед.), июнь-июль = сезон дождей — меньше трафика", "mitig": "Планировать вокруг Нового года, Open House в сухие выходные, онлайн-туры, транспорт в дождь"},
            {"risk": "Низкая конверсия", "impact": "Высокое", "prob": "Средняя", "desc": "Воронка = 1.5% конверсия. Если реально 0.8-1.0% → нужно 2x больше лидов = 2x бюджет", "mitig": "Отслеживать еженедельно, A/B тесты лендингов, скорость отклика, обучение отдела продаж, резерв +20%"},
        ],
        "risk_matrix": "Матрица рисков",
        "probability": "Вероятность",
        "impact": "Влияние",
        "prob_levels": ["Низкая", "Средняя", "Высокая"],
        "impact_levels": ["Низкое", "Среднее", "Высокое"],
        "opportunities": "Возможности для роста",
        "opp_cols": ["Возможность", "Потенциал дохода", "Спрос", "Реализация"],
        "opp_rows": [
            ["Английский язык", "Высокий", "Очень высокий", "Легко"],
            ["Доп. занятия", "Высокий", "Высокий", "Легко"],
            ["STEM-программы", "Средний", "Растущий", "Средне"],
            ["Школьный автобус", "Средний", "Высокий", "Сложно"],
            ["Летние программы", "Средний", "Средний", "Легко"],
            ["Родительское сообщество", "Низкий (косвенный)", "Высокий", "Легко"]
        ],
        # Tab 6
        "pbi_title": "Экспорт в Power BI",
        "pbi_desc": "Экспорт данных финансовой модели в форматах, готовых для Power BI. Скачайте Excel и импортируйте в Power BI Desktop.",
        "excel_export": "Excel-экспорт",
        "download_excel": "Скачать Excel (.xlsx)",
        "sheets_info": "8 листов со всеми данными модели",
        "dax_title": "DAX-формулы",
        "download_dax": "Скачать DAX (.dax)",
        "dax_info": "Готовые формулы для Power BI",
        "guide_title": "Инструкция",
        "download_guide": "Скачать инструкцию (.txt)",
        "guide_info": "Пошаговая настройка Power BI",
        "data_preview": "Предпросмотр данных",
        "select_table": "Выберите таблицу",
        "rows_cols": "{r} строк x {c} столбцов",
        "dax_ref": "DAX-формулы (справка)",
        "pbi_setup": "Инструкция по настройке Power BI",
        "pbi_steps": """
    1. **Импорт**: Power BI Desktop > Получить данные > Excel > выберите `.xlsx`
    2. **Выберите все листы** > Загрузить
    3. **Создайте связи** в представлении Модель
    4. **Добавьте DAX-формулы** из скачанного файла
    5. **Создайте визуализации** по инструкции""",
        "theme_title": "Тема оформления (JSON)",
        "download_theme": "Скачать тему (.json)",
        "footer": "WISC Cambodia — Финансовая модель | Streamlit + Python | Power BI Ready",
        "mln": "млн",
        "mlrd": "млрд",
    },
    "en": {
        "page_title": "WISC — Financial Model",
        "title": "WISC Cambodia — Financial & Marketing Strategy",
        "subtitle_tpl": "{n}-year financial projection with scenario analysis",
        "params": "Parameters",
        "language": "Language / Язык",
        "years": "Horizon (years)",
        "tuition": "Tuition ($/year)",
        "enrollment_fee": "Enrollment Fee ($/student)",
        "jsm_fee": "JSM Fee (% of revenue)",
        "jsm_years": "JSM Duration (years)",
        "salary_tax": "Salary Tax (%)",
        "scenario": "Scenario",
        "scenarios": {"base": "Base", "optimistic": "Optimistic", "pessimistic": "Pessimistic"},
        "tabs": ["Overview", "Revenue", "Expenses", "Scenarios", "Market Research", "Power BI", "Marketing Strategy", "Sales Strategy"],
        "total_revenue": "Revenue",
        "total_profit": "Profit",
        "npv": "NPV (10%)",
        "roi": "ROI",
        "breakeven": "Breakeven",
        "year_n": "Year {n}",
        "na": "N/A",
        "annual_pnl": "Annual P&L",
        "revenue": "Revenue",
        "expenses": "Expenses",
        "profit": "Profit",
        "cum_profit_margin": "Cumulative Profit & Margin",
        "cum_profit": "Cumulative Profit",
        "margin_pct": "Margin %",
        "year": "Year",
        "usd": "USD ($)",
        "margin": "Margin",
        "y1_monthly": "Year 1 — Monthly Cash Flow",
        "month": "Month",
        "pnl_table": "P&L Summary Table",
        "students": "Students",
        "cum_profit_col": "Cumul. Profit",
        "total_rev_label": "Total Revenue",
        "avg_annual_rev": "Avg Annual Revenue",
        "monthly_tuition": "Monthly Tuition",
        "rev_by_year": "Revenue by Year",
        "rev_growth": "Revenue Growth Rate",
        "growth_pct": "Growth (%)",
        "rev_summary": "Revenue Summary (Annual)",
        "rev_monthly": "Monthly Revenue Table (Year 1)",
        "rev_monthly_cols": {"month_name": "Month", "academic_year": "Acad. Year", "period": "Period", "students": "Students", "tuition_revenue": "Tuition Revenue", "enrollment_fee_revenue": "Enrollment Fee", "total_revenue": "Total Revenue"},
        "rev_monthly_title": "Monthly Revenue Table",
        "rev_monthly_note": """
**Calculation methodology (May 2026 — July 2027, 15 months):**
- **May-Jul 2026** (enrollment): enrollment fees collected ($350/student ÷ 3 months) + marketing
- **Aug 2026 — May 2027** (school year, 10 months): tuition (students × $4,000 ÷ 10 months)
- **Jun-Jul 2027** (vacation): no revenue, but teacher & admin salaries still paid
- Student count is **constant** every teaching month
""",
        "total_exp": "Expenses",
        "cost_student_y1": "Cost/Student (Y1)",
        "cost_student_last": "Cost/Student (Y{n})",
        "exp_structure": "Expense Structure (Year 1)",
        "exp_by_cat": "Expenses by Category (Annual)",
        "exp_table": "Expense Detail Table (Annual)",
        "exp_monthly": "Monthly Expense Table (Year 1)",
        "exp_monthly_cols": {"month_name": "Month", "academic_year": "Acad. Year", "period": "Period", "students": "Students", "teacher_cost": "Teacher Salaries", "admin_cost": "Admin Salaries", "salary_taxes": "Salary Taxes", "building": "Building Maint.", "operating": "Operating", "marketing": "Marketing", "jsm_fee": "JSM Fee", "total_expenses": "Total Expenses", "profit": "Profit"},
        "exp_monthly_title": "Monthly Expense Table",
        "exp_monthly_note": """
**Expense calculation methodology:**
- **Teacher salaries** — **Aug 2026 — Jul 2027** (12 months, incl. vacation). Annual ÷ 12.
- **Admin salaries** — **all 15 months** (May 2026 — Jul 2027). Annual ÷ 12.
- **Salary taxes** — 5% of current payroll each month.
- **Building maintenance** — **all 15 months**. Rent + utilities + repairs. Annual ÷ 12.
- **Operating** — **all 15 months**. Internet, office supplies. Annual ÷ 12.
- **Marketing** — **May-Jul 2026 only** (full budget ÷ 3 months).
- **JSM Fee** — 10% of tuition revenue, **Aug 2026 — May 2027 only**.
""",
        "cat_labels": {
            "teacher_cost": "Teacher Salaries",
            "admin_cost": "Admin Salaries",
            "salary_taxes": "Salary Taxes",
            "building": "Building Maintenance",
            "operating": "Operating",
            "marketing": "Marketing",
            "jsm_fee": "JSM Fee"
        },
        "scenario_compare": "Scenario Comparison",
        "profit_by_scenario": "Profit by Scenario",
        "cum_by_scenario": "Cumulative Profit by Scenario",
        "annual_profit": "Annual Profit ($)",
        "enrollment_forecast": "Enrollment Growth Forecast",
        "max_cap": "Max Capacity",
        "utilization": "Utilization %",
        "sensitivity": "Sensitivity Analysis — Tuition",
        "current": "Current",
        "tuition_year": "Tuition ($/year)",
        "stress_tests": "Stress Tests",
        "market_title": "Cambodia Education Market — Deep Research",
        "market_source": "Source: World Bank API (2024), Wikipedia, verified March 2026",
        "macro_overview": "Macroeconomic Overview (World Bank 2024)",
        "population": "Population",
        "gdp": "GDP",
        "gdp_capita": "GDP/Capita",
        "urbanization": "Urbanization",
        "gdp_growth": "GDP Growth",
        "private_ed_growth": "Private Education Growth",
        "secondary_growth": "Secondary Enrollment Growth",
        "private_share_axis": "Private Primary Enrollment (%)",
        "private_title": "4x growth in 9 years (CAGR ~17%)",
        "secondary_axis": "Gross Secondary Enrollment (%)",
        "secondary_title": "Growing market: +2pp/year",
        "school_age": "School-Age (6-18)",
        "private_share": "Private Share (est.)",
        "edu_spend": "Education Spend",
        "gni_capita": "GNI/Capita",
        "demographics": "Demographics & Demand (World Bank 2024)",
        "demo_text": """
    - **Population**: 17.64M, median age 26 — very young country
    - **School-age children (6-18)**: ~4.2 million
    - **Urbanization**: **40.9%** — large urban market
    - **GNI per capita**: $2,550 — growing middle class
    - **GDP growth**: 5.5%/year — one of fastest in ASEAN
    - **Fertility rate**: 2.58""",
        "edu_system": """
    ### Education System
    - **Structure**: 6+3+3 (Primary 1-6, Lower Secondary 7-9, Upper Secondary 10-12)
    - **Academic year**: October to August (break Aug-Sep)
    - **Curriculum**: MoEYS national curriculum (mandatory)
    - **Key exams**: Grade 9 National Exam, Grade 12 BAC II
    - **Primary enrollment**: 109% (gross) — universal coverage
    - **Secondary enrollment**: 58.8% — **growing opportunity** (+2pp/year)""",
        "competition": "Competitive Landscape",
        "comp_cols": ["Segment", "Tuition ($/year)", "# Schools", "Class Size"],
        "comp_segments": ["Budget\n$200-800", "Mid-Range\n$800-2,500", "Premium\n$2,500-5,000", "International\n$5,000-20,000"],
        "your_school": "YOUR SCHOOL\n$4,000/yr",
        "num_schools": "Estimated # of Schools",
        "market_pos_title": "Your Position: Upper Premium Local",
        "your_position": """
    ### Your Position: Premium ($4,000/year)
    - Upper end of premium local segment
    - Competing with ~100-200 schools
    - Key differentiators: teaching quality, facilities, English, exam results
    - **Market tailwind**: private education growing ~17% CAGR""",
        "competitors_title": "WISC Direct Competitors",
        "comp_name": "School",
        "comp_tuition": "Tuition ($/yr)",
        "comp_grades": "Grades",
        "comp_curriculum": "Curriculum",
        "comp_strengths": "Strengths",
        "comp_students": "Students",
        "comp_direct_data": None,
        "comp_intl_data": None,
        "comp_details": [
            {
                "name": "East-West International School (EWIS)",
                "founded": "2006",
                "website": "ewiscambodia.edu.kh",
                "campuses": "1 campus, BKK3",
                "students": "~465 students, 25+ nationalities",
                "staff": "88 teachers",
                "accreditation": "WASC, Cambridge International, MoEYS",
                "curriculum": "IPC / IMYC / Cambridge IGCSE / AS / A Levels + Khmer National",
                "languages": "English, Khmer (bilingual)",
                "fees": "Nursery $4,320 · K $5,800 · 1-3 $5,970 · 4-5 $6,320 · 6-8 $6,630 · 9-12 $7,040",
                "features": "95% of graduates pursue higher education, 11+ university partnerships, 5-20% sibling discounts",
                "source": "ewiscambodia.edu.kh, international-schools-database.com",
            },
            {
                "name": "Footprints International School",
                "founded": "2007",
                "website": "footprintsschool.edu.kh",
                "campuses": "2 campuses: Toul Kork, Toul Tom Poung",
                "students": "1,000+ students, 15+ nationalities",
                "staff": "329 staff and teachers",
                "accreditation": "WASC, Cambridge (CAIE), MoEYS",
                "curriculum": "IEYC / IPC / Cambridge + Khmer National",
                "languages": "English, Khmer, Mandarin",
                "fees": "Nursery $2,706 · K $4,563 · 1-5 $5,106 · 6-8 ~$5,500 · 9-12 $6,250",
                "features": "95% Khmer / 5% international, 15-20% sibling discounts, on-campus health center",
                "source": "footprintsschool.edu.kh, international-schools-database.com",
            },
            {
                "name": "Paragon International School (ex-Zaman)",
                "founded": "1997",
                "website": "paragonisc.edu.kh",
                "campuses": "1 new consolidated campus (2025), Svay Pak",
                "students": "1,100+ students",
                "staff": "Teachers from 9+ countries",
                "accreditation": "CIS, Cambridge (CAIE), MoEYS",
                "curriculum": "Bilingual (Khmer + Cambridge) and International (full CAIE: IGCSE, AS/A Levels)",
                "languages": "English, Khmer",
                "fees": "$4,650-13,620 (by grade and program), 15-20% sibling discounts",
                "features": "One of Cambodia's oldest intl schools, CIS accredited (rare), brand new campus 2025",
                "source": "paragonisc.edu.kh, wikipedia.org, schoolscambodia.com",
            },
            {
                "name": "The Westline School (WEG)",
                "founded": "2008",
                "website": "wegcambodia.com",
                "campuses": "19 campuses (Westline Education Group)",
                "students": "13,000+ students (WEG group)",
                "staff": "1,000+ staff",
                "accreditation": "MoEYS",
                "curriculum": "Khmer National + ESL (American standard) + Chinese",
                "languages": "English, Khmer, Chinese",
                "fees": "~$1,000/year — one of the most affordable",
                "features": "Largest network by student count, grew from 600 to 13,000+ in 15 years, own teacher training institute (EDI)",
                "source": "wegcambodia.com, schoolscambodia.com, phnompenhpost.com",
            },
            {
                "name": "BELTEI International School",
                "founded": "2002",
                "website": "beltei.edu.kh",
                "campuses": "26 campuses in Phnom Penh",
                "students": "10,000+ (est., 26 campuses × 30-40 per class)",
                "staff": "Not disclosed",
                "accreditation": "MoEYS, ISO 9001:2008, TAYO ASEAN Award",
                "curriculum": "Khmer National + ESL (American standard), IT, business",
                "languages": "English, Khmer",
                "fees": "$300-800/year (est.) — budget segment",
                "features": "BELTEI = Business, Economics, Law, Tourism, English, IT. Largest campus network, own university (BIU)",
                "source": "beltei.edu.kh, educationcambodia.org, schoolscambodia.com",
            },
            {
                "name": "Home of English International School",
                "founded": "1997 (started 1993 in Indonesia)",
                "website": "homeofenglish.edu.kh",
                "campuses": "4 campuses: BKK3 (HQ), BKK3 (kindergarten), Toul Kork/Sen Sok, Prek Eng/Mean Chey",
                "students": "Not disclosed, 40+ nationalities",
                "staff": "Low student-to-teacher ratio",
                "accreditation": "IB, MoEYS, CIS, AISA",
                "curriculum": "American + Cambodian, US Diploma track, critical thinking focus",
                "languages": "English (primary), Khmer",
                "fees": "Gr 1-4 $4,611 · Gr 5-8 $4,862 · Gr 9-12 $4,847 · registration $244",
                "features": "IB accredited (rare in Cambodia), 40+ nationalities, charity focus",
                "source": "homeofenglish.edu.kh, international-schools-database.com, educationcambodia.org",
            },
            {
                "name": "CIA First International School",
                "founded": "2004 (started with 17 children)",
                "website": "ciaschool.edu.kh",
                "campuses": "4 campuses: Sen Sok 1 (K-8), Sen Sok 2 (9-12), Chbar Ampov (K-12), Russey Keo (K-8)",
                "students": "5,500+ students, 20+ nationalities",
                "staff": "398 teachers, 1,100+ total personnel",
                "accreditation": "WASC, AP (College Board), MoEYS",
                "curriculum": "American (Common Core, AERO, NGSS), 20+ AP subjects, AP Capstone (first in Cambodia)",
                "languages": "English (primary), Khmer (FTC track)",
                "fees": "K3-K5 $3,950-5,950 · Gr 1-5 $6,600 · Gr 6-8 $7,550 · Gr 9-12 higher · registration $850",
                "features": "Largest premium intl school in Cambodia, first AP Capstone, acquired by Navis Capital (2020), grew 17 to 5,500",
                "source": "ciaschool.edu.kh, international-schools-database.com, schrole.com",
            },
        ],
        "competitors_intl_title": "International Schools (upper segment)",
        "comp_wisc_title": "WISC Positioning",
        "comp_wisc_text": """
- **WISC price ($4,000/yr)** — top 30% of direct competitors
- More expensive than EWIS ($1,680-3,500) and BELTEI ($1,500-3,000)
- On par with CIA First ($4,000-6,000) and Home of English ($4,600-4,900)
- Significantly cheaper than international (ISPP $9,500-29,000)
- **Differentiation**: bilingual + small classes + STEM + Russian language""",
        "regulations": "Regulatory Requirements (MoEYS)",
        "reg_cols": ["Requirement", "Details"],
        "reg_rows": [
            ["License", "MoEYS approval — application + inspection"],
            ["Curriculum", "Must follow national curriculum framework"],
            ["Teachers", "Bachelor's degree minimum, teaching cert. preferred"],
            ["Facilities", "Minimum classroom size, safety requirements"],
            ["Class Size", "Max 45 (gov.), private typically 25-35"],
            ["Registration", "Ministry of Commerce + MoEYS"],
            ["Reporting", "Annual enrollment & exam results to MoEYS"]
        ],
        "pp_private_title": "Phnom Penh Private Schools",
        "pp_schools": "Private Schools",
        "pp_public_schools": "Public Schools",
        "pp_nationwide": "Private Nationwide",
        "pp_share": "Phnom Penh Share",
        "pp_students_est": "Students (est. 2024)",
        "pp_students_nationwide": "Nationwide (est.)",
        "pp_text": """
- **519 private schools** in Phnom Penh vs 251 public — private sector dominates (67%)
- Nationwide: **2,295 private schools** (2024-2025, MoEYS)
- Phnom Penh = **22.6%** of all private schools in the country
- Estimated private school students in Phnom Penh: **~120,000** (2024)
- Growth since 2019: 218,357 students in 1,222 schools → est. ~450,000 in 2,295 schools""",
        "pp_by_level_title": "Phnom Penh Private School Students by Grade",
        "pp_level": "Level",
        "pp_schools_count": "Schools",
        "pp_students_count": "Students",
        "pp_grade": "Grade",
        "pp_level_data": [
            ["Kindergarten", 120, "12,000"],
            ["Primary (1-6)", 195, "55,000"],
            ["Lower Secondary (7-9)", 120, "32,000"],
            ["Upper Secondary (10-12)", 84, "21,000"],
            ["Total", 519, "120,000"],
        ],
        "pp_enrollment_rates": "Enrollment Rates by Level (MoEYS 2023-2024)",
        "pp_nationwide_title": "Schools Nationwide (MoEYS 2022-2023)",
        "salary_title": "Teacher Salaries in Private Schools",
        "salary_cols": ["School Type", "Min ($/mo)", "Max ($/mo)", "Note"],
        "salary_text": """
- **Public schools**: $250-350/mo — base MoEYS salary
- **Budget private**: $200-400/mo — low-cost local schools
- **Mid-range**: $350-700/mo — competitive pay
- **Premium schools**: $500-1,200/mo — high qualification requirements
- **Foreign ESL teachers**: $800-1,200/mo — language academies
- **International schools**: $1,500-2,500/mo — full package (housing, insurance, flights)""",
        "salary_note": "💡 For WISC (premium, $4,000/yr) expected teacher salary: **$500-1,200/mo**",
        "moeys_title": "MoEYS Standard — National Curriculum",
        "moeys_overview": "Overview",
        "moeys_structure_label": "Structure",
        "moeys_year_label": "Academic Year",
        "moeys_weeks_label": "Teaching Weeks",
        "moeys_lesson_label": "Lesson (min)",
        "moeys_lang_label": "Language",
        "moeys_primary_title": "Primary School (Grades 1-6)",
        "moeys_secondary_title": "Lower Secondary (Grades 7-9)",
        "moeys_upper_title": "Upper Secondary (Grades 10-12)",
        "moeys_subject": "Subject",
        "moeys_lessons_week": "Lessons/wk",
        "moeys_notes": "Note",
        "moeys_grades_1_3": "Grades 1-3",
        "moeys_grades_4_6": "Grades 4-6",
        "moeys_exams_title": "Key Examinations",
        "moeys_exam_name": "Exam",
        "moeys_exam_desc": "Description",
        "moeys_teacher_req_title": "Teacher Requirements (MoEYS)",
        "moeys_private_rules_title": "Rules for Private Schools",
        "moeys_private_rules_text": """
- **Mandatory**: follow MoEYS national curriculum
- **Khmer language** — compulsory subject in all private schools
- **Can add**: bilingual programs, international curricula (Cambridge, IB)
- **MoEYS license** required + annual facility inspection
- **Annual reporting**: enrollment numbers and exam results
- **2025 reform**: transition to 4-year teacher training (or 1 year for degree holders)""",
        "moeys_seasons_note": "💡 WISC can expand beyond MoEYS: add advanced English, STEM, Russian language — while keeping mandatory subjects",
        "social_title": "Social Media Reach in Cambodia",
        "social_users": "Users (mln)",
        "social_penetration": "Reach %",
        "social_platform": "Platform",
        "social_best_for": "Use for school",
        "social_total": "Total social media",
        "social_population": "of population",
        "fb_ads_title": "Facebook Ads — Cambodia",
        "fb_cpc": "CPC (click)",
        "fb_cpm": "CPM (1000 imp.)",
        "fb_cpl": "CPL (lead, edu)",
        "fb_discount": "Cheaper than US",
        "acq_title": "Student Acquisition Channels",
        "acq_channel": "Channel",
        "acq_share": "Share %",
        "acq_cost": "Cost",
        "acq_note": "Note",
        "recruit_title": "Teacher Recruitment Channels",
        "recruit_channel": "Channel",
        "recruit_target": "Target",
        "recruit_cost": "Cost",
        "recruit_note": "Note",
        "recruit_best_months": "Best hiring window: June-August",
        "persona_title": "Parent Persona — Target Segments",
        "persona_segment": "Segment",
        "persona_share": "Share %",
        "persona_income": "HH Income ($/mo)",
        "persona_profile": "Profile",
        "persona_priority": "Education Priority",
        "persona_channels": "Channels",
        "persona_location": "Areas",
        "persona_common_title": "Common Traits of Target Parents",
        "persona_decision": "Decision maker",
        "persona_research": "School research period",
        "persona_touches": "Touchpoints to enroll",
        "persona_concern": "Top concern",
        "persona_breaker": "Deal breaker",
        "persona_children": "Avg. children",
        "weeks_label": "wks",
        "social_platforms_data": None,
        "acq_channels_data": [
            ["Word of mouth / Referrals", "40%", "Low"],
            ["Facebook (organic + ads)", "25%", "Low-Medium"],
            ["Open House / School Tour", "15%", "Medium"],
            ["TikTok / YouTube content", "8%", "Low"],
            ["Online directories", "5%", "Low"],
            ["Billboards / Print", "4%", "High"],
            ["Partnerships / Embassy", "3%", "Low"],
        ],
        "acq_chart_labels": ["Word of mouth", "Facebook", "Open House", "TikTok", "Directories", "Billboards", "Partnerships"],
        "recruit_channels_data": [
            ["Facebook Groups", "Local + Foreign", "Free"],
            ["Khmer24.com", "Local Khmer", "Free"],
            ["BongThom.com", "Local Khmer", "Free"],
            ["CamHR.com", "Local + Foreign", "Medium"],
            ["LinkedIn", "Foreign + Senior", "Medium-High"],
            ["Teach Away / Schrole", "Foreign", "High"],
            ["Walk-in / Referral", "Local", "Free"],
            ["University partnerships", "Local junior", "Low"],
        ],
        "persona_segments_data": [
            {
                "name": "Khmer Upper-Middle",
                "profile": "Dual-income family, business owners or professionals, 30-45 years old",
                "priority": "Bilingual (Khmer+English), exam results, university prep",
                "channels": "Facebook, Word of mouth, Telegram groups",
                "factors": "Teaching quality | English proficiency | School reputation | Exam results",
            },
            {
                "name": "Khmer Affluent",
                "profile": "Business owners, government officials, 35-50 years old",
                "priority": "International curriculum, overseas university path, prestige",
                "channels": "Instagram, Word of mouth, Direct outreach",
                "factors": "Brand/prestige | International accreditation | Facilities | Networking",
            },
            {
                "name": "Expat Families",
                "profile": "NGO workers, diplomats, entrepreneurs, 30-50 years old",
                "priority": "English-medium, recognized curriculum (Cambridge/IB), global mobility",
                "channels": "Expat forums, Facebook groups, Embassy networks, Online directories",
                "factors": "Curriculum recognition | English quality | Community | Safety",
            },
            {
                "name": "Khmer Aspirational",
                "profile": "Single-income, skilled workers, first-gen private school, 28-40 years old",
                "priority": "Better than public, English skills, safe environment",
                "channels": "Facebook, TikTok, Neighbors/relatives",
                "factors": "Affordability | Location/transport | English program | Safety",
            },
        ],
        "persona_common_data": {
            "decision_maker": "Mother (70-80%), Father consults",
            "research_period": "4 wks",
            "top_concern": "Quality of English teaching",
            "deal_breaker": "Safety, distance, hidden fees",
        },
        "mktg_title": "Marketing Campaign Recommendations",
        "mktg_funnel_title": "Enrollment Funnel",
        "mktg_funnel_stages": ["Awareness", "Interest", "Consideration", "Application", "Enrollment"],
        "mktg_budget_title": "Recommended Budget Allocation",
        "mktg_channel": "Channel",
        "mktg_budget_pct": "Share %",
        "mktg_budget_usd": "Budget $",
        "mktg_leads": "Expected Leads",
        "mktg_campaigns_title": "Recommended Campaigns",
        "mktg_timing": "Timing",
        "mktg_goal": "Goal",
        "mktg_tactics": "Tactics",
        "mktg_kpi": "KPI",
        "mktg_calendar_title": "Marketing Calendar",
        "mktg_period": "Period",
        "mktg_activity": "Activity",
        "mktg_monthly_budget": "Recommended budget/mo",
        "mktg_cost_per_enroll": "Cost per enrollment",
        "mktg_enrollments_mo": "Enrollments/mo",
        "mktg_total_leads": "Leads/mo",
        "mktg_campaigns_data": [
            {
                "name": "Early Bird Enrollment",
                "goal": "Secure early enrollments with tuition discount",
                "tactics": "5-10% discount for early sign-up | Countdown timer ads | Parent testimonial videos | Limited spots messaging",
                "kpi": "100+ enrollments",
            },
            {
                "name": "Open House Campaign",
                "goal": "Drive campus visits, 25-30% visit-to-application rate",
                "tactics": "Campus tour livestream on Facebook | Student-led TikTok tours | Free snacks/gifts | Follow-up email within 24h",
                "kpi": "100+ families per event",
            },
            {
                "name": "Referral Wave",
                "goal": "Leverage existing parents, 4x conversion vs cold leads",
                "tactics": "$300 tuition credit per enrolled referral | Parent Ambassador badges | Referral leaderboard with prizes | Exclusive preview events",
                "kpi": "60+ referral enrollments/year",
            },
            {
                "name": "TikTok School Life",
                "goal": "Brand awareness among young parents 25-35",
                "tactics": "Day-in-the-life student videos | Teacher spotlight series | English class highlights | Before/after student progress",
                "kpi": "300K+ views/month, 1500+ followers/month",
            },
            {
                "name": "Back to School",
                "goal": "Capture late enrollments and brand awareness for next year",
                "tactics": "First day of school content | Parent community highlights | Results showcase | Billboard near schools",
                "kpi": "50+ late enrollments",
            },
            {
                "name": "Exam Results Showcase",
                "goal": "Build credibility with Grade 9/12 exam results",
                "tactics": "Student success stories | Comparison infographics | University acceptance announcements | Parent review videos",
                "kpi": "Brand trust, 500+ inquiries",
            },
        ],
        "mktg_calendar_data": [
            ["Jan-Feb", "Content creation, SEO optimization"],
            ["Mar-May", "Early Bird campaign, Open House series"],
            ["May-Jul", "Peak enrollment push, Referral Wave"],
            ["Aug-Sep", "Back to School campaign, late enrollment"],
            ["Oct-Nov", "Exam Results Showcase, brand building"],
            ["Dec", "Year review, planning next year"],
        ],
        "launch_title": "180-Student Launch Plan (April — July)",
        "launch_subtitle": "Step-by-step WISC launch plan — from 0 to 180 students in 4 months",
        "launch_total_budget": "Total Budget",
        "launch_target": "Target",
        "launch_period": "Period",
        "launch_cost_per": "Per Student",
        "launch_month": "Month",
        "launch_phase": "Phase",
        "launch_budget": "Budget",
        "launch_enrollments": "Enrollments",
        "launch_cumulative": "Cumulative",
        "launch_channels": "Channels",
        "launch_actions": "Key Actions",
        "launch_kpis_title": "Target KPIs for 4 Months",
        "launch_leads": "Total Leads",
        "launch_oh_attendees": "Open House Attendees",
        "launch_referrals": "Referral Enrollments",
        "launch_fb_reach": "Facebook Reach",
        "launch_tiktok_views": "TikTok Views",
        "launch_website": "Website Visits",
        "launch_conversion": "Conversion",
        "launch_months_data": [
            {"month": "April", "phase": "Launch & Awareness"},
            {"month": "May", "phase": "Peak Push"},
            {"month": "June", "phase": "Conversion Focus"},
            {"month": "July", "phase": "Urgency & Final Closing"},
        ],
        "launch_actions_data": [
            ["Grand launch event", "School tour video series", "Early bird -10% discount", "Billboard campaign in 5 areas", "Press release + media"],
            ["3 Open House events (weekends)", "Referral launch: $300 credit", "Parent testimonial campaign", "Targeted ads by neighborhood", "Telegram parent group launch"],
            ["Retargeting warm leads", "Last chance early bird", "1-on-1 campus tours", "Referral push with bonus prizes", "Expat community events"],
            ["Limited spots countdown", "Personal calls to warm leads", "Final Open House 'last chance'", "Ambassador parent outreach", "Uniform/supplies preview"],
        ],
        "launch_risks_title": "Enrollment Risks — 180 Students",
        "launch_risk": "Risk",
        "launch_risk_impact": "Impact",
        "launch_risk_prob": "Probability",
        "launch_risk_desc": "Description",
        "launch_risk_mitig": "Mitigation",
        "launch_risks_data": [
            {"risk": "No brand / track record", "impact": "Critical", "prob": "High", "desc": "New school with zero graduates, no exam results, no reviews — parents hesitate", "mitig": "Open House events, trial classes, teacher credentials, partner with known brands, early testimonials"},
            {"risk": "Short enrollment window", "impact": "High", "prob": "High", "desc": "4 months is aggressive — most schools recruit over 6-12 months, parents need 4+ weeks to decide", "mitig": "Front-load budget in April-May, pre-marketing from March, urgency tactics, 24h follow-up"},
            {"risk": "Competition from established schools", "impact": "High", "prob": "High", "desc": "519 private schools in Phnom Penh with loyal parent base, relationships, proven results", "mitig": "Unique differentiators (bilingual, small classes, modern facilities), target underserved areas"},
            {"risk": "MoEYS license delay", "impact": "Critical", "prob": "Medium", "desc": "License approval can take 2-6 months, cannot legally enroll students without it", "mitig": "Start process immediately, hire consultant, prepare all documents in advance"},
            {"risk": "Teacher hiring not ready", "impact": "High", "prob": "Medium", "desc": "Parents visit, see no teachers — kills trust. Need 15-20 teachers for 180 students", "mitig": "Hire core team (5-8) before marketing launch, show teacher profiles in ads"},
            {"risk": "Facility not ready on time", "impact": "Critical", "prob": "Medium", "desc": "Construction delays = Open House in unfinished building = credibility destroyed", "mitig": "Have 3-4 showcase classrooms ready by April, use 3D renders for incomplete areas"},
            {"risk": "Price resistance at $4,000/yr", "impact": "Medium", "prob": "High", "desc": "Premium pricing where mid-range is $800-2,500 — limits market to top 10-15% families", "mitig": "Communicate value clearly, payment plans, early bird discounts, sibling discounts, 2-3 scholarships"},
            {"risk": "Marketing fatigue", "impact": "Medium", "prob": "Medium", "desc": "Heavy ad spend in 4 months = audience fatigue, rising CPL, declining CTR", "mitig": "Rotate creatives every 2 weeks, diversify channels, organic content, word of mouth"},
            {"risk": "Seasonal timing conflict", "impact": "Medium", "prob": "Medium", "desc": "April = Khmer New Year (1 week), June-July = rainy season — lower foot traffic", "mitig": "Plan around New Year, dry weekend Open Houses, virtual tour options, transport on rain days"},
            {"risk": "Low conversion rate", "impact": "High", "prob": "Medium", "desc": "Funnel assumes 1.5% — if actual 0.8-1.0%, need 2x leads = 2x budget", "mitig": "Track weekly, A/B test landing pages, optimize follow-up speed, train sales team, contingency +20%"},
        ],
        "risk_matrix": "Risk Matrix",
        "probability": "Probability",
        "impact": "Impact",
        "prob_levels": ["Low", "Medium", "High"],
        "impact_levels": ["Low", "Medium", "High"],
        "opportunities": "Growth Opportunities",
        "opp_cols": ["Opportunity", "Revenue Potential", "Demand", "Implementation"],
        "opp_rows": [
            ["English language", "High", "Very High", "Easy"],
            ["After-school tutoring", "High", "High", "Easy"],
            ["STEM programs", "Medium", "Growing", "Medium"],
            ["School bus", "Medium", "High", "Complex"],
            ["Summer programs", "Medium", "Medium", "Easy"],
            ["Parent community", "Low (indirect)", "High", "Easy"]
        ],
        "pbi_title": "Power BI Export",
        "pbi_desc": "Export financial model data in Power BI-ready formats. Download the Excel file and import into Power BI Desktop.",
        "excel_export": "Excel Export",
        "download_excel": "Download Excel (.xlsx)",
        "sheets_info": "8 sheets with all model data",
        "dax_title": "DAX Measures",
        "download_dax": "Download DAX (.dax)",
        "dax_info": "Pre-built measures for Power BI",
        "guide_title": "Setup Guide",
        "download_guide": "Download Guide (.txt)",
        "guide_info": "Step-by-step Power BI setup",
        "data_preview": "Data Preview",
        "select_table": "Select table",
        "rows_cols": "{r} rows x {c} columns",
        "dax_ref": "DAX Measures Reference",
        "pbi_setup": "Power BI Setup Instructions",
        "pbi_steps": """
    1. **Import**: Power BI Desktop > Get Data > Excel > select `.xlsx`
    2. **Select all sheets** > Load
    3. **Create relationships** in Model view
    4. **Add DAX measures** from downloaded file
    5. **Build visuals** per the setup guide""",
        "theme_title": "Custom Theme (JSON)",
        "download_theme": "Download Theme (.json)",
        "footer": "WISC Cambodia — Financial Model | Streamlit + Python | Power BI Ready",
        "mln": "M",
        "mlrd": "B",
    }
}

# ============================================================
# KHMER translations — overrides on top of EN base.
# [AIJAN-REVIEW] — for missing keys the UI falls back to English.
# ============================================================
_KM_OVERRIDES = {
    "page_title": "WISC — គំរូហិរញ្ញវត្ថុ",
    "title": "WISC Cambodia — យុទ្ធសាស្ត្រហិរញ្ញវត្ថុ និងទីផ្សារ",
    "subtitle_tpl": "ការព្យាករហិរញ្ញវត្ថុ {n}-ឆ្នាំ ជាមួយការវិភាគ scenarios",
    # Sidebar
    "params": "ប៉ារ៉ាម៉ែត្រ",
    "language": "ភាសា / Language",
    "years": "ការព្យាករ (ឆ្នាំ)",
    "tuition": "ថ្លៃសិក្សា ($/ឆ្នាំ)",
    "enrollment_fee": "ថ្លៃចុះឈ្មោះ ($/សិស្ស)",
    "jsm_fee": "អាករ JSM (% នៃប្រាក់ចំណូល)",
    "jsm_years": "រយៈពេល JSM (ឆ្នាំ)",
    "salary_tax": "ពន្ធប្រាក់ខែ (%)",
    "scenario": "Scenario",
    "scenarios": {"base": "មូលដ្ឋាន", "optimistic": "សុទិដ្ឋិនិយម", "pessimistic": "ទុទិដ្ឋិនិយម"},
    # Tabs
    "tabs": ["ទិដ្ឋភាពទូទៅ", "ប្រាក់ចំណូល", "ការចំណាយ", "Scenarios",
             "ការស្រាវជ្រាវទីផ្សារ", "Power BI", "យុទ្ធសាស្ត្រទីផ្សារ", "យុទ្ធសាស្ត្រលក់"],
    # Tab 1
    "total_revenue": "ប្រាក់ចំណូល",
    "total_profit": "ប្រាក់ចំណេញ",
    "npv": "NPV (10%)",
    "roi": "ROI",
    "breakeven": "Breakeven",
    "year_n": "ឆ្នាំ {n}",
    "na": "N/A",
    "annual_pnl": "P&L ប្រចាំឆ្នាំ",
    "revenue": "ប្រាក់ចំណូល",
    "expenses": "ការចំណាយ",
    "profit": "ប្រាក់ចំណេញ",
    "cum_profit_margin": "ប្រាក់ចំណេញកន្សំ និង Margin",
    "cum_profit": "ប្រាក់ចំណេញកន្សំ",
    "margin_pct": "Margin %",
    "year": "ឆ្នាំ",
    "usd": "USD ($)",
    "margin": "Margin",
    "y1_monthly": "ឆ្នាំទី 1 — លំហូរសាច់ប្រាក់ប្រចាំខែ",
    "month": "ខែ",
    "pnl_table": "តារាងសង្ខេប P&L",
    "students": "សិស្ស",
    "cum_profit_col": "ប្រាក់ចំណេញកន្សំ",
    # Tab 2
    "total_rev_label": "ប្រាក់ចំណូលសរុប",
    "avg_annual_rev": "ប្រាក់ចំណូលមធ្យមប្រចាំឆ្នាំ",
    "monthly_tuition": "ថ្លៃសិក្សាប្រចាំខែ",
    "rev_by_year": "ប្រាក់ចំណូលតាមឆ្នាំ",
    "rev_growth": "អត្រាកំណើនប្រាក់ចំណូល",
    "growth_pct": "កំណើន (%)",
    "rev_summary": "សេចក្តីសង្ខេបប្រាក់ចំណូល",
    "rev_monthly": "តារាងប្រាក់ចំណូលប្រចាំខែ (ឆ្នាំទី 1)",
    # Tab 3
    "total_exp": "ការចំណាយ",
    "cost_student_y1": "ការចំណាយ/សិស្ស (ឆ្នាំ 1)",
    "cost_student_last": "ការចំណាយ/សិស្ស (ឆ្នាំ {n})",
    "exp_structure": "រចនាសម្ព័ន្ធការចំណាយ (ឆ្នាំទី 1)",
    "exp_by_cat": "ការចំណាយតាមប្រភេទ",
    "exp_table": "តារាងលម្អិតការចំណាយ",
    "exp_monthly": "តារាងការចំណាយប្រចាំខែ",
    # Tab 4
    "scenario_compare": "ការប្រៀបធៀប scenarios",
    "profit_by_scenario": "ប្រាក់ចំណេញតាម scenario",
    "cum_by_scenario": "ប្រាក់ចំណេញកន្សំតាម scenario",
    "annual_profit": "ប្រាក់ចំណេញប្រចាំឆ្នាំ ($)",
    "enrollment_forecast": "ការព្យាករការចុះឈ្មោះសិស្ស",
    "max_cap": "សមត្ថភាពអតិបរមា",
    "utilization": "ការប្រើប្រាស់ %",
    "sensitivity": "ការវិភាគភាពប្រែប្រួល — ថ្លៃសិក្សា",
    "current": "បច្ចុប្បន្ន",
    "tuition_year": "ថ្លៃសិក្សា ($/ឆ្នាំ)",
    "stress_tests": "ការធ្វើតេស្តទម្ងន់",
    # Tab 5
    "market_title": "ទីផ្សារការអប់រំនៅកម្ពុជា — ការស្រាវជ្រាវស៊ីជម្រៅ",
    "macro_overview": "ទិដ្ឋភាពម៉ាក្រូសេដ្ឋកិច្ច (World Bank 2024)",
    "population": "ចំនួនប្រជាជន",
    "gdp": "GDP",
    "gdp_capita": "GDP ក្នុងម្នាក់",
    "urbanization": "ទីក្រុងូបនីយកម្ម",
    "gdp_growth": "កំណើន GDP",
    "demographics": "ប្រជាសាស្ត្រ និង តម្រូវការ",
    "competition": "បរិយាកាសប្រកួតប្រជែង",
    # Tab 6
    "pbi_title": "ការនាំចេញ Power BI",
    "excel_export": "នាំចេញ Excel",
    "download_excel": "⬇️ ទាញយក Excel",
    "footer": "WISC Cambodia — គំរូហិរញ្ញវត្ថុ | Streamlit + Python | Power BI Ready",
    "mln": "M",
    "mlrd": "B",
}


def _build_km_lang(en_base: dict, km_overrides: dict) -> dict:
    """Build km dict: copy of en + km overrides. Missing keys fallback to English.
    Nested dicts (like 'scenarios') are recursively merged."""
    result = {}
    for key, en_val in en_base.items():
        if key in km_overrides:
            km_val = km_overrides[key]
            # nested dict merge
            if isinstance(en_val, dict) and isinstance(km_val, dict):
                merged = dict(en_val)
                merged.update(km_val)
                result[key] = merged
            else:
                result[key] = km_val
        else:
            result[key] = en_val
    return result


LANG["km"] = _build_km_lang(LANG["en"], _KM_OVERRIDES)


# --- Sidebar: Language & Years FIRST ---
st.sidebar.header("Settings / Настройки / ការកំណត់")
lang_choice = st.sidebar.radio(
    "🌐 Language / Язык / ភាសា",
    ["Русский", "English", "ភាសាខ្មែរ"],
    horizontal=False,
)
lang = {"Русский": "ru", "English": "en", "ភាសាខ្មែរ": "km"}[lang_choice]
# km falls back to en for financial-model tabs (LANG dict has no km keys)
t = LANG.get(lang, LANG["en"])

n_years = st.sidebar.slider(t["years"], 1, 10, 5, 1)

st.sidebar.markdown("---")
st.sidebar.header(t["params"])

tuition = st.sidebar.slider(t["tuition"], 2000, 8000, 4000, 100)
enrollment_fee = st.sidebar.slider(t["enrollment_fee"], 0, 1000, 300, 50)
jsm_fee_pct = st.sidebar.slider(t["jsm_fee"], 0, 20, 10, 1)
jsm_fee_years = st.sidebar.slider(t["jsm_years"], 0, 10, 5, 1)
salary_tax_pct = st.sidebar.slider(t["salary_tax"], 0, 15, 5, 1)

st.sidebar.markdown("---")
scenario = st.sidebar.selectbox(
    t["scenario"],
    list(t["scenarios"].keys()),
    format_func=lambda x: t["scenarios"][x]
)

# --- Build model ---
model = FinancialModel()
model.school["projection_years"] = n_years
model.revenue_params["tuition_per_year"] = tuition
model.revenue_params["enrollment_fee_per_student"] = enrollment_fee
model.expenses["jsm_fee_pct"] = jsm_fee_pct / 100
model.expenses["jsm_fee_years"] = jsm_fee_years
model.expenses["salary_tax_pct"] = salary_tax_pct / 100

revenue_agent = RevenueAgent(model)
expense_agent = ExpenseAgent(model)
growth_agent = GrowthAgent(model)
risk_agent = RiskAgent(model)
pbi_exporter = PowerBIExporter(model)

# --- Pre-compute all data (recalculates on every parameter change) ---
pnl = model.calculate_pnl(scenario)
npv = model.calculate_npv(scenario)
roi = model.calculate_roi(scenario)
bep_year = model.calculate_breakeven_year(scenario)
monthly = model.calculate_monthly_year1(scenario)
rev_data = revenue_agent.calculate(scenario)
exp_data = expense_agent.calculate(scenario)
growth_data = growth_agent.calculate(scenario)

# --- Header ---
st.title(t["title"])
st.markdown(t["subtitle_tpl"].format(n=n_years))

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(t["tabs"])

# ============================================================
# TAB 1: OVERVIEW
# ============================================================
with tab1:

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(t["total_revenue"], f"${pnl['revenue'].sum():,.0f}")
    col2.metric(t["total_profit"], f"${pnl['profit'].sum():,.0f}")
    col3.metric(t["npv"], f"${npv:,.0f}")
    col4.metric(t["roi"], f"{roi:.1%}")
    col5.metric(t["breakeven"], t["year_n"].format(n=bep_year) if bep_year else t["na"])

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(t["annual_pnl"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pnl["year"], y=pnl["revenue"], name=t["revenue"], marker_color="#2ecc71"))
        fig.add_trace(go.Bar(x=pnl["year"], y=pnl["expenses"], name=t["expenses"], marker_color="#e74c3c"))
        fig.add_trace(go.Scatter(x=pnl["year"], y=pnl["profit"], name=t["profit"],
                                 mode="lines+markers", line=dict(color="#3498db", width=3)))
        fig.update_layout(barmode="group", height=400, xaxis_title=t["year"], yaxis_title=t["usd"])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader(t["cum_profit_margin"])
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=pnl["year"], y=pnl["cumulative_profit"],
                              name=t["cum_profit"], marker_color="#9b59b6"), secondary_y=False)
        fig2.add_trace(go.Scatter(x=pnl["year"], y=pnl["margin"] * 100,
                                  name=t["margin_pct"], mode="lines+markers",
                                  line=dict(color="#f39c12", width=3)), secondary_y=True)
        fig2.update_yaxes(title_text=t["cum_profit"] + " ($)", secondary_y=False)
        fig2.update_yaxes(title_text=t["margin"] + " (%)", secondary_y=True)
        fig2.update_layout(height=400, xaxis_title=t["year"])
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader(t["y1_monthly"])
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=monthly["month_name"], y=monthly["total_revenue"], name=t["revenue"], marker_color="#2ecc71"))
    fig3.add_trace(go.Bar(x=monthly["month_name"], y=monthly["total_expenses"], name=t["expenses"], marker_color="#e74c3c"))
    fig3.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["profit"], name=t["profit"],
                              mode="lines+markers", line=dict(color="#3498db", width=2)))
    fig3.update_layout(barmode="group", height=350, xaxis_title=t["month"], yaxis_title=t["usd"])
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader(t["pnl_table"])
    dp = pnl.copy()
    dp.columns = [t["year"], t["students"], t["revenue"], t["expenses"], t["profit"], t["margin"], t["cum_profit_col"]]
    for c in [t["revenue"], t["expenses"], t["profit"], t["cum_profit_col"]]:
        dp[c] = dp[c].apply(lambda x: f"${x:,.0f}")
    dp[t["margin"]] = pnl["margin"].apply(lambda x: f"{x:.1%}")
    st.dataframe(dp, use_container_width=True, hide_index=True)

# ============================================================
# TAB 2: REVENUE
# ============================================================
with tab2:
    col1, col2, col3 = st.columns(3)
    col1.metric(t["total_rev_label"], f"${rev_data['total_revenue']:,.0f}")
    col2.metric(t["avg_annual_rev"], f"${rev_data['avg_annual_revenue']:,.0f}")
    col3.metric(t["monthly_tuition"], f"${rev_data['monthly_tuition']:,.0f}")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(t["rev_by_year"])
        fig = go.Figure()
        fig.add_trace(go.Bar(x=rev_data["years"], y=rev_data["annual_revenue"],
                             marker_color="#2ecc71", text=[f"${r:,.0f}" for r in rev_data["annual_revenue"]],
                             textposition="outside"))
        fig.update_layout(height=400, xaxis_title=t["year"], yaxis_title=t["revenue"] + " ($)")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader(t["rev_growth"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=rev_data["years"], y=[r * 100 for r in rev_data["growth_rates"]],
                                 mode="lines+markers+text",
                                 text=[f"{r:.1%}" for r in rev_data["growth_rates"]],
                                 textposition="top center",
                                 line=dict(color="#3498db", width=3)))
        fig.update_layout(height=400, xaxis_title=t["year"], yaxis_title=t["growth_pct"])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(t["rev_summary"])
    st.dataframe(rev_data["summary"], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader(t["rev_monthly_title"])
    rev_cols = ["month_name", "academic_year", "period", "students", "tuition_revenue", "enrollment_fee_revenue", "total_revenue"]
    monthly_rev = monthly[rev_cols].copy()
    monthly_rev.columns = [t["rev_monthly_cols"][c] for c in rev_cols]
    for c in monthly_rev.columns[4:]:
        monthly_rev[c] = monthly_rev[c].apply(lambda x: f"${x:,.0f}")
    st.dataframe(monthly_rev, use_container_width=True, hide_index=True)
    with st.expander("📋 " + t["rev_monthly_title"] + " — ?"):
        st.markdown(t["rev_monthly_note"])

# ============================================================
# TAB 3: EXPENSES
# ============================================================
with tab3:
    cat_map = t["cat_labels"]

    col1, col2, col3 = st.columns(3)
    col1.metric(t["total_exp"], f"${exp_data['total_5yr_expenses']:,.0f}")
    col2.metric(t["cost_student_y1"], f"${exp_data['cost_per_student'][0]:,.0f}")
    col3.metric(t["cost_student_last"].format(n=n_years), f"${exp_data['cost_per_student'][-1]:,.0f}")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(t["exp_structure"])
        structure = expense_agent.expense_structure(0, scenario)
        labels = [cat_map.get(k, k) for k in structure.keys()]
        values = list(structure.values())
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4)])
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader(t["exp_by_cat"])
        fig = go.Figure()
        colors = ["#e74c3c", "#3498db", "#f39c12", "#9b59b6", "#1abc9c", "#95a5a6", "#e67e22"]
        for i, (cat, vals) in enumerate(exp_data["breakdown"].items()):
            fig.add_trace(go.Bar(x=exp_data["years"], y=vals,
                                 name=cat_map.get(cat, cat),
                                 marker_color=colors[i % len(colors)]))
        fig.update_layout(barmode="stack", height=400, xaxis_title=t["year"], yaxis_title=t["usd"])
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(t["exp_table"])
    st.dataframe(exp_data["summary"], use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader(t["exp_monthly_title"])
    exp_cols = ["month_name", "academic_year", "period", "students", "teacher_cost", "admin_cost", "salary_taxes", "building", "operating", "marketing", "jsm_fee", "total_expenses", "profit"]
    monthly_exp = monthly[exp_cols].copy()
    monthly_exp.columns = [t["exp_monthly_cols"][c] for c in exp_cols]
    for c in monthly_exp.columns[4:]:
        monthly_exp[c] = monthly_exp[c].apply(lambda x: f"${x:,.0f}")
    st.dataframe(monthly_exp, use_container_width=True, hide_index=True)
    with st.expander("📋 " + t["exp_monthly_title"] + " — ?"):
        st.markdown(t["exp_monthly_note"])

# ============================================================
# TAB 4: SCENARIOS
# ============================================================
with tab4:
    st.subheader(t["scenario_compare"])
    comparison = risk_agent.scenario_comparison_table()
    st.dataframe(comparison, use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    colors_map = {"optimistic": "#2ecc71", "base": "#3498db", "pessimistic": "#e74c3c"}

    with c1:
        st.subheader(t["profit_by_scenario"])
        fig = go.Figure()
        for name in ["optimistic", "base", "pessimistic"]:
            pnl_s = model.calculate_pnl(name)
            fig.add_trace(go.Scatter(x=pnl_s["year"], y=pnl_s["profit"],
                                     name=t["scenarios"][name], mode="lines+markers",
                                     line=dict(color=colors_map[name], width=3)))
        fig.update_layout(height=400, xaxis_title=t["year"], yaxis_title=t["annual_profit"])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader(t["cum_by_scenario"])
        fig = go.Figure()
        for name in ["optimistic", "base", "pessimistic"]:
            pnl_s = model.calculate_pnl(name)
            fig.add_trace(go.Scatter(x=pnl_s["year"], y=pnl_s["cumulative_profit"],
                                     name=t["scenarios"][name], mode="lines+markers",
                                     fill="tozeroy" if name == "optimistic" else None,
                                     line=dict(color=colors_map[name], width=2)))
        fig.update_layout(height=400, xaxis_title=t["year"], yaxis_title=t["cum_profit"] + " ($)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(t["enrollment_forecast"])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=growth_data["years"], y=growth_data["enrollment"],
                         name=t["students"], marker_color="#3498db"))
    fig.add_hline(y=model.school["max_capacity"], line_dash="dash", line_color="red",
                  annotation_text=f"{t['max_cap']}: {model.school['max_capacity']}")
    fig.add_trace(go.Scatter(x=growth_data["years"],
                             y=[u * 100 for u in growth_data["utilization"]],
                             name=t["utilization"], yaxis="y2",
                             mode="lines+markers", line=dict(color="#f39c12", width=3)))
    fig.update_layout(height=400, xaxis_title=t["year"],
                      yaxis=dict(title=t["students"]),
                      yaxis2=dict(title=t["utilization"], overlaying="y", side="right"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader(t["sensitivity"])
    sens = risk_agent.sensitivity_analysis("tuition_per_year", 0.3, 7)
    if not sens.empty:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=sens["value"], y=sens["npv"],
                                 mode="lines+markers", line=dict(color="#9b59b6", width=3)))
        fig.add_vline(x=tuition, line_dash="dash", line_color="green", annotation_text=t["current"])
        fig.update_layout(height=350, xaxis_title=t["tuition_year"], yaxis_title="NPV ($)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(t["stress_tests"])
    stress = risk_agent.stress_test()
    st.dataframe(stress, use_container_width=True, hide_index=True)

# ============================================================
# TAB 5: MARKET RESEARCH
# ============================================================
with tab5:
    st.subheader(t["market_title"])
    st.caption(t["market_source"])

    with open(Path(__file__).parent.parent / "data" / "market_research.json") as f:
        research = json.load(f)

    st.markdown(f"### {t['macro_overview']}")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(t["population"], f"{research['macro']['population']/1e6:.1f} {t['mln']}")
    col2.metric(t["gdp"], f"${research['macro']['gdp_usd']/1e9:.1f} {t['mlrd']}")
    col3.metric(t["gdp_capita"], f"${research['macro']['gdp_per_capita_usd']:,}")
    col4.metric(t["urbanization"], f"{research['macro']['urbanization_pct']}%")
    col5.metric(t["gdp_growth"], f"{research['macro']['gdp_growth_pct']}%")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"### {t['private_ed_growth']}")
        trend = research["private_share_trend"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(trend.keys()), y=list(trend.values()),
                                 mode="lines+markers+text",
                                 text=[f"{v:.1f}%" for v in trend.values()],
                                 textposition="top center",
                                 line=dict(color="#2ecc71", width=3),
                                 fill="tozeroy", fillcolor="rgba(46,204,113,0.1)"))
        fig.update_layout(height=350, xaxis_title=t["year"],
                          yaxis_title=t["private_share_axis"], title=t["private_title"])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"### {t['secondary_growth']}")
        sec_trend = research["secondary_enrollment_trend"]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(sec_trend.keys()), y=list(sec_trend.values()),
                                 mode="lines+markers+text",
                                 text=[f"{v}%" for v in sec_trend.values()],
                                 textposition="top center",
                                 line=dict(color="#3498db", width=3),
                                 fill="tozeroy", fillcolor="rgba(52,152,219,0.1)"))
        fig.update_layout(height=350, xaxis_title=t["year"],
                          yaxis_title=t["secondary_axis"], title=t["secondary_title"])
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t["school_age"], f"{research['demographics']['school_age_6_18']/1e6:.1f} {t['mln']}")
    col2.metric(t["private_share"], f"~{research['education']['private_primary_share_est_2024_pct']}%")
    col3.metric(t["edu_spend"], f"${research['macro']['education_spend_usd']/1e6:.0f}M", f"{research['macro']['education_gdp_pct']}% GDP")
    col4.metric(t["gni_capita"], f"${research['macro']['gni_per_capita_usd']:,}")

    st.markdown(f"### {t['demographics']}")
    st.markdown(t["demo_text"])
    st.markdown(t["edu_system"])

    st.markdown("---")
    st.markdown(f"### {t['competition']}")
    comp_data = pd.DataFrame(research["competition"]["segments"])
    comp_data.columns = t["comp_cols"]
    st.dataframe(comp_data, use_container_width=True, hide_index=True)

    fig = go.Figure()
    schools = [3000, 650, 150, 65]
    fig.add_trace(go.Bar(x=t["comp_segments"], y=schools,
                         marker_color=["#95a5a6", "#3498db", "#e74c3c", "#9b59b6"]))
    fig.add_annotation(x=t["comp_segments"][2], y=150, text=t["your_school"],
                       showarrow=True, arrowhead=2, font=dict(size=14, color="red"))
    fig.update_layout(height=350, yaxis_title=t["num_schools"], title=t["market_pos_title"])
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(t["your_position"])

    # --- Direct Competitors ---
    st.markdown(f"#### {t['competitors_title']}")
    dc = research["competition"]["direct_competitors"]
    dc_tr = t.get("comp_direct_data")
    if dc_tr:
        dc_rows = dc_tr
    else:
        dc_rows = [[c["name"], c["tuition"], c["grades"], c["curriculum"], c["strengths"], c.get("students", "")]
                    for c in dc]
    st.dataframe(pd.DataFrame(dc_rows,
                  columns=[t["comp_name"], t["comp_tuition"], t["comp_grades"],
                           t["comp_curriculum"], t["comp_strengths"], t["comp_students"]]),
                  use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        names = [c["name"].split("(")[0].strip()[:15] for c in dc] + ["WISC"]
        maxfees = [int(c["tuition"].split("-")[-1].replace(",", "")) for c in dc] + [4000]
        colors = ["#3498db"] * len(dc) + ["#e74c3c"]
        fig.add_trace(go.Bar(name="Max", x=names, y=maxfees, marker_color=colors,
                             text=[f"${f:,}" for f in maxfees], textposition="auto"))
        fig.update_layout(height=350, yaxis_title="$/year",
                          margin=dict(l=20, r=20, t=20, b=80), xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"#### {t['competitors_intl_title']}")
        ic = research["competition"]["international_competitors"]
        ic_tr = t.get("comp_intl_data")
        if ic_tr:
            ic_rows = ic_tr
        else:
            ic_rows = [[c["name"], c["tuition"], c["curriculum"], c["strengths"]] for c in ic]
        st.dataframe(pd.DataFrame(ic_rows,
                      columns=[t["comp_name"], t["comp_tuition"], t["comp_curriculum"], t["comp_strengths"]]),
                      use_container_width=True, hide_index=True)

    # Detailed competitor profiles in expanders
    comp_details = t.get("comp_details", [])
    for cd in comp_details:
        with st.expander(f"📋 {cd['name']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**{t.get('launch_period', 'Founded')}**: {cd['founded']}")
                st.markdown(f"**Website**: {cd['website']}")
                st.markdown(f"**{t.get('launch_channels', 'Campuses')}**: {cd['campuses']}")
                st.markdown(f"**{t['comp_students']}**: {cd['students']}")
                if cd.get('staff'):
                    st.markdown(f"**Staff**: {cd['staff']}")
            with c2:
                st.markdown(f"**{t['comp_curriculum']}**: {cd['curriculum']}")
                st.markdown(f"**Accreditation**: {cd['accreditation']}")
                st.markdown(f"**Languages**: {cd['languages']}")
            st.markdown(f"**{t['comp_tuition']}**: {cd['fees']}")
            st.markdown(f"**{t['comp_strengths']}**: {cd['features']}")
            st.caption(f"Source: {cd['source']}")

    st.markdown(f"#### {t['comp_wisc_title']}")
    st.markdown(t["comp_wisc_text"])

    st.markdown("---")
    st.markdown(f"### {t['pp_private_title']}")
    pp = research["phnom_penh_private"]
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    col_a.metric(t["pp_schools"], f"{pp['private_schools']}")
    col_b.metric(t["pp_public_schools"], f"{pp['public_schools']}")
    col_c.metric(t["pp_share"], f"{pp['phnom_penh_share_pct']}%")
    col_d.metric(t["pp_students_est"], f"~{pp['students_private_phnom_penh_est_2024']//1000}K")
    col_e.metric(t["pp_students_nationwide"], f"~{pp['students_private_nationwide_est_2024']//1000}K")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(t["pp_text"])
        # Schools by level table
        st.markdown(f"**{t['pp_by_level_title']}**")
        st.dataframe(pd.DataFrame(t["pp_level_data"],
                      columns=[t["pp_level"], t["pp_schools_count"], t["pp_students_count"]]),
                      use_container_width=True, hide_index=True)

    with c2:
        # Students by grade bar chart
        grades_data = pp["phnom_penh_by_level"]["students_by_grade_est"]
        grade_labels = [g["grade"] for g in grades_data]
        grade_students = [g["students"] for g in grades_data]
        grade_colors = (["#9b59b6"] +
                        ["#2ecc71"] * 6 +
                        ["#3498db"] * 3 +
                        ["#e74c3c"] * 3)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=grade_labels, y=grade_students,
                             marker_color=grade_colors,
                             text=[f"{s//1000}K" for s in grade_students],
                             textposition="auto"))
        fig.update_layout(height=380, yaxis_title=t["pp_students_count"],
                          xaxis_title=t["pp_grade"],
                          margin=dict(l=20, r=20, t=30, b=20),
                          title=t["pp_by_level_title"])
        st.plotly_chart(fig, use_container_width=True)

        # Enrollment rates
        er = pp["phnom_penh_by_level"]["enrollment_rates"]
        st.markdown(f"**{t['pp_enrollment_rates']}**")
        er1, er2, er3 = st.columns(3)
        er1.metric("Primary", f"{er['primary_pct']}%")
        er2.metric("Lower Sec.", f"{er['lower_secondary_pct']}%")
        er3.metric("Upper Sec.", f"{er['upper_secondary_pct']}%")

    st.markdown("---")
    st.markdown(f"### {t['salary_title']}")
    sal = research["teacher_salaries"]
    sal_keys = ["government_public", "private_budget", "private_midrange", "private_premium", "foreign_english", "international"]

    c1, c2 = st.columns([2, 3])
    with c1:
        salary_rows = []
        for key in sal_keys:
            s = sal[key]
            salary_rows.append([s["note"], f"${s['min']}", f"${s['max']}"])
        salary_df = pd.DataFrame(salary_rows, columns=t["salary_cols"][:3])
        st.dataframe(salary_df, use_container_width=True, hide_index=True)
    with c2:
        fig = go.Figure()
        labels = [sal[k]["note"] for k in sal_keys]
        mins = [sal[k]["min"] for k in sal_keys]
        maxs = [sal[k]["max"] for k in sal_keys]
        fig.add_trace(go.Bar(name="Min $/mo", x=labels, y=mins, marker_color="#3498db"))
        fig.add_trace(go.Bar(name="Max $/mo", x=labels, y=maxs, marker_color="#e74c3c"))
        fig.update_layout(height=380, barmode="group", yaxis_title="$/month",
                          margin=dict(l=20, r=20, t=40, b=100),
                          xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
    st.markdown(t["salary_text"])
    st.info(t["salary_note"])

    st.markdown("---")
    st.markdown(f"### {t['moeys_title']}")
    cur = research["moeys_curriculum"]
    ov = cur["overview"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t["moeys_structure_label"], ov["structure"].split(" ")[0])
    col2.metric(t["moeys_weeks_label"], f"{ov['teaching_weeks']}")
    col3.metric(t["moeys_lesson_label"], f"{ov['lesson_duration_primary_min']}-{ov['lesson_duration_upper_sec_min']}")
    col4.metric(t["moeys_lang_label"], ov["language_of_instruction"])

    cur_tab1, cur_tab2, cur_tab3 = st.tabs([
        t["moeys_primary_title"], t["moeys_secondary_title"], t["moeys_upper_title"]
    ])

    with cur_tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{t['moeys_grades_1_3']}** — {cur['primary_grades_1_3']['total_lessons_per_week']} {t['moeys_lessons_week']}")
            p13 = cur["primary_grades_1_3"]
            rows_13 = [[s["subject"], s["lessons"]] for s in p13["subjects"]]
            rows_13.append(["TOTAL", p13["total_lessons_per_week"]])
            st.dataframe(pd.DataFrame(rows_13, columns=[t["moeys_subject"], t["moeys_lessons_week"]]),
                          use_container_width=True, hide_index=True)
        with c2:
            st.markdown(f"**{t['moeys_grades_4_6']}** — {cur['primary_grades_4_6']['total_lessons_per_week']} {t['moeys_lessons_week']}")
            p46 = cur["primary_grades_4_6"]
            rows_46 = []
            for s in p46["subjects"]:
                if "lessons" in s:
                    rows_46.append([s["subject"], str(s["lessons"]), str(s["lessons"])])
                else:
                    g4 = s.get("lessons_g4", "")
                    g56 = s.get("lessons_g5_6", "")
                    rows_46.append([s["subject"], str(g4), str(g56)])
            rows_46.append(["TOTAL", str(p46["total_lessons_per_week"]), str(p46["total_lessons_per_week"])])
            st.dataframe(pd.DataFrame(rows_46, columns=[t["moeys_subject"], "Gr.4", "Gr.5-6"]),
                          use_container_width=True, hide_index=True)

    with cur_tab2:
        c1, c2 = st.columns([3, 2])
        with c1:
            ls = cur["lower_secondary_7_9"]
            rows_ls = [[s["subject"], s["lessons"]] for s in ls["subjects"]]
            rows_ls.append(["TOTAL", ls["total_lessons_per_week"]])
            st.dataframe(pd.DataFrame(rows_ls, columns=[t["moeys_subject"], t["moeys_lessons_week"]]),
                          use_container_width=True, hide_index=True)
        with c2:
            fig = go.Figure()
            subj_names = [s["subject"].split("(")[0].strip() for s in ls["subjects"]]
            subj_hours = [s["lessons"] for s in ls["subjects"]]
            fig.add_trace(go.Pie(labels=subj_names, values=subj_hours,
                                 hole=0.4, textinfo="label+value"))
            fig.update_layout(height=400, showlegend=False,
                              margin=dict(l=10, r=10, t=40, b=10),
                              title=t["moeys_lessons_week"])
            st.plotly_chart(fig, use_container_width=True)

    with cur_tab3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Grade 10**")
            us10 = cur["upper_secondary_10"]
            rows_10 = [[s["subject"], s["lessons"]] for s in us10["subjects"]]
            rows_10.append(["TOTAL", us10["total_lessons_per_week"]])
            st.dataframe(pd.DataFrame(rows_10, columns=[t["moeys_subject"], t["moeys_lessons_week"]]),
                          use_container_width=True, hide_index=True)
        with c2:
            st.markdown("**Grades 11-12**")
            us12 = cur["upper_secondary_11_12"]
            rows_12 = []
            for s in us12["compulsory"]:
                if "lessons" in s:
                    rows_12.append([s["subject"], str(s["lessons"])])
                else:
                    basic = s.get("lessons_basic", "")
                    adv = s.get("lessons_advanced", "")
                    rows_12.append([s["subject"], f"{basic} / {adv}"])
            st.dataframe(pd.DataFrame(rows_12, columns=[t["moeys_subject"], t["moeys_lessons_week"]]),
                          use_container_width=True, hide_index=True)
            st.caption(us12["electives_note"])

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### {t['moeys_exams_title']}")
        exam_rows = [[e["name"], e["description"]] for e in cur["key_exams"]]
        st.dataframe(pd.DataFrame(exam_rows, columns=[t["moeys_exam_name"], t["moeys_exam_desc"]]),
                      use_container_width=True, hide_index=True)

        st.markdown(f"#### {t['moeys_teacher_req_title']}")
        tr = cur["teacher_requirements"]
        teacher_rows = [
            [t["moeys_structure_label"], tr["minimum_education"]],
            ["Certification", tr["certification"]],
            ["Reform 2025", tr["training_reform_2025"]],
            [t["moeys_lang_label"], tr["language"]],
        ]
        st.dataframe(pd.DataFrame(teacher_rows, columns=[t["moeys_subject"], t["moeys_notes"]]),
                      use_container_width=True, hide_index=True)

    with c2:
        st.markdown(f"#### {t['moeys_private_rules_title']}")
        st.markdown(t["moeys_private_rules_text"])

    st.info(t["moeys_seasons_note"])

    # --- Social Media ---
    st.markdown("---")
    st.markdown(f"### {t['social_title']}")
    sm = research["social_media"]
    fb = sm["facebook_ads"]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(t["social_total"], f"{sm['total_users']/1e6:.0f}M", f"{sm['penetration_pct']}%")
    c2.metric(t["fb_cpc"], f"${fb['avg_cpc_usd']}")
    c3.metric(t["fb_cpm"], f"${fb['avg_cpm_usd']}")
    c4.metric(t["fb_cpl"], f"${fb['education_cpl_usd']}")
    c5.metric(t["fb_discount"], f"-{fb['vs_us_discount_pct']}%")

    sm_translate = t.get("social_platforms_data")
    c1, c2 = st.columns([3, 2])
    with c1:
        plat_rows = []
        for p in sm["platforms"]:
            best = sm_translate.get(p["best_for"], p["best_for"]) if sm_translate else p["best_for"]
            plat_rows.append([p["name"], p["users_mln"], f"{p['penetration_pct']}%", best])
        st.dataframe(pd.DataFrame(plat_rows,
                      columns=[t["social_platform"], t["social_users"], t["social_penetration"], t["social_best_for"]]),
                      use_container_width=True, hide_index=True)
    with c2:
        fig = go.Figure()
        p_names = [p["name"] for p in sm["platforms"]]
        p_users = [p["users_mln"] for p in sm["platforms"]]
        colors = ["#1877F2", "#000000", "#0088cc", "#25D366", "#E4405F", "#FF0000", "#0A66C2"]
        fig.add_trace(go.Bar(x=p_names, y=p_users, marker_color=colors,
                             text=[f"{u}M" for u in p_users], textposition="auto"))
        fig.update_layout(height=350, yaxis_title=t["social_users"],
                          margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # --- Student Acquisition + Teacher Recruitment side by side ---
    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"### {t['acq_title']}")
        acq_data = t["acq_channels_data"]
        st.dataframe(pd.DataFrame(acq_data,
                      columns=[t["acq_channel"], t["acq_share"], t["acq_cost"]]),
                      use_container_width=True, hide_index=True)

        fig = go.Figure()
        ch_labels = t["acq_chart_labels"]
        ch_vals = [ch["effectiveness_pct"] for ch in research["student_acquisition"]["channels"]]
        fig.add_trace(go.Bar(x=ch_labels, y=ch_vals,
                             marker_color=["#2ecc71", "#1877F2", "#e74c3c", "#000000", "#3498db", "#f39c12", "#9b59b6"],
                             text=[f"{v}%" for v in ch_vals], textposition="auto"))
        fig.update_layout(height=320, yaxis_title="%",
                          margin=dict(l=20, r=20, t=20, b=60),
                          xaxis_tickangle=-25)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"### {t['recruit_title']}")
        rec_data = t["recruit_channels_data"]
        st.dataframe(pd.DataFrame(rec_data,
                      columns=[t["recruit_channel"], t["recruit_target"], t["recruit_cost"]]),
                      use_container_width=True, hide_index=True)
        st.info(t["recruit_best_months"])

    # --- Parent Persona ---
    st.markdown("---")
    st.markdown(f"### {t['persona_title']}")
    persona = research["parent_persona"]
    persona_tr = t["persona_segments_data"]

    c1, c2 = st.columns([3, 2])
    with c1:
        persona_tabs = st.tabs([s["name"] for s in persona_tr])
        for i, seg in enumerate(persona["segments"]):
            with persona_tabs[i]:
                seg_t = persona_tr[i]
                m1, m2 = st.columns(2)
                m1.metric(t["persona_share"], f"{seg['share_pct']}%")
                m2.metric(t["persona_income"], f"${seg['household_income_usd']}")
                st.markdown(f"**{t['persona_profile']}**: {seg_t['profile']}")
                st.markdown(f"**{t['persona_priority']}**: {seg_t['priority']}")
                st.markdown(f"**{t['persona_channels']}**: {seg_t['channels']}")
                st.markdown(f"**{t['persona_location']}**: {seg['location']}")
                st.caption(seg_t["factors"])
    with c2:
        fig = go.Figure()
        seg_names = [s["name"] for s in persona_tr]
        seg_shares = [s["share_pct"] for s in persona["segments"]]
        fig.add_trace(go.Pie(labels=seg_names, values=seg_shares,
                             hole=0.4, textinfo="label+percent",
                             marker=dict(colors=["#3498db", "#e74c3c", "#2ecc71", "#f39c12"])))
        fig.update_layout(height=350, showlegend=False,
                          margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig, use_container_width=True)

        common_tr = t["persona_common_data"]
        st.markdown(f"#### {t['persona_common_title']}")
        st.markdown(f"- **{t['persona_decision']}**: {common_tr['decision_maker']}")
        st.markdown(f"- **{t['persona_research']}**: {common_tr['research_period']}")
        st.markdown(f"- **{t['persona_touches']}**: {persona['common_traits']['touchpoints_before_enroll']}")
        st.markdown(f"- **{t['persona_concern']}**: {common_tr['top_concern']}")
        st.markdown(f"- **{t['persona_breaker']}**: {common_tr['deal_breaker']}")
        st.markdown(f"- **{t['persona_children']}**: {persona['common_traits']['avg_children']}")

    # --- Marketing Campaigns ---
    st.markdown("---")
    st.markdown(f"### {t['mktg_title']}")
    mktg = research["marketing_campaigns"]
    bm = mktg["budget_model"]

    st.markdown(
        f"**{t['mktg_monthly_budget']}**: \\${bm['monthly_budget_usd']:,} · "
        f"**{t['mktg_total_leads']}**: ~{bm['total_expected_leads']:,} · "
        f"**{t['mktg_enrollments_mo']}**: {bm['expected_enrollments_per_month']} · "
        f"**{t['mktg_cost_per_enroll']}**: \\${bm['cost_per_enrollment_usd']}"
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"#### {t['mktg_funnel_title']}")
        funnel = mktg["funnel"]
        funnel_stages = t["mktg_funnel_stages"]
        funnel_vals = [funnel[k]["conversion_pct"] for k in funnel]
        fig = go.Figure(go.Funnel(
            y=funnel_stages, x=funnel_vals,
            textinfo="value+percent initial",
            marker=dict(color=["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"])
        ))
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"#### {t['mktg_budget_title']}")
        fig = go.Figure()
        ch_names = [a["channel"] for a in bm["allocation"]]
        ch_budgets = [a["budget"] for a in bm["allocation"]]
        ch_leads = [a["expected_leads"] for a in bm["allocation"]]
        fig.add_trace(go.Bar(name=t["mktg_budget_usd"], x=ch_names, y=ch_budgets,
                             marker_color="#3498db", text=[f"${b}" for b in ch_budgets], textposition="auto"))
        fig.update_layout(height=320, yaxis_title="$",
                          margin=dict(l=20, r=20, t=20, b=80),
                          xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)

    budget_rows = [[a["channel"], f"{a['pct']}%", f"${a['budget']}", a["expected_leads"]]
                    for a in bm["allocation"]]
    st.dataframe(pd.DataFrame(budget_rows,
                  columns=[t["mktg_channel"], t["mktg_budget_pct"], t["mktg_budget_usd"], t["mktg_leads"]]),
                  use_container_width=True, hide_index=True)

    # Campaigns
    st.markdown(f"#### {t['mktg_campaigns_title']}")
    camp_data = t["mktg_campaigns_data"]
    camp_json = mktg["campaigns"]

    camp_tabs = st.tabs([c["name"] for c in camp_data])
    for i, camp in enumerate(camp_data):
        with camp_tabs[i]:
            cj = camp_json[i]
            st.markdown(
                f"**{t['mktg_timing']}**: {cj['timing']} · "
                f"**{t['mktg_channel']}**: {cj['channel']} · "
                f"**{t['mktg_kpi']}**: {camp['kpi']}"
            )
            st.markdown(f"**{t['mktg_goal']}**: {camp['goal']}")
            tactics = camp["tactics"].split(" | ")
            for tactic in tactics:
                st.markdown(f"- {tactic}")

    # Calendar
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown(f"#### {t['mktg_calendar_title']}")
        cal_data = t["mktg_calendar_data"]
        st.dataframe(pd.DataFrame(cal_data, columns=[t["mktg_period"], t["mktg_activity"]]),
                      use_container_width=True, hide_index=True)

    # --- Launch Plan 180 ---
    st.markdown("---")
    st.markdown(f"### {t['launch_title']}")
    st.caption(t["launch_subtitle"])
    lp = research["launch_plan_180"]

    # Top metrics
    st.markdown(
        f"**{t['launch_total_budget']}**: \\${lp['total_budget_usd']:,} · "
        f"**{t['launch_target']}**: {lp['target_students']} · "
        f"**{t['launch_period']}**: {lp['period']} · "
        f"**{t['launch_cost_per']}**: \\${lp['cost_per_enrollment_usd']}"
    )

    # Monthly plan — tabs
    lp_months = t["launch_months_data"]
    lp_actions = t["launch_actions_data"]
    lp_tabs = st.tabs([m["month"] for m in lp_months])

    for i, mp in enumerate(lp["monthly_plan"]):
        with lp_tabs[i]:
            mt = lp_months[i]
            st.markdown(
                f"**{t['launch_phase']}**: {mt['phase']} · "
                f"**{t['launch_budget']}**: \\${mp['budget_usd']:,} · "
                f"**{t['launch_enrollments']}**: +{mp['target_enrollments']} · "
                f"**{t['launch_cumulative']}**: {mp['cumulative']}/180"
            )

            cc1, cc2 = st.columns(2)
            with cc1:
                st.markdown(f"**{t['launch_channels']}**")
                ch_rows = [[ch, f"${val:,}"] for ch, val in mp["channels"].items()]
                st.dataframe(pd.DataFrame(ch_rows, columns=[t["mktg_channel"], t["launch_budget"]]),
                              use_container_width=True, hide_index=True)
            with cc2:
                st.markdown(f"**{t['launch_actions']}**")
                for action in lp_actions[i]:
                    st.markdown(f"- {action}")

    # Cumulative chart + Budget chart
    months_labels = [m["month"] for m in lp_months]
    cumul = [mp["cumulative"] for mp in lp["monthly_plan"]]
    enrollments = [mp["target_enrollments"] for mp in lp["monthly_plan"]]
    budgets = [mp["budget_usd"] for mp in lp["monthly_plan"]]

    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure()
        fig.add_trace(go.Bar(name=t["launch_enrollments"], x=months_labels, y=enrollments,
                             marker_color="#2ecc71",
                             text=[f"+{e}" for e in enrollments], textposition="auto"))
        fig.add_trace(go.Scatter(name=t["launch_cumulative"], x=months_labels, y=cumul,
                                  mode="lines+markers+text",
                                  text=[str(c) for c in cumul],
                                  textposition="top center",
                                  line=dict(color="#e74c3c", width=3)))
        fig.update_layout(height=350, yaxis_title=t["launch_enrollments"],
                          margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months_labels, y=budgets,
                             marker_color="#3498db",
                             text=[f"${b:,}" for b in budgets], textposition="auto"))
        fig.update_layout(height=350, yaxis_title="$",
                          margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    # KPIs
    st.markdown(f"#### {t['launch_kpis_title']}")
    kp = lp["kpis"]
    k1, k2, k3 = st.columns(3)
    k1.metric(t["launch_leads"], f"{kp['total_leads_needed']:,}")
    k2.metric(t["launch_oh_attendees"], str(kp["open_house_attendees"]))
    k3.metric(t["launch_referrals"], str(kp["referral_enrollments"]))
    k4, k5, k6 = st.columns(3)
    k4.metric(t["launch_fb_reach"], f"{kp['facebook_reach']//1000}K")
    k5.metric(t["launch_tiktok_views"], f"{kp['tiktok_views']//1000000:.1f}M")
    k6.metric(t["launch_conversion"], f"{kp['conversion_rate_pct']}%")

    # --- Enrollment Risks ---
    st.markdown(f"#### {t['launch_risks_title']}")
    lr_data = t["launch_risks_data"]

    impact_colors = {"Critical": "#e74c3c", "Критический": "#e74c3c",
                     "High": "#f39c12", "Высокое": "#f39c12", "Высокая": "#f39c12",
                     "Medium": "#3498db", "Среднее": "#3498db", "Средняя": "#3498db"}

    # Risk matrix scatter
    c1, c2 = st.columns([2, 3])
    with c1:
        impact_map = {"Critical": 3, "Критический": 3, "High": 2, "Высокое": 2, "Medium": 1, "Среднее": 1}
        prob_map = {"High": 3, "Высокая": 3, "Medium": 2, "Средняя": 2, "Low": 1, "Низкая": 1}
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[prob_map.get(r["prob"], 2) for r in lr_data],
            y=[impact_map.get(r["impact"], 2) for r in lr_data],
            mode="markers+text",
            text=[r["risk"][:18] for r in lr_data],
            textposition="top center",
            textfont=dict(size=9),
            marker=dict(size=18, color=[impact_colors.get(r["impact"], "#95a5a6") for r in lr_data])
        ))
        prob_labels = [t.get("prob_levels", ["Low", "Medium", "High"])][0]
        impact_labels = [t.get("impact_levels", ["Low", "Medium", "High"])][0]
        fig.update_layout(height=380,
                          xaxis=dict(title=t["launch_risk_prob"], tickvals=[1, 2, 3], ticktext=prob_labels),
                          yaxis=dict(title=t["launch_risk_impact"], tickvals=[1, 2, 3], ticktext=["Medium", "High", "Critical"]),
                          margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        risk_rows = [[r["risk"], r["impact"], r["prob"]] for r in lr_data]
        st.dataframe(pd.DataFrame(risk_rows,
                      columns=[t["launch_risk"], t["launch_risk_impact"], t["launch_risk_prob"]]),
                      use_container_width=True, hide_index=True)

    # Detailed risks in expanders
    for r in lr_data:
        color = impact_colors.get(r["impact"], "#95a5a6")
        with st.expander(f"{'🔴' if 'rit' in r['impact'] or 'Крит' in r['impact'] else '🟡' if r['impact'] in ('High','Высокое') else '🔵'} {r['risk']} — {r['impact']}"):
            st.markdown(f"**{t['launch_risk_desc']}**: {r['desc']}")
            st.markdown(f"**{t['launch_risk_mitig']}**: {r['mitig']}")

    st.markdown("---")
    st.markdown(f"### {t['regulations']}")
    reg_data = pd.DataFrame(t["reg_rows"], columns=t["reg_cols"])
    st.dataframe(reg_data, use_container_width=True, hide_index=True)

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown(f"### {t['risk_matrix']}")
        impact_map = {"Low": 1, "Medium": 2, "High": 3}
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[impact_map[r["probability"]] for r in research["risks"]],
            y=[impact_map[r["impact"]] for r in research["risks"]],
            mode="markers+text",
            text=[r["name"][:15] for r in research["risks"]],
            textposition="top center",
            marker=dict(size=20, color=["#f39c12", "#e74c3c", "#e74c3c", "#e74c3c", "#f39c12", "#2ecc71"])
        ))
        fig.update_layout(height=350,
                          xaxis=dict(title=t["probability"], tickvals=[1, 2, 3], ticktext=t["prob_levels"]),
                          yaxis=dict(title=t["impact"], tickvals=[1, 2, 3], ticktext=t["impact_levels"]))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"### {t['opportunities']}")
        opps = pd.DataFrame(t["opp_rows"], columns=t["opp_cols"])
        st.dataframe(opps, use_container_width=True, hide_index=True)

# ============================================================
# TAB 6: POWER BI
# ============================================================
with tab6:
    st.subheader(t["pbi_title"])
    st.markdown(t["pbi_desc"])

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"### {t['excel_export']}")
        buffer = io.BytesIO()
        tables = {
            "PnL_Annual": pbi_exporter._build_pnl_table(),
            "Monthly_Year1": pbi_exporter._build_monthly_table(),
            "Expense_Breakdown": pbi_exporter._build_expense_breakdown_table(),
            "Staffing": pbi_exporter._build_staffing_table(),
            "KPI_Summary": pbi_exporter._build_kpi_table(),
            "Sensitivity": pbi_exporter._build_sensitivity_table(),
            "Growth": pbi_exporter._build_growth_table(),
            "Calendar": pbi_exporter._build_calendar_dim(),
        }
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for sheet_name, df in tables.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        st.download_button(label=t["download_excel"], data=buffer.getvalue(),
                           file_name="seasons_school_powerbi.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.caption(t["sheets_info"])

    with col2:
        st.markdown(f"### {t['dax_title']}")
        dax = pbi_exporter.get_dax_measures()
        st.download_button(label=t["download_dax"], data=dax,
                           file_name="dax_measures.dax", mime="text/plain")
        st.caption(t["dax_info"])

    with col3:
        st.markdown(f"### {t['guide_title']}")
        guide = pbi_exporter.get_powerbi_setup_guide()
        st.download_button(label=t["download_guide"], data=guide,
                           file_name="powerbi_setup_guide.txt", mime="text/plain")
        st.caption(t["guide_info"])

    st.markdown("---")
    st.subheader(t["data_preview"])
    selected_table = st.selectbox(t["select_table"], list(tables.keys()))
    st.dataframe(tables[selected_table], use_container_width=True, hide_index=True)
    st.caption(t["rows_cols"].format(r=len(tables[selected_table]), c=len(tables[selected_table].columns)))

    st.markdown("---")
    st.subheader(t["dax_ref"])
    st.code(dax, language="sql")

    st.subheader(t["pbi_setup"])
    st.markdown(t["pbi_steps"])

    st.subheader(t["theme_title"])
    theme_json = json.dumps({
        "name": "WISC",
        "dataColors": ["#2ecc71", "#e74c3c", "#3498db", "#9b59b6", "#f39c12", "#1abc9c", "#e67e22", "#95a5a6"],
        "background": "#ffffff", "foreground": "#2c3e50", "tableAccent": "#3498db"
    }, indent=2)
    st.code(theme_json, language="json")
    st.download_button(label=t["download_theme"], data=theme_json,
                       file_name="seasons_school_theme.json", mime="application/json")

# ============================================================
# TAB 7: MARKETING STRATEGY
# ============================================================
with tab7:
    marketing_tab.render(lang)

# ============================================================
# TAB 8: SALES STRATEGY
# ============================================================
with tab8:
    sales_tab.render(lang)

st.markdown("---")
st.caption(t["footer"])
