"""
Core Financial Model for WISC Cambodia
10-year projection aligned with owner's spreadsheet data
Includes: teacher/admin salaries, salary taxes, building maintenance,
operating expenses, marketing, JSM fee, enrollment fees, partnership split
"""
import json
import numpy as np
import pandas as pd
from pathlib import Path


def load_assumptions(path=None):
    if path is None:
        path = Path(__file__).parent.parent / "data" / "assumptions.json"
    with open(path) as f:
        return json.load(f)


class FinancialModel:
    def __init__(self, assumptions=None):
        self.assumptions = assumptions or load_assumptions()
        self.enrollment = self.assumptions["enrollment"]
        self.expenses = self.assumptions["expenses"]
        self.revenue_params = self.assumptions["revenue"]
        self.financial = self.assumptions["financial"]
        self.school = self.assumptions["school"]

    def _n_years(self):
        return self.school["projection_years"]

    def get_enrollment_by_year(self, scenario="base"):
        mult = self.assumptions["scenarios"][scenario]["enrollment_multiplier"]
        max_cap = self.school["max_capacity"]
        base = self.enrollment["year_students"]
        result = []
        for y in range(self._n_years()):
            if y < len(base):
                s = int(base[y] * mult)
            else:
                s = int(base[-1] * mult)
            result.append(min(s, max_cap))
        return result

    def get_enrollment_monthly_year1(self, scenario="base"):
        """Not used directly anymore — see calculate_monthly_year1."""
        return self.get_enrollment_by_year(scenario)[0]

    def _get_annual_value(self, values_list, year, scenario="base"):
        """Get value from a per-year list, with scenario multiplier for expenses."""
        exp_mult = self.assumptions["scenarios"][scenario]["expense_multiplier"]
        if year < len(values_list):
            return values_list[year] * exp_mult
        return values_list[-1] * exp_mult

    def calculate_annual_revenue(self, scenario="base"):
        """Annual revenue per academic year (tuition + enrollment fee)."""
        enrollment = self.get_enrollment_by_year(scenario)
        tuition_base = self.revenue_params["tuition_per_year"]
        tuition_growth = self.revenue_params.get("tuition_growth_rate", 0)
        enroll_fee = self.revenue_params.get("enrollment_fee_per_student", 0)
        revenues = []
        for y, students in enumerate(enrollment):
            tuition_rate = tuition_base * ((1 + tuition_growth) ** y)
            tuition_rev = students * tuition_rate
            enrollment_rev = students * enroll_fee
            revenues.append(tuition_rev + enrollment_rev)
        return revenues

    def calculate_annual_expenses(self, scenario="base"):
        enrollment = self.get_enrollment_by_year(scenario)
        n = self._n_years()
        yearly = []

        for y in range(n):
            students = enrollment[y]

            teacher_salary = self._get_annual_value(
                self.expenses["teacher_salary_annual"], y, scenario)
            admin_salary = self._get_annual_value(
                self.expenses["admin_salary_annual"], y, scenario)

            # Salary taxes
            gross_salaries = teacher_salary + admin_salary
            salary_taxes = gross_salaries * self.expenses["salary_tax_pct"]

            building = self._get_annual_value(
                self.expenses["building_maintenance_annual"], y, scenario)
            operating = self._get_annual_value(
                self.expenses["operating_expenses_annual"], y, scenario)
            marketing = self._get_annual_value(
                self.expenses["marketing_annual"], y, scenario)

            # JSM fee: % of revenue, first N years only
            jsm_fee = 0
            if y < self.expenses.get("jsm_fee_years", 0):
                tuition_base = self.revenue_params["tuition_per_year"]
                tuition_growth = self.revenue_params.get("tuition_growth_rate", 0)
                enroll_fee = self.revenue_params.get("enrollment_fee_per_student", 0)
                tuition_rate = tuition_base * ((1 + tuition_growth) ** y)
                revenue_y = students * tuition_rate + students * enroll_fee
                jsm_fee = revenue_y * self.expenses.get("jsm_fee_pct", 0)

            total = (teacher_salary + admin_salary + salary_taxes +
                     building + operating + marketing + jsm_fee)

            yearly.append({
                "total": total,
                "teachers_salary": teacher_salary,
                "admin_salary": admin_salary,
                "salary_taxes": salary_taxes,
                "building_maintenance": building,
                "operating_expenses": operating,
                "marketing": marketing,
                "jsm_fee": jsm_fee,
                "students": students
            })
        return yearly

    def calculate_monthly_year1(self, scenario="base"):
        """Wrapper — returns full monthly table for all years in horizon."""
        return self.calculate_monthly_all(scenario)

    def calculate_monthly_all(self, scenario="base"):
        """
        Помесячный расчёт на весь горизонт планирования.

        Каждый учебный год (цикл 15 мес. для Года 1, 12 мес. для последующих):

        === ЦИКЛ УЧЕБНОГО ГОДА N ===
        Май-Июль:   НАБОР — маркетинг + сбор вступительных взносов
        Авг-Май:    УЧЁБА (10 мес.) — плата, ЗП, все расходы
        Июн-Июль:  КАНИКУЛЫ — ЗП платится, доходов нет

        Год 1:  Май 2026 — Июль 2027  (набор → учёба → каникулы)
        Год 2:  Май 2027 — Июль 2028  (набор → учёба → каникулы)
        ...и т.д.

        Набор года N+1 (май-июль) перекрывается с учёбой/каникулами года N.
        В таблице они НЕ дублируются — каждый месяц показан один раз
        с суммой всех доходов/расходов за этот месяц.
        """
        n_years = self._n_years()
        all_expenses = self.calculate_annual_expenses(scenario)
        enrollment = self.get_enrollment_by_year(scenario)
        tuition_base = self.revenue_params["tuition_per_year"]
        tuition_growth = self.revenue_params.get("tuition_growth_rate", 0)
        enroll_fee = self.revenue_params.get("enrollment_fee_per_student", 0)
        jsm_pct = self.expenses.get("jsm_fee_pct", 0)
        jsm_years = self.expenses.get("jsm_fee_years", 0)
        teaching_months = 10

        MONTH_NAMES_RU = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
                          "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]

        # Build calendar: May 2026 through July (2026 + n_years)
        # Year 1 starts May 2026, last year ends July (2026 + n_years)
        start_year = 2026
        start_month = 5  # May (1-indexed)

        # Total months: from May 2026 to July (2026+n_years)
        # = (n_years * 12) + 3  for the initial May-Jul + n_years full academic cycles
        # Actually: Year 1 = May'26-Jul'27 (15), Year 2 = overlap, adds Aug'27-Jul'28 (12)
        # Simpler: generate May 2026 to Jul (2026+n_years), each month once
        end_year = start_year + n_years
        end_month = 7  # July

        # Generate all months
        months_list = []
        cy, cm = start_year, start_month
        while (cy < end_year) or (cy == end_year and cm <= end_month):
            months_list.append((cy, cm))
            cm += 1
            if cm > 12:
                cm = 1
                cy += 1

        # For each month, find ALL active academic year periods.
        # May-Jul can overlap: teaching/vacation of year N + enrollment of year N+1.
        # We sum all revenue/expenses from overlapping periods into one row.
        def get_all_periods(year, month):
            """Returns list of (academic_year_index, period_type) for a month."""
            results = []
            for ay in range(n_years):
                ay_start = start_year + ay
                if year == ay_start and 5 <= month <= 7:
                    results.append((ay, "enrollment"))
                if year == ay_start and 8 <= month <= 12:
                    results.append((ay, "teaching"))
                if year == ay_start + 1 and 1 <= month <= 5:
                    results.append((ay, "teaching"))
                if year == ay_start + 1 and 6 <= month <= 7:
                    results.append((ay, "vacation"))
            return results

        period_labels = {"enrollment": "Набор", "teaching": "Учёба", "vacation": "Каникулы"}
        rows = []
        cumulative = 0

        for cy, cm in months_list:
            month_label = f"{MONTH_NAMES_RU[cm-1]} {cy}"
            periods = get_all_periods(cy, cm)

            if not periods:
                continue

            # Aggregate all periods for this calendar month
            tuition_rev = 0
            enroll_rev = 0
            teacher_cost = 0
            admin_cost = 0
            building = 0
            operating = 0
            marketing = 0
            salary_taxes = 0
            jsm_fee = 0
            students = 0
            period_names = []
            primary_ay = periods[0][0]  # for display

            for ay, ptype in periods:
                ay_idx = min(ay, len(all_expenses) - 1)
                exp = all_expenses[ay_idx]
                st_target = enrollment[min(ay, len(enrollment) - 1)]
                t_rate = tuition_base * ((1 + tuition_growth) ** ay)

                if ptype == "enrollment":
                    # Набор: взносы + маркетинг
                    enroll_rev += st_target * enroll_fee / 3
                    marketing += exp["marketing"] / 3
                    period_names.append(f"{period_labels[ptype]} (Г{ay+1})")

                elif ptype == "teaching":
                    # Учёба: плата + полные расходы
                    tuition_rev += st_target * t_rate / teaching_months
                    teacher_cost += exp["teachers_salary"] / 12
                    admin_cost += exp["admin_salary"] / 12
                    building += exp["building_maintenance"] / 12
                    operating += exp["operating_expenses"] / 12
                    students = st_target
                    primary_ay = ay
                    period_names.append(f"{period_labels[ptype]} (Г{ay+1})")

                elif ptype == "vacation":
                    # Каникулы: ЗП платится, доходов нет
                    teacher_cost += exp["teachers_salary"] / 12
                    admin_cost += exp["admin_salary"] / 12
                    building += exp["building_maintenance"] / 12
                    operating += exp["operating_expenses"] / 12
                    period_names.append(f"{period_labels[ptype]} (Г{ay+1})")

            # Налоги: 5% от всего ФОТ за месяц
            salary_taxes = (teacher_cost + admin_cost) * self.expenses["salary_tax_pct"]

            # JSM fee: 10% от платы за обучение
            if tuition_rev > 0 and primary_ay < jsm_years:
                jsm_fee = tuition_rev * jsm_pct

            total_revenue = tuition_rev + enroll_rev
            total_expense = (teacher_cost + admin_cost + salary_taxes +
                             building + operating + marketing + jsm_fee)
            profit = total_revenue - total_expense
            cumulative += profit

            rows.append({
                "month": len(rows) + 1,
                "month_name": month_label,
                "academic_year": primary_ay + 1,
                "period": " + ".join(period_names),
                "students": students,
                "tuition_revenue": tuition_rev,
                "enrollment_fee_revenue": enroll_rev,
                "total_revenue": total_revenue,
                "teacher_cost": teacher_cost,
                "admin_cost": admin_cost,
                "salary_taxes": salary_taxes,
                "building": building,
                "operating": operating,
                "marketing": marketing,
                "jsm_fee": jsm_fee,
                "total_expenses": total_expense,
                "profit": profit,
                "cumulative_profit": cumulative,
            })
        return pd.DataFrame(rows)

    def calculate_pnl(self, scenario="base"):
        """Annual P&L per academic year (matches owner's spreadsheet structure)."""
        revenue = self.calculate_annual_revenue(scenario)
        expenses = self.calculate_annual_expenses(scenario)
        years = list(range(1, self._n_years() + 1))

        rows = []
        cumulative_profit = 0
        for y, (rev, exp) in enumerate(zip(revenue, expenses)):
            profit = rev - exp["total"]
            cumulative_profit += profit
            rows.append({
                "year": years[y],
                "students": self.get_enrollment_by_year(scenario)[y],
                "revenue": rev,
                "expenses": exp["total"],
                "profit": profit,
                "margin": profit / rev if rev > 0 else 0,
                "cumulative_profit": cumulative_profit
            })
        return pd.DataFrame(rows)

    def calculate_npv(self, scenario="base"):
        pnl = self.calculate_pnl(scenario)
        rate = self.financial["discount_rate"]
        cash_flows = pnl["profit"].tolist()
        return sum(cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows))

    def calculate_roi(self, scenario="base"):
        pnl = self.calculate_pnl(scenario)
        total_investment = pnl.iloc[0]["expenses"]
        total_profit = pnl["profit"].sum()
        return total_profit / total_investment if total_investment > 0 else 0

    def calculate_breakeven_year(self, scenario="base"):
        pnl = self.calculate_pnl(scenario)
        for _, row in pnl.iterrows():
            if row["cumulative_profit"] >= 0:
                return int(row["year"])
        return None

    def calculate_breakeven_students(self, scenario="base"):
        """Approximate breakeven student count for Year 1."""
        exp_y1 = self.calculate_annual_expenses(scenario)[0]
        tuition = self.revenue_params["tuition_per_year"]
        enroll_fee = self.revenue_params.get("enrollment_fee_per_student", 0)
        rev_per_student = tuition + enroll_fee

        # Fixed costs (don't change much with students)
        fixed = exp_y1["building_maintenance"] + exp_y1["operating_expenses"]
        # Semi-fixed (admin doesn't change much in Y1)
        fixed += exp_y1["admin_salary"]

        # Variable per student approximation
        students_y1 = self.get_enrollment_by_year(scenario)[0]
        variable_total = exp_y1["total"] - fixed
        variable_per_student = variable_total / students_y1 if students_y1 > 0 else 0

        if rev_per_student <= variable_per_student:
            return None
        return int(np.ceil(fixed / (rev_per_student - variable_per_student)))

    def calculate_partnership(self, scenario="base"):
        """Calculate partnership profit split (Option #2)."""
        pnl = self.calculate_pnl(scenario)
        partner = self.assumptions.get("partnership", {})
        phase1_split = partner.get("phase1_split_sorphea", 1.0)
        phase2_split = partner.get("phase2_split", 0.5)

        rows = []
        investment_returned = False
        cumulative_sorphea = 0

        for _, row in pnl.iterrows():
            profit = row["profit"]
            if not investment_returned and row["cumulative_profit"] < 0:
                # Phase 1: Sorphea gets 100%
                sorphea = profit * phase1_split
                jsm = profit * (1 - phase1_split)
            else:
                if not investment_returned:
                    investment_returned = True
                # Phase 2: 50/50
                sorphea = profit * phase2_split
                jsm = profit * phase2_split

            cumulative_sorphea += sorphea
            rows.append({
                "year": int(row["year"]),
                "profit": profit,
                "sorphea_share": sorphea,
                "jsm_share": jsm,
                "phase": "Payback" if not investment_returned else "50/50",
                "cumulative_sorphea": cumulative_sorphea
            })
        return pd.DataFrame(rows)

    # Legacy compatibility methods
    def get_teachers_needed(self, students):
        spt = 25
        return max(int(np.ceil(students / spt)), 1)

    def get_admin_costs_monthly(self, students=None):
        y = 0
        return self.expenses["admin_salary_annual"][y] / 12

    def get_admin_staff_scaled(self, students):
        return {"admin_team": {"count": 1, "salary": self.get_admin_costs_monthly(students)}}

    def get_overhead_monthly(self):
        return self.expenses["operating_expenses_annual"][0] / 12
