"""Agent 4: Risk — scenario analysis and sensitivity testing."""
import pandas as pd
import numpy as np
from models.financial_model import FinancialModel


class RiskAgent:
    def __init__(self, model: FinancialModel = None):
        self.model = model or FinancialModel()

    def calculate(self):
        scenarios = {}
        for name in ["optimistic", "base", "pessimistic"]:
            pnl = self.model.calculate_pnl(name)
            npv = self.model.calculate_npv(name)
            roi = self.model.calculate_roi(name)
            bep_year = self.model.calculate_breakeven_year(name)
            bep_students = self.model.calculate_breakeven_students(name)

            scenarios[name] = {
                "pnl": pnl,
                "npv": npv,
                "roi": roi,
                "breakeven_year": bep_year,
                "breakeven_students": bep_students,
                "total_revenue": pnl["revenue"].sum(),
                "total_expenses": pnl["expenses"].sum(),
                "total_profit": pnl["profit"].sum(),
                "final_margin": pnl.iloc[-1]["margin"]
            }
        return scenarios

    def sensitivity_analysis(self, variable="tuition_per_year", range_pct=0.3, steps=7):
        original = self.model.revenue_params.get(variable)
        if original is None:
            return pd.DataFrame()
        results = []
        for mult in np.linspace(1 - range_pct, 1 + range_pct, steps):
            self.model.revenue_params[variable] = original * mult
            npv = self.model.calculate_npv("base")
            pnl = self.model.calculate_pnl("base")
            results.append({
                "variable": variable,
                "multiplier": mult,
                "value": original * mult,
                "npv": npv,
                "total_profit": pnl["profit"].sum(),
                "breakeven_year": self.model.calculate_breakeven_year("base")
            })
        self.model.revenue_params[variable] = original
        return pd.DataFrame(results)

    def stress_test(self):
        tests = []
        # Test 1: Low enrollment
        orig = self.model.assumptions["scenarios"]["pessimistic"]["enrollment_multiplier"]
        self.model.assumptions["scenarios"]["pessimistic"]["enrollment_multiplier"] = 0.65
        pnl = self.model.calculate_pnl("pessimistic")
        tests.append({
            "scenario": "Severe downturn",
            "description": "65% enrollment target",
            "total_profit": pnl["profit"].sum(),
            "npv": self.model.calculate_npv("pessimistic"),
            "breakeven": self.model.calculate_breakeven_year("pessimistic")
        })
        self.model.assumptions["scenarios"]["pessimistic"]["enrollment_multiplier"] = orig

        # Test 2: Delayed start
        orig_students = list(self.model.enrollment["year_students"])
        self.model.enrollment["year_students"] = [int(s * 0.5) for s in orig_students]
        pnl = self.model.calculate_pnl("base")
        tests.append({
            "scenario": "Delayed start",
            "description": "50% of enrollment target",
            "total_profit": pnl["profit"].sum(),
            "npv": self.model.calculate_npv("base"),
            "breakeven": self.model.calculate_breakeven_year("base")
        })
        self.model.enrollment["year_students"] = orig_students

        # Test 3: No JSM fee removal (continues paying 10%)
        orig_jsm = self.model.expenses["jsm_fee_years"]
        self.model.expenses["jsm_fee_years"] = 10
        pnl = self.model.calculate_pnl("base")
        tests.append({
            "scenario": "JSM fee 10 years",
            "description": "JSM fee continues full 10 years",
            "total_profit": pnl["profit"].sum(),
            "npv": self.model.calculate_npv("base"),
            "breakeven": self.model.calculate_breakeven_year("base")
        })
        self.model.expenses["jsm_fee_years"] = orig_jsm

        return pd.DataFrame(tests)

    def scenario_comparison_table(self):
        scenarios = self.calculate()
        rows = []
        for name, data in scenarios.items():
            rows.append({
                "Scenario": name.capitalize(),
                "Total Revenue": f"${data['total_revenue']:,.0f}",
                "Total Expenses": f"${data['total_expenses']:,.0f}",
                "Total Profit": f"${data['total_profit']:,.0f}",
                "NPV": f"${data['npv']:,.0f}",
                "ROI": f"{data['roi']:.1%}",
                "Breakeven Year": data["breakeven_year"] or "N/A",
                "Final Margin": f"{data['final_margin']:.1%}"
            })
        return pd.DataFrame(rows)
