# HRAgent — Agentic AI System for HR Intelligence

> **"Which employees are flight risks?"** → HRAgent answers with a full flight-risk report, department performance analysis, and a Q3 hiring plan. In one command.

Built with [CrewAI](https://github.com/joaomdmoura/crewai). Four specialised agents collaborate, each using purpose-built tools, to transform raw HR data into an executive-ready intelligence report.

---

## What it does

You ask a natural language HR question. HRAgent decomposes it, routes sub-tasks to the right agents, runs each analysis in sequence (passing context downstream), and synthesises a structured markdown report.

**Example queries**

```
"Which employees are flight risks based on tenure and performance trends?"
"Draft a hiring plan for Q3 given our current attrition rate."
"Which departments have the most stagnant performers and what's the headcount impact?"
```

---

## Architecture

```
User query
    │
    ▼
Orchestrator Agent          ← routes, delegates, synthesises
    │
    ├── Attrition Analyst   ← flight_risk_tool       (tenure + manager churn signals)
    ├── Performance Analyst ← performance_trend_tool  (score trends + promotion lag)
    ├── Hiring Planner      ← attrition_rate_tool     (projected exits → hires needed)
    └── Report Writer       ← format_report_tool      (saves markdown to outputs/)
```

Each agent is isolated — it only sees the tools and context it needs. The `report_writer` receives the outputs of all three analyst tasks as context before synthesising.

---

## Project structure

```
hragent/
├── crew.py               # Entry point — builds and kicks off the crew
├── agents.py             # Agent definitions (role, goal, backstory, tools)
├── tasks.py              # Task definitions (description, expected_output, context)
├── tools/
│   └── hr_tools.py       # Four @tool-decorated functions (CrewAI tool API)
├── data/
│   └── employees.csv     # Sample HR dataset (15 employees, 12 features)
├── outputs/
│   └── hr_report.md      # Generated report (created at runtime)
├── requirements.txt
└── .env.example
```

---

## Quickstart

```bash
# 1. Clone and enter
git clone https://github.com/YOUR_USERNAME/hragent.git
cd hragent

# 2. Create virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your OpenAI key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 5. Run with the default query
python crew.py

# Or ask your own question
python crew.py --query "Which departments are at highest hiring risk in Q3?"
```

The report is printed to stdout and saved to `outputs/hr_report.md`.

---

## The tools

| Tool | Purpose | Input |
|------|---------|-------|
| `flight_risk_tool` | Scores employees by attrition risk using tenure, manager changes, leave flags, and performance | `threshold`: high / medium / all |
| `performance_trend_tool` | Aggregates performance scores and promotion lag by department | `department`: optional filter |
| `attrition_rate_tool` | Calculates projected exits and hires needed per department for a planning period | `period`: Q3, Q4, H1 |
| `format_report_tool` | Formats and saves the final markdown report to disk | `content`, `title` |

All tools are decorated with `@tool` from `crewai.tools` and are fully typed. Swap the CSV for a real HRIS API (Workday, BambooHR) by replacing `_load_employees()` in `hr_tools.py`.

---

## Extending HRAgent

**Swap the LLM** — replace `ChatOpenAI` in `crew.py` with any LangChain-compatible model (Anthropic, Mistral, local Ollama).

**Add real data** — replace `_load_employees()` in `hr_tools.py` with a call to your HRIS API or a SQL query. The rest of the system is data-source agnostic.

**Add agents** — create a new `Agent` in `agents.py`, a new `@tool` in `hr_tools.py`, and a new `Task` in `tasks.py`. Add it to the `context` list of any downstream task.

**Add memory** — set `memory=True` in `crew.py` to enable CrewAI's built-in cross-run memory, so the crew learns from previous reports.

---

## Sample output (truncated)

```
# HR Intelligence Report

## TL;DR
- 6 employees are high flight risks, concentrated in Sales and Engineering (junior cohort).
- Sales department shows lowest avg performance (2.8) with 3+ manager changes per risk employee.
- Q3 hiring plan requires 8 total hires: 5 backfills, 3 growth positions.

## Flight-risk employees
| Name | Department | Tenure | Risk Factors |
|------|-----------|--------|-------------|
| Alice Nguyen | Engineering | 1.2 yrs | Short tenure, 2 manager changes |
| Carol Smith | Sales | 2.1 yrs | 3 manager changes, 2 leave flags |
...
```

---

## Tech stack

- **[CrewAI](https://github.com/joaomdmoura/crewai)** — multi-agent orchestration framework
- **[LangChain OpenAI](https://github.com/langchain-ai/langchain)** — LLM connector
- **GPT-4o** — reasoning backbone (swappable)
- **Python 3.11+**

---

## Why this matters

Most HR analytics is static — dashboards that answer questions no one asked. HRAgent is conversational and composable: you describe the business problem, the crew figures out which data to pull, how to combine it, and what to recommend. It's the difference between a report and a thinking partner.

---

## License

MIT
