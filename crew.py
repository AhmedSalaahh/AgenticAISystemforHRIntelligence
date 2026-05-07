"""
crew.py — HRAgent entry point.

Run with:
    python crew.py
    python crew.py --query "Draft a hiring plan for Q3 given our attrition rate."
"""

import argparse
import os

from crewai import Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents import build_agents
from tasks import build_tasks

load_dotenv()

DEFAULT_QUERY = (
    "Which employees are flight risks based on tenure and performance trends? "
    "And draft a Q3 hiring plan given our current attrition rate."
)


def build_crew(query: str) -> Crew:
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o"),
        temperature=0.2,
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    agents = build_agents(llm)
    tasks = build_tasks(agents, query)

    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,   # each task feeds context into the next
        verbose=True,
        memory=False,                  # set True to enable cross-run memory
    )


def main():
    parser = argparse.ArgumentParser(description="HRAgent — Agentic AI System for HR Intelligence")
    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY,
        help="The HR question to answer (wrap in quotes).",
    )
    args = parser.parse_args()

    print("\n" + "═" * 60)
    print("  HRAgent  —  HR Intelligence Crew")
    print("═" * 60)
    print(f"\n  Query: {args.query}\n")
    print("═" * 60 + "\n")

    crew = build_crew(args.query)
    result = crew.kickoff()

    print("\n" + "═" * 60)
    print("  Final Report")
    print("═" * 60)
    print(result)
    print("\n  Report saved to: outputs/hr_report.md")


if __name__ == "__main__":
    main()
