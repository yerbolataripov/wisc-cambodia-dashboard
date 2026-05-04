"""
Power BI Export Module
Exports financial model data to Power BI-ready formats:
- Excel (.xlsx) with multiple sheets for Power BI import
- CSV files for Power BI dataflows
- DAX measures reference
"""
import json
import os
from pathlib import Path
import pandas as pd
import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.financial_model import FinancialModel
from agents.revenue_agent import RevenueAgent
from agents.expense_agent import ExpenseAgent
from agents.growth_agent import GrowthAgent
from agents.risk_agent import RiskAgent


class PowerBIExporter:
    """Exports all financial model data in Power BI-optimized format."""

    def __init__(self, model: FinancialModel = None):
        self.model = model or FinancialModel()
        self.revenue_agent = RevenueAgent(self.model)
        self.expense_agent = ExpenseAgent(self.model)
        self.growth_agent = GrowthAgent(self.model)
        self.risk_agent = RiskAgent(self.model)

    def _build_pnl_table(self):
        """Fact table: Annual P&L for all scenarios."""
        rows = []
        for scenario in ["optimistic", "base", "pessimistic"]:
            pnl = self.model.calculate_pnl(scenario)
            for _, row in pnl.iterrows():
                rows.append({
                    "Scenario": scenario.capitalize(),
                    "Year": int(row["year"]),
                    "Students": int(row["students"]),
                    "Revenue": round(row["revenue"], 2),
                    "Expenses": round(row["expenses"], 2),
                    "Profit": round(row["profit"], 2),
                    "Margin": round(row["margin"], 4),
                    "Cumulative_Profit": round(row["cumulative_profit"], 2)
                })
        return pd.DataFrame(rows)

    def _build_monthly_table(self):
        """Fact table: Monthly data for Year 1, all scenarios."""
        rows = []
        for scenario in ["optimistic", "base", "pessimistic"]:
            monthly = self.model.calculate_monthly_year1(scenario)
            for _, row in monthly.iterrows():
                rows.append({
                    "Scenario": scenario.capitalize(),
                    "Month": int(row["month"]),
                    "Students": int(row["students"]),
                    "Tuition_Revenue": round(row.get("tuition_revenue", 0), 2),
                    "Enrollment_Fee": round(row.get("enrollment_fee_revenue", 0), 2),
                    "Total_Revenue": round(row.get("total_revenue", 0), 2),
                    "Teacher_Cost": round(row.get("teacher_cost", 0), 2),
                    "Admin_Cost": round(row.get("admin_cost", 0), 2),
                    "Salary_Taxes": round(row.get("salary_taxes", 0), 2),
                    "Building": round(row.get("building", 0), 2),
                    "Operating": round(row.get("operating", 0), 2),
                    "Marketing": round(row.get("marketing", 0), 2),
                    "JSM_Fee": round(row.get("jsm_fee", 0), 2),
                    "Total_Expenses": round(row.get("total_expenses", 0), 2),
                    "Profit": round(row.get("profit", 0), 2),
                })
        return pd.DataFrame(rows)

    def _build_expense_breakdown_table(self):
        """Fact table: Expense breakdown by category and year."""
        rows = []
        for scenario in ["optimistic", "base", "pessimistic"]:
            expenses = self.model.calculate_annual_expenses(scenario)
            enrollment = self.model.get_enrollment_by_year(scenario)
            for y, (exp, students) in enumerate(zip(expenses, enrollment)):
                for category, value in exp.items():
                    if category in ("total", "students"):
                        continue
                    rows.append({
                        "Scenario": scenario.capitalize(),
                        "Year": y + 1,
                        "Students": students,
                        "Category": category.replace("_", " ").title(),
                        "Amount": round(value, 2)
                    })
        return pd.DataFrame(rows)

    def _build_staffing_table(self):
        """Dimension table: Staffing plan by year."""
        rows = []
        for scenario in ["optimistic", "base", "pessimistic"]:
            enrollment = self.model.get_enrollment_by_year(scenario)
            for y, students in enumerate(enrollment):
                teachers = self.model.get_teachers_needed(students)
                rows.append({
                    "Scenario": scenario.capitalize(),
                    "Year": y + 1,
                    "Students": students,
                    "Teachers": teachers,
                    "Student_Teacher_Ratio": round(students / teachers, 1) if teachers else 0
                })
        return pd.DataFrame(rows)

    def _build_kpi_table(self):
        """KPI summary table for Power BI cards."""
        rows = []
        for scenario in ["optimistic", "base", "pessimistic"]:
            pnl = self.model.calculate_pnl(scenario)
            rows.append({
                "Scenario": scenario.capitalize(),
                "Total_Revenue_5Y": round(pnl["revenue"].sum(), 2),
                "Total_Expenses_5Y": round(pnl["expenses"].sum(), 2),
                "Total_Profit_5Y": round(pnl["profit"].sum(), 2),
                "NPV": round(self.model.calculate_npv(scenario), 2),
                "ROI": round(self.model.calculate_roi(scenario), 4),
                "Breakeven_Year": self.model.calculate_breakeven_year(scenario),
                "Breakeven_Students": self.model.calculate_breakeven_students(scenario),
                "Final_Year_Margin": round(pnl.iloc[-1]["margin"], 4),
                "Max_Capacity": self.model.school["max_capacity"],
                "Y1_Students": int(pnl.iloc[0]["students"]),
                "Y5_Students": int(pnl.iloc[-1]["students"])
            })
        return pd.DataFrame(rows)

    def _build_sensitivity_table(self):
        """Sensitivity analysis data for Power BI."""
        variables = ["tuition_per_year", "enrollment_fee_per_student"]
        all_rows = []
        for var in variables:
            try:
                sens = self.risk_agent.sensitivity_analysis(var, 0.3, 9)
                for _, row in sens.iterrows():
                    all_rows.append({
                        "Variable": var.replace("_", " ").title(),
                        "Multiplier": round(row["multiplier"], 2),
                        "Value": round(row["value"], 2),
                        "NPV": round(row["npv"], 2),
                        "Total_Profit": round(row["total_profit"], 2),
                        "Breakeven_Year": row["breakeven_year"]
                    })
            except (KeyError, Exception):
                continue
        return pd.DataFrame(all_rows)

    def _build_growth_table(self):
        """Growth and capacity utilization table."""
        rows = []
        for scenario in ["optimistic", "base", "pessimistic"]:
            growth = self.growth_agent.calculate(scenario)
            for i in range(len(growth["years"])):
                rows.append({
                    "Scenario": scenario.capitalize(),
                    "Year": growth["years"][i],
                    "Students": growth["enrollment"][i],
                    "Utilization": round(growth["utilization"][i], 4),
                    "New_Students_Needed": growth["new_students_needed"][i],
                    "YoY_Growth": growth["yoy_growth"][i],
                    "Max_Capacity": growth["max_capacity"]
                })
        return pd.DataFrame(rows)

    def _build_calendar_dim(self):
        """Calendar dimension table for Power BI date relationships."""
        rows = []
        for year in range(1, 6):
            for month in range(1, 13):
                rows.append({
                    "Year": year,
                    "Month": month,
                    "Month_Name": pd.Timestamp(2026, month, 1).strftime("%B"),
                    "Quarter": f"Q{(month - 1) // 3 + 1}",
                    "Period": f"Y{year}M{month:02d}",
                    "Is_School_Year": month not in [7, 8]  # Jul-Aug summer break
                })
        return pd.DataFrame(rows)

    def export_excel(self, output_path=None):
        """Export all tables to a single Excel file for Power BI."""
        if output_path is None:
            output_path = Path(__file__).parent.parent / "exports" / "powerbi_data.xlsx"

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        tables = {
            "PnL_Annual": self._build_pnl_table(),
            "Monthly_Year1": self._build_monthly_table(),
            "Expense_Breakdown": self._build_expense_breakdown_table(),
            "Staffing": self._build_staffing_table(),
            "KPI_Summary": self._build_kpi_table(),
            "Sensitivity": self._build_sensitivity_table(),
            "Growth": self._build_growth_table(),
            "Calendar": self._build_calendar_dim(),
        }

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet_name, df in tables.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        return output_path, tables

    def export_csv(self, output_dir=None):
        """Export all tables as separate CSV files for Power BI dataflows."""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "exports" / "csv"

        os.makedirs(output_dir, exist_ok=True)

        tables = {
            "pnl_annual": self._build_pnl_table(),
            "monthly_year1": self._build_monthly_table(),
            "expense_breakdown": self._build_expense_breakdown_table(),
            "staffing": self._build_staffing_table(),
            "kpi_summary": self._build_kpi_table(),
            "sensitivity": self._build_sensitivity_table(),
            "growth": self._build_growth_table(),
            "calendar": self._build_calendar_dim(),
        }

        paths = {}
        for name, df in tables.items():
            path = Path(output_dir) / f"{name}.csv"
            df.to_csv(path, index=False)
            paths[name] = str(path)

        return paths

    def get_dax_measures(self):
        """Return recommended DAX measures for Power BI."""
        return """
-- ============================================
-- DAX Measures for Cambodia School Financial Model
-- Import these into Power BI Desktop
-- ============================================

-- REVENUE MEASURES
Total Revenue = SUM(PnL_Annual[Revenue])
Total Expenses = SUM(PnL_Annual[Expenses])
Total Profit = SUM(PnL_Annual[Profit])
Profit Margin = DIVIDE([Total Profit], [Total Revenue], 0)

-- YoY Revenue Growth
Revenue YoY Growth =
VAR CurrentYear = MAX(PnL_Annual[Year])
VAR CurrentRevenue = CALCULATE([Total Revenue], PnL_Annual[Year] = CurrentYear)
VAR PriorRevenue = CALCULATE([Total Revenue], PnL_Annual[Year] = CurrentYear - 1)
RETURN DIVIDE(CurrentRevenue - PriorRevenue, PriorRevenue, 0)

-- ENROLLMENT MEASURES
Total Students = MAX(PnL_Annual[Students])
Capacity Utilization = DIVIDE(MAX(PnL_Annual[Students]), MAX(Growth[Max_Capacity]), 0)

-- COST MEASURES
Cost Per Student = DIVIDE([Total Expenses], [Total Students], 0)
Revenue Per Student = DIVIDE([Total Revenue], [Total Students], 0)

-- KPI CARDS
NPV = MAX(KPI_Summary[NPV])
ROI = MAX(KPI_Summary[ROI])
Breakeven Year = MIN(KPI_Summary[Breakeven_Year])

-- STAFFING
Student Teacher Ratio = DIVIDE(MAX(Staffing[Students]), MAX(Staffing[Teachers]), 0)
Total Staff = MAX(Staffing[Total_Staff])

-- CONDITIONAL FORMATTING
Profit Color =
IF([Total Profit] > 0, "#2ecc71", "#e74c3c")

Margin Color =
IF([Profit Margin] > 0.5, "#2ecc71",
IF([Profit Margin] > 0.2, "#f39c12", "#e74c3c"))

-- SCENARIO COMPARISON
Base Profit = CALCULATE([Total Profit], PnL_Annual[Scenario] = "Base")
Optimistic Profit = CALCULATE([Total Profit], PnL_Annual[Scenario] = "Optimistic")
Pessimistic Profit = CALCULATE([Total Profit], PnL_Annual[Scenario] = "Pessimistic")
Profit Range = [Optimistic Profit] - [Pessimistic Profit]
"""

    def get_powerbi_setup_guide(self):
        """Return Power BI setup instructions."""
        return """
=== POWER BI SETUP GUIDE ===

1. IMPORT DATA:
   - Open Power BI Desktop
   - Get Data > Excel > select "powerbi_data.xlsx"
   - Select ALL sheets > Load

2. DATA MODEL (Relationships):
   PnL_Annual[Year] → Calendar[Year] (Many-to-One)
   PnL_Annual[Scenario] → KPI_Summary[Scenario] (Many-to-One)
   Monthly_Year1[Month] → Calendar[Month] (Many-to-One)
   Expense_Breakdown[Year] → Calendar[Year] (Many-to-One)
   Growth[Year] → Calendar[Year] (Many-to-One)
   Staffing[Year] → Calendar[Year] (Many-to-One)

3. RECOMMENDED VISUALS:

   Page 1 — Executive Overview:
   - KPI Cards: Revenue, Profit, NPV, ROI, Breakeven
   - Clustered Bar: Revenue vs Expenses by Year
   - Line Chart: Cumulative Profit by Scenario
   - Donut Chart: Expense Structure Y1

   Page 2 — Revenue Deep Dive:
   - Waterfall: Revenue growth by year
   - Line: Revenue by Scenario
   - Matrix: Revenue breakdown table
   - Gauge: Capacity utilization

   Page 3 — Cost Analysis:
   - Stacked Bar: Expenses by Category
   - Table: Staffing Plan
   - Treemap: Cost structure
   - KPI: Cost per Student trend

   Page 4 — Risk & Scenarios:
   - Line Chart: 3 scenarios comparison
   - Scatter: Sensitivity analysis
   - Table: Stress test results
   - Slicer: Scenario filter

4. THEME (optional — paste in View > Themes > Custom):
   {
     "name": "Cambodia School",
     "dataColors": [
       "#2ecc71", "#e74c3c", "#3498db",
       "#9b59b6", "#f39c12", "#1abc9c",
       "#e67e22", "#95a5a6"
     ]
   }
"""


def main():
    """Generate all Power BI export files."""
    exporter = PowerBIExporter()

    print("Exporting Power BI data...")

    # Excel
    xlsx_path, tables = exporter.export_excel()
    print(f"\nExcel: {xlsx_path}")
    for name, df in tables.items():
        print(f"  - {name}: {len(df)} rows x {len(df.columns)} cols")

    # CSV
    csv_paths = exporter.export_csv()
    print(f"\nCSV files:")
    for name, path in csv_paths.items():
        print(f"  - {path}")

    # DAX
    dax_path = Path(__file__).parent.parent / "exports" / "dax_measures.dax"
    with open(dax_path, "w") as f:
        f.write(exporter.get_dax_measures())
    print(f"\nDAX measures: {dax_path}")

    # Guide
    guide_path = Path(__file__).parent.parent / "exports" / "powerbi_setup_guide.txt"
    with open(guide_path, "w") as f:
        f.write(exporter.get_powerbi_setup_guide())
    print(f"Setup guide: {guide_path}")

    print("\nDone! Import powerbi_data.xlsx into Power BI Desktop.")


if __name__ == "__main__":
    main()
