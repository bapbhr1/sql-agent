from __future__ import annotations

import re

from langchain_core.messages import HumanMessage, SystemMessage

from src.db import run_query
from src.llm import get_llm
from src.state import AgentState

MAX_RETRIES = 3


def _clean_sql(raw: str) -> str:
    text = raw.strip()
    fence = re.match(r"^```[a-zA-Z]*\s*(.*?)\s*```$", text, flags=re.DOTALL)
    if fence:
        text = fence.group(1)
    text = text.replace("```", "").strip()
    text = re.sub(r"^\s*sql\s*:?\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def generate_sql(state: AgentState) -> AgentState:
    is_correction = state.get("sql_error") is not None
    retry_count = state["retry_count"]

    if is_correction:
        retry_count += 1
        print(f"\n[Correction #{retry_count}] {state['sql_error']}")
    else:
        print("\n[generate_sql]")

    system_prompt = (
        "Tu es expert SQLite. Écris une requête SQL valide.\n"
        "Réponds UNIQUEMENT avec la requête SQL, rien d'autre.\n"
        "Sans markdown, sans commentaires, sans texte explicatif."
    )

    user_prompt = f"Schéma :\n{state['schema']}\n\nQuestion :\n{state['question']}"

    if is_correction:
        user_prompt += (
            f"\n\nRequête échouée :\n{state['sql_query']}"
            f"\nErreur : {state['sql_error']}\n\nCorrige-la."
        )

    llm = get_llm()
    response = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    )

    sql_query = _clean_sql(str(response.content))
    print(f"  {sql_query}")
    return {**state, "sql_query": sql_query, "retry_count": retry_count}


def execute_sql(state: AgentState) -> AgentState:
    print("[execute_sql]")
    try:
        result = run_query(state["sql_query"])
        print(f"  {len(result)} ligne(s)")
        return {**state, "query_result": result, "sql_error": None}
    except Exception as exc:
        error_message = f"{type(exc).__name__}: {exc}"
        print(f"  Échec: {error_message}")
        return {**state, "query_result": None, "sql_error": error_message}


def format_answer(state: AgentState) -> AgentState:
    print("[format_answer]")
    if state.get("sql_error") is not None:
        final_answer = f"Erreur après {MAX_RETRIES} essais: {state['sql_error']}"
        return {**state, "final_answer": final_answer}

    system_prompt = (
        "Tu es analyste de données. Réponds en français, concis, "
        "mettant en avant les chiffres clés. Ne rien inventer."
    )

    user_prompt = (
        f"Question : {state['question']}\n"
        f"Résultats SQL : {state['query_result']}"
    )

    llm = get_llm()
    response = llm.invoke(
        [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
    )
    return {**state, "final_answer": str(response.content).strip()}


def should_continue(state: AgentState) -> str:
    if state.get("sql_error") is not None and state["retry_count"] < MAX_RETRIES:
        return "generate_sql"
    return "format_answer"
