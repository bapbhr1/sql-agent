from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, List

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.getenv(
    "DB_PATH", os.path.join(_PROJECT_ROOT, "ecommerce.db")
)


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_schema(db_path: str = DEFAULT_DB_PATH) -> str:
    with get_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT sql FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name;"
        )
        statements = [row["sql"] for row in cursor.fetchall() if row["sql"]]

    if not statements:
        return "-- Aucune table trouvée."

    return "\n\n".join(f"{stmt};" for stmt in statements)


def run_query(query: str, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
