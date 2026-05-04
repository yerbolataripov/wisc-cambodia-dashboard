# WISC Cambodia — Financial & Strategy Dashboard

Streamlit dashboard for **World International School Cambodia**: 5-year financial model, marketing strategy, and sales playbooks. Bilingual (RU / EN / KM).

## Run locally

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
```

App will be available at <http://localhost:8501>.

## Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Open <https://share.streamlit.io/> and connect the repo.
3. Set the entry point to `dashboard/app.py` and Python 3.11.
4. Deploy — no secrets required.

## What's inside

- `dashboard/app.py` — main entry point, sidebar params + 8 tabs.
- `dashboard/marketing_tab.py` — marketing strategy section.
- `dashboard/sales_tab.py` — sales section (response playbook, scripts, objections, tour, training, KPIs).
- `models/financial_model.py` — 5-year P&L, NPV, ROI, payback.
- `agents/` — revenue / expense / growth / risk agents.
- `data/*.json` + `data/*.csv` — editable content (scripts, objections, tour playbook, training modules…). All RU/EN/KM blocks can be edited from the UI with auto-translate via Google Translate (`deep-translator`, no API key).
- `exports/` — Power BI exports.

## Editable content (RU / EN / KM auto-translate)

Inside the **Strategy of Sales** tab you can edit and auto-translate:

- Response Playbook → off-hours auto-reply
- Message Scripts (12 scripts)
- Objections Matrix (15 objections, objection text + answer)
- Campus Tour Playbook (6 phases + "what never to do")
- Admissions Officer Training (10 modules: title, goal, theory, exercises)

Each editor: **3 textareas → pick source language → auto-translate → Save**. Saves go straight to `data/*.json`.
