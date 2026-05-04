"""
Sales Strategy tab — WISC Cambodia admissions conversion hub.
Handles post-lead: scripts, objections, tours, training, CRM discipline, KPIs.
Reuses design-system (PALETTE + _inject_styles) from marketing_tab.py.
Scripts & objections live in data/*.{json,csv} — editable without code changes.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from dashboard.marketing_tab import PALETTE, _inject_styles, _divider, _get_lang, _brand_header, translate_text

DATA_DIR = Path(__file__).parent.parent / "data"

_SALES_VERSION = "v1 · launch-ready"

# ============================================================
# I18N
# ============================================================
SALES_LANG = {
    "ru": {
        "header": "Стратегия продаж — конверсия лидов в enrollments",
        "subheader": "Что делать после того как лид пришёл: скрипты, возражения, туры, обучение ПК, KPI-дисциплина.",
        "sections": [
            "Overview & Performance", "Funnel & Pipeline", "Response Playbook",
            "Message Scripts", "Objections Matrix", "Tour Playbook",
            "Training Course", "Product Deep-Dive", "Competitor Battle Cards",
            "Sales KPIs", "✍️ Script Translator",
        ],
        "lang_ru": "🇷🇺 Русский",
        "lang_en": "🇬🇧 English",
        "lang_km": "🇰🇭 Khmer [AIJAN-REVIEW]",
        "when": "Когда использовать",
        "goal": "Цель",
        "dont": "❌ Чего НЕ делать",
        # Script Translator
        "tr_title": "✍️ Script Translator — пиши на RU, получай EN + KM автоматически",
        "tr_help": "Быстрый генератор переводов через Google Translate. Кхмерский — черновой, Айжан утвердит. После правок можешь сохранить в data/sales_scripts.json.",
        "tr_input_label": "Текст на русском",
        "tr_source_label": "Исходный язык",
        "tr_translate_btn": "🔄 Перевести",
        "tr_en_result": "🇬🇧 English (авто)",
        "tr_km_result": "🇰🇭 Khmer (черновой · Айжан проверит)",
        "tr_save_as": "Заголовок скрипта (для сохранения)",
        "tr_save_btn": "💾 Добавить в sales_scripts.json",
        "tr_saved": "Добавлено в sales_scripts.json",
        "tr_offline_hint": "⚠️ Требуется интернет для Google Translate. Если не работает — проверь подключение.",
        "rule": "Правило",
        "objection_label": "Возражение",
        "answer_label": "Ответ",
        # 3.1 Overview
        "hero_eyebrow": "Admissions pipeline · Live",
        "hero_title": "Sales Performance",
        "hero_active": "активных лидов в pipeline",
        "tours_scheduled": "Tours scheduled",
        "this_week": "на этой неделе",
        "tours_target": "Target: 8+ / неделю",
        "apps_mtd": "Applications MTD",
        "apps_unit": "apps",
        "pipeline_to_deposit": "→ pipeline to deposit",
        "deposits_mtd": "Deposits MTD",
        "deposits_paid": "оплачено",
        "target_200": "Target: 200 к 1 сентября",
        "key_metrics": "Ключевые sales-метрики (target)",
        "speed_lead": "Speed to lead",
        "working_hours_sla": "рабочие часы — SLA",
        "showup_rate": "Show-up rate",
        "target_label": "target",
        "lead_to_enr": "Lead → Enrollment",
        "base_scenario": "базовый сценарий",
        "response_rate_sla": "Response rate SLA",
        "enrollment_pacing": "Enrollment pacing — actual vs target",
        "target_linear": "Target (linear to 200)",
        "actual": "Actual",
        "week": "Week",
        "cum_enrollments": "Cumulative enrollments",
        "team_actions_week": "Команда на этой неделе — action items",
        "deadline": "Дедлайн",
        # 3.2 Funnel
        "sales_funnel": "Sales funnel — current period",
        "sla_transitions": "Target SLA по переходам",
        "transition": "Переход",
        "target_conv": "Target conv.",
        "time": "Time",
        "owner": "Owner",
        "overall_conv_note": "Итоговая lead-to-enrollment conversion: ~8-12% (базовый сценарий)",
        "pipeline_live": "Pipeline — live lead tracker",
        "pipeline_help": "Редактируемая таблица. Для персистентности правь data/sales_pipeline.csv напрямую.",
        "save_pipeline": "💾 Сохранить pipeline в CSV",
        "saved_pipeline": "Сохранено в data/sales_pipeline.csv",
        # 3.3 Response
        "first_5": "⚡ Первые 5 минут — самый важный момент воронки",
        "rule_5min_title": "< 5 мин",
        "rule_5min_desc": "Все входящие лиды в рабочие часы (8:00–18:00 GMT+7)",
        "rule_30min_title": "< 30 мин",
        "rule_30min_desc": "Auto-bot reply вне рабочих часов + personal reply <30 мин со следующего рабочего дня",
        "rule_lang_title": "Language match",
        "rule_lang_desc": "Отвечать на том же языке, на котором написал родитель",
        "rule_oneq_title": "One question",
        "rule_oneq_desc": "Представиться, назвать школу, задать ОДИН уточняющий вопрос — не перегружать",
        "autoreply_title": "🤖 Авто-ответ вне рабочих часов",
        "autoreply_help": "Поставить в WhatsApp Business / Telegram / Messenger как away message. Переключать согласно языку лида.",
        "messengers_title": "📱 Мессенджеры по сегментам",
        "messengers_help": "В Камбодже все 3 одинаково важны. Настроить и мониторить параллельно.",
        "wa_desc": "Primary для expat + китайской диаспоры",
        "tg_desc": "Primary для кхмерского среднего класса",
        "fb_desc": "Primary для массового кхмерского сегмента (lead ads идут сюда)",
        # 3.4 Scripts
        "scripts_title": "📝 Message Scripts Library — 12 скриптов × 3 языка",
        "scripts_help": "Все скрипты в <code>data/sales_scripts.json</code> — команда может править без касания кода. Кхмерские блоки помечены <code>[AIJAN-REVIEW]</code>.",
        "script_n": "Script",
        "scripts_edit_help": "✏️ Редактируйте текст в любом из трёх полей. Выберите язык-источник и нажмите «Перевести» — другие 2 поля заполнятся автоматически. Нажмите «Сохранить», чтобы записать в <code>data/sales_scripts.json</code>.",
        "scripts_source": "Источник перевода",
        "scripts_autofill": "🔄 Перевести из источника в остальные языки",
        "scripts_save": "💾 Сохранить изменения",
        "scripts_saved": "✅ Сохранено в data/sales_scripts.json",
        "scripts_revert": "↺ Сбросить к файлу",
        "scripts_translating": "Перевожу…",
        # 3.5 Objections
        "obj_rules_title": "🧩 Правило работы с возражениями — 6 шагов",
        "obj_matrix_title": "Matrix — 15 возражений с ответами на 3 языках",
        "filter_category": "Фильтр по категории",
        "all": "Все",
        # 3.6 Tour
        "tour_title": "🗺️ Campus Tour — 60-минутный timeline",
        "tour_intro": "Тур — это <b>продукт</b>, не прогулка. Правильно проведённый тур закрывает 70%+ на application. Плохой тур губит самый горячий лид.",
        "tour_never": "🚫 Чего НИКОГДА не делать на туре",
        # 3.7 Training
        "training_title_short": "Admissions Officer Training",
        "training_modules_sub": "10 модулей · 3 дня интенсив",
        "passing_score": "проходной балл",
        "start_label": "Start",
        "end_label": "End",
        "golive_label": "Go-live",
        "launch_day": "Launch day",
        "course_progress": "Progress курса",
        "goal_emoji": "🎯 Цель",
        "theory_emoji": "📖 Теория",
        "video": "🎬 Видео",
        "exercises_emoji": "🏋️ Практические упражнения",
        "quiz_emoji": "✅ Quiz",
        "correct": "✅ Верно",
        "incorrect": "❌ Не верно",
        "module_done": "Модуль пройден",
        # 3.8 Product
        "pricing_title": "💰 Pricing cheatsheet — калькулятор скидок",
        "pricing_help": "Выберите класс и применяемые скидки — получите финальную сумму по 3 payment-вариантам.",
        "grade_label": "Класс",
        "discounts_label": "Применяемые скидки",
        "discount_eb15": "Early Bird 15% (до 31 мая)",
        "discount_eb10": "Early Bird 10% (до 30 июня)",
        "discount_sib5": "Sibling −5% (2-й ребёнок)",
        "discount_sib10": "Sibling −10% (3-й+)",
        "discount_annual": "Annual payment −10%",
        "annual_pay": "Annual (1 pay)",
        "semester_pay": "Semester (2×)",
        "term_pay": "Term (3×)",
        "base_tuition": "Base tuition",
        "per_year": "/ год",
        "max_total": "Максимум суммарной скидки: 25%",
        "program_title": "📘 Program comparison by grade",
        "infra_title": "🏫 Infrastructure gallery + selling lines",
        "infra_help": "Selling line — готовая фраза для тура. Каждый ПК должен знать все 10 наизусть.",
        # 3.9 Competitors
        "comp_title": "⚔️ Competitor Battle Cards",
        "comp_intro": "Placeholder для 7 конкурентов. Айжан финализирует после secret shopping. Поля редактируемые — правь <code>data/competitor_battle_cards.json</code>.",
        "their_strengths": "💪 Их сильные стороны",
        "their_weaknesses": "⚠️ Их слабые стороны",
        "our_edge": "🎯 Наше преимущество",
        "pitch_against": "🗣️ Pitch против них",
        # 3.10 KPIs
        "kpis_title": "📊 Individual KPIs — Admissions Officer scorecard",
        "kpis_intro": "Еженедельно обновляет команда. Правь <code>data/sales_kpis.csv</code>. Цветовой код: 🟢 on-target / 🟡 attention / 🔴 behind.",
        "tier_top": "Top-of-funnel",
        "tier_mid": "Mid-funnel",
        "tier_bottom": "Bottom-funnel",
        "tier_quality": "Quality",
        "tier_activity": "Activity",
        "recording_title": "🎧 Recording & review cadence",
        "incentives_title": "💵 Incentives — предложение (команда утвердит)",
    },
    "en": {
        "header": "Sales strategy — lead-to-enrollment conversion",
        "subheader": "What to do after the lead lands: scripts, objections, tours, training, KPI discipline.",
        "sections": [
            "Overview & Performance", "Funnel & Pipeline", "Response Playbook",
            "Message Scripts", "Objections Matrix", "Tour Playbook",
            "Training Course", "Product Deep-Dive", "Competitor Battle Cards",
            "Sales KPIs", "✍️ Script Translator",
        ],
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "lang_km": "🇰🇭 Khmer [AIJAN-REVIEW]",
        "when": "When to use",
        "goal": "Goal",
        "dont": "❌ What NOT to do",
        # Script Translator
        "tr_title": "✍️ Script Translator — write in RU/EN, get the other languages auto",
        "tr_help": "Quick translation generator via Google Translate. Khmer is draft — Aizhan will approve. You can save edited scripts to data/sales_scripts.json.",
        "tr_input_label": "Source text",
        "tr_source_label": "Source language",
        "tr_translate_btn": "🔄 Translate",
        "tr_en_result": "🇬🇧 English (auto)",
        "tr_km_result": "🇰🇭 Khmer (draft · Aizhan to review)",
        "tr_save_as": "Script title (for saving)",
        "tr_save_btn": "💾 Append to sales_scripts.json",
        "tr_saved": "Added to sales_scripts.json",
        "tr_offline_hint": "⚠️ Internet required for Google Translate. If it fails — check your connection.",
        "rule": "Rule",
        "objection_label": "Objection",
        "answer_label": "Answer",
        # 3.1 Overview
        "hero_eyebrow": "Admissions pipeline · Live",
        "hero_title": "Sales Performance",
        "hero_active": "active leads in pipeline",
        "tours_scheduled": "Tours scheduled",
        "this_week": "this week",
        "tours_target": "Target: 8+ / week",
        "apps_mtd": "Applications MTD",
        "apps_unit": "apps",
        "pipeline_to_deposit": "→ pipeline to deposit",
        "deposits_mtd": "Deposits MTD",
        "deposits_paid": "paid",
        "target_200": "Target: 200 by Sep 1",
        "key_metrics": "Key sales metrics (target)",
        "speed_lead": "Speed to lead",
        "working_hours_sla": "working hours SLA",
        "showup_rate": "Show-up rate",
        "target_label": "target",
        "lead_to_enr": "Lead → Enrollment",
        "base_scenario": "base scenario",
        "response_rate_sla": "Response rate SLA",
        "enrollment_pacing": "Enrollment pacing — actual vs target",
        "target_linear": "Target (linear to 200)",
        "actual": "Actual",
        "week": "Week",
        "cum_enrollments": "Cumulative enrollments",
        "team_actions_week": "Team this week — action items",
        "deadline": "Due",
        # 3.2 Funnel
        "sales_funnel": "Sales funnel — current period",
        "sla_transitions": "Target SLA per stage transition",
        "transition": "Transition",
        "target_conv": "Target conv.",
        "time": "Time",
        "owner": "Owner",
        "overall_conv_note": "Overall lead-to-enrollment conversion: ~8-12% (base scenario)",
        "pipeline_live": "Pipeline — live lead tracker",
        "pipeline_help": "Editable table. For persistence edit data/sales_pipeline.csv directly.",
        "save_pipeline": "💾 Save pipeline to CSV",
        "saved_pipeline": "Saved to data/sales_pipeline.csv",
        # 3.3 Response
        "first_5": "⚡ First 5 minutes — the most important moment of the funnel",
        "rule_5min_title": "< 5 min",
        "rule_5min_desc": "All inbound leads during working hours (8:00–18:00 GMT+7)",
        "rule_30min_title": "< 30 min",
        "rule_30min_desc": "Auto-bot reply off-hours + personal reply <30 min from start of next working day",
        "rule_lang_title": "Language match",
        "rule_lang_desc": "Reply in the same language the parent used",
        "rule_oneq_title": "One question",
        "rule_oneq_desc": "Introduce yourself, name the school, ask ONE clarifying question — don't overload",
        "autoreply_title": "🤖 Off-hours auto-reply",
        "autoreply_help": "Set in WhatsApp Business / Telegram / Messenger as away message. Switch based on lead's language.",
        "messengers_title": "📱 Messengers by segment",
        "messengers_help": "In Cambodia all 3 are equally important. Configure and monitor in parallel.",
        "wa_desc": "Primary for expat + Chinese diaspora",
        "tg_desc": "Primary for Khmer middle class",
        "fb_desc": "Primary for mass-market Khmer segment (lead ads land here)",
        # 3.4 Scripts
        "scripts_title": "📝 Message Scripts Library — 12 scripts × 3 languages",
        "scripts_help": "All scripts live in <code>data/sales_scripts.json</code> — team can edit text without touching code. Khmer blocks marked <code>[AIJAN-REVIEW]</code>.",
        "script_n": "Script",
        "scripts_edit_help": "✏️ Edit any of the three text fields. Pick a source language and press «Translate» — the other 2 fields will fill in automatically. Press «Save» to write back to <code>data/sales_scripts.json</code>.",
        "scripts_source": "Translate from",
        "scripts_autofill": "🔄 Translate source into the other languages",
        "scripts_save": "💾 Save changes",
        "scripts_saved": "✅ Saved to data/sales_scripts.json",
        "scripts_revert": "↺ Reset to file",
        "scripts_translating": "Translating…",
        # 3.5 Objections
        "obj_rules_title": "🧩 Objection-handling rules — 6 steps",
        "obj_matrix_title": "Matrix — 15 objections with answers in 3 languages",
        "filter_category": "Filter by category",
        "all": "All",
        # 3.6 Tour
        "tour_title": "🗺️ Campus Tour — 60-minute timeline",
        "tour_intro": "A tour is a <b>product</b>, not a stroll. Done right it closes 70%+ on application. Done wrong it kills the hottest lead.",
        "tour_never": "🚫 What NEVER to do on a tour",
        # 3.7 Training
        "training_title_short": "Admissions Officer Training",
        "training_modules_sub": "10 modules · 3-day intensive",
        "passing_score": "passing score",
        "start_label": "Start",
        "end_label": "End",
        "golive_label": "Go-live",
        "launch_day": "Launch day",
        "course_progress": "Course progress",
        "goal_emoji": "🎯 Goal",
        "theory_emoji": "📖 Theory",
        "video": "🎬 Video",
        "exercises_emoji": "🏋️ Exercises",
        "quiz_emoji": "✅ Quiz",
        "correct": "✅ Correct",
        "incorrect": "❌ Incorrect",
        "module_done": "Module completed",
        # 3.8 Product
        "pricing_title": "💰 Pricing cheatsheet — discount calculator",
        "pricing_help": "Pick a grade and applicable discounts — see final price across 3 payment options.",
        "grade_label": "Grade",
        "discounts_label": "Applicable discounts",
        "discount_eb15": "Early Bird 15% (by May 31)",
        "discount_eb10": "Early Bird 10% (by Jun 30)",
        "discount_sib5": "Sibling −5% (2nd child)",
        "discount_sib10": "Sibling −10% (3rd+)",
        "discount_annual": "Annual payment −10%",
        "annual_pay": "Annual (1 pay)",
        "semester_pay": "Semester (2×)",
        "term_pay": "Term (3×)",
        "base_tuition": "Base tuition",
        "per_year": "/ year",
        "max_total": "Max combined discount: 25%",
        "program_title": "📘 Program comparison by grade",
        "infra_title": "🏫 Infrastructure gallery + selling lines",
        "infra_help": "Selling line — ready-to-use phrase for tours. Every Admissions Officer should know all 10 by heart.",
        # 3.9 Competitors
        "comp_title": "⚔️ Competitor Battle Cards",
        "comp_intro": "Placeholder for 7 competitors. Aizhan will finalize after secret shopping. Editable — edit <code>data/competitor_battle_cards.json</code>.",
        "their_strengths": "💪 Their strengths",
        "their_weaknesses": "⚠️ Their weaknesses",
        "our_edge": "🎯 Our edge",
        "pitch_against": "🗣️ Pitch against them",
        # 3.10 KPIs
        "kpis_title": "📊 Individual KPIs — Admissions Officer scorecard",
        "kpis_intro": "Team updates weekly. Edit <code>data/sales_kpis.csv</code>. Color code: 🟢 on-target / 🟡 attention / 🔴 behind.",
        "tier_top": "Top-of-funnel",
        "tier_mid": "Mid-funnel",
        "tier_bottom": "Bottom-funnel",
        "tier_quality": "Quality",
        "tier_activity": "Activity",
        "recording_title": "🎧 Recording & review cadence",
        "incentives_title": "💵 Incentives — proposal (team to approve)",
    },
    "km": {
        # [AIJAN-REVIEW] — Khmer UI translations; fallback to EN for missing keys
        "header": "យុទ្ធសាស្ត្រលក់ — បំប្លែងលីដទៅការចុះឈ្មោះ",
        "subheader": "អ្វីដែលត្រូវធ្វើបន្ទាប់ពីលីដមកដល់: ស្គ្រីប, ការឆ្លើយតបជម្លោះ, ទស្សនកិច្ច, ការបណ្តុះបណ្តាល, វិន័យ KPI។",
        "sections": [
            "ទិដ្ឋភាពទូទៅ", "Funnel & Pipeline", "ស្គ្រីបឆ្លើយតប",
            "បណ្ណាល័យស្គ្រីប", "តារាងជម្លោះ", "មគ្គុទ្ទេសក៍ទស្សនកិច្ច",
            "វគ្គបណ្តុះបណ្តាល", "ចំណេះដឹងផលិតផល", "ប្រៀបធៀបដៃគូប្រកួតប្រជែង",
            "Sales KPIs", "✍️ Script Translator",
        ],
        "lang_ru": "🇷🇺 Russian",
        "lang_en": "🇬🇧 English",
        "lang_km": "🇰🇭 Khmer",
        "when": "ពេលណាត្រូវប្រើ",
        "goal": "គោលដៅ",
        "dont": "❌ អ្វីដែលមិនត្រូវធ្វើ",
        "rule": "ច្បាប់",
        "objection_label": "ជម្លោះ",
        "answer_label": "ចម្លើយ",
        # 3.1
        "hero_eyebrow": "បញ្ជីលីដ · ផ្ទាល់",
        "hero_title": "ប្រសិទ្ធភាពលក់",
        "hero_active": "លីដសកម្មនៅក្នុង pipeline",
        "tours_scheduled": "ទស្សនកិច្ចបានកំណត់",
        "this_week": "សប្តាហ៍នេះ",
        "tours_target": "គោលដៅ: 8+ / សប្តាហ៍",
        "apps_mtd": "ពាក្យដាក់ (ខែ)",
        "apps_unit": "ពាក្យ",
        "pipeline_to_deposit": "→ ឆ្ពោះទៅ deposit",
        "deposits_mtd": "Deposits (ខែ)",
        "deposits_paid": "បានបង់",
        "target_200": "គោលដៅ: 200 នៅថ្ងៃ 1 កញ្ញា",
        "key_metrics": "រង្វាយតម្លៃលក់ (គោលដៅ)",
        "speed_lead": "ល្បឿនឆ្លើយតបលីដ",
        "working_hours_sla": "ម៉ោងធ្វើការ SLA",
        "showup_rate": "អត្រាមកដល់ទស្សនកិច្ច",
        "target_label": "គោលដៅ",
        "lead_to_enr": "លីដ → ការចុះឈ្មោះ",
        "base_scenario": "ស្ថានភាពមូលដ្ឋាន",
        "response_rate_sla": "អត្រាឆ្លើយតប SLA",
        "enrollment_pacing": "ការចុះឈ្មោះ — ជាក់ស្តែង vs គោលដៅ",
        "target_linear": "គោលដៅ (linear ដល់ 200)",
        "actual": "ជាក់ស្តែង",
        "week": "សប្តាហ៍",
        "cum_enrollments": "ការចុះឈ្មោះកន្សំ",
        "team_actions_week": "ក្រុមសប្តាហ៍នេះ — action items",
        "deadline": "ថ្ងៃកំណត់",
        # 3.2
        "sales_funnel": "Sales funnel — រយៈពេលបច្ចុប្បន្ន",
        "sla_transitions": "គោលដៅ SLA តាមដំណាក់កាល",
        "transition": "ការផ្លាស់ប្តូរ",
        "target_conv": "គោលដៅ",
        "time": "ពេលវេលា",
        "owner": "ម្ចាស់",
        "overall_conv_note": "ការបំប្លែងសរុប លីដ-ទៅ-ការចុះឈ្មោះ: ~8-12%",
        "pipeline_live": "Pipeline — ការតាមដានលីដផ្ទាល់",
        "pipeline_help": "តារាងអាចកែបាន។ សម្រាប់ភាពជាប់លាប់ កែ data/sales_pipeline.csv ដោយផ្ទាល់។",
        "save_pipeline": "💾 រក្សាទុក pipeline ទៅ CSV",
        "saved_pipeline": "បានរក្សាទុកទៅ data/sales_pipeline.csv",
        # 3.3
        "first_5": "⚡ 5 នាទីដំបូង — ពេលវេលាសំខាន់បំផុត",
        "rule_5min_title": "< 5 នាទី",
        "rule_5min_desc": "លីដទាំងអស់ក្នុងម៉ោងធ្វើការ (8:00–18:00 GMT+7)",
        "rule_30min_title": "< 30 នាទី",
        "rule_30min_desc": "Auto-reply ក្រៅម៉ោងធ្វើការ + ឆ្លើយតបផ្ទាល់ <30 នាទីពេលចាប់ផ្តើមថ្ងៃធ្វើការបន្ទាប់",
        "rule_lang_title": "ភាសាដូចគ្នា",
        "rule_lang_desc": "ឆ្លើយតបជាភាសាដែលឪពុកម្តាយបានសរសេរ",
        "rule_oneq_title": "សំណួរមួយ",
        "rule_oneq_desc": "ណែនាំខ្លួន, ឈ្មោះសាលា, សួរសំណួរបញ្ជាក់មួយ — កុំផ្ទុកលើស",
        "autoreply_title": "🤖 ការឆ្លើយតបក្រៅម៉ោងធ្វើការ",
        "autoreply_help": "ដាក់ក្នុង WhatsApp Business / Telegram / Messenger ជា away message",
        "messengers_title": "📱 Messengers តាមផ្នែក",
        "messengers_help": "នៅកម្ពុជាទាំង 3 សំខាន់ដូចគ្នា។ រៀបចំនិងតាមដានស្របគ្នា",
        "wa_desc": "Primary សម្រាប់ expat + ជនជាតិចិន",
        "tg_desc": "Primary សម្រាប់ជាន់កណ្តាលខ្មែរ",
        "fb_desc": "Primary សម្រាប់ផ្នែកខ្មែរមួលដ្ឋានធំ (lead ads ចូលមកទីនេះ)",
        # 3.4
        "scripts_title": "📝 បណ្ណាល័យស្គ្រីប — 12 ស្គ្រីប × 3 ភាសា",
        "scripts_help": "ស្គ្រីបទាំងអស់នៅក្នុង <code>data/sales_scripts.json</code> — ក្រុមអាចកែបានដោយមិនប៉ះកូដ",
        "script_n": "ស្គ្រីប",
        "scripts_edit_help": "✏️ កែប្រែអក្សរក្នុងវាលណាមួយក្នុងបី។ ជ្រើសរើសភាសាប្រភព ហើយចុច «បកប្រែ» — វាល 2 ផ្សេងទៀតនឹងបំពេញដោយស្វ័យប្រវត្តិ។ ចុច «រក្សាទុក» ដើម្បីសរសេរទៅកាន់ <code>data/sales_scripts.json</code>។",
        "scripts_source": "ប្រភពបកប្រែ",
        "scripts_autofill": "🔄 បកប្រែពីប្រភពទៅភាសាដទៃ",
        "scripts_save": "💾 រក្សាទុកការកែប្រែ",
        "scripts_saved": "✅ បានរក្សាទុកទៅ data/sales_scripts.json",
        "scripts_revert": "↺ កំណត់ឡើងវិញតាមឯកសារ",
        "scripts_translating": "កំពុងបកប្រែ…",
        # 3.5
        "obj_rules_title": "🧩 ច្បាប់ដោះស្រាយជម្លោះ — 6 ជំហាន",
        "obj_matrix_title": "តារាង — 15 ជម្លោះជាមួយចម្លើយ 3 ភាសា",
        "filter_category": "ច្រោះតាមប្រភេទ",
        "all": "ទាំងអស់",
        # 3.6
        "tour_title": "🗺️ ទស្សនកិច្ច — timeline 60 នាទី",
        "tour_intro": "ទស្សនកិច្ចគឺជា <b>ផលិតផល</b> មិនមែនជាដំណើរកំសាន្តទេ។ ការធ្វើបានត្រឹមត្រូវបិទបាន 70%+ នៅ application។",
        "tour_never": "🚫 អ្វីដែលមិនត្រូវធ្វើនៅលើទស្សនកិច្ច",
        # 3.7
        "training_title_short": "ការបណ្តុះបណ្តាល Admissions Officer",
        "training_modules_sub": "10 modules · 3 ថ្ងៃ intensive",
        "passing_score": "ពិន្ទុឆ្លងកាត់",
        "start_label": "ចាប់ផ្តើម",
        "end_label": "បញ្ចប់",
        "golive_label": "Go-live",
        "launch_day": "ថ្ងៃបើកដំណើរការ",
        "course_progress": "វឌ្ឍនភាពវគ្គ",
        "goal_emoji": "🎯 គោលដៅ",
        "theory_emoji": "📖 ទ្រឹស្តី",
        "video": "🎬 វីដេអូ",
        "exercises_emoji": "🏋️ លំហាត់",
        "quiz_emoji": "✅ Quiz",
        "correct": "✅ ត្រឹមត្រូវ",
        "incorrect": "❌ មិនត្រឹមត្រូវ",
        "module_done": "Module បានបញ្ចប់",
        # 3.8
        "pricing_title": "💰 ម៉ាស៊ីនគណនាតម្លៃ + ការបញ្ចុះតម្លៃ",
        "pricing_help": "ជ្រើសរើសថ្នាក់ និង discounts — បង្ហាញតម្លៃចុងក្រោយជា 3 វិធីបង់ប្រាក់",
        "grade_label": "ថ្នាក់",
        "discounts_label": "ការបញ្ចុះតម្លៃដែលអនុវត្តបាន",
        "discount_eb15": "Early Bird 15% (មុនថ្ងៃ 31 ឧសភា)",
        "discount_eb10": "Early Bird 10% (មុនថ្ងៃ 30 មិថុនា)",
        "discount_sib5": "បងប្អូន −5% (កូនទី 2)",
        "discount_sib10": "បងប្អូន −10% (កូនទី 3+)",
        "discount_annual": "ទូទាត់ប្រចាំឆ្នាំ −10%",
        "annual_pay": "ប្រចាំឆ្នាំ (1)",
        "semester_pay": "ឆមាស (2×)",
        "term_pay": "Term (3×)",
        "base_tuition": "Tuition មូលដ្ឋាន",
        "per_year": "/ ឆ្នាំ",
        "max_total": "អតិបរមានៃការបញ្ចុះសរុប: 25%",
        "program_title": "📘 ប្រៀបធៀបកម្មវិធីតាមថ្នាក់",
        "infra_title": "🏫 គ្រឿងបរិក្ខារ + ប្រយោគសម្រាប់លក់",
        "infra_help": "Selling line — ប្រយោគត្រៀមសម្រាប់ទស្សនកិច្ច",
        # 3.9
        "comp_title": "⚔️ Battle Cards ដៃគូប្រកួតប្រជែង",
        "comp_intro": "ទីតាំងសម្រាប់ដៃគូប្រកួតប្រជែង 7 នាក់។ Aizhan នឹងបញ្ចប់បន្ទាប់ពី secret shopping។",
        "their_strengths": "💪 ភាពខ្លាំងរបស់ពួកគេ",
        "their_weaknesses": "⚠️ ភាពខ្សោយរបស់ពួកគេ",
        "our_edge": "🎯 អត្ថប្រយោជន៍របស់យើង",
        "pitch_against": "🗣️ Pitch ប្រឆាំងនឹងពួកគេ",
        # 3.10
        "kpis_title": "📊 KPIs ផ្ទាល់ខ្លួន — Admissions Officer scorecard",
        "kpis_intro": "ក្រុមធ្វើបច្ចុប្បន្នភាពជារៀងរាល់សប្តាហ៍។ លេខពណ៌: 🟢 ផ្លូវល្អ / 🟡 យកចិត្តទុកដាក់ / 🔴 យឺត។",
        "tier_top": "Top-of-funnel",
        "tier_mid": "Mid-funnel",
        "tier_bottom": "Bottom-funnel",
        "tier_quality": "គុណភាព",
        "tier_activity": "សកម្មភាព",
        "recording_title": "🎧 Recording & review cadence",
        "incentives_title": "💵 Incentives — ការស្នើសុំ",
    },
}


# ============================================================
# LOADERS
# ============================================================
@st.cache_data
def _load_json(filename: str) -> dict:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def _load_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / filename)


# ============================================================
# GENERIC TRILINGUAL EDITOR (auto-translate + save + revert)
# ============================================================
def _save_json_file(filename: str, data: dict):
    """Atomic-ish write of a JSON file in data/."""
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _cb_translate_block(prefix: str, src_code: str):
    src_text = st.session_state.get(f"{prefix}_{src_code}", "")
    if not src_text or not src_text.strip():
        return
    for tgt in ("en", "ru", "km"):
        if tgt == src_code:
            continue
        st.session_state[f"{prefix}_{tgt}"] = translate_text(src_text, target=tgt, source=src_code)


def _cb_revert_block(prefix: str, originals: dict):
    for code in ("en", "ru", "km"):
        st.session_state[f"{prefix}_{code}"] = originals.get(code, "")
    st.session_state.pop(f"{prefix}_saved_flag", None)


def _seed_block(prefix: str, en: str, ru: str, km: str):
    """Seed st.session_state from file values once per prefix."""
    for code, val in (("en", en), ("ru", ru), ("km", km)):
        key = f"{prefix}_{code}"
        if key not in st.session_state:
            st.session_state[key] = val or ""


def _render_trilingual_editor(
    *,
    L: dict,
    lang: str,
    prefix: str,
    en: str,
    ru: str,
    km: str,
    on_save=None,       # zero-arg callable; required when show_save_revert=True
    height: int = 220,
    lang_labels: dict = None,
    show_save_revert: bool = True,
):
    """Renders 3 textareas (en/ru/km) + auto-translate radio + save/revert buttons.
    Caller provides on_save (no args) — it should read values from st.session_state[f"{prefix}_{code}"]
    and write them to the relevant data file, then optionally st.cache_data.clear().
    """
    if lang_labels is None:
        lang_labels = {"en": L["lang_en"], "ru": L["lang_ru"], "km": L["lang_km"]}

    _seed_block(prefix, en, ru, km)

    cols = st.columns(3)
    for col, code in zip(cols, ("en", "ru", "km")):
        with col:
            st.markdown(f"**{lang_labels[code]}**")
            st.text_area(
                label=f"{lang_labels[code]} body",
                key=f"{prefix}_{code}",
                height=height,
                label_visibility="collapsed",
            )

    if show_save_revert:
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.2, 2.5, 1.2, 1.2])
    else:
        ctrl1, ctrl2 = st.columns([1.2, 4.9])
    with ctrl1:
        src_code = st.radio(
            L["scripts_source"],
            options=("en", "ru", "km"),
            format_func=lambda c: lang_labels[c],
            horizontal=False,
            key=f"{prefix}_src",
            index={"ru": 1, "en": 0, "km": 2}.get(lang, 0),
        )
    with ctrl2:
        st.button(
            L["scripts_autofill"],
            key=f"{prefix}_translate_btn",
            on_click=_cb_translate_block,
            args=(prefix, src_code),
            use_container_width=True,
        )
    if show_save_revert:
        with ctrl3:
            def _save_wrapper():
                on_save()
                st.cache_data.clear()
                st.session_state[f"{prefix}_saved_flag"] = True
            st.button(
                L["scripts_save"],
                key=f"{prefix}_save_btn",
                on_click=_save_wrapper,
                type="primary",
                use_container_width=True,
            )
        with ctrl4:
            st.button(
                L["scripts_revert"],
                key=f"{prefix}_revert_btn",
                on_click=_cb_revert_block,
                args=(prefix, {"en": en, "ru": ru, "km": km}),
                use_container_width=True,
            )

        if st.session_state.pop(f"{prefix}_saved_flag", False):
            st.success(L["scripts_saved"])


# ============================================================
# SECTION 3.1 — SALES OVERVIEW & PERFORMANCE
# ============================================================
def _section_overview(L: dict, lang: str):
    # Pipeline data
    pipe = _load_csv("sales_pipeline.csv")

    # Metrics
    active = len(pipe[~pipe["stage"].isin(["Enrolled", "Lost"])])
    tours_week = len(pipe[pipe["stage"].isin(["Tour Booked", "Tour Done"])])
    apps_mtd = len(pipe[pipe["stage"].isin(["Application", "Deposit", "Enrolled"])])
    deposits_mtd = len(pipe[pipe["stage"].isin(["Deposit", "Enrolled"])])

    # Hero block
    st.markdown(
        f"""
        <div class="mkt-hero-big">
            <div class="mkt-hero-grid">
                <div>
                    <div class="mkt-hero-label">{L['hero_eyebrow']}</div>
                    <div class="mkt-hero-title">{L['hero_title']}</div>
                    <div class="mkt-hero-value">{active}</div>
                    <div class="mkt-meta" style="margin-top:4px;">{L['hero_active']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['tours_scheduled']}</div>
                    <div class="mkt-hero-counter">{tours_week}<span class="unit">{L['this_week']}</span></div>
                    <div class="mkt-hero-date">{L['tours_target']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['apps_mtd']}</div>
                    <div class="mkt-hero-counter">{apps_mtd}<span class="unit">{L['apps_unit']}</span></div>
                    <div class="mkt-hero-date">{L['pipeline_to_deposit']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['deposits_mtd']}</div>
                    <div class="mkt-hero-counter">{deposits_mtd}<span class="unit">{L['deposits_paid']}</span></div>
                    <div class="mkt-hero-date">{L['target_200']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _divider()

    # KPI row
    st.markdown(f'<div class="mkt-eyebrow">{L["key_metrics"]}</div>', unsafe_allow_html=True)
    m = st.columns(4)
    m[0].metric(L["speed_lead"], "< 5 min", delta=L["working_hours_sla"])
    m[1].metric(L["showup_rate"], "> 70%", delta=L["target_label"])
    m[2].metric(L["lead_to_enr"], "12%", delta=L["base_scenario"])
    m[3].metric(L["response_rate_sla"], "> 95%", delta=L["target_label"])

    _divider()

    # Enrollment pacing
    st.markdown(f'<div class="mkt-eyebrow">{L["enrollment_pacing"]}</div>', unsafe_allow_html=True)
    weeks = pd.date_range(start="2026-05-04", end="2026-08-31", freq="W-MON")
    n = len(weeks)
    target = [round(200 * (i + 1) / n) for i in range(n)]
    actual = [0] * n
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks, y=target, mode="lines", name=L["target_linear"],
        line=dict(color=PALETTE["text_faint"], width=2, dash="dash")
    ))
    fig.add_trace(go.Scatter(
        x=weeks, y=actual, mode="lines+markers", name=L["actual"],
        line=dict(color=PALETTE["primary"], width=3)
    ))
    fig.update_layout(
        height=320, margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=L["week"], yaxis_title=L["cum_enrollments"],
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=PALETTE["text"]),
    )
    st.plotly_chart(fig, use_container_width=True)

    _divider()

    # Team action items this week — bilingual
    st.markdown(f'<div class="mkt-eyebrow">{L["team_actions_week"]}</div>', unsafe_allow_html=True)
    actions_ru = [
        ("Admissions Officer", "Ответить всем new leads < 5 мин", "Daily", "🟢"),
        ("Admissions Officer", "15 звонков warm leads", "Пятница", "🟡"),
        ("Айжан", "Finalize Khmer scripts [AIJAN-REVIEW]", "30 апреля", "🟡"),
        ("Кайсар", "Review call recordings × 5", "Пятница", "🟢"),
        ("ПК + Кайсар", "Training course Modules 1-3 (product / segments / psychology)", "28 апреля", "🔴"),
        ("Admissions Officer", "Забронировать 10 tour slots в Calendly на май", "28 апреля", "🟡"),
    ]
    actions_en = [
        ("Admissions Officer", "Reply to all new leads < 5 min", "Daily", "🟢"),
        ("Admissions Officer", "15 calls to warm leads", "Friday", "🟡"),
        ("Aizhan", "Finalize Khmer scripts [AIJAN-REVIEW]", "Apr 30", "🟡"),
        ("Kaisar", "Review call recordings × 5", "Friday", "🟢"),
        ("Officer + Kaisar", "Training course Modules 1-3 (product / segments / psychology)", "Apr 28", "🔴"),
        ("Admissions Officer", "Book 10 tour slots in Calendly for May", "Apr 28", "🟡"),
    ]
    actions = actions_ru if lang == "ru" else actions_en
    for who, what, due, dot in actions:
        st.markdown(
            f"""
            <div class="mkt-meeting">
                <div>
                    <div class="mkt-meeting-title">{what}</div>
                    <div class="mkt-meeting-agenda">👤 {who} · {L['deadline']}: {due}</div>
                </div>
                <div class="mkt-meeting-who">{dot}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# SECTION 3.2 — FUNNEL & PIPELINE
# ============================================================
_FUNNEL_STAGES = ["New", "Contacted", "Qualified", "Tour Booked", "Tour Done",
                  "Application", "Entrance Test", "Deposit", "Enrolled"]


def _section_funnel(L: dict, lang: str):
    pipe = _load_csv("sales_pipeline.csv")

    st.markdown(f'<div class="mkt-eyebrow">{L["sales_funnel"]}</div>', unsafe_allow_html=True)

    # Count leads by stage
    stage_counts = {s: 0 for s in _FUNNEL_STAGES}
    for st_name in pipe["stage"]:
        if st_name in stage_counts:
            stage_counts[st_name] += 1
    # Cumulative for funnel (stages lower down = subset)
    cumulative = {}
    remaining = len(pipe)
    for s in _FUNNEL_STAGES:
        cumulative[s] = remaining
        remaining -= stage_counts[s]

    c1, c2 = st.columns([1.2, 1])
    with c1:
        fig = go.Figure(go.Funnel(
            y=_FUNNEL_STAGES,
            x=[cumulative[s] for s in _FUNNEL_STAGES],
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": [PALETTE["primary"], "#e67e22", PALETTE["warning"], PALETTE["gold"],
                              "#d4a74a", PALETTE["info"], "#6bb6ec", "#8e44ad", PALETTE["success"]]},
        ))
        fig.update_layout(height=480, margin=dict(l=10, r=10, t=10, b=10),
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font=dict(color=PALETTE["text"]))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f'<div class="mkt-eyebrow">{L["sla_transitions"]}</div>', unsafe_allow_html=True)
        sla_rows_ru = [
            ("New → Contacted", "95%", "< 5 мин (раб) / < 30 мин (off-hours)", "ПК"),
            ("Contacted → Qualified", "70%", "1 день", "ПК"),
            ("Qualified → Tour Booked", "60%", "2 дня", "ПК"),
            ("Tour Booked → Tour Done", "75% (show-up)", "Назначенная дата", "ПК"),
            ("Tour Done → Application", "40%", "3 дня после тура", "ПК + Кайсар"),
            ("Application → Deposit", "75%", "7 дней", "ПК"),
            ("Deposit → Enrolled", "98%", "До 1 сентября", "ПК + Кайсар"),
        ]
        sla_rows_en = [
            ("New → Contacted", "95%", "< 5 min (hrs) / < 30 min (off-hrs)", "Officer"),
            ("Contacted → Qualified", "70%", "1 day", "Officer"),
            ("Qualified → Tour Booked", "60%", "2 days", "Officer"),
            ("Tour Booked → Tour Done", "75% (show-up)", "Scheduled date", "Officer"),
            ("Tour Done → Application", "40%", "3 days after tour", "Officer + Kaisar"),
            ("Application → Deposit", "75%", "7 days", "Officer"),
            ("Deposit → Enrolled", "98%", "By Sep 1", "Officer + Kaisar"),
        ]
        sla_rows = sla_rows_ru if lang == "ru" else sla_rows_en
        sla_df = pd.DataFrame(sla_rows, columns=[L["transition"], L["target_conv"], L["time"], L["owner"]])
        st.dataframe(sla_df, use_container_width=True, hide_index=True, height=300)
        st.caption(L["overall_conv_note"])

    _divider()

    # Editable pipeline table
    st.markdown(f'<div class="mkt-eyebrow">{L["pipeline_live"]}</div>', unsafe_allow_html=True)
    st.caption(L["pipeline_help"])
    owner_options = (["ПК", "ПК + Кайсар", "Кайсар", "Айжан"] if lang == "ru"
                     else ["Officer", "Officer + Kaisar", "Kaisar", "Aizhan"])
    edited = st.data_editor(
        pipe,
        key="sales_pipeline_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "stage": st.column_config.SelectboxColumn("Stage", options=_FUNNEL_STAGES + ["Lost"]),
            "priority": st.column_config.SelectboxColumn("Priority", options=["Hot", "Warm", "Cold"]),
            "owner": st.column_config.SelectboxColumn("Owner", options=owner_options),
        },
        hide_index=True,
        height=500,
    )
    if st.button(L["save_pipeline"], key="sales_pipe_save"):
        edited.to_csv(DATA_DIR / "sales_pipeline.csv", index=False)
        st.cache_data.clear()
        st.success(L["saved_pipeline"])


# ============================================================
# SECTION 3.3 — RESPONSE PLAYBOOK
# ============================================================
def _section_response(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["first_5"]}</div>', unsafe_allow_html=True)

    rules = [
        (L["rule_5min_title"], L["rule_5min_desc"], PALETTE["primary"]),
        (L["rule_30min_title"], L["rule_30min_desc"], PALETTE["warning"]),
        (L["rule_lang_title"], L["rule_lang_desc"], PALETTE["info"]),
        (L["rule_oneq_title"], L["rule_oneq_desc"], PALETTE["success"]),
    ]
    for title, desc, color in rules:
        st.markdown(
            f"""
            <div class="mkt-sla-row" style="--accent:{color};">
                <div class="mkt-sla-label">{title}</div>
                <div class="mkt-sla-value">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _divider()

    # Auto-reply (3 languages, editable + auto-translate)
    st.markdown(f'<div class="mkt-eyebrow">{L["autoreply_title"]}</div>', unsafe_allow_html=True)
    st.caption(L["autoreply_help"])
    st.markdown(f'<div class="mkt-section-intro">{L["scripts_edit_help"]}</div>', unsafe_allow_html=True)
    auto = _load_json("sales_scripts.json")["auto_reply_off_hours"]

    def _save_auto():
        full = _load_json("sales_scripts.json")
        full["auto_reply_off_hours"] = {
            "en": st.session_state.get("autoreply_en", auto["en"]),
            "ru": st.session_state.get("autoreply_ru", auto["ru"]),
            "km": st.session_state.get("autoreply_km", auto["km"]),
        }
        _save_json_file("sales_scripts.json", full)

    _render_trilingual_editor(
        L=L,
        lang=lang,
        prefix="autoreply",
        en=auto["en"],
        ru=auto["ru"],
        km=auto["km"],
        on_save=_save_auto,
        height=180,
    )

    _divider()

    # Messenger channels
    st.markdown(f'<div class="mkt-eyebrow">{L["messengers_title"]}</div>', unsafe_allow_html=True)
    st.caption(L["messengers_help"])
    msg_cols = st.columns(3)
    channels = [
        ("WhatsApp", L["wa_desc"], PALETTE["success"]),
        ("Telegram", L["tg_desc"], PALETTE["info"]),
        ("Facebook Messenger", L["fb_desc"], PALETTE["primary"]),
    ]
    for col, (name, desc, color) in zip(msg_cols, channels):
        with col:
            st.markdown(
                f"""
                <div class="mkt-card" style="border-left:3px solid {color};">
                    <div class="mkt-card-title">{name}</div>
                    <div class="mkt-card-body">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# SECTION 3.4 — MESSAGE SCRIPTS LIBRARY (editable + auto-translate)
# ============================================================
def _save_all_scripts_to_json(scripts_payload: list):
    """Persist the full scripts list back to data/sales_scripts.json (preserves _comment + auto_reply_off_hours)."""
    path = DATA_DIR / "sales_scripts.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["scripts"] = scripts_payload
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _cb_translate_script(sid: str, src_code: str):
    """on_click callback: translate text from src_code into the other two languages."""
    src_text = st.session_state.get(f"script_{sid}_{src_code}", "")
    if not src_text or not src_text.strip():
        return
    for tgt in ("en", "ru", "km"):
        if tgt == src_code:
            continue
        translated = translate_text(src_text, target=tgt, source=src_code)
        st.session_state[f"script_{sid}_{tgt}"] = translated


def _cb_save_script(sid: str, scripts_snapshot: list):
    """on_click callback: persist current edits for one script into the JSON file."""
    updated = []
    for s in scripts_snapshot:
        if s["id"] == sid:
            new = dict(s)
            for code in ("en", "ru", "km"):
                new[code] = st.session_state.get(f"script_{sid}_{code}", s[code])
            updated.append(new)
        else:
            updated.append(s)
    _save_all_scripts_to_json(updated)
    st.cache_data.clear()
    st.session_state[f"script_{sid}_saved_flag"] = True


def _cb_revert_script(sid: str, original: dict):
    """on_click callback: drop edits for this script and reload from file."""
    for code in ("en", "ru", "km"):
        st.session_state[f"script_{sid}_{code}"] = original[code]
    st.session_state.pop(f"script_{sid}_saved_flag", None)


def _section_scripts(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["scripts_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["scripts_help"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["scripts_edit_help"]}</div>', unsafe_allow_html=True)

    scripts = _load_json("sales_scripts.json")["scripts"]

    # Pre-seed session_state with file values for any script not yet touched
    for s in scripts:
        for code in ("en", "ru", "km"):
            key = f"script_{s['id']}_{code}"
            if key not in st.session_state:
                st.session_state[key] = s[code]

    lang_labels = {"en": L["lang_en"], "ru": L["lang_ru"], "km": L["lang_km"]}

    for i, s in enumerate(scripts, 1):
        sid = s["id"]
        with st.expander(f"**{L['script_n']} {i}**: {s['title']}"):
            st.markdown(f"**{L['when']}**: {s.get(f'when_{lang}', s.get('when_en', ''))}")
            st.markdown(f"**{L['goal']}**: {s.get(f'goal_{lang}', s.get('goal_en', ''))}")
            st.markdown(f"**{L['dont']}**: {s.get(f'dont_{lang}', s.get('dont_en', ''))}")
            st.markdown("---")

            c_en, c_ru, c_km = st.columns(3)
            for col, code in zip((c_en, c_ru, c_km), ("en", "ru", "km")):
                with col:
                    st.markdown(f"**{lang_labels[code]}**")
                    st.text_area(
                        label=f"{lang_labels[code]} body",
                        key=f"script_{sid}_{code}",
                        height=240,
                        label_visibility="collapsed",
                    )

            st.markdown("")
            ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.2, 2.5, 1.2, 1.2])
            with ctrl1:
                src_code = st.radio(
                    L["scripts_source"],
                    options=("en", "ru", "km"),
                    format_func=lambda c: lang_labels[c],
                    horizontal=False,
                    key=f"script_{sid}_src",
                    index={"ru": 1, "en": 0, "km": 2}.get(lang, 0),
                )
            with ctrl2:
                st.button(
                    L["scripts_autofill"],
                    key=f"script_{sid}_translate_btn",
                    on_click=_cb_translate_script,
                    args=(sid, src_code),
                    use_container_width=True,
                )
            with ctrl3:
                st.button(
                    L["scripts_save"],
                    key=f"script_{sid}_save_btn",
                    on_click=_cb_save_script,
                    args=(sid, scripts),
                    type="primary",
                    use_container_width=True,
                )
            with ctrl4:
                st.button(
                    L["scripts_revert"],
                    key=f"script_{sid}_revert_btn",
                    on_click=_cb_revert_script,
                    args=(sid, s),
                    use_container_width=True,
                )

            if st.session_state.pop(f"script_{sid}_saved_flag", False):
                st.success(L["scripts_saved"])


# ============================================================
# SECTION 3.5 — OBJECTIONS MATRIX
# ============================================================
_OBJECTION_RULES = {
    "ru": [
        ("1. Слушать до конца", "Не перебивать. Родитель договаривает свою мысль полностью."),
        ("2. Признать", "«Понимаю, это важно». НЕ «Но...» — это триггерит защиту."),
        ("3. Задать уточняющий вопрос", "Чтобы понять СУТЬ за возражением, а не социально приемлемую отговорку."),
        ("4. Ответить по сути", "Конкретно, с цифрами/фактами."),
        ("5. Чек-ин", "«Это отвечает на ваш вопрос?»"),
        ("6. Продвинуть дальше", "Следующий маленький шаг (тур / тест / заявка)."),
    ],
    "en": [
        ("1. Listen fully", "Don't interrupt. Let the parent finish their thought completely."),
        ("2. Acknowledge", "«I understand, this matters». NOT «But...» — it triggers defense."),
        ("3. Ask clarifying question", "To understand the REAL reason behind the objection, not the socially acceptable excuse."),
        ("4. Answer concretely", "Specific, with numbers/facts."),
        ("5. Check in", "«Does this answer your question?»"),
        ("6. Move forward", "Next small step (tour / test / application)."),
    ],
}


def _section_objections(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["obj_rules_title"]}</div>', unsafe_allow_html=True)
    grid = st.columns(3)
    for i, (title, desc) in enumerate(_OBJECTION_RULES.get(lang, _OBJECTION_RULES["en"])):
        with grid[i % 3]:
            st.markdown(
                f"""
                <div class="mkt-card mkt-card--accent-red" style="margin-bottom:10px;">
                    <div class="mkt-card-title">{title}</div>
                    <div class="mkt-card-body">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _divider()

    st.markdown(f'<div class="mkt-eyebrow">{L["obj_matrix_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["scripts_edit_help"]}</div>', unsafe_allow_html=True)
    matrix = _load_json("objections_matrix.json")["objections"]

    cat_key = "category" if lang == "ru" else "category_en"
    rule_key = "rule" if lang == "ru" else "rule_en"

    # Filter by category
    categories = [L["all"]] + sorted({o.get(cat_key, o["category"]) for o in matrix})
    sel_cat = st.selectbox(L["filter_category"], categories, key="obj_filter")
    shown = matrix if sel_cat == L["all"] else [o for o in matrix if o.get(cat_key, o["category"]) == sel_cat]

    # Use the index in the original matrix as a stable identifier
    full_index = {id(o): idx for idx, o in enumerate(matrix)}

    def _save_objection(idx: int):
        full = _load_json("objections_matrix.json")
        target = full["objections"][idx]
        for code in ("en", "ru", "km"):
            target[f"objection_{code}"] = st.session_state.get(f"obj_{idx}_objection_{code}", target.get(f"objection_{code}", ""))
            target[f"answer_{code}"] = st.session_state.get(f"obj_{idx}_answer_{code}", target.get(f"answer_{code}", ""))
        target["category"] = st.session_state.get(f"obj_{idx}_category_ru", target.get("category", ""))
        target["category_en"] = st.session_state.get(f"obj_{idx}_category_en", target.get("category_en", ""))
        target["rule"] = st.session_state.get(f"obj_{idx}_rule_ru", target.get("rule", ""))
        target["rule_en"] = st.session_state.get(f"obj_{idx}_rule_en", target.get("rule_en", ""))
        _save_json_file("objections_matrix.json", full)

    for o in shown:
        idx = full_index[id(o)]
        cat_display = o.get(cat_key, o["category"])
        obj_display = o.get(f"objection_{lang}", o.get("objection_en", o.get("objection", ""))) if lang in ("ru", "en") else o["objection_ru"]
        with st.expander(f"**{cat_display}** · {obj_display}"):
            # Category + rule (RU/EN, no Khmer in source data)
            cat_c1, cat_c2 = st.columns(2)
            with cat_c1:
                st.text_input(f"{L['rule']} · category (RU)", value=o.get("category", ""), key=f"obj_{idx}_category_ru")
                st.text_area(f"{L['rule']} (RU)", value=o.get("rule", ""), key=f"obj_{idx}_rule_ru", height=80)
            with cat_c2:
                st.text_input(f"{L['rule']} · category (EN)", value=o.get("category_en", ""), key=f"obj_{idx}_category_en")
                st.text_area(f"{L['rule']} (EN)", value=o.get("rule_en", ""), key=f"obj_{idx}_rule_en", height=80)

            st.markdown("---")
            st.markdown(f"**{L['objection_label']}**")
            _render_trilingual_editor(
                L=L,
                lang=lang,
                prefix=f"obj_{idx}_objection",
                en=o.get("objection_en", ""),
                ru=o.get("objection_ru", ""),
                km=o.get("objection_km", ""),
                on_save=lambda i=idx: _save_objection(i),
                height=100,
            )

            st.markdown("---")
            st.markdown(f"**{L['answer_label']}**")
            _render_trilingual_editor(
                L=L,
                lang=lang,
                prefix=f"obj_{idx}_answer",
                en=o.get("answer_en", ""),
                ru=o.get("answer_ru", ""),
                km=o.get("answer_km", ""),
                on_save=lambda i=idx: _save_objection(i),
                height=180,
            )


# ============================================================
# SECTION 3.6 — CAMPUS TOUR PLAYBOOK
# ============================================================
_TOUR_TIMELINE = {
    "ru": [
        ("День -2 до тура", "Подготовка", [
            "Подготовить персонализированную папку (имя ребёнка, класс, 1-2 особенности)",
            "Уведомить учителя релевантного класса",
            "Проверить что бассейн/лаборатории доступны для показа",
            "Охрана/ресепшен знает о визите (имя + время)",
            "Подготовить welcome drink (вода/чай/кофе + snacks для детей)",
        ], PALETTE["info"]),
        ("Минуты 0-5", "Встреча у ресепшена", [
            "Встретить по имени (родителя И ребёнка)",
            "Обратиться к ребёнку на его уровне глаз, поздороваться",
            "Предложить напиток + WiFi",
            "Показать родителям комнату для ожидания",
        ], PALETTE["gold"]),
        ("Минуты 5-15", "Warm-up conversation (mini-discovery)", [
            "«Как давно в Пномпене?» (expat/local/returning)",
            "«Какая сейчас школа? Что нравится / не нравится?» (конкуренты + триггеры)",
            "«Что для вас самое важное в школе для [имя ребёнка]?» (ценности)",
            "«Что вы знаете о WISC уже?» (уровень awareness)",
            "⚠️ Задавать естественно, не как анкету",
        ], PALETTE["warning"]),
        ("Минуты 15-35", "Walk-through — эмоциональный маршрут", [
            "1. Classroom релевантного класса → «вот где будет [имя ребёнка]»",
            "2. Library → reading program",
            "3. Science lab → hands-on experiments каждую неделю",
            "4. Art / Music room → каждый ребёнок развивается творчески",
            "5. Swimming pool → почти всегда wow-момент",
            "6. Sports field → extracurriculars",
            "7. Dining hall → safety & hygiene",
            "🎯 Рассказывать ИСТОРИИ не факты. Подключать ребёнка. НЕ говорить про деньги!",
        ], PALETTE["primary"]),
        ("Минуты 35-50", "Sit-down (кофе и вопросы)", [
            "Вынести папку с fee structure",
            "Показать discount calculator (Product Deep-Dive → Pricing cheatsheet)",
            "Отвечать без защитной позиции",
            "Не знаешь ответ — «Отличный вопрос, уточню у директора и напишу сегодня вечером»",
        ], PALETTE["info"]),
        ("Минуты 50-60", "Close & Next Steps", [
            "«Что думаете после тура?»",
            "Если позитив → assumptive close: «Отправлю application сейчас, entrance test на [день]»",
            "Если hesitation → «Какой самый важный нерешённый вопрос? Сфокусируемся на нём»",
            "Если «подумаем» → Script 9 через 3 дня + Stage «Tour Done, Nurturing» в CRM",
            "❗ Обязательно close на КОНКРЕТНЫЙ next step",
        ], PALETTE["success"]),
    ],
    "en": [
        ("Day -2 before tour", "Preparation", [
            "Prepare personalized folder (child's name, grade, 1-2 specifics)",
            "Notify the teacher of the relevant grade",
            "Verify pool/labs are accessible for walk-through",
            "Security/reception knows about the visit (name + time)",
            "Prepare welcome drinks (water/tea/coffee + snacks for kids)",
        ], PALETTE["info"]),
        ("Minutes 0-5", "Reception greeting", [
            "Greet by name (both parent AND child)",
            "Address the child at their eye level, say hello",
            "Offer a drink + WiFi",
            "Show parents the waiting room",
        ], PALETTE["gold"]),
        ("Minutes 5-15", "Warm-up conversation (mini-discovery)", [
            "«How long have you been in Phnom Penh?» (expat/local/returning)",
            "«What school now? What do you like / dislike?» (competitors + triggers)",
            "«What's most important in a school for [child's name]?» (values)",
            "«What do you know about WISC already?» (awareness level)",
            "⚠️ Ask naturally, not like a survey",
        ], PALETTE["warning"]),
        ("Minutes 15-35", "Walk-through — emotional route", [
            "1. Classroom of the relevant grade → «this is where [child's name] will be»",
            "2. Library → reading program",
            "3. Science lab → hands-on experiments every week",
            "4. Art / Music room → every child develops creatively",
            "5. Swimming pool → almost always the wow moment",
            "6. Sports field → extracurriculars",
            "7. Dining hall → safety & hygiene",
            "🎯 Tell STORIES, not facts. Engage the child. DO NOT talk money here!",
        ], PALETTE["primary"]),
        ("Minutes 35-50", "Sit-down (coffee and questions)", [
            "Bring out the fee structure folder",
            "Show the discount calculator (Product Deep-Dive → Pricing cheatsheet)",
            "Answer without getting defensive",
            "Don't know? «Great question, I'll check with the director and write you tonight»",
        ], PALETTE["info"]),
        ("Minutes 50-60", "Close & Next Steps", [
            "«What are your thoughts after the tour?»",
            "If positive → assumptive close: «I'll send the application now, entrance test on [day]»",
            "If hesitation → «What's the biggest remaining question? Let's focus on that»",
            "If «we'll think» → Script 9 in 3 days + stage «Tour Done, Nurturing» in CRM",
            "❗ ALWAYS close on a CONCRETE next step",
        ], PALETTE["success"]),
    ],
}

_TOUR_NEVER = {
    "ru": [
        "Плохо говорить про конкурентов",
        "Обещать то, чего нет",
        "Оставлять ребёнка скучать пока говоришь с родителем",
        "Рассказывать про цену в первые 30 минут",
        "Отпускать родителей без чёткого next step",
        "Торопиться на следующую встречу — родитель это чувствует",
    ],
    "en": [
        "Speak badly about competitors",
        "Promise something we don't have",
        "Let the child get bored while talking to parents",
        "Talk about price in the first 30 minutes",
        "Let parents leave without a clear next step",
        "Rush to the next meeting — the parent feels it",
    ],
}


def _save_tour_phase(idx: int):
    """Persist edits for one timeline phase back to tour_playbook.json."""
    full = _load_json("tour_playbook.json")
    target = full["timeline"][idx]
    for code in ("en", "ru", "km"):
        target[f"timing_{code}"] = st.session_state.get(f"tour_{idx}_timing_{code}", target.get(f"timing_{code}", ""))
        target[f"phase_{code}"] = st.session_state.get(f"tour_{idx}_phase_{code}", target.get(f"phase_{code}", ""))
        items_text = st.session_state.get(f"tour_{idx}_items_{code}", "")
        target[f"items_{code}"] = [ln for ln in (items_text or "").split("\n") if ln.strip()]
    _save_json_file("tour_playbook.json", full)


def _save_tour_never():
    full = _load_json("tour_playbook.json")
    for code in ("en", "ru", "km"):
        text = st.session_state.get(f"tour_never_{code}", "")
        full[f"never_{code}"] = [ln for ln in (text or "").split("\n") if ln.strip()]
    _save_json_file("tour_playbook.json", full)


def _section_tour(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["tour_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["tour_intro"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["scripts_edit_help"]}</div>', unsafe_allow_html=True)

    tour = _load_json("tour_playbook.json")
    timeline = tour["timeline"]
    color_map = {
        "primary": PALETTE["primary"],
        "gold": PALETTE["gold"],
        "info": PALETTE["info"],
        "warning": PALETTE["warning"],
        "success": PALETTE["success"],
    }
    expand_label = "Минуты 15-35" if lang == "ru" else "Minutes 15-35"

    for idx, phase in enumerate(timeline):
        timing_disp = phase.get(f"timing_{lang}") or phase.get("timing_en", "")
        phase_disp = phase.get(f"phase_{lang}") or phase.get("phase_en", "")
        with st.expander(f"**{timing_disp}** · {phase_disp}", expanded=(timing_disp == expand_label)):
            # Header line: timing + phase per language (single-line text inputs)
            head_cols = st.columns(3)
            for col, code in zip(head_cols, ("en", "ru", "km")):
                with col:
                    st.markdown(f"**{ {'en':L['lang_en'],'ru':L['lang_ru'],'km':L['lang_km']}[code] }**")
                    st.text_input(
                        "Timing",
                        value=phase.get(f"timing_{code}", ""),
                        key=f"tour_{idx}_timing_{code}",
                        label_visibility="collapsed",
                        placeholder="Timing",
                    )
                    st.text_input(
                        "Phase",
                        value=phase.get(f"phase_{code}", ""),
                        key=f"tour_{idx}_phase_{code}",
                        label_visibility="collapsed",
                        placeholder="Phase",
                    )

            # Render current items as readable bullets (live preview from chosen UI lang)
            preview_items = phase.get(f"items_{lang}") or phase.get("items_en", [])
            if preview_items:
                st.markdown("\n".join(f"- {it}" for it in preview_items))

            st.markdown("---")

            # Items: one bullet per line, editable on 3 languages with auto-translate
            items_seed = {code: "\n".join(phase.get(f"items_{code}", []) or []) for code in ("en", "ru", "km")}
            _render_trilingual_editor(
                L=L,
                lang=lang,
                prefix=f"tour_{idx}_items",
                en=items_seed["en"],
                ru=items_seed["ru"],
                km=items_seed["km"],
                on_save=lambda i=idx: _save_tour_phase(i),
                height=200,
            )

    _divider()

    st.markdown(f'<div class="mkt-eyebrow">{L["tour_never"]}</div>', unsafe_allow_html=True)
    never_seed = {code: "\n".join(tour.get(f"never_{code}", []) or []) for code in ("en", "ru", "km")}
    # Show preview of currently active language as red rows
    for n in tour.get(f"never_{lang}", tour.get("never_en", [])):
        st.markdown(
            f"""
            <div class="mkt-sla-row" style="--accent:{PALETTE['primary']};">
                <div class="mkt-sla-label">❌ {n}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("")
    _render_trilingual_editor(
        L=L,
        lang=lang,
        prefix="tour_never",
        en=never_seed["en"],
        ru=never_seed["ru"],
        km=never_seed["km"],
        on_save=_save_tour_never,
        height=180,
    )


# ============================================================
# SECTION 3.7 — ADMISSIONS OFFICER TRAINING COURSE
# ============================================================
def _section_training(L: dict, lang: str):
    training = _load_json("training_modules.json")
    meta = training["course_meta"]

    # Course hero
    st.markdown(
        f"""
        <div class="mkt-hero-big">
            <div class="mkt-hero-grid">
                <div>
                    <div class="mkt-hero-label">{L['training_title_short']}</div>
                    <div class="mkt-hero-title">{L['training_modules_sub']}</div>
                    <div class="mkt-hero-value">{meta['passing_score_pct']}%</div>
                    <div class="mkt-meta" style="margin-top:4px;">{L['passing_score']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['start_label']}</div>
                    <div class="mkt-hero-counter" style="font-size:28px;">{meta['start_date']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['end_label']}</div>
                    <div class="mkt-hero-counter" style="font-size:28px;">{meta['end_date']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['golive_label']}</div>
                    <div class="mkt-hero-counter" style="font-size:28px;">May 1</div>
                    <div class="mkt-hero-date">{L['launch_day']}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _divider()

    # Progress
    total_modules = len(training["modules"])
    completed = sum(1 for m in training["modules"]
                    if st.session_state.get(f"sales_mod_{m['id']}_done", False))
    pct = int(completed / total_modules * 100) if total_modules else 0
    st.markdown(
        f"""
        <div class="mkt-card mkt-card--accent-red" style="margin-bottom:14px;">
            <div class="mkt-card-head">
                <div class="mkt-card-title">{L['course_progress']}</div>
                <span class="mkt-chip mkt-chip--red">{completed} / {total_modules} · {pct}%</span>
            </div>
            <div style="background:{PALETTE['border_strong']};border-radius:6px;height:8px;overflow:hidden;margin-top:8px;">
                <div style="background:{PALETTE['primary']};width:{pct}%;height:100%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Modules — language-aware + editable
    def _save_module(mid: str):
        full = _load_json("training_modules.json")
        for mm in full["modules"]:
            if mm["id"] != mid:
                continue
            for code in ("en", "ru", "km"):
                mm[f"title_{code}"] = st.session_state.get(f"train_{mid}_title_{code}", mm.get(f"title_{code}", ""))
                mm[f"goal_{code}"] = st.session_state.get(f"train_{mid}_goal_{code}", mm.get(f"goal_{code}", ""))
                theory_text = st.session_state.get(f"train_{mid}_theory_{code}", "")
                mm[f"theory_{code}"] = [ln for ln in (theory_text or "").split("\n") if ln.strip()]
                ex_text = st.session_state.get(f"train_{mid}_exercises_{code}", "")
                mm[f"exercises_{code}"] = [ln for ln in (ex_text or "").split("\n") if ln.strip()]
            mm["video"] = st.session_state.get(f"train_{mid}_video", mm.get("video", ""))
            break
        _save_json_file("training_modules.json", full)

    for m in training["modules"]:
        mid = m["id"]
        done_key = f"sales_mod_{mid}_done"
        is_done = st.session_state.get(done_key, False)
        tick = "✅" if is_done else "⏳"
        title = m.get(f"title_{lang}") or m.get("title_en") or m.get("title_ru", "")
        goal = m.get(f"goal_{lang}") or m.get("goal_en") or m.get("goal_ru", "")
        theory = m.get(f"theory_{lang}") or m.get("theory_en") or m.get("theory_ru", []) or []
        exercises = m.get(f"exercises_{lang}") or m.get("exercises_en") or m.get("exercises_ru", []) or []

        with st.expander(f"{tick} **{title}**"):
            st.markdown(f"**{L['goal_emoji']}**: {goal}")
            st.markdown(f"**{L['theory_emoji']}**:")
            for t in theory:
                st.markdown(f"- {t}")
            st.caption(f"{L['video']}: {m.get('video', '—')}")
            st.markdown(f"**{L['exercises_emoji']}**:")
            for ex in exercises:
                st.markdown(f"- {ex}")

            st.markdown(f"**{L['quiz_emoji']}**:")
            for qi, quiz in enumerate(m["quiz"]):
                q_text = quiz.get(f"q_{lang}", quiz.get("q_en", quiz.get("q", ""))) if lang != "ru" else quiz.get("q", quiz.get("q_ru", ""))
                q_opts = quiz.get(f"options_{lang}", quiz.get("options_en", quiz.get("options", []))) if lang != "ru" else quiz.get("options", quiz.get("options_ru", []))
                q_explain = quiz.get(f"explain_{lang}", quiz.get("explain_en", quiz.get("explain", ""))) if lang != "ru" else quiz.get("explain", "")
                st.markdown(f"**Q{qi+1}**: {q_text}")
                ans_key = f"sales_quiz_{mid}_{qi}_{lang}"
                chosen = st.radio(
                    q_text,
                    options=q_opts,
                    index=None,
                    key=ans_key,
                    label_visibility="collapsed",
                )
                if chosen is not None:
                    if q_opts.index(chosen) == quiz["correct_idx"]:
                        st.success(f"{L['correct']}. {q_explain}")
                    else:
                        st.error(f"{L['incorrect']}. {q_explain}")

            st.checkbox("Модуль пройден", key=done_key)

            # ============ Editable section ============
            st.markdown("---")
            st.markdown(f"### ✏️ {L['scripts_save'].replace('💾 ', '')}")
            st.markdown(f'<div class="mkt-section-intro">{L["scripts_edit_help"]}</div>', unsafe_allow_html=True)

            # Title (single line × 3 langs)
            st.markdown(f"**Title**")
            _render_trilingual_editor(
                L=L, lang=lang, prefix=f"train_{mid}_title",
                en=m.get("title_en", ""), ru=m.get("title_ru", ""), km=m.get("title_km", ""),
                height=70, show_save_revert=False,
            )

            st.markdown(f"**{L['goal_emoji']}**")
            _render_trilingual_editor(
                L=L, lang=lang, prefix=f"train_{mid}_goal",
                en=m.get("goal_en", ""), ru=m.get("goal_ru", ""), km=m.get("goal_km", ""),
                height=80, show_save_revert=False,
            )

            st.markdown(f"**{L['theory_emoji']}** (одна строка = один пункт)")
            _render_trilingual_editor(
                L=L, lang=lang, prefix=f"train_{mid}_theory",
                en="\n".join(m.get("theory_en", []) or []),
                ru="\n".join(m.get("theory_ru", []) or []),
                km="\n".join(m.get("theory_km", []) or []),
                height=200, show_save_revert=False,
            )

            st.markdown(f"**{L['exercises_emoji']}** (одна строка = один пункт)")
            _render_trilingual_editor(
                L=L, lang=lang, prefix=f"train_{mid}_exercises",
                en="\n".join(m.get("exercises_en", []) or []),
                ru="\n".join(m.get("exercises_ru", []) or []),
                km="\n".join(m.get("exercises_km", []) or []),
                height=120, show_save_revert=False,
            )

            st.text_input(
                f"{L['video']}",
                value=m.get("video", ""),
                key=f"train_{mid}_video",
            )

            sv1, sv2, _ = st.columns([1.2, 1.2, 4])
            with sv1:
                def _save_wrap(mid_=mid):
                    _save_module(mid_)
                    st.cache_data.clear()
                    st.session_state[f"train_{mid_}_saved_flag"] = True
                st.button(
                    L["scripts_save"],
                    key=f"train_{mid}_save",
                    on_click=_save_wrap,
                    type="primary",
                    use_container_width=True,
                )
            with sv2:
                def _revert_module(m_=m, mid_=mid):
                    for code in ("en", "ru", "km"):
                        st.session_state[f"train_{mid_}_title_{code}"] = m_.get(f"title_{code}", "")
                        st.session_state[f"train_{mid_}_goal_{code}"] = m_.get(f"goal_{code}", "")
                        st.session_state[f"train_{mid_}_theory_{code}"] = "\n".join(m_.get(f"theory_{code}", []) or [])
                        st.session_state[f"train_{mid_}_exercises_{code}"] = "\n".join(m_.get(f"exercises_{code}", []) or [])
                    st.session_state[f"train_{mid_}_video"] = m_.get("video", "")
                    st.session_state.pop(f"train_{mid_}_saved_flag", None)
                st.button(
                    L["scripts_revert"],
                    key=f"train_{mid}_revert",
                    on_click=_revert_module,
                    use_container_width=True,
                )
            if st.session_state.pop(f"train_{mid}_saved_flag", False):
                st.success(L["scripts_saved"])


# ============================================================
# SECTION 3.8 — PRODUCT KNOWLEDGE DEEP-DIVE
# ============================================================
_TUITION = {
    "Pre-school & Nursery": 3500,
    "K1-K2": 3700,
    "G1-G5": 4200,
    "G6-G8": 4300,
    "G9-G12": 4500,
}

_INFRASTRUCTURE = {
    "ru": [
        ("Swimming pool", "Crown jewel для семей с активными детьми", "«Увидят бассейн — и дети уже не хотят уходить. Запишитесь на тур — Grade [X] как раз ходит в среду»"),
        ("Football pitch", "Полноценное поле для команды и PE", "«У нас школьная команда — дети участвуют в Cambodia schools league»"),
        ("Science lab", "Hands-on experiments каждую неделю", "«Grade 5 на прошлой неделе делал эксперимент с...»"),
        ("Art room", "Full art curriculum", "«Каждый ребёнок получает art portfolio в конце года»"),
        ("Music room", "Инструменты + vocal studio", "«Annual concert — все дети выступают»"),
        ("Robotics lab", "Unique для KH schools at this price point", "«Robotics club 2 раза в неделю — соревнования в регионе»"),
        ("Computer lab", "Современные PC + coding curriculum", "«Grade 7+ учат Python и JavaScript»"),
        ("Library", "3000+ books + reading program", "«20 минут reading time каждый день — формирует привычку»"),
        ("Dining hall", "Safety & hygiene сертификаты", "«Меню разработано nutrition consultant»"),
        ("KG game zone", "Отдельная безопасная зона для малышей", "«Pre-school и K1-K2 играют отдельно от старших»"),
    ],
    "en": [
        ("Swimming pool", "Crown jewel for families with active kids", "«They see the pool — and kids don't want to leave. Book a tour — Grade [X] uses it on Wednesdays»"),
        ("Football pitch", "Full-size pitch for team and PE", "«We have a school team — kids compete in the Cambodia schools league»"),
        ("Science lab", "Hands-on experiments every week", "«Grade 5 last week did an experiment with...»"),
        ("Art room", "Full art curriculum", "«Every child gets an art portfolio at year end»"),
        ("Music room", "Instruments + vocal studio", "«Annual concert — every kid performs»"),
        ("Robotics lab", "Unique for KH schools at this price point", "«Robotics club 2×/week — regional competitions»"),
        ("Computer lab", "Modern PCs + coding curriculum", "«Grade 7+ learn Python and JavaScript»"),
        ("Library", "3000+ books + reading program", "«20 min reading time daily — builds the habit»"),
        ("Dining hall", "Safety & hygiene certified", "«Menu designed by a nutrition consultant»"),
        ("KG game zone", "Separate safe zone for toddlers", "«Pre-school and K1-K2 play separately from older kids»"),
    ],
}


def _section_product(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["pricing_title"]}</div>', unsafe_allow_html=True)
    st.caption(L["pricing_help"])

    discount_options = [
        L["discount_eb15"], L["discount_eb10"], L["discount_sib5"],
        L["discount_sib10"], L["discount_annual"],
    ]

    c1, c2 = st.columns([1, 2])
    with c1:
        grade = st.selectbox(L["grade_label"], list(_TUITION.keys()), key="prod_grade")
        discounts = st.multiselect(L["discounts_label"], discount_options, key="prod_discounts")
    with c2:
        base = _TUITION[grade]
        multiplier = 1.0
        for d in discounts:
            if d == L["discount_eb15"]:
                multiplier *= 0.85
            elif d == L["discount_eb10"]:
                multiplier *= 0.90
            elif d == L["discount_sib5"]:
                multiplier *= 0.95
            elif d == L["discount_sib10"]:
                multiplier *= 0.90
            elif d == L["discount_annual"]:
                multiplier *= 0.90
        multiplier = max(multiplier, 0.75)
        total_savings_pct = (1 - multiplier) * 100

        final_annual = base * multiplier
        annual_selected = L["discount_annual"] in discounts
        non_annual_mult = multiplier / (0.90 if annual_selected else 1.0)
        final_semester = base * non_annual_mult * 0.95
        final_term = base * non_annual_mult

        m = st.columns(3)
        m[0].metric(L["annual_pay"], f"${final_annual:,.0f}", delta=f"-{total_savings_pct:.0f}%")
        m[1].metric(L["semester_pay"], f"${final_semester:,.0f}")
        m[2].metric(L["term_pay"], f"${final_term:,.0f}")
        st.caption(f"{L['base_tuition']} ({grade}): ${base:,} {L['per_year']} · {L['max_total']}")

    _divider()

    # B. Program comparison
    st.markdown(f'<div class="mkt-eyebrow">{L["program_title"]}</div>', unsafe_allow_html=True)
    program_cols_ru = ["Класс", "Основная программа", "Khmer lessons", "Chinese lessons", "Assessments", "Extracurriculars"]
    program_cols_en = ["Grade", "Core curriculum", "Khmer lessons", "Chinese lessons", "Assessments", "Extracurriculars"]
    program_rows_ru = [
        ["Pre-school & Nursery", "Play-based + English immersion", "Khmer 5/wk", "Chinese 3/wk", "—", "Art, Music, Swim"],
        ["K1-K2", "Pre-Cambridge foundation", "Khmer 8/wk", "Chinese 5/wk", "—", "Swim, Art, Music, Dance"],
        ["G1-G5", "Cambridge Primary (Edexcel)", "Khmer 10/wk", "Chinese 5/wk", "MAP (G3+)", "Все 9 extracurriculars"],
        ["G6-G8", "Cambridge Lower Secondary → WASC transition", "Khmer 8/wk", "Chinese 5/wk", "MAP", "Все + TEDx/Debate"],
        ["G9-G12", "WASC + SAT/IELTS prep", "Khmer 5/wk", "Chinese 5/wk", "MAP, PSAT (G10)", "Все + leadership"],
    ]
    program_rows_en = [
        ["Pre-school & Nursery", "Play-based + English immersion", "Khmer 5/wk", "Chinese 3/wk", "—", "Art, Music, Swim"],
        ["K1-K2", "Pre-Cambridge foundation", "Khmer 8/wk", "Chinese 5/wk", "—", "Swim, Art, Music, Dance"],
        ["G1-G5", "Cambridge Primary (Edexcel)", "Khmer 10/wk", "Chinese 5/wk", "MAP (G3+)", "All 9 extracurriculars"],
        ["G6-G8", "Cambridge Lower Secondary → WASC transition", "Khmer 8/wk", "Chinese 5/wk", "MAP", "All + TEDx/Debate"],
        ["G9-G12", "WASC + SAT/IELTS prep", "Khmer 5/wk", "Chinese 5/wk", "MAP, PSAT (G10)", "All + leadership"],
    ]
    if lang == "ru":
        program_df = pd.DataFrame(program_rows_ru, columns=program_cols_ru)
    else:
        program_df = pd.DataFrame(program_rows_en, columns=program_cols_en)
    st.dataframe(program_df, use_container_width=True, hide_index=True)

    _divider()

    # C. Infrastructure gallery
    st.markdown(f'<div class="mkt-eyebrow">{L["infra_title"]}</div>', unsafe_allow_html=True)
    st.caption(L["infra_help"])
    grid = st.columns(2)
    for i, (name, desc, selling) in enumerate(_INFRASTRUCTURE.get(lang, _INFRASTRUCTURE["en"])):
        with grid[i % 2]:
            st.markdown(
                f"""
                <div class="mkt-card mkt-card--accent-gold" style="margin-bottom:10px;">
                    <div class="mkt-card-title">{name}</div>
                    <div class="mkt-card-body">{desc}</div>
                    <div class="mkt-card-body" style="margin-top:6px;font-style:italic;color:{PALETTE['gold']};">💬 {selling}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# SECTION 3.9 — COMPETITOR BATTLE CARDS
# ============================================================
def _section_competitors(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["comp_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["comp_intro"]}</div>', unsafe_allow_html=True)

    data = _load_json("competitor_battle_cards.json")["competitors"]

    for c in data:
        with st.expander(f"🏫 **{c['name']}** · G1 {c['tuition_g1']} · G6 {c['tuition_g6']} · G10 {c['tuition_g10']}"):
            cols = st.columns(2)
            with cols[0]:
                st.markdown(
                    f"""
                    <div class="mkt-card mkt-card--accent-red">
                        <div class="mkt-card-title" style="color:{PALETTE['primary']};">{L['their_strengths']}</div>
                        <div class="mkt-card-body">{c['strengths']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("")
                st.markdown(
                    f"""
                    <div class="mkt-card mkt-card--accent-navy">
                        <div class="mkt-card-title" style="color:{PALETTE['info']};">{L['their_weaknesses']}</div>
                        <div class="mkt-card-body">{c['weaknesses']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with cols[1]:
                st.markdown(
                    f"""
                    <div class="mkt-card mkt-card--accent-gold">
                        <div class="mkt-card-title" style="color:{PALETTE['gold']};">{L['our_edge']}</div>
                        <div class="mkt-card-body">{c['our_edge']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("")
                st.markdown(
                    f"""
                    <div class="mkt-card" style="border-left:3px solid {PALETTE['success']};">
                        <div class="mkt-card-title" style="color:{PALETTE['success']};">{L['pitch_against']}</div>
                        <div class="mkt-card-body" style="font-style:italic;">{c['pitch']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ============================================================
# SECTION 3.10 — SALES KPIs & ACCOUNTABILITY
# ============================================================
def _section_kpis(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["kpis_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["kpis_intro"]}</div>', unsafe_allow_html=True)

    kpis = _load_csv("sales_kpis.csv")

    # Group by tier
    for tier, tier_label in [("top", L["tier_top"]), ("mid", L["tier_mid"]),
                              ("bottom", L["tier_bottom"]), ("quality", L["tier_quality"]),
                              ("activity", L["tier_activity"])]:
        subset = kpis[kpis["tier"] == tier]
        if subset.empty:
            continue
        st.markdown(f'<div class="mkt-eyebrow" style="margin-top:16px;">{tier_label}</div>',
                    unsafe_allow_html=True)
        cols = st.columns(min(len(subset), 4) or 1)
        for i, (_, row) in enumerate(subset.iterrows()):
            with cols[i % len(cols)]:
                target = row["target"]
                current = row["current"]
                unit = row["unit"]
                # Traffic light
                if unit == "pct":
                    on_target = current >= target
                elif unit == "min":
                    on_target = current > 0 and current <= target
                else:  # count
                    on_target = current >= target
                status_chip = "🟢" if on_target and current > 0 else ("🔴" if current == 0 else "🟡")

                val = f"{current}"
                if unit == "pct":
                    val = f"{current}%"
                elif unit == "min":
                    val = f"{current} min"

                target_str = f"target: {target}{'%' if unit == 'pct' else (' min' if unit == 'min' else '')}"
                st.markdown(
                    f"""
                    <div class="mkt-card" style="border-left:3px solid {PALETTE['primary'] if not on_target else PALETTE['success']};margin-bottom:10px;">
                        <div class="mkt-card-head">
                            <div class="mkt-meta">{row['kpi']}</div>
                            <span>{status_chip}</span>
                        </div>
                        <div style="font-size:26px;font-weight:800;color:{PALETTE['text']};">{val}</div>
                        <div class="mkt-meta" style="margin-top:4px;">{target_str}</div>
                        <div class="mkt-card-body" style="margin-top:6px;font-size:11px;">💡 {row['tip']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    _divider()

    # Recording & review cadence
    st.markdown(f'<div class="mkt-eyebrow">{L["recording_title"]}</div>', unsafe_allow_html=True)
    cadence_ru = [
        ("Weekly call review", "Кайсар", "Слушает 5 звонков ПК, читает 20 чатов — разбор"),
        ("Bi-weekly 1:1", "Айжан", "Разбор тона, script adherence, Khmer localization"),
        ("Monthly scorecard review", "Ерболат + Кайсар", "Итоги месяца, корректировка KPI targets"),
    ]
    cadence_en = [
        ("Weekly call review", "Kaisar", "Listens to 5 officer calls, reads 20 chats — debrief"),
        ("Bi-weekly 1:1", "Aizhan", "Tone, script adherence, Khmer localization review"),
        ("Monthly scorecard review", "Yerbolat + Kaisar", "Monthly results, KPI target adjustments"),
    ]
    for title, who, what in (cadence_ru if lang == "ru" else cadence_en):
        st.markdown(
            f"""
            <div class="mkt-meeting">
                <div>
                    <div class="mkt-meeting-title">{title}</div>
                    <div class="mkt-meeting-agenda">{what}</div>
                </div>
                <div class="mkt-meeting-who">{who}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _divider()

    # Incentives proposal
    st.markdown(f'<div class="mkt-eyebrow">{L["incentives_title"]}</div>', unsafe_allow_html=True)
    inc_cols = st.columns(3)
    incentives_ru = [
        ("Base salary", "Фиксированный оклад", "Полная загрузка, основа", PALETTE["info"]),
        ("Per-enrollment bonus", "$50-100 за каждый enrollment", "Mild incentive — не жёсткая «продажа любой ценой»", PALETTE["gold"]),
        ("Quality bonus", "$300-500 quarterly", "При sustained SLA >95% и show-up >70%", PALETTE["success"]),
    ]
    incentives_en = [
        ("Base salary", "Fixed monthly salary", "Full-time, the foundation", PALETTE["info"]),
        ("Per-enrollment bonus", "$50-100 per enrollment", "Mild incentive — not aggressive «sell at any cost»", PALETTE["gold"]),
        ("Quality bonus", "$300-500 quarterly", "For sustained SLA >95% and show-up >70%", PALETTE["success"]),
    ]
    incentives = incentives_ru if lang == "ru" else incentives_en
    for col, (title, amount, desc, color) in zip(inc_cols, incentives):
        with col:
            st.markdown(
                f"""
                <div class="mkt-card" style="border-left:3px solid {color};">
                    <div class="mkt-card-title">{title}</div>
                    <div style="font-size:22px;font-weight:800;color:{color};margin:6px 0;">{amount}</div>
                    <div class="mkt-card-body">{desc}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# SECTION 3.11 — SCRIPT TRANSLATOR (auto RU→EN+KM)
# ============================================================
def _section_translator(L: dict, lang: str):
    st.markdown(f'<div class="mkt-eyebrow">{L["tr_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["tr_help"]}</div>', unsafe_allow_html=True)

    # Source picker + text area side by side
    c_src, c_lang = st.columns([4, 1])
    with c_lang:
        src_lang = st.selectbox(
            L["tr_source_label"],
            options=[("ru", "🇷🇺 RU"), ("en", "🇬🇧 EN")],
            format_func=lambda x: x[1],
            index=0,
            key="tr_src_lang",
        )[0]
    with c_src:
        source_text = st.text_area(
            L["tr_input_label"],
            value=st.session_state.get("tr_source_text", ""),
            height=160,
            key="tr_source_text",
            placeholder="Здравствуйте! Спасибо за интерес к WISC 🌟\nПодскажите, для какого класса рассматриваете школу?",
        )

    st.caption(L["tr_offline_hint"])

    # Auto-translate on every change (deep-translator is cached; st.cache_data + TTL=1h)
    en_text = ""
    km_text = ""
    if source_text and source_text.strip():
        if src_lang == "ru":
            with st.spinner("Translating..."):
                en_text = translate_text(source_text, target="en", source="ru")
                km_text = translate_text(source_text, target="km", source="ru")
        else:  # source = en
            with st.spinner("Translating..."):
                en_text = source_text  # already EN
                km_text = translate_text(source_text, target="km", source="en")
                # Also give RU for internal reference
                ru_internal = translate_text(source_text, target="ru", source="en")
                st.session_state["_tr_ru_internal"] = ru_internal

    # Display 3 columns: source (as-is) + EN + KM
    _divider()
    col_en, col_km = st.columns(2)
    with col_en:
        st.markdown(f"**{L['tr_en_result']}**")
        if en_text:
            st.code(en_text, language="text")
    with col_km:
        st.markdown(f"**{L['tr_km_result']}**")
        if km_text:
            st.code(km_text, language="text")

    # If user entered EN, also show RU back-translation for supervisor review
    if src_lang == "en" and st.session_state.get("_tr_ru_internal"):
        st.markdown("**🇷🇺 Russian (back-translation, for RU-speaking supervisor)**")
        st.code(st.session_state["_tr_ru_internal"], language="text")

    # Save to JSON
    _divider()
    c_title, c_btn = st.columns([3, 1])
    with c_title:
        script_title = st.text_input(L["tr_save_as"], key="tr_save_title",
                                     placeholder="e.g. Custom follow-up for Chinese parents")
    with c_btn:
        if st.button(L["tr_save_btn"], key="tr_save_btn", disabled=not (source_text and script_title)):
            _save_translated_script(script_title, src_lang, source_text, en_text, km_text)
            st.cache_data.clear()
            st.success(L["tr_saved"])


def _save_translated_script(title: str, src_lang: str, source_text: str, en: str, km: str):
    """Append a new script to sales_scripts.json."""
    path = DATA_DIR / "sales_scripts.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Normalize: ensure all 3 bodies populated
    body_ru = source_text if src_lang == "ru" else translate_text(source_text, "ru", source="en")
    body_en = en
    body_km = km
    # Slug ID
    import re as _re
    slug = _re.sub(r"[^a-z0-9_]+", "_", title.lower()).strip("_") or f"custom_{len(data['scripts'])+1}"
    new_script = {
        "id": f"custom_{slug}",
        "title": title,
        "when_ru": "TODO: заполнить",
        "when_en": "TODO: fill in",
        "goal_ru": "TODO: заполнить",
        "goal_en": "TODO: fill in",
        "dont_ru": "—",
        "dont_en": "—",
        "en": body_en,
        "ru": body_ru,
        "km": body_km,
    }
    data["scripts"].append(new_script)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# ROUTER
# ============================================================
def render(lang: str = "ru"):
    _inject_styles()
    L = _get_lang(SALES_LANG, lang)

    _brand_header(
        tagline_ru="СТРАТЕГИЯ ПРОДАЖ · AY 2026-2027",
        tagline_en="SALES STRATEGY · AY 2026-2027",
        tagline_km="យុទ្ធសាស្ត្រលក់ · AY 2026-2027",
        lang=lang,
    )

    st.markdown(
        f"""
        <h2 style="display:inline-block;margin-bottom:6px;color:{PALETTE['text']};font-size:26px;">
            {L["header"]}
            <span class="mkt-v-badge">{_SALES_VERSION}</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )
    st.caption(L["subheader"])

    sub_tabs = st.tabs(L["sections"])

    with sub_tabs[0]:
        _section_overview(L, lang)
    with sub_tabs[1]:
        _section_funnel(L, lang)
    with sub_tabs[2]:
        _section_response(L, lang)
    with sub_tabs[3]:
        _section_scripts(L, lang)
    with sub_tabs[4]:
        _section_objections(L, lang)
    with sub_tabs[5]:
        _section_tour(L, lang)
    with sub_tabs[6]:
        _section_training(L, lang)
    with sub_tabs[7]:
        _section_product(L, lang)
    with sub_tabs[8]:
        _section_competitors(L, lang)
    with sub_tabs[9]:
        _section_kpis(L, lang)
    with sub_tabs[10]:
        _section_translator(L, lang)
