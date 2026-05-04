"""
Marketing Strategy tab — WISC Cambodia admissions launch hub (AY 2026-2027).
Bilingual RU/EN. Data lives in project/data/marketing_*.{csv,json}.
Статусы — в st.session_state (сбрасываются при рестарте сервера).
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"

# ============================================================
# DESIGN SYSTEM — WISC brand (navy shield + champagne gold trefoil)
# ============================================================
PALETTE = {
    "bg":            "#0a1324",   # deep navy background
    "surface":       "#162339",   # WISC shield navy
    "surface_2":     "#1f2e48",   # elevated surface
    "border":        "rgba(201,169,92,0.14)",   # subtle gold-tinted border
    "border_strong": "rgba(201,169,92,0.32)",
    "text":          "#f2ede0",   # cream-white (matches "WISC" wordmark)
    "text_mute":     "#a6b0c2",   # cool grey
    "text_faint":    "#5d6986",
    "primary":       "#c9a95c",   # BRAND GOLD — trefoil leaf
    "primary_soft":  "rgba(201,169,92,0.16)",
    "gold":          "#c9a95c",
    "gold_deep":     "#b59246",
    "gold_soft":     "rgba(201,169,92,0.20)",
    "navy":          "#162339",
    "navy_deep":     "#0a1324",
    "navy_light":    "#22345a",
    "silver":        "#d6dae2",   # shield border silver
    "success":       "#6aa57d",   # refined muted green
    "success_soft":  "rgba(106,165,125,0.16)",
    "warning":       "#d4a74a",
    "warning_soft":  "rgba(212,167,74,0.18)",
    "danger":        "#b84648",   # dignified brick red (not neon)
    "danger_soft":   "rgba(184,70,72,0.16)",
    "info":          "#5d8fba",   # refined steel blue
    "info_soft":     "rgba(93,143,186,0.16)",
}

def _inject_styles():
    """CSS block — injected every render (Streamlit may clear style between reruns)."""
    st.markdown(f"""
    <style>
    /* All classes prefixed mkt-* to avoid collision with other tabs */
    .mkt-eyebrow {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.4px;
        color: {PALETTE['text_mute']};
        font-weight: 700;
        margin-bottom: 10px;
    }}
    .mkt-section-intro {{
        color: {PALETTE['text_mute']};
        font-size: 14px;
        line-height: 1.5;
        margin: -6px 0 18px 0;
    }}
    .mkt-v-badge {{
        display:inline-block;
        background: {PALETTE['primary']};
        color: {PALETTE['navy_deep']};
        font-size: 10.5px;
        font-weight: 800;
        letter-spacing: 1.2px;
        padding: 3px 10px;
        border-radius: 999px;
        margin-left: 10px;
        vertical-align: middle;
    }}
    /* WISC brand banner */
    .wisc-brand {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 20px;
        background: linear-gradient(90deg, {PALETTE['navy']} 0%, {PALETTE['navy_deep']} 100%);
        border: 1px solid {PALETTE['border_strong']};
        border-radius: 14px;
        margin-bottom: 18px;
    }}
    .wisc-shield {{
        width: 44px;
        height: 52px;
        background: {PALETTE['navy']};
        border: 2px solid {PALETTE['silver']};
        border-radius: 6px 6px 22px 22px;
        position: relative;
        flex-shrink: 0;
    }}
    .wisc-shield::before {{
        content: "WISC";
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {PALETTE['text']};
        font-weight: 900;
        font-size: 12px;
        letter-spacing: 1px;
    }}
    .wisc-shield::after {{
        content: "";
        position: absolute;
        bottom: 6px;
        left: 50%;
        transform: translateX(-50%);
        width: 10px;
        height: 10px;
        background: {PALETTE['gold']};
        clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
        opacity: 0.9;
    }}
    .wisc-brand-text {{
        color: {PALETTE['text']};
    }}
    .wisc-brand-title {{
        font-size: 16px;
        font-weight: 800;
        letter-spacing: 2px;
    }}
    .wisc-brand-sub {{
        font-size: 10.5px;
        color: {PALETTE['text_mute']};
        letter-spacing: 2.5px;
        text-transform: uppercase;
        margin-top: 2px;
    }}
    .mkt-hero-big {{
        background: linear-gradient(135deg, {PALETTE['navy']} 0%, {PALETTE['navy_deep']} 100%);
        padding: 28px 32px;
        border-radius: 22px;
        border: 1px solid {PALETTE['border_strong']};
        color: {PALETTE['text']};
        margin-bottom: 18px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    }}
    .mkt-hero-big::before {{
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, {PALETTE['gold']} 0%, {PALETTE['gold_deep']} 100%);
    }}
    .mkt-hero-big::after {{
        content: "";
        position: absolute;
        right: -60px;
        top: -60px;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(201,169,92,0.22), transparent 70%);
        pointer-events: none;
    }}
    .mkt-hero-grid {{
        display: grid;
        grid-template-columns: 1.3fr 1fr 1fr 1fr;
        gap: 24px;
        align-items: end;
    }}
    .mkt-hero-label {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: {PALETTE['text_mute']};
        font-weight: 700;
        margin-bottom: 6px;
    }}
    .mkt-hero-title {{
        font-size: 22px;
        font-weight: 800;
        line-height: 1.15;
        color: {PALETTE['text']};
        margin: 6px 0 2px 0;
    }}
    .mkt-hero-value {{
        font-size: 56px;
        font-weight: 900;
        line-height: 1;
        color: {PALETTE['gold']};
        text-shadow: 0 0 24px rgba(201,169,92,0.25);
        margin: 2px 0 0 0;
    }}
    .mkt-hero-counter {{
        font-size: 48px;
        font-weight: 900;
        color: {PALETTE['text']};
        line-height: 1;
    }}
    .mkt-hero-counter .unit {{
        font-size: 14px;
        color: {PALETTE['text_mute']};
        margin-left: 6px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .mkt-hero-date {{
        font-size: 12px;
        color: {PALETTE['text_mute']};
        margin-top: 4px;
    }}
    .mkt-card {{
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 14px;
        padding: 16px 18px;
        color: {PALETTE['text']};
        height: 100%;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }}
    .mkt-card:hover {{
        border-color: {PALETTE['border_strong']};
        transform: translateY(-1px);
    }}
    .mkt-countdown {{
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-radius: 14px;
        padding: 14px 16px 16px 16px;
        color: {PALETTE['text']};
        margin-bottom: 12px;
        position: relative;
    }}
    .mkt-countdown-num {{
        font-size: 40px;
        font-weight: 900;
        line-height: 1;
        color: {PALETTE['text']};
    }}
    .mkt-countdown-num .unit {{
        font-size: 12px;
        color: {PALETTE['text_mute']};
        font-weight: 600;
        margin-left: 6px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .mkt-countdown--red    {{ border-left: 4px solid {PALETTE['primary']}; }}
    .mkt-countdown--red .mkt-countdown-num {{ color: {PALETTE['primary']}; }}
    .mkt-countdown--gold   {{ border-left: 4px solid {PALETTE['gold']}; }}
    .mkt-countdown--gold .mkt-countdown-num {{ color: {PALETTE['gold']}; }}
    .mkt-countdown--navy   {{ border-left: 4px solid {PALETTE['info']}; }}
    .mkt-countdown--navy .mkt-countdown-num {{ color: {PALETTE['info']}; }}
    .mkt-countdown--mute   {{ border-left: 4px solid {PALETTE['text_faint']}; opacity: 0.7; }}
    .mkt-card--accent-red {{
        border-left: 3px solid {PALETTE['primary']};
    }}
    .mkt-card--accent-gold {{
        border-left: 3px solid {PALETTE['gold']};
    }}
    .mkt-card--accent-navy {{
        border-left: 3px solid {PALETTE['info']};
    }}
    .mkt-card-head {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }}
    .mkt-card-title {{
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 0.2px;
    }}
    .mkt-card-body {{
        font-size: 12.5px;
        color: {PALETTE['text_mute']};
        line-height: 1.5;
    }}
    .mkt-chip {{
        display: inline-block;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 0.5px;
        padding: 3px 9px;
        border-radius: 999px;
        text-transform: uppercase;
    }}
    .mkt-chip--red    {{ background: {PALETTE['primary']};  color: white; }}
    .mkt-chip--gold   {{ background: {PALETTE['gold']};     color: #1a1a1a; }}
    .mkt-chip--navy   {{ background: {PALETTE['info']};     color: white; }}
    .mkt-chip--mute   {{ background: rgba(139,152,165,0.25); color: {PALETTE['text_mute']}; }}
    .mkt-chip--success{{ background: {PALETTE['success']};  color: white; }}
    .mkt-chip--warn   {{ background: {PALETTE['warning']};  color: white; }}
    .mkt-chip--danger {{ background: {PALETTE['danger']};   color: white; }}
    .mkt-meta {{
        font-size: 12px;
        color: {PALETTE['text_faint']};
    }}
    .mkt-kv {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid {PALETTE['border']};
        font-size: 13px;
    }}
    .mkt-kv:last-child {{ border-bottom: none; }}
    .mkt-kv-label {{ color: {PALETTE['text_mute']}; }}
    .mkt-kv-value {{ color: {PALETTE['text']}; font-weight: 600; }}
    .mkt-sla-row {{
        display: flex;
        align-items: center;
        gap: 12px;
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-left: 3px solid var(--accent, {PALETTE['info']});
        padding: 10px 14px;
        border-radius: 10px;
        margin-bottom: 6px;
    }}
    .mkt-sla-label {{ font-weight: 700; color: {PALETTE['text']}; font-size: 13.5px; min-width: 180px; }}
    .mkt-sla-value {{ color: {PALETTE['text_mute']}; font-size: 13px; }}
    .mkt-journey {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        border-top: 3px solid var(--accent);
        padding: 14px;
        border-radius: 12px;
        min-height: 150px;
    }}
    .mkt-journey-step {{ font-size: 10.5px; font-weight: 700; letter-spacing: 1px; color: var(--accent); text-transform: uppercase; }}
    .mkt-journey-title {{ font-size: 15px; font-weight: 700; color: {PALETTE['text']}; }}
    .mkt-journey-desc {{ font-size: 12px; color: {PALETTE['text_mute']}; line-height: 1.45; }}
    .mkt-meeting {{
        display: flex;
        justify-content: space-between;
        background: {PALETTE['surface']};
        border: 1px solid {PALETTE['border']};
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 6px;
    }}
    .mkt-meeting-title {{ font-weight: 700; color: {PALETTE['text']}; font-size: 14px; }}
    .mkt-meeting-agenda {{ color: {PALETTE['text_mute']}; font-size: 12px; margin-top: 2px; }}
    .mkt-meeting-who {{ color: {PALETTE['text_faint']}; font-size: 12px; text-align: right; min-width: 200px; }}
    .mkt-positioning {{
        background: linear-gradient(135deg, {PALETTE['navy']} 0%, {PALETTE['navy_deep']} 100%);
        padding: 28px 32px;
        border-radius: 18px;
        border: 1px solid {PALETTE['border_strong']};
        border-left: 4px solid {PALETTE['gold']};
        color: {PALETTE['text']};
        margin-top: 8px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }}
    .mkt-positioning-headline {{
        color: {PALETTE['gold']};
    }}
    .mkt-positioning-label {{ font-size: 11px; letter-spacing: 1.3px; text-transform: uppercase; opacity: 0.65; font-weight: 600; }}
    .mkt-positioning-headline {{ font-size: 22px; font-weight: 700; line-height: 1.35; margin: 10px 0 12px 0; }}
    .mkt-positioning-sub {{ font-size: 14px; opacity: 0.85; line-height: 1.5; }}
    /* Section divider — subtle, not default hr */
    .mkt-divider {{
        border: none;
        border-top: 1px solid {PALETTE['border']};
        margin: 22px 0 18px 0;
    }}
    /* Force code blocks to wrap text (scripts are long, need readability) */
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCode"] pre,
    .stCodeBlock pre,
    .stCode pre,
    pre code {{
        white-space: pre-wrap !important;
        word-break: break-word !important;
        overflow-wrap: anywhere !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def _wrap_open():
    """No-op — kept for backwards compatibility."""
    pass


def _wrap_close():
    """No-op — kept for backwards compatibility."""
    pass


def _divider():
    st.markdown('<hr class="mkt-divider" />', unsafe_allow_html=True)


def _get_lang(lang_dict: dict, lang: str) -> dict:
    """Merge requested lang with EN fallback (for Khmer — fallback to EN on missing keys)."""
    result = dict(lang_dict.get("en", {}))
    result.update(lang_dict.get(lang, {}))
    return result


# ============================================================
# AUTO-TRANSLATE (Google Translate via deep-translator, no API key needed)
# ============================================================
@st.cache_data(show_spinner=False, ttl=3600)
def translate_text(text: str, target: str, source: str = "auto") -> str:
    """Translate text to target language. Cached for 1h per (text, target) pair.
    Returns the input text unchanged if translation fails (no internet, rate limit, etc.)."""
    if not text or not text.strip():
        return ""
    if target == source:
        return text
    try:
        from deep_translator import GoogleTranslator
        # Map our language codes to Google's
        lang_map = {"ru": "ru", "en": "en", "km": "km"}
        tgt = lang_map.get(target, target)
        src = lang_map.get(source, source) if source != "auto" else "auto"
        result = GoogleTranslator(source=src, target=tgt).translate(text)
        return result or text
    except Exception as e:
        return f"[translate failed: {type(e).__name__}] {text}"


def _brand_header(tagline_ru: str, tagline_en: str, tagline_km: str, lang: str):
    """WISC brand banner — navy + gold, CSS-rendered (no logo file needed)."""
    tagline = {"ru": tagline_ru, "en": tagline_en, "km": tagline_km}.get(lang, tagline_en)
    st.markdown(
        f"""
        <div class="wisc-brand">
            <div class="wisc-shield"></div>
            <div class="wisc-brand-text">
                <div class="wisc-brand-title">WORLD INTERNATIONAL SCHOOL CAMBODIA</div>
                <div class="wisc-brand-sub">{tagline}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# I18N
# ============================================================
MKT_LANG = {
    "ru": {
        "header": "Маркетинговая стратегия — запуск приёмной комиссии",
        "subheader": "Операционный хаб: таймлайн, воронка, каналы, команда. AY 2026-2027.",
        "sections": [
            "Обзор & Countdown",
            "🚀 Launch Playbook",
            "Аудитория & Позиционирование",
            "Funnel Model",
            "Каналы & Бюджет",
            "Креативы & Контент",
            "Admissions & Конверсия",
            "Команда (RACI)",
            "KPI Dashboard",
            "✍️ Translator",
        ],
        "status_labels": {"not_started": "Не начато", "in_progress": "В работе", "done": "Готово"},
        "status_colors": {"not_started": "#e74c3c", "in_progress": "#f39c12", "done": "#2ecc71"},
        "owner": "Ответственный",
        "deliverables": "Deliverables",
        "status": "Статус",
        "due_date": "Дедлайн",
        "days_left": "дней",
        "today_label": "Сегодня",
        "d_to_may1": "До 1 мая (старт приёмки)",
        "d_to_sep1": "До 1 сентября (старт уч. года)",
        "goal_min": "Цель min",
        "goal_max": "Цель max",
        "students": "учеников",
        "target_enrollments": "Enrollments (набор)",
        "work_blocks": "Статус ключевых блоков работ",
        "kpi_targets": "KPI Targets (на весь сезон)",
        "leads": "Leads",
        "tours": "Booked Tours",
        "applications": "Applications",
        "deposits": "Deposits",
        "enrollments": "Enrollments",
        "timeline_header": "Countdown по ключевым дедлайнам",
        "overdue": "Просрочено",
        "todo_update": "TODO: обновить после запуска",
        # 3.2
        "sec_audience_title": "Сегменты аудитории (приоритет)",
        "seg_khmer_title": "Средний+ кхмерский класс",
        "seg_khmer_badge": "PRIMARY",
        "seg_chinese_title": "Китайская диаспора",
        "seg_chinese_badge": "SECONDARY",
        "seg_elite_title": "Local Elite",
        "seg_elite_badge": "HIGH-LTV",
        "seg_size": "Размер сегмента",
        "seg_size_todo": "TODO: оценка после Market Entry Memo (Айжан)",
        "seg_criteria": "Критерии выбора школы",
        "seg_channels": "Каналы",
        "seg_language": "Язык коммуникации",
        "seg_price": "Чувствительность к цене",
        "seg_objections": "Ключевые возражения",
        "positioning_title": "Positioning Statement",
        "positioning_headline": "A premier international education — nurturing globally-minded learners, rooted in Cambodian values.",
        "positioning_sub": "Cambridge curriculum + трилингва (English / Khmer / Chinese) + international pathway + full-day immersive learning.",
        "rtb_title": "RTB (Reasons to Believe) — дифференциаторы",
        # 3.3
        "funnel_title": "Funnel Model — расчёт воронки",
        "funnel_help": "Двигай слайдеры — воронка и метрики пересчитаются в реальном времени.",
        "funnel_inputs": "Входные параметры",
        "funnel_outputs": "Результат",
        "inp_target_enroll": "Target enrollments",
        "inp_lead_tour": "Lead → Booked Tour, %",
        "inp_showup": "Tour show-up rate, %",
        "inp_tour_app": "Tour → Application, %",
        "inp_app_dep": "Application → Deposit, %",
        "inp_dep_enr": "Deposit → Enrollment, %",
        "inp_cpl": "Target CPL, USD",
        "out_leads": "Required Leads",
        "out_tours": "Required Booked Tours",
        "out_showups": "Required Show-ups",
        "out_apps": "Required Applications",
        "out_deps": "Required Deposits",
        "out_spend": "Estimated Ad Spend",
        "out_cac": "CAC (Customer Acquisition Cost)",
        "out_payback": "Payback (месяцев tuition)",
        "out_ltv_cac": "LTV / CAC (5 лет, retention 85%)",
        "funnel_stages": ["Leads", "Booked Tours", "Tour Show-ups", "Applications", "Deposits", "Enrollments"],
        "scenarios_title": "Scenario Comparison",
        "sc_conservative": "Conservative",
        "sc_base": "Base",
        "sc_aggressive": "Aggressive",
        # 3.4
        "channels_title": "Channel Strategy & Budget Allocation",
        "channels_help": "Таблица редактируемая. Сохранение обновляет только текущий вид. Для персистентности — правь data/marketing_channels.csv напрямую.",
        "channels_total_row": "Итого",
        "channels_budget_chart": "Распределение бюджета по каналам",
        "channels_leads_chart": "Ожидаемые лиды / мес по каналам",
        "save_csv": "💾 Сохранить в CSV",
        "saved_ok": "Сохранено в data/marketing_channels.csv",
        # 3.5
        "creative_title": "Creative & Content Plan",
        "creative_deadline_title": "Production sprint — дедлайн 29 апреля",
        "creative_langs": "Языковые версии: English + Khmer + Chinese (3 версии каждого креатива для топ-3 сегментов)",
        "content_pillars_title": "Content Pillars (post-launch)",
        # 3.6
        "adm_title": "Admissions Funnel & Conversion System",
        "adm_sla": "Response SLA (нужно соблюдать)",
        "adm_journey": "Parent Journey — 6 шагов",
        "adm_scripts": "Скрипты (placeholders — финальные напишет Айжан)",
        "adm_objections": "Частые возражения и как снимать",
        # 3.7
        "raci_title": "Команда и ответственность (RACI)",
        "raci_legend": "R = Responsible (делает) · A = Accountable (отвечает) · C = Consulted · I = Informed",
        "meetings_title": "Ритм встреч",
        # KPI Dashboard
        "kpi_title": "KPI Dashboard",
        "kpi_help": "Данные — из data/marketing_kpi.csv (команда обновляет еженедельно).",
        "kpi_no_data": "Data source не настроен — обновите data/marketing_kpi.csv чтобы увидеть live-данные.",
        "kpi_top_funnel": "Top-of-funnel",
        "kpi_mid_funnel": "Mid-funnel",
        "kpi_bottom_funnel": "Bottom-funnel",
        "kpi_total_leads": "Total leads (cumulative)",
        "kpi_qualified_pct": "Qualified leads %",
        "kpi_cpl_avg": "Avg CPL",
        "kpi_speed_to_lead": "Speed to lead (min)",
        "kpi_booked_tours": "Booked tours",
        "kpi_showup_pct": "Show-up rate",
        "kpi_tour_app": "Tour → Application",
        "kpi_apps": "Applications",
        "kpi_deposits": "Deposits",
        "kpi_enrollments": "Enrollments",
        "kpi_l2e": "Lead → Enrollment",
        "kpi_cac": "CAC",
        "kpi_pacing": "Pacing vs target (200)",
        "kpi_chart_enrollments": "Еженедельный прогресс по enrollments vs target",
        "kpi_chart_by_grade": "Enrollments по grade band",
        "kpi_chart_funnel_now": "Воронка текущего периода",
        "kpi_target_line": "Target (linear to 200 by Sep 1)",
        "kpi_actual_line": "Actual",
        # Launch Playbook
        "lp_title": "Launch Playbook — что нужно сделать чтобы 1 мая взлететь",
        "lp_subtitle": "Задачи с 💡 — это мои добавки поверх твоего брифа: без них 1 мая не взлетит даже с идеальными креативами.",
        "lp_tabs": ["Sprint 8 дней", "Weekly Playbook (Май–Авг)", "💡 Growth Hacks", "Risk Register"],
        "lp_progress": "Прогресс спринта",
        "lp_bonus_marker": "💡",
        "lp_today": "Сегодня",
        "lp_done_of": "сделано из",
        "lp_weekly_title": "Что делать каждую неделю",
        "lp_hacks_title": "Growth hacks (не из брифа — мои добавки)",
        "lp_risks_title": "Risk register — что может положить сезон",
        "lp_risk_prob": "Вероятность",
        "lp_risk_impact": "Импакт",
        "lp_risk_mitigation": "Митигация",
        "lp_risk_event": "Риск",
    },
    "en": {
        "header": "Marketing strategy — admissions launch",
        "subheader": "Ops hub: timeline, funnel, channels, team. AY 2026-2027.",
        "sections": [
            "Overview & Countdown",
            "🚀 Launch Playbook",
            "Audience & Positioning",
            "Funnel Model",
            "Channels & Budget",
            "Creatives & Content",
            "Admissions & Conversion",
            "Team (RACI)",
            "KPI Dashboard",
            "✍️ Translator",
        ],
        "status_labels": {"not_started": "Not started", "in_progress": "In progress", "done": "Done"},
        "status_colors": {"not_started": "#e74c3c", "in_progress": "#f39c12", "done": "#2ecc71"},
        "owner": "Owner",
        "deliverables": "Deliverables",
        "status": "Status",
        "due_date": "Due",
        "days_left": "days",
        "today_label": "Today",
        "d_to_may1": "To May 1 (admissions open)",
        "d_to_sep1": "To Sep 1 (school year start)",
        "goal_min": "Goal min",
        "goal_max": "Goal max",
        "students": "students",
        "target_enrollments": "Enrollments (target)",
        "work_blocks": "Key work block status",
        "kpi_targets": "KPI Targets (full season)",
        "leads": "Leads",
        "tours": "Booked Tours",
        "applications": "Applications",
        "deposits": "Deposits",
        "enrollments": "Enrollments",
        "timeline_header": "Countdown to key deadlines",
        "overdue": "Overdue",
        "todo_update": "TODO: update post-launch",
        # 3.2
        "sec_audience_title": "Audience segments (priority)",
        "seg_khmer_title": "Affluent Khmer middle-class+",
        "seg_khmer_badge": "PRIMARY",
        "seg_chinese_title": "Chinese diaspora",
        "seg_chinese_badge": "SECONDARY",
        "seg_elite_title": "Local Elite",
        "seg_elite_badge": "HIGH-LTV",
        "seg_size": "Segment size",
        "seg_size_todo": "TODO: estimate after Market Entry Memo (Aizhan)",
        "seg_criteria": "School choice criteria",
        "seg_channels": "Channels",
        "seg_language": "Language",
        "seg_price": "Price sensitivity",
        "seg_objections": "Key objections",
        "positioning_title": "Positioning Statement",
        "positioning_headline": "A premier international education — nurturing globally-minded learners, rooted in Cambodian values.",
        "positioning_sub": "Cambridge curriculum + trilingual (English / Khmer / Chinese) + international pathway + full-day immersive learning.",
        "rtb_title": "RTB (Reasons to Believe) — differentiators",
        # 3.3
        "funnel_title": "Funnel Model",
        "funnel_help": "Move sliders — funnel and metrics recalc live.",
        "funnel_inputs": "Inputs",
        "funnel_outputs": "Outputs",
        "inp_target_enroll": "Target enrollments",
        "inp_lead_tour": "Lead → Booked Tour, %",
        "inp_showup": "Tour show-up rate, %",
        "inp_tour_app": "Tour → Application, %",
        "inp_app_dep": "Application → Deposit, %",
        "inp_dep_enr": "Deposit → Enrollment, %",
        "inp_cpl": "Target CPL, USD",
        "out_leads": "Required Leads",
        "out_tours": "Required Booked Tours",
        "out_showups": "Required Show-ups",
        "out_apps": "Required Applications",
        "out_deps": "Required Deposits",
        "out_spend": "Estimated Ad Spend",
        "out_cac": "CAC (Customer Acquisition Cost)",
        "out_payback": "Payback (tuition months)",
        "out_ltv_cac": "LTV / CAC (5 yrs, 85% retention)",
        "funnel_stages": ["Leads", "Booked Tours", "Tour Show-ups", "Applications", "Deposits", "Enrollments"],
        "scenarios_title": "Scenario Comparison",
        "sc_conservative": "Conservative",
        "sc_base": "Base",
        "sc_aggressive": "Aggressive",
        # 3.4
        "channels_title": "Channel Strategy & Budget Allocation",
        "channels_help": "Editable table. Save sends nothing — just updates the view. Persistence: change data/marketing_channels.csv directly.",
        "channels_total_row": "Total",
        "channels_budget_chart": "Budget allocation by channel",
        "channels_leads_chart": "Expected leads / month by channel",
        "save_csv": "💾 Save to CSV",
        "saved_ok": "Saved to data/marketing_channels.csv",
        # 3.5
        "creative_title": "Creative & Content Plan",
        "creative_deadline_title": "Production sprint — deadline 29 April",
        "creative_langs": "Language versions: English + Khmer + Chinese (3 versions per creative for top-3 segments)",
        "content_pillars_title": "Content Pillars (post-launch)",
        # 3.6
        "adm_title": "Admissions Funnel & Conversion System",
        "adm_sla": "Response SLA (must-have)",
        "adm_journey": "Parent Journey — 6 steps",
        "adm_scripts": "Scripts (placeholders — Aizhan will finalize)",
        "adm_objections": "Common objections & how to address",
        # 3.7
        "raci_title": "Team & Responsibilities (RACI)",
        "raci_legend": "R = Responsible · A = Accountable · C = Consulted · I = Informed",
        "meetings_title": "Meeting rhythm",
        # KPI Dashboard
        "kpi_title": "KPI Dashboard",
        "kpi_help": "Data from data/marketing_kpi.csv (team updates weekly).",
        "kpi_no_data": "Data source not configured yet — update data/marketing_kpi.csv to see live data.",
        "kpi_top_funnel": "Top-of-funnel",
        "kpi_mid_funnel": "Mid-funnel",
        "kpi_bottom_funnel": "Bottom-funnel",
        "kpi_total_leads": "Total leads (cumulative)",
        "kpi_qualified_pct": "Qualified leads %",
        "kpi_cpl_avg": "Avg CPL",
        "kpi_speed_to_lead": "Speed to lead (min)",
        "kpi_booked_tours": "Booked tours",
        "kpi_showup_pct": "Show-up rate",
        "kpi_tour_app": "Tour → Application",
        "kpi_apps": "Applications",
        "kpi_deposits": "Deposits",
        "kpi_enrollments": "Enrollments",
        "kpi_l2e": "Lead → Enrollment",
        "kpi_cac": "CAC",
        "kpi_pacing": "Pacing vs target (200)",
        "kpi_chart_enrollments": "Weekly enrollment progress vs target",
        "kpi_chart_by_grade": "Enrollments by grade band",
        "kpi_chart_funnel_now": "Current-period funnel",
        "kpi_target_line": "Target (linear to 200 by Sep 1)",
        "kpi_actual_line": "Actual",
        # Launch Playbook
        "lp_title": "Launch Playbook — what's needed to go live May 1",
        "lp_subtitle": "Items marked 💡 are my additions on top of your brief: without them, May 1 won't fly even with perfect creatives.",
        "lp_tabs": ["8-day Sprint", "Weekly Playbook (May-Aug)", "💡 Growth Hacks", "Risk Register"],
        "lp_progress": "Sprint progress",
        "lp_bonus_marker": "💡",
        "lp_today": "Today",
        "lp_done_of": "done of",
        "lp_weekly_title": "What to do each week",
        "lp_hacks_title": "Growth hacks (not in brief — my additions)",
        "lp_risks_title": "Risk register — what could kill the season",
        "lp_risk_prob": "Probability",
        "lp_risk_impact": "Impact",
        "lp_risk_mitigation": "Mitigation",
        "lp_risk_event": "Risk",
    },
    "km": {
        # [AIJAN-REVIEW] — Khmer UI; falls back to EN for missing keys
        "header": "យុទ្ធសាស្ត្រទីផ្សារ — ការបើកដំណើរការទទួលនិស្សិត",
        "subheader": "Ops hub: timeline, funnel, channels, team. AY 2026-2027.",
        "sections": [
            "ទិដ្ឋភាព & Countdown",
            "🚀 Launch Playbook",
            "ទស្សនិកជន & Positioning",
            "Funnel Model",
            "ឆានែល & ថវិកា",
            "Creatives & Content",
            "Admissions & Conversion",
            "ក្រុម (RACI)",
            "KPI Dashboard",
            "✍️ Translator",
        ],
        "status_labels": {"not_started": "មិនទាន់ចាប់ផ្តើម", "in_progress": "កំពុងដំណើរការ", "done": "រួចរាល់"},
        "status_colors": {"not_started": PALETTE["danger"], "in_progress": PALETTE["warning"], "done": PALETTE["success"]},
        "owner": "ម្ចាស់",
        "deliverables": "Deliverables",
        "status": "ស្ថានភាព",
        "due_date": "ថ្ងៃកំណត់",
        "days_left": "ថ្ងៃ",
        "today_label": "ថ្ងៃនេះ",
        "d_to_may1": "ដល់ថ្ងៃ 1 ឧសភា (ទទួលពាក្យ)",
        "d_to_sep1": "ដល់ថ្ងៃ 1 កញ្ញា (ចាប់ផ្តើមឆ្នាំសិក្សា)",
        "goal_min": "គោលដៅ min",
        "goal_max": "គោលដៅ max",
        "students": "សិស្ស",
        "target_enrollments": "ការចុះឈ្មោះ (គោលដៅ)",
        "work_blocks": "ស្ថានភាពការងារសំខាន់",
        "kpi_targets": "គោលដៅ KPI (ពេញរដូវ)",
        "leads": "Leads",
        "tours": "Tours",
        "applications": "Applications",
        "deposits": "Deposits",
        "enrollments": "Enrollments",
        "timeline_header": "Countdown ដល់ថ្ងៃកំណត់សំខាន់",
        "overdue": "ហួសពេល",
        "todo_update": "TODO: ធ្វើបច្ចុប្បន្នភាពក្រោយការបើកដំណើរការ",
        # 3.2
        "sec_audience_title": "ផ្នែកទស្សនិកជន (អាទិភាព)",
        "seg_khmer_title": "ជាន់កណ្តាលខ្មែរ",
        "seg_khmer_badge": "PRIMARY",
        "seg_chinese_title": "ជនជាតិចិន",
        "seg_chinese_badge": "SECONDARY",
        "seg_elite_title": "Local Elite",
        "seg_elite_badge": "HIGH-LTV",
        "seg_size": "ទំហំផ្នែក",
        "seg_size_todo": "TODO: នឹងធ្វើបច្ចុប្បន្នភាពក្រោយ Market Entry Memo",
        "seg_criteria": "លក្ខណៈវិនិច្ឆ័យជ្រើសរើសសាលា",
        "seg_channels": "ឆានែល",
        "seg_language": "ភាសា",
        "seg_price": "ភាពប្រែប្រួលតម្លៃ",
        "seg_objections": "ជម្លោះសំខាន់",
        "positioning_title": "សេចក្តីថ្លែងការណ៍ Positioning",
        "positioning_headline": "A premier international education — nurturing globally-minded learners, rooted in Cambodian values.",
        "positioning_sub": "Cambridge + trilingual (English / Khmer / Chinese) + international pathway + full-day immersive learning.",
        "rtb_title": "RTB (Reasons to Believe) — ភាពខុសគ្នា",
        # 3.3
        "funnel_title": "Funnel Model",
        "funnel_help": "រំកិល sliders — funnel និង metrics គណនាឡើងវិញផ្ទាល់",
        "funnel_inputs": "Inputs",
        "funnel_outputs": "Outputs",
        "inp_target_enroll": "គោលដៅ enrollments",
        "inp_lead_tour": "Lead → Tour, %",
        "inp_showup": "អត្រាមកដល់ tour, %",
        "inp_tour_app": "Tour → Application, %",
        "inp_app_dep": "Application → Deposit, %",
        "inp_dep_enr": "Deposit → Enrollment, %",
        "inp_cpl": "គោលដៅ CPL, USD",
        "out_leads": "Leads ត្រូវការ",
        "out_tours": "Tours ត្រូវការ",
        "out_showups": "មកដល់ Tour",
        "out_apps": "Applications",
        "out_deps": "Deposits",
        "out_spend": "ការចំណាយប៉ាន់ស្មាន",
        "out_cac": "CAC",
        "out_payback": "Payback (ខែ)",
        "out_ltv_cac": "LTV / CAC",
        "funnel_stages": ["Leads", "Tours", "Show-ups", "Applications", "Deposits", "Enrollments"],
        "scenarios_title": "ការប្រៀបធៀប Scenarios",
        "sc_conservative": "Conservative",
        "sc_base": "Base",
        "sc_aggressive": "Aggressive",
        # 3.4
        "channels_title": "យុទ្ធសាស្ត្រ & ថវិកាតាមឆានែល",
        "channels_help": "តារាងអាចកែបាន។ កែ data/marketing_channels.csv ដោយផ្ទាល់",
        "channels_total_row": "សរុប",
        "channels_budget_chart": "ថវិកាតាមឆានែល",
        "channels_leads_chart": "Leads / ខែ តាមឆានែល",
        "save_csv": "💾 រក្សាទុកទៅ CSV",
        "saved_ok": "បានរក្សាទុក",
        # 3.5
        "creative_title": "ផែនការ Creative & Content",
        "creative_deadline_title": "Production sprint — ដល់ថ្ងៃ 29 មេសា",
        "creative_langs": "ភាសា: English + Khmer + Chinese",
        "content_pillars_title": "Content Pillars",
        # 3.6
        "adm_title": "Admissions Funnel & ប្រព័ន្ធបំប្លែង",
        "adm_sla": "SLA ឆ្លើយតប",
        "adm_journey": "ដំណើរឪពុកម្តាយ — 6 ជំហាន",
        "adm_scripts": "ស្គ្រីប",
        "adm_objections": "ការជំទាស់ញឹកញាប់",
        # 3.7
        "raci_title": "ក្រុមនិងការទទួលខុសត្រូវ (RACI)",
        "raci_legend": "R = Responsible · A = Accountable · C = Consulted · I = Informed",
        "meetings_title": "ចង្វាក់ប្រជុំ",
        "kpi_title": "KPI Dashboard",
        "kpi_help": "ទិន្នន័យពី data/marketing_kpi.csv",
        # Launch Playbook
        "lp_title": "Launch Playbook — អ្វីដែលត្រូវធ្វើដើម្បីហោះថ្ងៃ 1 ឧសភា",
        "lp_subtitle": "ការងារដែលមានសញ្ញា 💡 — ជាការបន្ថែមលើ brief",
        "lp_tabs": ["Sprint 8 ថ្ងៃ", "Weekly Playbook", "💡 Growth Hacks", "Risk Register"],
        "lp_progress": "វឌ្ឍនភាព sprint",
        "lp_bonus_marker": "💡",
        "lp_today": "ថ្ងៃនេះ",
        "lp_done_of": "រួចពី",
        "lp_weekly_title": "អ្វីដែលត្រូវធ្វើប្រចាំសប្តាហ៍",
        "lp_hacks_title": "Growth hacks (ការបន្ថែម)",
        "lp_risks_title": "Risk register",
        "lp_risk_prob": "លទ្ធភាព",
        "lp_risk_impact": "ផលប៉ះពាល់",
        "lp_risk_mitigation": "ការកាត់បន្ថយ",
        "lp_risk_event": "ហានិភ័យ",
    },
}


# ============================================================
# DATA LOADERS
# ============================================================
from dashboard.datastore import load_json as _load_json_backend


def _load_json(filename: str) -> dict:
    """Backend-aware loader (Gist on prod, local files in dev)."""
    return _load_json_backend(filename)


@st.cache_data
def _load_csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / filename)


# ============================================================
# HELPERS
# ============================================================
def _days_between(target: date, today: date | None = None) -> int:
    today = today or date.today()
    return (target - today).days


def _urgency_color(days: int) -> str:
    """red = <=7d, amber = <=30d, navy = >30d, grey = overdue."""
    if days < 0:
        return PALETTE["text_faint"]
    if days <= 7:
        return PALETTE["primary"]
    if days <= 30:
        return PALETTE["gold"]
    return PALETTE["info"]


def _urgency_chip_class(days: int) -> str:
    if days < 0:
        return "mkt-chip mkt-chip--mute"
    if days <= 7:
        return "mkt-chip mkt-chip--red"
    if days <= 30:
        return "mkt-chip mkt-chip--gold"
    return "mkt-chip mkt-chip--navy"


def _urgency_accent_class(days: int) -> str:
    if days < 0:
        return ""
    if days <= 7:
        return "mkt-card--accent-red"
    if days <= 30:
        return "mkt-card--accent-gold"
    return "mkt-card--accent-navy"


def _milestone_status(milestone_id: str, default: str) -> str:
    key = f"mkt_milestone_status_{milestone_id}"
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def _render_countdown_card(title: str, target_date: date, owner: str, deliverables: str,
                           status: str, status_labels: dict, overdue_label: str, days_label: str):
    days = _days_between(target_date)
    date_str = target_date.strftime("%d %b %Y")
    status_label = status_labels.get(status, status)

    if days < 0:
        tone = "mute"
        big_num = "—"
        unit_text = overdue_label
    else:
        tone = "red" if days <= 7 else ("gold" if days <= 30 else "navy")
        big_num = str(days)
        unit_text = days_label

    st.markdown(
        f"""
        <div class="mkt-countdown mkt-countdown--{tone}">
            <div class="mkt-meta" style="margin-bottom:4px;">{date_str}</div>
            <div class="mkt-countdown-num">{big_num}<span class="unit">{unit_text}</span></div>
            <div class="mkt-card-title" style="margin:10px 0 6px 0;">{title}</div>
            <div class="mkt-card-body">
                <div>👥 {owner}</div>
                <div style="margin-top:4px;">📋 {deliverables}</div>
            </div>
            <div class="mkt-meta" style="margin-top:8px;">● {status_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# SECTION 3.1 — OVERVIEW & COUNTDOWN
# ============================================================
def _section_overview(L: dict, lang: str):
    _wrap_open()
    today = date.today()
    may1 = date(2026, 5, 1)
    sep1 = date(2026, 9, 1)

    # HERO — single bold panel
    days_to_may1 = _days_between(may1)
    days_to_sep1 = _days_between(sep1)
    st.markdown(
        f"""
        <div class="mkt-hero-big">
            <div class="mkt-hero-grid">
                <div>
                    <div class="mkt-hero-label">WISC Cambodia · AY 2026-2027</div>
                    <div class="mkt-hero-title">{L['target_enrollments']}</div>
                    <div class="mkt-hero-value">200–500</div>
                    <div class="mkt-meta" style="margin-top:4px;">{L['goal_min']} / {L['goal_max']} {L['students']}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['d_to_may1']}</div>
                    <div class="mkt-hero-counter">{days_to_may1}<span class="unit">{L['days_left']}</span></div>
                    <div class="mkt-hero-date">{may1.strftime('%d %b %Y')}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['d_to_sep1']}</div>
                    <div class="mkt-hero-counter">{days_to_sep1}<span class="unit">{L['days_left']}</span></div>
                    <div class="mkt-hero-date">{sep1.strftime('%d %b %Y')}</div>
                </div>
                <div>
                    <div class="mkt-hero-label">{L['today_label']}</div>
                    <div class="mkt-hero-counter" style="font-size:28px;">{today.strftime('%d %b')}</div>
                    <div class="mkt-hero-date">{today.strftime('%A · %Y')}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _divider()

    # TIMELINE COUNTDOWN
    st.subheader(L["timeline_header"])
    timeline = _load_json("marketing_timeline.json")["milestones"]
    # sort by date
    timeline_sorted = sorted(timeline, key=lambda m: m["date"])
    cols = st.columns(min(len(timeline_sorted), 4) or 1)
    for i, m in enumerate(timeline_sorted):
        with cols[i % len(cols)]:
            target = datetime.strptime(m["date"], "%Y-%m-%d").date()
            status = _milestone_status(m["id"], m["status"])
            _render_countdown_card(
                title=m.get(f"title_{lang}", m.get("title_en", m.get("title", ""))),
                target_date=target,
                owner=m["owner"],
                deliverables=m.get(f"deliverables_{lang}", m.get("deliverables_en", m.get("deliverables", ""))),
                status=status,
                status_labels=L["status_labels"],
                overdue_label=L["overdue"],
                days_label=L["days_left"],
            )

    _divider()

    # WORK BLOCKS STATUS — grid 2×3 with selectbox
    st.markdown(f'<div class="mkt-eyebrow">{L["work_blocks"]}</div>', unsafe_allow_html=True)
    status_opts = list(L["status_labels"].keys())
    defaults = {
        "creatives": "in_progress",
        "offers": "in_progress",
        "scripts": "not_started",
        "crm": "not_started",
        "landing": "not_started",
        "tracking": "not_started",
    }
    blocks_ru = [
        ("creatives", "Креативы (видео + статика)"),
        ("offers", "Офферы (Early Bird, Sibling)"),
        ("scripts", "Скрипты (WA/TG/звонки)"),
        ("crm", "CRM pipeline + дашборд"),
        ("landing", "Лендинг"),
        ("tracking", "Трекинг (pixels/UTM)"),
    ]
    blocks_en = [
        ("creatives", "Creatives (video + static)"),
        ("offers", "Offers (Early Bird, Sibling)"),
        ("scripts", "Scripts (WA/TG/calls)"),
        ("crm", "CRM pipeline + dashboard"),
        ("landing", "Landing page"),
        ("tracking", "Tracking (pixels/UTM)"),
    ]
    blocks = blocks_ru if lang == "ru" else blocks_en
    grid = st.columns(3)
    for i, (key, title) in enumerate(blocks):
        ss_key = f"mkt_block_{key}"
        if ss_key not in st.session_state:
            st.session_state[ss_key] = defaults.get(key, "not_started")
        with grid[i % 3]:
            st.selectbox(
                title,
                options=status_opts,
                index=status_opts.index(st.session_state[ss_key]),
                format_func=lambda v: L["status_labels"][v],
                key=f"{ss_key}_sel",
            )
            st.session_state[ss_key] = st.session_state[f"{ss_key}_sel"]

    _divider()

    # KPI TARGETS (placeholder)
    _divider()
    st.markdown(f'<div class="mkt-eyebrow">{L["kpi_targets"]}</div>', unsafe_allow_html=True)
    st.caption(L["todo_update"])
    kpi_cols = st.columns(5)
    # target funnel for 200 enrollments (Base scenario)
    targets = {
        "leads": 2400,
        "tours": 600,
        "applications": 300,
        "deposits": 240,
        "enrollments": 200,
    }
    for col, (k, v) in zip(kpi_cols, targets.items()):
        col.metric(L[k], f"{v:,}", delta="target")
    _wrap_close()


# ============================================================
# SECTION 3.2 — AUDIENCE & POSITIONING
# ============================================================
_SEGMENTS = {
    "ru": [
        {
            "badge_key": "seg_khmer_badge",
            "title_key": "seg_khmer_title",
            "bg": "#c0392b",
            "criteria": "Качество английского, international pathway, безопасность, статус",
            "channels": "Facebook, TikTok, mom communities, детские центры",
            "language": "Khmer + English (mix)",
            "price": "HIGH → акцент на Early Bird + Sibling + Annual (до −25%)",
            "objections": [
                "«Слишком дорого»",
                "«Сильный ли английский на самом деле?»",
                "«Подходят ли кхмерские дети в такую школу?»",
            ],
        },
        {
            "badge_key": "seg_chinese_badge",
            "title_key": "seg_chinese_title",
            "bg": "#2c3e50",
            "criteria": "Академические результаты, дисциплина, pathway в CN / international университеты",
            "channels": "WeChat, китайские expat-группы, preschool-партнёрства",
            "language": "Chinese + English; Chinese language в программе — hook",
            "price": "MID → важнее качество и признание сертификатов",
            "objections": [
                "«Признают ли сертификаты в Китае?»",
                "«Сколько китайских детей в классе?»",
            ],
        },
        {
            "badge_key": "seg_elite_badge",
            "title_key": "seg_elite_title",
            "bg": "#8e44ad",
            "criteria": "Престиж, networking, international exposure",
            "channels": "Closed communities, embassy circles, business associations, word-of-mouth",
            "language": "English, luxury tone",
            "price": "LOW → платят за статус и network",
            "objections": [
                "«Чем вы лучше существующих топ-школ Пномпеня?»",
            ],
        },
    ],
    "en": [
        {
            "badge_key": "seg_khmer_badge",
            "title_key": "seg_khmer_title",
            "bg": "#c0392b",
            "criteria": "English quality, international pathway, safety, status",
            "channels": "Facebook, TikTok, mom communities, child centers",
            "language": "Khmer + English (mix)",
            "price": "HIGH → push Early Bird + Sibling + Annual (up to −25%)",
            "objections": [
                "\"Too expensive\"",
                "\"Is English really strong?\"",
                "\"Do Khmer children fit?\"",
            ],
        },
        {
            "badge_key": "seg_chinese_badge",
            "title_key": "seg_chinese_title",
            "bg": "#2c3e50",
            "criteria": "Academic results, discipline, pathway to CN / international universities",
            "channels": "WeChat, Chinese expat groups, preschool partnerships",
            "language": "Chinese + English; Chinese language in curriculum is a hook",
            "price": "MID → quality & certificate recognition matter more",
            "objections": [
                "\"Are certificates recognized in China?\"",
                "\"How many Chinese kids per class?\"",
            ],
        },
        {
            "badge_key": "seg_elite_badge",
            "title_key": "seg_elite_title",
            "bg": "#8e44ad",
            "criteria": "Prestige, networking, international exposure",
            "channels": "Closed communities, embassy circles, business associations, word-of-mouth",
            "language": "English, luxury tone",
            "price": "LOW → pay for status and network",
            "objections": [
                "\"How are you better than existing top schools in PP?\"",
            ],
        },
    ],
}

_RTB = [
    "Cambridge curriculum + Khmer program + Chinese language",
    "Singapore Math, PBL (Project-Based Learning), PSHE, Social-Emotional Learning",
    "Full-day 8:00–16:00",
    "Инфраструктура: футбольное поле, бассейн, science lab, art room, music room, robotics lab, computer lab, library",
    "Extracurriculars 2×/неделю (Swimming, Karate/Taekwondo, Robotics, Drama, Debate/TEDx, Dance, Art)",
    "International assessments: MAP Test (G3-G10), PSAT (G10)",
    "Pathway: 1-6 Edexcel → 7-10 Transition to WASC → 11 SAT/IELTS/K-12",
]


def _section_audience(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["sec_audience_title"]}</div>', unsafe_allow_html=True)
    segments = _SEGMENTS.get(lang, _SEGMENTS["en"])
    accents = ["mkt-card--accent-red", "mkt-card--accent-navy", "mkt-card--accent-gold"]
    chips = ["mkt-chip mkt-chip--red", "mkt-chip mkt-chip--navy", "mkt-chip mkt-chip--gold"]

    cols = st.columns(3)
    for i, (col, seg) in enumerate(zip(cols, segments)):
        with col:
            kv = lambda label, val: (
                f'<div class="mkt-kv"><span class="mkt-kv-label">{label}</span></div>'
                f'<div class="mkt-card-body" style="padding:6px 0 12px 0;">{val}</div>'
            )
            body = (
                kv(L["seg_criteria"], seg["criteria"])
                + kv(L["seg_channels"], seg["channels"])
                + kv(L["seg_language"], seg["language"])
                + kv(L["seg_price"], seg["price"])
            )
            obj_html = "".join(
                f'<div class="mkt-card-body" style="padding:3px 0;">• {o}</div>'
                for o in seg["objections"]
            )
            st.markdown(
                f"""
                <div class="mkt-card {accents[i]}">
                    <div class="mkt-card-head">
                        <span class="{chips[i]}">{L[seg['badge_key']]}</span>
                    </div>
                    <div class="mkt-card-title" style="font-size:17px;margin-bottom:4px;">{L[seg['title_key']]}</div>
                    <div class="mkt-meta" style="font-style:italic;margin-bottom:14px;">{L['seg_size_todo']}</div>
                    {body}
                    <div class="mkt-kv"><span class="mkt-kv-label">{L['seg_objections']}</span></div>
                    {obj_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

    _divider()
    st.markdown(
        f"""
        <div class="mkt-positioning">
            <div class="mkt-positioning-label">{L['positioning_title']}</div>
            <div class="mkt-positioning-headline">«{L['positioning_headline']}»</div>
            <div class="mkt-positioning-sub">{L['positioning_sub']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander(L["rtb_title"]):
        for item in _RTB:
            st.markdown(f"- {item}")
    _wrap_close()


# ============================================================
# SECTION 3.3 — FUNNEL MODEL & TARGETS
# ============================================================
_AVG_TUITION = 4000        # used for CAC payback
_AVG_YEARS = 5             # LTV horizon
_RETENTION = 0.85          # year-over-year retention


def _compute_funnel(target_enroll: int, lead_tour: float, showup: float,
                    tour_app: float, app_dep: float, dep_enr: float, cpl: float):
    deposits = target_enroll / dep_enr
    applications = deposits / app_dep
    tours_done = applications / tour_app
    tours_booked = tours_done / showup
    leads = tours_booked / lead_tour
    spend = leads * cpl
    cac = spend / target_enroll if target_enroll else 0
    ltv = _AVG_TUITION * sum(_RETENTION ** i for i in range(_AVG_YEARS))
    payback_months = (cac / _AVG_TUITION) * 12 if _AVG_TUITION else 0
    ltv_cac = ltv / cac if cac else 0
    return {
        "leads": leads,
        "tours_booked": tours_booked,
        "tours_done": tours_done,
        "applications": applications,
        "deposits": deposits,
        "enrollments": target_enroll,
        "spend": spend,
        "cac": cac,
        "payback_months": payback_months,
        "ltv_cac": ltv_cac,
    }


def _section_funnel(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["funnel_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["funnel_help"]}</div>', unsafe_allow_html=True)

    c_in, c_out = st.columns([1, 1.4])
    with c_in:
        st.markdown(f"**{L['funnel_inputs']}**")
        target_enroll = st.slider(L["inp_target_enroll"], 200, 500, 200, 10, key="mkt_f_target")
        lead_tour = st.slider(L["inp_lead_tour"], 15, 40, 25, 1, key="mkt_f_lt") / 100
        showup = st.slider(L["inp_showup"], 50, 85, 70, 1, key="mkt_f_show") / 100
        tour_app = st.slider(L["inp_tour_app"], 20, 50, 35, 1, key="mkt_f_ta") / 100
        app_dep = st.slider(L["inp_app_dep"], 60, 90, 80, 1, key="mkt_f_ad") / 100
        dep_enr = st.slider(L["inp_dep_enr"], 85, 98, 95, 1, key="mkt_f_de") / 100
        cpl = st.slider(L["inp_cpl"], 5, 40, 15, 1, key="mkt_f_cpl")

    r = _compute_funnel(target_enroll, lead_tour, showup, tour_app, app_dep, dep_enr, cpl)

    with c_out:
        # Funnel chart
        stages = L["funnel_stages"]
        values = [r["leads"], r["tours_booked"], r["tours_done"],
                  r["applications"], r["deposits"], r["enrollments"]]
        fig = go.Figure(go.Funnel(
            y=stages,
            x=[round(v) for v in values],
            textposition="inside",
            textinfo="value+percent initial",
            marker={"color": ["#e74c3c", "#e67e22", "#f39c12", "#3498db", "#9b59b6", "#2ecc71"]},
            connector={"line": {"color": "#2c3e50"}},
        ))
        fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

    # Output metrics row
    m = st.columns(5)
    m[0].metric(L["out_leads"], f"{r['leads']:,.0f}")
    m[1].metric(L["out_tours"], f"{r['tours_booked']:,.0f}")
    m[2].metric(L["out_apps"], f"{r['applications']:,.0f}")
    m[3].metric(L["out_deps"], f"{r['deposits']:,.0f}")
    m[4].metric(L["enrollments"], f"{r['enrollments']:,.0f}")

    m2 = st.columns(4)
    m2[0].metric(L["out_spend"], f"${r['spend']:,.0f}")
    m2[1].metric(L["out_cac"], f"${r['cac']:,.0f}")
    m2[2].metric(L["out_payback"], f"{r['payback_months']:.1f}")
    m2[3].metric(L["out_ltv_cac"], f"{r['ltv_cac']:.1f}×")

    _divider()
    # Scenario comparison
    st.subheader(L["scenarios_title"])
    preset = [
        (L["sc_conservative"], 200, 0.20, 0.65, 0.30, 0.75, 0.93, 20),
        (L["sc_base"],         300, 0.25, 0.70, 0.35, 0.80, 0.95, 15),
        (L["sc_aggressive"],   500, 0.30, 0.72, 0.38, 0.82, 0.95, 12),
    ]
    rows = []
    for name, en, lt, su, ta, ad, de, c in preset:
        x = _compute_funnel(en, lt, su, ta, ad, de, c)
        rows.append({
            "Scenario": name,
            L["enrollments"]: f"{en:,}",
            L["inp_cpl"]: f"${c}",
            L["out_leads"]: f"{x['leads']:,.0f}",
            L["out_tours"]: f"{x['tours_booked']:,.0f}",
            L["out_spend"]: f"${x['spend']:,.0f}",
            L["out_cac"]: f"${x['cac']:,.0f}",
            L["out_ltv_cac"]: f"{x['ltv_cac']:.1f}×",
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    _wrap_close()


# ============================================================
# SECTION 3.4 — CHANNEL STRATEGY & BUDGET ALLOCATION
# ============================================================
_CHANNELS_CSV = DATA_DIR / "marketing_channels.csv"


def _section_channels(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["channels_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["channels_help"]}</div>', unsafe_allow_html=True)

    df = pd.read_csv(_CHANNELS_CSV)

    # store edit in session state so saving works
    edited = st.data_editor(
        df,
        key="mkt_channels_editor",
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "monthly_budget_usd": st.column_config.NumberColumn("Budget $/mo", format="$%d"),
            "target_cpl_usd": st.column_config.NumberColumn("Target CPL $", format="$%d"),
            "expected_leads_month": st.column_config.NumberColumn("Leads/mo"),
            "priority": st.column_config.SelectboxColumn("Priority", options=["P0", "P1", "P2"]),
            "status": st.column_config.SelectboxColumn("Status",
                options=["Setup", "Live", "Paused", "Planning", "Not started"]),
        },
        hide_index=True,
    )

    # Totals
    total_budget = edited["monthly_budget_usd"].sum()
    total_leads = edited["expected_leads_month"].sum()
    blended_cpl = (total_budget / total_leads) if total_leads else 0
    k = st.columns(3)
    k[0].metric(f"Total monthly budget", f"${total_budget:,.0f}")
    k[1].metric(f"Expected leads / mo", f"{total_leads:,.0f}")
    k[2].metric(f"Blended CPL", f"${blended_cpl:,.1f}")

    if st.button(L["save_csv"], key="mkt_channels_save"):
        edited.to_csv(_CHANNELS_CSV, index=False)
        st.cache_data.clear()
        st.success(L["saved_ok"])

    _divider()
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{L['channels_budget_chart']}**")
        fig_b = go.Figure(go.Bar(
            x=edited["channel"], y=edited["monthly_budget_usd"],
            marker_color=["#e74c3c" if p == "P0" else "#f39c12" if p == "P1" else "#95a5a6"
                          for p in edited["priority"]],
            text=[f"${v:,.0f}" for v in edited["monthly_budget_usd"]],
            textposition="outside",
        ))
        fig_b.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=80),
                            xaxis_tickangle=-35, yaxis_title="USD/mo")
        st.plotly_chart(fig_b, use_container_width=True)
    with c2:
        st.markdown(f"**{L['channels_leads_chart']}**")
        fig_l = go.Figure(go.Bar(
            x=edited["channel"], y=edited["expected_leads_month"],
            marker_color="#3498db",
            text=edited["expected_leads_month"],
            textposition="outside",
        ))
        fig_l.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=80),
                            xaxis_tickangle=-35, yaxis_title="Leads/mo")
        st.plotly_chart(fig_l, use_container_width=True)
    _wrap_close()


# ============================================================
# SECTION 3.5 — CREATIVE & CONTENT PLAN
# ============================================================
_CREATIVE_CHECKLIST = {
    "ru": [
        ("3 видео-креатива «Day in the life at WISC» (15s / 30s / 60s)", "Жигер"),
        ("2 видео-креатива с директором школы (message + vision)", "Жигер + Кайсар"),
        ("5-8 статических креативов для Meta (carousel)", "Жигер"),
        ("5 статических креативов для TikTok (vertical)", "Жигер"),
        ("3 offer-креатива (Early Bird 15%, Sibling, Annual)", "Жигер + Кайсар"),
        ("Лендинг (форма заявки, виртуальный тур, фото инфраструктуры)", "Бакир + Жигер"),
        ("Брошюра PDF для скачивания", "Жигер"),
    ],
    "en": [
        ("3 video creatives \"Day in the life at WISC\" (15s / 30s / 60s)", "Zhiger"),
        ("2 video creatives with Head of School (message + vision)", "Zhiger + Kaisar"),
        ("5-8 static creatives for Meta (carousel)", "Zhiger"),
        ("5 static creatives for TikTok (vertical)", "Zhiger"),
        ("3 offer creatives (Early Bird 15%, Sibling, Annual)", "Zhiger + Kaisar"),
        ("Landing page (application form, virtual tour, facility photos)", "Bakir + Zhiger"),
        ("Brochure PDF for download", "Zhiger"),
    ],
}

_CONTENT_PILLARS = {
    "ru": [
        ("Academic excellence", "Cambridge results, Singapore Math, MAP/PSAT; примеры задач, портреты учителей, сравнение с национальной программой.", "📚"),
        ("Child development", "PBL, SEL, extracurriculars; кейсы проектов, эмоциональное развитие, soft skills.", "🧠"),
        ("International pathway", "Edexcel → WASC → universities; карта пути, alumni-истории, SAT/IELTS-готовность.", "🎓"),
        ("Community & culture", "Трилингвальная среда, Khmer roots, international mindset; национальные праздники, Chinese New Year, Khmer New Year.", "🌏"),
        ("Campus & facilities", "Бассейн, лаборатории, библиотека, спорт; виртуальный тур, behind-the-scenes, таймлапсы.", "🏫"),
        ("Parent testimonials & events", "Отзывы, Open Days, family events, Q&A с Head of School.", "👨‍👩‍👧"),
    ],
    "en": [
        ("Academic excellence", "Cambridge results, Singapore Math, MAP/PSAT; sample problems, teacher portraits, curriculum comparison.", "📚"),
        ("Child development", "PBL, SEL, extracurriculars; project cases, emotional development, soft skills.", "🧠"),
        ("International pathway", "Edexcel → WASC → universities; pathway map, alumni stories, SAT/IELTS readiness.", "🎓"),
        ("Community & culture", "Trilingual environment, Khmer roots, international mindset; national holidays, Chinese NY, Khmer NY.", "🌏"),
        ("Campus & facilities", "Pool, labs, library, sports; virtual tour, behind-the-scenes, timelapses.", "🏫"),
        ("Parent testimonials & events", "Testimonials, Open Days, family events, Q&A with Head of School.", "👨‍👩‍👧"),
    ],
}


def _section_creative(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["creative_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-eyebrow" style="color:{PALETTE["primary"]};">🔥 {L["creative_deadline_title"]}</div>', unsafe_allow_html=True)

    checklist = _CREATIVE_CHECKLIST.get(lang, _CREATIVE_CHECKLIST["en"])
    for i, (task, owner) in enumerate(checklist):
        key = f"mkt_creative_{i}"
        if key not in st.session_state:
            st.session_state[key] = False
        c1, c2 = st.columns([6, 1])
        c1.checkbox(f"{task} — _{owner}_", key=key)
        c2.caption("🎬" if "видео" in task.lower() or "video" in task.lower() else "🖼️")

    st.info(L["creative_langs"])
    _divider()

    # Content pillars
    st.markdown(f'<div class="mkt-eyebrow">{L["content_pillars_title"]}</div>', unsafe_allow_html=True)
    pillars = _CONTENT_PILLARS.get(lang, _CONTENT_PILLARS["en"])
    for title, ideas, icon in pillars:
        with st.expander(f"{icon} {title}"):
            st.write(ideas)
    _wrap_close()


# ============================================================
# SECTION 3.6 — ADMISSIONS FUNNEL & CONVERSION SYSTEM
# ============================================================
_SLA_ITEMS = {
    "ru": [
        ("Reply to inbound lead", "< 5 мин в рабочие часы, < 30 мин вне часов", "#e74c3c"),
        ("Schedule tour", "в течение 24 часов после первого контакта", "#f39c12"),
        ("Pre-tour reminder", "за 1 день и за 2 часа до тура", "#3498db"),
        ("Post-tour follow-up", "в течение 24 часов после тура", "#3498db"),
        ("Deposit nudge", "3 → 7 → 14 дней после тура", "#9b59b6"),
    ],
    "en": [
        ("Reply to inbound lead", "< 5 min business hours, < 30 min off-hours", "#e74c3c"),
        ("Schedule tour", "within 24h after first contact", "#f39c12"),
        ("Pre-tour reminder", "1 day before and 2h before tour", "#3498db"),
        ("Post-tour follow-up", "within 24h after tour", "#3498db"),
        ("Deposit nudge", "3 → 7 → 14 days after tour", "#9b59b6"),
    ],
}

_JOURNEY = {
    "ru": [
        ("Awareness", "Реклама / referral / partnership", "—"),
        ("Interest", "Клик на лендинг, заявка", "TODO"),
        ("First contact", "Ответ ПК (WA / TG / Messenger)", "TODO"),
        ("Tour", "Школьный тур, знакомство с командой", "TODO"),
        ("Application + Test", "Заявка, $20 test fee, $350 registration", "TODO"),
        ("Deposit + Enrollment", "Подтверждение места", "TODO"),
    ],
    "en": [
        ("Awareness", "Ads / referral / partnership", "—"),
        ("Interest", "Landing click, form filled", "TODO"),
        ("First contact", "Admissions reply (WA / TG / Messenger)", "TODO"),
        ("Tour", "School tour, team intro", "TODO"),
        ("Application + Test", "Application, $20 test fee, $350 registration", "TODO"),
        ("Deposit + Enrollment", "Place confirmed", "TODO"),
    ],
}

_OBJECTIONS = {
    "ru": [
        ("«Слишком дорого»",
         "Показать Early Bird + Sibling + Annual: до 25% total. Пример G1-G5: $4,200 → $3,375."),
        ("«Английский ребёнка слабый»",
         "Multilingual Learner Support (Cambridge) $110/мес для G1-G10 — intensive scaffolding."),
        ("«Мы подумаем»",
         "Закрепить Early Bird 15% дедлайн (31 мая). Мягкий follow-up через 3/7/14 дней."),
        ("«А китайских детей много?»",
         "Показать структуру класса, Chinese language programme, cultural integration activities."),
        ("«А кхмерский язык сохраняется?»",
         "Khmer Academic Support $25/мес для G1-G5, 10 уроков/неделю. Khmer program встроен."),
    ],
    "en": [
        ("\"Too expensive\"",
         "Show Early Bird + Sibling + Annual: up to 25% total. G1-G5 example: $4,200 → $3,375."),
        ("\"Child's English is weak\"",
         "Multilingual Learner Support (Cambridge) $110/mo for G1-G10 — intensive scaffolding."),
        ("\"We'll think about it\"",
         "Anchor Early Bird 15% deadline (May 31). Soft follow-up at 3/7/14 days."),
        ("\"How many Chinese kids?\"",
         "Share class composition, Chinese language programme, cultural integration activities."),
        ("\"Is Khmer preserved?\"",
         "Khmer Academic Support $25/mo for G1-G5, 10 lessons/week. Khmer program embedded."),
    ],
}

_SCRIPTS = {
    "ru": {
        "First reply (WA, <5 min)":
            "Здравствуйте! Спасибо за интерес к WISC 🎓\n"
            "Меня зовут {name}, я из приёмной комиссии WISC.\n"
            "Можно уточнить класс ребёнка и удобное время для короткого звонка или школьного тура?\n"
            "Пока пришлю брошюру и виртуальный тур по кампусу 👇\n"
            "TODO: финальный тон — Айжан.",
        "Tour invitation":
            "{parent_name}, приглашаем на школьный тур WISC.\n"
            "Ближайшие слоты: {slot1}, {slot2}, {slot3}.\n"
            "Тур ~45 мин: знакомство с директором, осмотр кампуса (бассейн, labs, library), Q&A.\n"
            "Подтвердите удобный слот — я забронирую.",
        "Post-tour follow-up (≤24h)":
            "{parent_name}, спасибо, что были на туре в WISC ✨\n"
            "Приложил: полную брошюру, календарь учебного года, детальный fee sheet.\n"
            "Early Bird 15% действует до 31 мая — в этом году сэкономите до 25% с sibling + annual.\n"
            "Есть вопросы — пишите, отвечу в течение часа.",
    },
    "en": {
        "First reply (WA, <5 min)":
            "Hello! Thanks for your interest in WISC 🎓\n"
            "I'm {name} from WISC Admissions.\n"
            "Could you share the child's grade and a good time for a quick call or school tour?\n"
            "Sending the brochure and virtual campus tour now 👇\n"
            "TODO: final tone — Aizhan.",
        "Tour invitation":
            "{parent_name}, you're invited for a WISC school tour.\n"
            "Nearest slots: {slot1}, {slot2}, {slot3}.\n"
            "Tour ~45 min: meet Head of School, campus walkthrough (pool, labs, library), Q&A.\n"
            "Confirm a slot and I'll lock it in.",
        "Post-tour follow-up (≤24h)":
            "{parent_name}, thank you for visiting WISC ✨\n"
            "Attached: full brochure, academic calendar, detailed fee sheet.\n"
            "Early Bird 15% runs until May 31 — with sibling + annual you save up to 25% total.\n"
            "Questions — reply any time, I'll get back within an hour.",
    },
}


def _section_admissions(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">⚡ {L["adm_sla"]}</div>', unsafe_allow_html=True)
    sla = _SLA_ITEMS.get(lang, _SLA_ITEMS["en"])
    for title, val, color in sla:
        st.markdown(
            f"""
            <div class="mkt-sla-row" style="--accent:{color};">
                <div class="mkt-sla-label">{title}</div>
                <div class="mkt-sla-value">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _divider()
    st.markdown(f'<div class="mkt-eyebrow">🗺️ {L["adm_journey"]}</div>', unsafe_allow_html=True)
    journey = _JOURNEY.get(lang, _JOURNEY["en"])
    cols = st.columns(len(journey))
    accents = [PALETTE["primary"], PALETTE["warning"], PALETTE["gold"],
               PALETTE["info"], "#9b59b6", PALETTE["success"]]
    for i, (col, step) in enumerate(zip(cols, journey)):
        step_title, step_desc, drop_off = step
        with col:
            st.markdown(
                f"""
                <div class="mkt-journey" style="--accent:{accents[i]};">
                    <div class="mkt-journey-step">STEP {i+1}</div>
                    <div class="mkt-journey-title">{step_title}</div>
                    <div class="mkt-journey-desc">{step_desc}</div>
                    <div class="mkt-meta" style="margin-top:auto;">Drop-off: {drop_off}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    _divider()
    st.markdown(f'<div class="mkt-eyebrow">💬 {L["adm_objections"]}</div>', unsafe_allow_html=True)
    for q, a in _OBJECTIONS.get(lang, _OBJECTIONS["en"]):
        with st.expander(q):
            st.write(a)

    _divider()
    st.markdown(f'<div class="mkt-eyebrow">📝 {L["adm_scripts"]}</div>', unsafe_allow_html=True)
    for title, body in _SCRIPTS.get(lang, _SCRIPTS["en"]).items():
        with st.expander(title):
            st.code(body, language="text")
    _wrap_close()


# ============================================================
# SECTION 3.7 — TEAM & RESPONSIBILITIES (RACI)
# ============================================================
_RACI_COLORS = {
    "R": "#c0392b",   # responsible — primary red
    "A": "#d4a74a",   # accountable — gold
    "C": "#3498db",   # consulted — info blue
    "I": "#556472",   # informed — muted
    "":  "transparent",
}

_MEETINGS = {
    "ru": [
        ("Weekly Commercial Sync", "Кайсар + вся команда", "Лиды, воронка, action plan"),
        ("Weekly Admissions Review", "Кайсар + Айжан + ПК", "Скрипты, follow-up, возражения"),
        ("Biweekly Marketing Review", "Кайсар + Бакир + Жигер + Айжан", "Креативы, каналы, гипотезы"),
        ("Monthly Strategic Review", "Ерболат + Кайсар + Айжан", "Итоги месяца, KPI, стратегия"),
    ],
    "en": [
        ("Weekly Commercial Sync", "Kaisar + full team", "Leads, funnel, action plan"),
        ("Weekly Admissions Review", "Kaisar + Aizhan + Admissions Officer", "Scripts, follow-up, objections"),
        ("Biweekly Marketing Review", "Kaisar + Bakir + Zhiger + Aizhan", "Creatives, channels, hypotheses"),
        ("Monthly Strategic Review", "Yerbolat + Kaisar + Aizhan", "Monthly results, KPIs, strategy"),
    ],
}


def _section_raci(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["raci_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["raci_legend"]}</div>', unsafe_allow_html=True)

    raci_data = _load_json("marketing_raci.json")
    team = raci_data["team"]
    tasks = raci_data["tasks"]

    rows = []
    for t in tasks:
        row = {"Task": t.get(f"task_{lang}", t.get("task_en", t.get("task", "")))}
        for i, p in enumerate(team):
            row[p] = t["raci"][i]
        rows.append(row)
    df = pd.DataFrame(rows)

    def _style_cell(val: str):
        color = _RACI_COLORS.get(val, "transparent")
        if val in ("R", "A", "C", "I"):
            return f"background-color: {color}; color: white; font-weight: 700; text-align: center;"
        return ""

    styled = df.style.map(_style_cell, subset=team)
    st.dataframe(styled, use_container_width=True, hide_index=True, height=min(40 + 36 * len(df), 800))

    _divider()
    st.markdown(f'<div class="mkt-eyebrow">📅 {L["meetings_title"]}</div>', unsafe_allow_html=True)
    for mtg, who, agenda in _MEETINGS.get(lang, _MEETINGS["en"]):
        st.markdown(
            f"""
            <div class="mkt-meeting">
                <div>
                    <div class="mkt-meeting-title">{mtg}</div>
                    <div class="mkt-meeting-agenda">{agenda}</div>
                </div>
                <div class="mkt-meeting-who">{who}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    _wrap_close()


# ============================================================
# SECTION 3.8 — KPI DASHBOARD
# ============================================================
def _section_kpi(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["kpi_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["kpi_help"]}</div>', unsafe_allow_html=True)

    df = _load_csv("marketing_kpi.csv").copy()
    df["week_start"] = pd.to_datetime(df["week_start"])
    df = df.sort_values("week_start")
    has_data = df.drop(columns=["week_start"]).sum().sum() > 0
    if not has_data:
        st.warning(L["kpi_no_data"])

    total_leads = int(df["leads_total"].sum())
    qualified_pct = (df["qualified_leads"].sum() / total_leads * 100) if total_leads else 0
    total_spend = df["ad_spend_usd"].sum()
    avg_cpl = (total_spend / total_leads) if total_leads else 0
    speed_med = df["speed_to_lead_min"].median()

    total_tours_booked = int(df["booked_tours"].sum())
    total_tours_done = int(df["tours_completed"].sum())
    showup_pct = (total_tours_done / total_tours_booked * 100) if total_tours_booked else 0
    total_apps = int(df["applications"].sum())
    tour_app_pct = (total_apps / total_tours_done * 100) if total_tours_done else 0

    total_deps = int(df["deposits"].sum())
    total_enrs = int(df["enrollments"].sum())
    l2e_pct = (total_enrs / total_leads * 100) if total_leads else 0
    cac = (total_spend / total_enrs) if total_enrs else 0
    pacing_pct = (total_enrs / 200 * 100)

    # Top-of-funnel
    st.markdown(f"#### {L['kpi_top_funnel']}")
    r1 = st.columns(4)
    r1[0].metric(L["kpi_total_leads"], f"{total_leads:,}")
    r1[1].metric(L["kpi_qualified_pct"], f"{qualified_pct:.0f}%")
    r1[2].metric(L["kpi_cpl_avg"], f"${avg_cpl:.1f}")
    r1[3].metric(L["kpi_speed_to_lead"], f"{speed_med:.0f} min")

    # Mid-funnel
    st.markdown(f"#### {L['kpi_mid_funnel']}")
    r2 = st.columns(3)
    r2[0].metric(L["kpi_booked_tours"], f"{total_tours_booked:,}")
    r2[1].metric(L["kpi_showup_pct"], f"{showup_pct:.0f}%")
    r2[2].metric(L["kpi_tour_app"], f"{tour_app_pct:.0f}%")

    # Bottom-funnel
    st.markdown(f"#### {L['kpi_bottom_funnel']}")
    r3 = st.columns(5)
    r3[0].metric(L["kpi_apps"], f"{total_apps:,}")
    r3[1].metric(L["kpi_deposits"], f"{total_deps:,}")
    r3[2].metric(L["kpi_enrollments"], f"{total_enrs:,}")
    r3[3].metric(L["kpi_l2e"], f"{l2e_pct:.1f}%")
    r3[4].metric(L["kpi_cac"], f"${cac:,.0f}")

    st.progress(min(pacing_pct / 100, 1.0), text=f"{L['kpi_pacing']}: {total_enrs}/200 ({pacing_pct:.0f}%)")

    _divider()

    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{L['kpi_chart_enrollments']}**")
        weeks = df["week_start"].tolist()
        cum_enr = df["enrollments"].cumsum().tolist()
        # linear target to 200 across the weeks
        n = len(weeks)
        target_line = [round(200 * (i + 1) / n) for i in range(n)] if n else []
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weeks, y=target_line, mode="lines",
                                 name=L["kpi_target_line"],
                                 line=dict(color="#95a5a6", width=2, dash="dash")))
        fig.add_trace(go.Scatter(x=weeks, y=cum_enr, mode="lines+markers",
                                 name=L["kpi_actual_line"],
                                 line=dict(color="#e74c3c", width=3)))
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=20, b=20),
                          xaxis_title="Week", yaxis_title="Cumulative enrollments")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(f"**{L['kpi_chart_by_grade']}**")
        grades = _load_csv("marketing_enrollment_by_grade.csv")
        fig_g = go.Figure()
        fig_g.add_trace(go.Bar(x=grades["grade_band"], y=grades["target_min"],
                               name="Target min", marker_color="#95a5a6"))
        fig_g.add_trace(go.Bar(x=grades["grade_band"], y=grades["current"],
                               name="Current", marker_color="#e74c3c"))
        fig_g.update_layout(barmode="overlay", height=380,
                            margin=dict(l=10, r=10, t=20, b=20),
                            yaxis_title="Students")
        st.plotly_chart(fig_g, use_container_width=True)

    # Current-period funnel
    st.markdown(f"**{L['kpi_chart_funnel_now']}**")
    stage_vals = [total_leads, total_tours_booked, total_tours_done,
                  total_apps, total_deps, total_enrs]
    fig_f = go.Figure(go.Funnel(
        y=L["funnel_stages"],
        x=stage_vals,
        textposition="inside",
        textinfo="value+percent initial",
        marker={"color": ["#e74c3c", "#e67e22", "#f39c12", "#3498db", "#9b59b6", "#2ecc71"]},
    ))
    fig_f.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_f, use_container_width=True)
    _wrap_close()


# ============================================================
# LAUNCH PLAYBOOK — my strategic additions on top of the brief
# ============================================================
_WEEKLY_PLAYBOOK = {
    "ru": [
        ("Недели 1-2 (1-14 мая) — «Flood + measure»",
         "#e74c3c",
         [
             "Daily stand-up 9:00 (30 мин): вчерашние лиды, конверсия, CPL по каналам, что меняем сегодня",
             "Цель: 200+ лидов, 40+ туров, 15+ депозитов",
             "🚨 Red flags: CPL >$25 на Meta / response time >10 мин / tour show-up <60%",
             "A/B тесты каждые 3 дня: выключаем loser'ов, удваиваем winner'ов",
             "💡 Daily lead audit: все лиды >5 мин без ответа — разбор причин (каждый случай)",
         ]),
        ("Недели 3-4 (15-31 мая) — «Double down or pivot»",
         "#e67e22",
         [
             "Удваиваем бюджет на winning creatives, убиваем losers",
             "Early Bird 15% closing push: последние 72 часа — ретаргет всех tour/application без депозита",
             "💡 Referral program launch: «Приведи друга — $200 off» для уже внёсших депозит",
             "💡 Scholarship PR: объявить 2-3 стипендии для high-potential local kids → эмоциональный контент",
             "💡 Competitor switcher кампания: targeting на parents недовольных текущими школами (post-exam period)",
         ]),
        ("Недели 5-8 (Июнь) — «Depth play»",
         "#f39c12",
         [
             "Физический Open Day — 2 события с RSVP (середина и конец месяца)",
             "💡 Corporate B2B outreach: US/UK/AU/KR embassies, ACLEDA, Wing, ADB, WB — пакеты для 3+ семей",
             "💡 Preschool partnerships: $150 за enrolled child — договариваемся с 5-7 feeder школами",
             "Early Bird 10% closing push (последние 72 часа до 30 июня)",
             "Content shift на social proof: testimonials первых семей",
         ]),
        ("Недели 9-12 (Июль) — «Quality seats remaining»",
         "#3498db",
         [
             "💡 Messaging pivot: не «присоединяйся», а «осталось N мест в G1-G5» (scarcity)",
             "💡 Waitlist for popular grades: даже если есть места — создаём ожидание в 1-2 классах (FOMO)",
             "Phone blitz: прозвонить ВСЕ applications без депозита",
             "Летние camps как low-commit entry: попробовать школу 2 недели → вероятность записи ×3",
             "💡 Year-2 retention: продумываем already-now механику re-enrollment discount для текущих семей",
         ]),
        ("Недели 13-17 (Август) — «Last call + onboarding»",
         "#9b59b6",
         [
             "Back-to-school urgency campaign",
             "Финальный push для недозаполненных grade bands (где < min target)",
             "Warm handover enrolled семей → onboarding specialist (uniform, schedule, first-day logistics)",
             "💡 First-week social proof plan: 5 видео-отзывов от семей для Year-2 marketing",
             "Подведение итогов сезона: что сработало / не сработало → план Year-2 через 14 дней после 1 сент.",
         ]),
    ],
    "en": [
        ("Weeks 1-2 (May 1-14) — «Flood + measure»",
         "#e74c3c",
         [
             "Daily stand-up 9:00 (30 min): yesterday's leads, conversion, CPL by channel, what we change today",
             "Goal: 200+ leads, 40+ tours, 15+ deposits",
             "🚨 Red flags: CPL >$25 on Meta / response time >10 min / tour show-up <60%",
             "A/B tests every 3 days: kill losers, double winners",
             "💡 Daily lead audit: any lead >5 min unanswered — root-cause each one",
         ]),
        ("Weeks 3-4 (May 15-31) — «Double down or pivot»",
         "#e67e22",
         [
             "Double budget on winning creatives, kill losers",
             "Early Bird 15% closing push: last 72h — retarget all tours/applications without deposit",
             "💡 Referral program launch: «Bring a friend — $200 off» for families with deposit",
             "💡 Scholarship PR: announce 2-3 full scholarships for high-potential local kids → emotional content",
             "💡 Competitor switcher campaign: target parents unhappy with current school (post-exam period)",
         ]),
        ("Weeks 5-8 (June) — «Depth play»",
         "#f39c12",
         [
             "Physical Open Day — 2 events with RSVP (mid and end of month)",
             "💡 Corporate B2B outreach: US/UK/AU/KR embassies, ACLEDA, Wing, ADB, WB — packages for 3+ families",
             "💡 Preschool partnerships: $150 per enrolled child — deals with 5-7 feeder schools",
             "Early Bird 10% closing push (last 72h before June 30)",
             "Content shift to social proof: testimonials from first families",
         ]),
        ("Weeks 9-12 (July) — «Quality seats remaining»",
         "#3498db",
         [
             "💡 Messaging pivot: not «join us» but «N seats left in G1-G5» (scarcity)",
             "💡 Waitlist for popular grades: create waitlist in 1-2 classes even if seats remain (FOMO)",
             "Phone blitz: call ALL applications without deposit",
             "Summer camps as low-commit entry: try school for 2 weeks → enrollment probability ×3",
             "💡 Year-2 retention: design re-enrollment discount mechanic NOW for existing families",
         ]),
        ("Weeks 13-17 (August) — «Last call + onboarding»",
         "#9b59b6",
         [
             "Back-to-school urgency campaign",
             "Final push for under-filled grade bands (< min target)",
             "Warm handover: enrolled families → onboarding specialist (uniform, schedule, first-day logistics)",
             "💡 First-week social proof plan: 5 family testimonial videos for Year-2 marketing",
             "Season retrospective: what worked / didn't → Year-2 plan within 14 days of Sep 1",
         ]),
    ],
}

_GROWTH_HACKS = {
    "ru": [
        ("Waitlist scarcity (без реальных waitlist'ов)",
         "Даже если все места свободны — показываем «G3: 2 места», «G7: waitlist». FOMO поднимает конверсию tour→application на 15-25%. Важно: не врать о количестве, но работать с доступными местами по классу."),
        ("Scholarship PR play — 2-3 полные стипендии",
         "Выделить $12K-18K (3× tuition) на full scholarships для high-potential local kids. Это одновременно: (1) эмоциональная PR-история в местных СМИ, (2) контент для соц. сетей, (3) реальный impact, (4) justification для $4K fee богатым семьям («мы инвестируем в Cambodia»)."),
        ("Competitor-switcher hunt",
         "Target ads на parents со interests «BELTEI», «Paragon», «CIA First» + keyword triggers «change school», «transfer». Окно возможности — июнь (после exam results семьи недовольны и сравнивают)."),
        ("B2B corporate packages",
         "Outreach к 10 embassies + 10 крупных KH/международных компаний (ACLEDA, Wing, ABA, ADB, WB). Пакет: -10% при 3+ семьях + dedicated HR contact. Одно embassy может дать 5-10 enrollments."),
        ("Preschool partnerships (feeder program)",
         "Договор с 5-7 kindergartens/preschools: $150 referral per enrolled child. Это легально в KH (в отличие от некоторых стран). 5 schools × 5 детей × 12 месяцев = 60-100 лидов в год без рекламы."),
        ("Year-1 retention thinking — СЕЙЧАС, не в апреле 2027",
         "LTV/CAC модель ломается если retention < 85%. Механика уже на стадии onboarding: (1) re-enrollment discount для Year 2 объявляется в ноябре, (2) «родительский совет» из 5-7 активных семей в первый семестр, (3) individual check-in с каждой семьёй в конце Year 1."),
        ("Paid ambassadors вместо influencers",
         "Вместо дорогих бьюти-блогеров — 3-5 mom-ambassadors из реальных parent communities ($300-500/мес + бесплатное обучение sibling'а). Authentic reach > paid reach в Камбодже."),
        ("Khmer New Year / Chinese New Year контент-календарь",
         "Заранее spланирован контент на Pchum Ben, Khmer NY, Chinese NY — не просто поздравления, а demonstration of cultural competence (fluent Khmer teachers, Chinese language program). Hook для skeptical parents."),
        ("Lead scoring + tiered SLA",
         "Не все лиды равны. Hot (WA ответ <1h + P0 grade): tour в 24 часа, A-player обрабатывает. Warm: tour в 48 часов. Cold: email drip и мониторинг. Повышает conversion и снижает burnout."),
        ("Tour experience design как продукт",
         "Не просто «показываем школу», а сценарий: (1) greeter с именем ребёнка на табличке, (2) первая комната — самая wow-worthy (бассейн или robotics lab), (3) снэки для детей пока говорим с родителями, (4) 5-минутная встреча с Head of School, (5) goodie bag с брошюрой + written quote на Early Bird. Конверсия tour→application поднимается с 35% до 50%+."),
    ],
    "en": [
        ("Waitlist scarcity (without actual waitlists)",
         "Even with all seats open — show «G3: 2 spots left», «G7: waitlist». FOMO lifts tour→application conversion by 15-25%. Don't lie about counts — work with per-class availability."),
        ("Scholarship PR play — 2-3 full scholarships",
         "Allocate $12K-18K (3× tuition) for full scholarships for high-potential local kids. This gives you: (1) emotional PR story in local media, (2) social content, (3) real impact, (4) justification for $4K fee to wealthy families («we invest in Cambodia»)."),
        ("Competitor-switcher hunt",
         "Target ads on parents with interests «BELTEI», «Paragon», «CIA First» + keyword triggers «change school», «transfer». Opportunity window — June (post-exam families are unhappy and comparing)."),
        ("B2B corporate packages",
         "Outreach to 10 embassies + 10 large KH/intl companies (ACLEDA, Wing, ABA, ADB, WB). Package: -10% for 3+ families + dedicated HR contact. One embassy can deliver 5-10 enrollments."),
        ("Preschool partnerships (feeder program)",
         "Deals with 5-7 kindergartens/preschools: $150 referral per enrolled child. Legal in Cambodia (unlike some countries). 5 schools × 5 kids × 12 months = 60-100 leads/year without ads."),
        ("Year-1 retention thinking — NOW, not April 2027",
         "LTV/CAC breaks if retention < 85%. Mechanics in the onboarding stage: (1) Year-2 re-enrollment discount announced in November, (2) «parent council» of 5-7 active families in first semester, (3) individual check-in at end of Year 1."),
        ("Paid ambassadors over influencers",
         "Instead of pricey beauty bloggers — 3-5 mom-ambassadors from real parent communities ($300-500/mo + free sibling spot). Authentic reach > paid reach in Cambodia."),
        ("Cultural calendar content plan",
         "Pre-planned content for Pchum Ben, Khmer NY, Chinese NY — not just greetings but demonstration of cultural competence (fluent Khmer teachers, Chinese program). Hook for skeptical parents."),
        ("Lead scoring + tiered SLA",
         "Not all leads are equal. Hot (WA reply <1h + P0 grade): tour within 24h, A-player handles. Warm: tour within 48h. Cold: email drip + monitor. Lifts conversion, reduces burnout."),
        ("Tour experience as a product",
         "Not just «show the school» but a script: (1) greeter with child's name on a sign, (2) first room — most wow-worthy (pool or robotics lab), (3) snacks for kids while parents talk, (4) 5-min meeting with Head of School, (5) goodie bag with brochure + written Early Bird quote. Tour→application lifts from 35% to 50%+."),
    ],
}

_RISK_REGISTER = {
    "ru": [
        ("MoEYS licensing задержка", "Low", "Критический", "Проверить статус НА ЭТОЙ НЕДЕЛЕ, иметь копию лицензии готовой к демонстрации родителям"),
        ("Meta account ban / ad review reject", "Medium", "High", "Настроить 2 Business Manager'а параллельно, запасной FB page, сразу запустить Google + TikTok — не зависим от одного канала"),
        ("CPL в 2× выше плана на 1-й неделе", "High", "Medium", "Weekly budget review, готовы shift в cheap каналы (Telegram/WeChat/referral), усиление партнёрств"),
        ("Head of School недоступен для туров/контента", "Low", "High", "Backup speaker (Academic Lead), заранее записать 10+ интервью/видео"),
        ("Admissions Officer burnout (один человек на 200+ лидов)", "Medium", "High", "Шеринг нагрузки: Айжан covers 20%, Кайсар overflow в часы пик, hire 2-го ПК на 2-й неделе если лиды >50/день"),
        ("Competitor price war (EWIS/Paragon режут fees)", "Medium", "Medium", "Не входим в ценовую гонку — усиливаем differentiation (trilingual, Cambridge pathway, infrastructure)"),
        ("Currency / macro shock (USD fees vs KHR income)", "Low", "Medium", "Гибкие payment plans (term × 3), local bank transfer, sibling + annual stack"),
        ("Утечка персональных данных родителей", "Low", "Критический", "GDPR-like privacy policy на лендинге, SSL, CRM access control, no sharing с третьими сторонами"),
        ("Negative review / PR incident на старте", "Medium", "High", "Response protocol: владелец — Ерболат, reply в 2 часа, transparent, monitoring Google Reviews / FB / Khmer forums"),
        ("Tours срывается (no-show) >40%", "Medium", "Medium", "SMS/WA reminder за 1 день и 2 часа, incentive за явку (gift for child), reconfirm за 24 часа"),
    ],
    "en": [
        ("MoEYS licensing delay", "Low", "Critical", "Confirm status THIS WEEK, have license copy ready to show parents"),
        ("Meta account ban / ad review reject", "Medium", "High", "Set up 2 Business Managers in parallel, backup FB page, launch Google + TikTok immediately — no single-channel dependency"),
        ("CPL 2× over plan in week 1", "High", "Medium", "Weekly budget review, ready to shift to cheap channels (Telegram/WeChat/referral), partnerships boost"),
        ("Head of School unavailable for tours/content", "Low", "High", "Backup speaker (Academic Lead), pre-record 10+ interviews/videos"),
        ("Admissions Officer burnout (solo on 200+ leads)", "Medium", "High", "Share load: Aizhan covers 20%, Kaisar overflow during peak, hire 2nd PK in week 2 if leads >50/day"),
        ("Competitor price war (EWIS/Paragon cut fees)", "Medium", "Medium", "Don't enter price race — strengthen differentiation (trilingual, Cambridge pathway, infrastructure)"),
        ("Currency / macro shock (USD fees vs KHR income)", "Low", "Medium", "Flexible payment plans (term × 3), local bank transfer, sibling + annual stack"),
        ("Parent data leak", "Low", "Critical", "GDPR-like privacy policy on landing, SSL, CRM access control, no third-party sharing"),
        ("Negative review / PR incident at launch", "Medium", "High", "Response protocol: owner — Yerbolat, reply in 2h, transparent, monitor Google Reviews / FB / Khmer forums"),
        ("Tour no-shows >40%", "Medium", "Medium", "SMS/WA reminder 1 day + 2h before, show-up incentive (kid gift), reconfirm 24h before"),
    ],
}


def _section_launch_playbook(L: dict, lang: str):
    _wrap_open()
    st.markdown(f'<div class="mkt-eyebrow">{L["lp_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mkt-section-intro">{L["lp_subtitle"]}</div>', unsafe_allow_html=True)

    lp_sub_tabs = st.tabs(L["lp_tabs"])

    # --- 8-day Sprint ---
    with lp_sub_tabs[0]:
        data = _load_json("marketing_launch_sprint.json")["days"]
        today = date.today()

        total_items = sum(len(d["items"]) for d in data)
        done_items = sum(
            1 for d in data for it in d["items"]
            if st.session_state.get(f"mkt_lp_{it['id']}", False)
        )
        pct = int(done_items / total_items * 100) if total_items else 0
        # Nice progress header
        st.markdown(
            f"""
            <div class="mkt-card mkt-card--accent-red" style="margin-bottom:14px;">
                <div class="mkt-card-head">
                    <div class="mkt-card-title">{L['lp_progress']}</div>
                    <span class="mkt-chip mkt-chip--red">{done_items} / {total_items} · {pct}%</span>
                </div>
                <div style="background:{PALETTE['border_strong']};border-radius:6px;height:8px;overflow:hidden;margin-top:8px;">
                    <div style="background:{PALETTE['primary']};width:{pct}%;height:100%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for d in data:
            day_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
            days_left = _days_between(day_date, today)
            is_today = day_date == today
            day_done = sum(1 for it in d["items"]
                           if st.session_state.get(f"mkt_lp_{it['id']}", False))
            day_total = len(d["items"])
            days_text = (f"{days_left} {L['days_left']}" if days_left > 0
                         else (L['lp_today'] if days_left == 0 else L['overdue']))

            theme = d.get(f"theme_{lang}", d.get("theme_en", "—"))
            header = (f"{d['day_label']} · {d['date']} · "
                      f"{theme} · {day_done}/{day_total} · {days_text}")

            with st.expander(header, expanded=is_today):
                for it in d["items"]:
                    key = f"mkt_lp_{it['id']}"
                    if key not in st.session_state:
                        st.session_state[key] = False
                    label = it.get(f"task_{lang}", it.get("task_en", it.get("task", "")))
                    if it.get("bonus"):
                        label = f"{L['lp_bonus_marker']} {label}"
                    label = f"{label}  _— {it['owner']}_"
                    st.checkbox(label, key=key)

    # --- Weekly Playbook ---
    with lp_sub_tabs[1]:
        st.markdown(f'<div class="mkt-eyebrow">{L["lp_weekly_title"]}</div>', unsafe_allow_html=True)
        for title, color, bullets in _WEEKLY_PLAYBOOK.get(lang, _WEEKLY_PLAYBOOK["en"]):
            with st.expander(title, expanded=False):
                for b in bullets:
                    st.markdown(f"- {b}")

    # --- Growth Hacks ---
    with lp_sub_tabs[2]:
        st.markdown(f'<div class="mkt-eyebrow">{L["lp_hacks_title"]}</div>', unsafe_allow_html=True)
        for title, body in _GROWTH_HACKS.get(lang, _GROWTH_HACKS["en"]):
            with st.expander(f"💡 {title}"):
                st.write(body)

    # --- Risk Register ---
    with lp_sub_tabs[3]:
        st.markdown(f'<div class="mkt-eyebrow">{L["lp_risks_title"]}</div>', unsafe_allow_html=True)
        rows = _RISK_REGISTER.get(lang, _RISK_REGISTER["en"])
        df = pd.DataFrame(rows, columns=[
            L["lp_risk_event"], L["lp_risk_prob"], L["lp_risk_impact"], L["lp_risk_mitigation"]
        ])

        def _style_risk(row):
            prob = row[L["lp_risk_prob"]]
            impact = row[L["lp_risk_impact"]]
            critical = {"Critical", "Критический"}
            high = {"High"}
            if impact in critical or (impact in high and prob == "High"):
                color = PALETTE["primary"]
            elif impact in high or prob == "High":
                color = PALETTE["warning"]
            else:
                color = "#7f8c8d"
            return [f"background-color: {color}; color: white;" if c in (L["lp_risk_prob"], L["lp_risk_impact"]) else "" for c in row.index]

        styled = df.style.apply(_style_risk, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True,
                     height=min(40 + 36 * len(df), 600))

    _wrap_close()


# ============================================================
# SECTION — TRANSLATOR (marketing creative/ad-copy helper)
# ============================================================
def _section_marketing_translator(L: dict, lang: str):
    st.markdown(
        '<div class="mkt-eyebrow">✍️ Переводчик — пиши на RU, получай EN + KM автоматически</div>'
        if lang == "ru" else
        '<div class="mkt-eyebrow">✍️ Translator — write in RU, get EN + KM auto</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mkt-section-intro">Для креативов, заголовков рекламы, описаний постов. '
        'Через Google Translate (требует интернет). Кхмерский — черновой, Айжан финализирует.</div>'
        if lang == "ru" else
        '<div class="mkt-section-intro">For creatives, ad headlines, post descriptions. '
        'Via Google Translate (internet required). Khmer is draft — Aizhan will finalize.</div>',
        unsafe_allow_html=True,
    )

    source_text = st.text_area(
        "Source text / Исходный текст",
        value=st.session_state.get("mkt_tr_source", ""),
        height=160,
        key="mkt_tr_source",
        placeholder=(
            "Ранняя запись до 31 мая — скидка 15%! 🌟\n"
            "Международная программа Cambridge, трёхязычная среда, full-day 8:00–16:00."
        ),
    )

    if source_text and source_text.strip():
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**🇬🇧 English (auto)**")
            with st.spinner(""):
                en = translate_text(source_text, target="en", source="auto")
            st.code(en, language="text")
        with c2:
            st.markdown("**🇰🇭 Khmer (черновой · [AIJAN-REVIEW])**")
            with st.spinner(""):
                km = translate_text(source_text, target="km", source="auto")
            st.code(km, language="text")


# ============================================================
# ROUTER
# ============================================================
_MKT_VERSION = "v2 · polished"


def render(lang: str = "ru"):
    _inject_styles()
    L = _get_lang(MKT_LANG, lang)

    _brand_header(
        tagline_ru="МАРКЕТИНГОВАЯ СТРАТЕГИЯ · AY 2026-2027",
        tagline_en="MARKETING STRATEGY · AY 2026-2027",
        tagline_km="យុទ្ធសាស្ត្រទីផ្សារ · AY 2026-2027",
        lang=lang,
    )

    st.markdown(
        f"""
        <h2 style="display:inline-block;margin-bottom:6px;color:{PALETTE['text']};font-size:26px;">
            {L["header"]}
            <span class="mkt-v-badge">{_MKT_VERSION}</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )
    st.caption(L["subheader"])

    sub_tabs = st.tabs(L["sections"])

    with sub_tabs[0]:
        _section_overview(L, lang)
    with sub_tabs[1]:
        _section_launch_playbook(L, lang)
    with sub_tabs[2]:
        _section_audience(L, lang)
    with sub_tabs[3]:
        _section_funnel(L, lang)
    with sub_tabs[4]:
        _section_channels(L, lang)
    with sub_tabs[5]:
        _section_creative(L, lang)
    with sub_tabs[6]:
        _section_admissions(L, lang)
    with sub_tabs[7]:
        _section_raci(L, lang)
    with sub_tabs[8]:
        _section_kpi(L, lang)
    with sub_tabs[9]:
        _section_marketing_translator(L, lang)
