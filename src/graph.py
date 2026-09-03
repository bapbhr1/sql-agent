from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.nodes import execute_sql, format_answer, generate_sql, should_continue
from src.state import AgentState


def build_graph() -> CompiledStateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("generate_sql", generate_sql)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("format_answer", format_answer)

    workflow.set_entry_point("generate_sql")
    workflow.add_edge("generate_sql", "execute_sql")
    workflow.add_conditional_edges(
        "execute_sql",
        should_continue,
        {"generate_sql": "generate_sql", "format_answer": "format_answer"},
    )
    workflow.add_edge("format_answer", END)

    return workflow.compile()
