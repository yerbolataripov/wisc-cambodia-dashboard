"""Agent 1: Revenue — tuition forecasting and revenue analysis."""
import pandas as pd
from models.financial_model import FinancialModel


class RevenueAgent:
    def __init__(self, model: FinancialModel = None):
        self.model = model or FinancialModel()

    def calculate(self, scenario="base"):
        enrollment = self.model.get_enrollment_by_year(scenario)
        revenues = self.model.calculate_annual_revenue(scenario)
        n = self.model._n_years()
        years = list(range(1, n + 1))

        tuition_base = self.model.revenue_params["tuition_per_year"]
        enroll_fee = self.model.revenue_params.get("enrollment_fee_per_student", 0)

        growth_rates = [0]
        for i in range(1, len(revenues)):
            rate = (revenues[i] - revenues[i - 1]) / revenues[i - 1] if revenues[i - 1] else 0
            growth_rates.append(rate)

        return {
            "years": years,
            "enrollment": enrollment,
            "annual_revenue": revenues,
            "growth_rates": growth_rates,
            "total_revenue": sum(revenues),
            "avg_annual_revenue": sum(revenues) / len(revenues),
            "monthly_tuition": tuition_base / 12,
            "enrollment_fee": enroll_fee,
            "summary": pd.DataFrame({
                "Year": years,
                "Students": enrollment,
                "Revenue ($)": revenues,
                "Growth (%)": [f"{r:.1%}" for r in growth_rates],
            })
        }

    def monthly_breakdown(self, scenario="base"):
        return self.model.calculate_monthly_year1(scenario)[
            ["month", "students", "revenue"]
        ]
