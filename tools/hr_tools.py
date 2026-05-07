"""
hr_tools.py — Custom CrewAI tools for HRAgent.

Each tool wraps a discrete HR data operation. Agents call these
tools like functions; CrewAI serialises arguments automatically.
"""

import csv
import json
from pathlib import Path
from typing import Optional

from crewai.tools import tool

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_employees() -> list[dict]:
    """Read employees.csv and return list of dicts."""
    path = DATA_DIR / "employees.csv"
    with path.open() as f:
        return list(csv.DictReader(f))


# ─────────────────────────────────────────────
# Tool 1: Flight-risk scorer
# ─────────────────────────────────────────────

@tool("flight_risk_tool")
def flight_risk_tool(threshold: str = "medium") -> str:
    """
    Identifies employees at risk of leaving based on tenure,
    manager changes, flag_leaves, and performance scores.

    Args:
        threshold: Filter level — 'high', 'medium', or 'all'.
                   Defaults to 'medium' (returns high + medium risks).

    Returns:
        JSON string of at-risk employees with risk factors.
    """
    employees = _load_employees()
    levels = {"high": ["high"], "medium": ["high", "medium"], "all": ["high", "medium", "low"]}
    target = levels.get(threshold, ["high", "medium"])

    at_risk = []
    for emp in employees:
        if emp["attrition_risk"] not in target:
            continue
        risk_factors = []
        if float(emp["tenure_years"]) < 2:
            risk_factors.append("short tenure (<2 yrs)")
        if int(emp["manager_changes"]) >= 2:
            risk_factors.append(f"{emp['manager_changes']} manager changes")
        if int(emp["flag_leaves"]) >= 2:
            risk_factors.append(f"{emp['flag_leaves']} leave flags")
        if float(emp["performance_score"]) < 3.0:
            risk_factors.append(f"low perf score ({emp['performance_score']})")

        at_risk.append({
            "id": emp["employee_id"],
            "name": emp["name"],
            "department": emp["department"],
            "tenure_years": emp["tenure_years"],
            "attrition_risk": emp["attrition_risk"],
            "risk_factors": risk_factors,
        })

    return json.dumps({"threshold": threshold, "count": len(at_risk), "employees": at_risk}, indent=2)


# ─────────────────────────────────────────────
# Tool 2: Performance trend analyser
# ─────────────────────────────────────────────

@tool("performance_trend_tool")
def performance_trend_tool(department: Optional[str] = None) -> str:
    """
    Analyses performance scores and promotion lag across the workforce.
    Highlights departments with declining or stagnant performers.

    Args:
        department: Optional department filter. If omitted, analyses all.

    Returns:
        JSON string with department-level performance stats.
    """
    employees = _load_employees()

    dept_data: dict[str, list] = {}
    for emp in employees:
        dept = emp["department"]
        if department and dept != department:
            continue
        dept_data.setdefault(dept, []).append(emp)

    summary = []
    for dept, members in dept_data.items():
        scores = [float(m["performance_score"]) for m in members]
        promo_lag = [float(m["last_promotion_years"]) for m in members]
        avg_score = round(sum(scores) / len(scores), 2)
        avg_promo = round(sum(promo_lag) / len(promo_lag), 2)
        low_performers = [m["name"] for m in members if float(m["performance_score"]) < 3.0]
        summary.append({
            "department": dept,
            "headcount": len(members),
            "avg_performance_score": avg_score,
            "avg_years_since_promotion": avg_promo,
            "low_performers": low_performers,
            "flag": "at risk" if avg_score < 3.5 or avg_promo > 2 else "healthy",
        })

    return json.dumps({"departments": summary}, indent=2)


# ─────────────────────────────────────────────
# Tool 3: Attrition rate calculator
# ─────────────────────────────────────────────

@tool("attrition_rate_tool")
def attrition_rate_tool(period: str = "Q3") -> str:
    """
    Calculates current attrition rate and projects headcount gap
    for a given planning period, broken down by department.

    Args:
        period: Planning horizon label, e.g. 'Q3', 'Q4', 'H1'.

    Returns:
        JSON string with attrition rates and projected hiring needs.
    """
    employees = _load_employees()
    total = len(employees)

    dept_counts: dict[str, dict] = {}
    for emp in employees:
        dept = emp["department"]
        dept_counts.setdefault(dept, {"total": 0, "high_risk": 0, "medium_risk": 0})
        dept_counts[dept]["total"] += 1
        if emp["attrition_risk"] == "high":
            dept_counts[dept]["high_risk"] += 1
        elif emp["attrition_risk"] == "medium":
            dept_counts[dept]["medium_risk"] += 1

    results = []
    total_hires_needed = 0
    for dept, counts in dept_counts.items():
        projected_exits = counts["high_risk"] + round(counts["medium_risk"] * 0.4)
        attrition_rate = round((projected_exits / counts["total"]) * 100, 1)
        hires_needed = projected_exits + max(0, round(counts["total"] * 0.05))  # 5% growth buffer
        total_hires_needed += hires_needed
        results.append({
            "department": dept,
            "current_headcount": counts["total"],
            "projected_exits": projected_exits,
            "attrition_rate_pct": attrition_rate,
            "hires_needed_for_period": hires_needed,
        })

    return json.dumps({
        "period": period,
        "total_employees": total,
        "total_hires_needed": total_hires_needed,
        "by_department": results,
    }, indent=2)


# ─────────────────────────────────────────────
# Tool 4: Report formatter
# ─────────────────────────────────────────────

@tool("format_report_tool")
def format_report_tool(content: str) -> str:
    """
    Formats a structured markdown HR report and saves it to outputs/hr_report.md.

    Args:
        content: Full markdown body of the report generated by the report writer.

    Returns:
        File path of the saved report.
    """
    output_dir = Path(__file__).parent.parent / "outputs"
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "hr_report.md"

    full_report = f"# HR Intelligence Report\n\n{content}\n"
    output_path.write_text(full_report)

    return str(output_path)
