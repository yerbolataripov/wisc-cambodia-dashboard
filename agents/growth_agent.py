"""Agent 3: Growth — enrollment forecasting and capacity planning."""
import pandas as pd
import numpy as np
from models.financial_model import FinancialModel


class GrowthAgent:
    def __init__(self, model: FinancialModel = None):
        self.model = model or FinancialModel()

    def calculate(self, scenario="base"):
        enrollment = self.model.get_enrollment_by_year(scenario)
        max_cap = self.model.school["max_capacity"]
        n = self.model._n_years()
        years = list(range(1, n + 1))

        utilization = [s / max_cap for s in enrollment]

        yoy_growth = [0]
        for i in range(1, len(enrollment)):
            yoy_growth.append(enrollment[i] - enrollment[i - 1])

        retention = self.model.enrollment["retention_rate"]
        new_students_needed = [enrollment[0]]
        for i in range(1, len(enrollment)):
            retained = int(enrollment[i - 1] * retention)
            needed = enrollment[i] - retained
            new_students_needed.append(max(needed, 0))

        years_to_full = None
        for i, s in enumerate(enrollment):
            if s >= max_cap:
                years_to_full = i + 1
                break

        return {
            "years": years,
            "enrollment": enrollment,
            "utilization": utilization,
            "yoy_growth": yoy_growth,
            "new_students_needed": new_students_needed,
            "max_capacity": max_cap,
            "years_to_full_capacity": years_to_full,
            "retention_rate": retention,
            "summary": pd.DataFrame({
                "Year": years,
                "Students": enrollment,
                "Utilization (%)": [f"{u:.0%}" for u in utilization],
                "New Students": new_students_needed,
                "YoY Growth": yoy_growth
            })
        }

    def capacity_forecast(self, scenario="base"):
        data = self.calculate(scenario)
        return {"years_to_full": data["years_to_full_capacity"],
                "enrollment_extended": data["enrollment"]}
