from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict):
    question: str
    schema: str
    sql_query: str
    sql_error: Optional[str]
    query_result: Optional[List[Dict[str, Any]]]
    retry_count: int
    final_answer: str
