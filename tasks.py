"""
tasks.py — CrewAI task definitions for HRAgent.

Tasks wire an agent to a concrete deliverable. The expected_output
field is used by CrewAI to validate and route results between tasks.
"""

from crewai import Task


def build_tasks(agents: dict, query: str) -> list[Task]:
    """
    Build the task pipeline for a given user query.

    Tasks are ordered so that each feeds into the next:
      1. Flight-risk analysis
      2. Performance trend analysis
      3. Hiring plan (depends on attrition numbers)
      4. Report synthesis (depends on all three above)
    """

    flight_risk_task = Task(
        description=(
            f"The user asked: '{query}'\n\n"
            "Use the flight_risk_tool to identify employees at medium or high "
            "attrition risk. For each flagged employee, list their key risk factors "
            "(short tenure, manager churn, leave flags, low performance). "
            "Group findings by department and note which department has the "
            "most concentrated risk."
        ),
        expected_output=(
            "A structured list of at-risk employees grouped by department, "
            "with risk factors and an overall department risk rating."
        ),
        agent=agents["attrition_analyst"],
    )

    performance_task = Task(
        description=(
            f"The user asked: '{query}'\n\n"
            "Use the performance_trend_tool to analyse performance scores and "
            "promotion lag across all departments. Flag any department with an "
            "average performance score below 3.5 or average promotion lag above "
            "2 years. Identify individual low performers and note whether they "
            "also appear in the flight-risk list."
        ),
        expected_output=(
            "A department-level performance summary table with avg score, "
            "avg promotion lag, and a health flag (healthy / at risk). "
            "Call out any individual employees who are both low-performers "
            "and flight risks."
        ),
        agent=agents["performance_analyst"],
    )

    hiring_plan_task = Task(
        description=(
            f"The user asked: '{query}'\n\n"
            "Use the attrition_rate_tool for Q3 to calculate projected exits "
            "and required hires per department. Include the 5% growth buffer. "
            "Prioritise departments by hiring urgency (highest attrition rate first). "
            "Estimate whether each department's hiring need is a backfill, "
            "a growth hire, or both."
        ),
        expected_output=(
            "A Q3 hiring plan table: department | current headcount | "
            "projected exits | hires needed | hire type. "
            "Plus a total hires-needed figure and a top-3 urgent departments list."
        ),
        agent=agents["hiring_planner"],
        context=[flight_risk_task],
    )

    report_task = Task(
        description=(
            f"The user asked: '{query}'\n\n"
            "Synthesise the outputs from the attrition analyst, performance analyst, "
            "and hiring planner into a single executive HR intelligence report. "
            "Structure it as follows:\n"
            "1. TL;DR (3 bullets, max 20 words each)\n"
            "2. Flight-risk summary with named employees and risk factors\n"
            "3. Performance health by department\n"
            "4. Q3 hiring plan table\n"
            "5. Recommended actions (prioritised, owner-assignable, 30-day horizon)\n\n"
            "Use the format_report_tool to save the final markdown to disk."
        ),
        expected_output=(
            "A saved markdown file path and a full preview of the HR report "
            "covering flight risks, performance trends, hiring plan, and actions."
        ),
        agent=agents["report_writer"],
        context=[flight_risk_task, performance_task, hiring_plan_task],
    )

    return [flight_risk_task, performance_task, hiring_plan_task, report_task]
