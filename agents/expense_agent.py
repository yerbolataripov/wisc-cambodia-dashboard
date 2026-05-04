"""Agent 2: Expenses — cost structure (from annual expense arrays, matching spreadsheet)."""
import pandas as pd
from models.financial_model import FinancialModel


class ExpenseAgent:
    def __init__(self, model: FinancialModel = None):
        self.model = model or FinancialModel()

    def calculate(self, scenario="base"):
        enrollment = self.model.get_enrollment_by_year(scenario)
        expenses = self.model.calculate_annual_expenses(scenario)
        n = self.model._n_years()
        years = list(range(1, n + 1))

        categories = ["teachers_salary", "admin_salary", "salary_taxes",
                       "building_maintenance", "operating_expenses",
                       "marketing", "jsm_fee"]

        breakdown = {cat: [e[cat] for e in expenses] for cat in categories}
        totals = [e["total"] for e in expenses]
        cost_per_student = [t / s if s > 0 else 0 for t, s in zip(totals, enrollment)]

        # Map internal keys to display-friendly keys for dashboard cat_labels
        key_map = {
            "teachers_salary": "teacher_cost",
            "admin_salary": "admin_cost",
            "salary_taxes": "salary_taxes",
            "building_maintenance": "building",
            "operating_expenses": "operating",
            "marketing": "marketing",
            "jsm_fee": "jsm_fee",
        }
        breakdown_display = {key_map[k]: v for k, v in breakdown.items()}

        summary_data = {
            "Year": years,
            "Students": enrollment,
            "Total ($)": [f"{t:,.0f}" for t in totals],
            "Teachers ($)": [f"{b:,.0f}" for b in breakdown["teachers_salary"]],
            "Admin ($)": [f"{b:,.0f}" for b in breakdown["admin_salary"]],
            "Taxes ($)": [f"{b:,.0f}" for b in breakdown["salary_taxes"]],
            "Building ($)": [f"{b:,.0f}" for b in breakdown["building_maintenance"]],
            "Operating ($)": [f"{b:,.0f}" for b in breakdown["operating_expenses"]],
            "Marketing ($)": [f"{b:,.0f}" for b in breakdown["marketing"]],
            "JSM Fee ($)": [f"{b:,.0f}" for b in breakdown["jsm_fee"]],
            "Cost/Student ($)": [f"{c:,.0f}" for c in cost_per_student]
        }

        return {
            "years": years,
            "totals": totals,
            "breakdown": breakdown_display,
            "cost_per_student": cost_per_student,
            "total_expenses": sum(totals),
            "total_5yr_expenses": sum(totals[:5]),
            "summary": pd.DataFrame(summary_data)
        }

    def expense_structure(self, year=0, scenario="base"):
        """Expense structure for a given year as percentages."""
        expenses = self.model.calculate_annual_expenses(scenario)[year]
        total = expenses["total"]
        if total == 0:
            return {}
        key_map = {
            "teachers_salary": "teacher_cost",
            "admin_salary": "admin_cost",
            "salary_taxes": "salary_taxes",
            "building_maintenance": "building",
            "operating_expenses": "operating",
            "marketing": "marketing",
            "jsm_fee": "jsm_fee",
        }
        return {key_map[k]: v / total for k, v in expenses.items()
                if k in key_map}
