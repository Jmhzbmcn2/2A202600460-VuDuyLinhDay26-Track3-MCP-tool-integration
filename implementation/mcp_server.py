import json
from pathlib import Path

from fastmcp import FastMCP

try:
    from .db import DB_PATH, SQLiteAdapter, ValidationError
    from .init_db import create_database
except ImportError:
    from db import DB_PATH, SQLiteAdapter, ValidationError
    from init_db import create_database


if not Path(DB_PATH).exists():
    create_database(DB_PATH)

adapter = SQLiteAdapter(DB_PATH)
mcp = FastMCP("SQLite Lab MCP Server")


def handle_validation(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except ValidationError as exc:
        return {"error": str(exc)}


@mcp.tool(name="search")
def search(
    table: str,
    filters: list[dict] | dict | None = None,
    columns: list[str] | None = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str | None = None,
    descending: bool = False,
):
    """Search rows in a validated SQLite table with optional filters and pagination."""
    return handle_validation(
        adapter.search,
        table=table,
        filters=filters,
        columns=columns,
        limit=limit,
        offset=offset,
        order_by=order_by,
        descending=descending,
    )


@mcp.tool(name="insert")
def insert(table: str, values: dict):
    """Insert one row into a validated SQLite table and return the inserted payload."""
    return handle_validation(adapter.insert, table=table, values=values)


@mcp.tool(name="aggregate")
def aggregate(
    table: str,
    metric: str,
    column: str | None = None,
    filters: list[dict] | dict | None = None,
    group_by: str | list[str] | None = None,
):
    """Run count, avg, sum, min, or max over a validated SQLite table."""
    return handle_validation(
        adapter.aggregate,
        table=table,
        metric=metric,
        column=column,
        filters=filters,
        group_by=group_by,
    )


@mcp.resource("schema://database")
def database_schema():
    """Return the full database schema as JSON text."""
    return json.dumps(adapter.get_database_schema(), indent=2)


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str):
    """Return one table schema as JSON text."""
    result = handle_validation(adapter.get_table_schema, table=table_name)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
