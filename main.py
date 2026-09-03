from __future__ import annotations

import os
import sys

from dotenv import load_dotenv

from src.db import DEFAULT_DB_PATH, get_schema
from src.graph import build_graph
from src.state import AgentState


def _ensure_database() -> None:
    if not os.path.exists(DEFAULT_DB_PATH):
        print(f"Base introuvable: {DEFAULT_DB_PATH}\nExécutez : python setup_db.py")
        sys.exit(1)


def main() -> None:
    load_dotenv()
    _ensure_database()

    model = os.getenv("LLM_MODEL", "phi3")
    print(f"Agent SQL-to-Text (Ollama: {model})\n")

    schema = get_schema()
    graph = build_graph()

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not question or question.lower() in {"quit", "exit", "q"}:
            print("Bye.")
            break

        try:
            state: AgentState = {
                "question": question,
                "schema": schema,
                "sql_query": "",
                "sql_error": None,
                "query_result": None,
                "retry_count": 0,
                "final_answer": "",
            }
            result = graph.invoke(state)
            print(f"\n{result['final_answer']}\n")
        except Exception as exc:
            print(f"\nErreur: {exc}\n")


if __name__ == "__main__":
    main()
