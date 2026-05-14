import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("lab.db")


class ValidationError(Exception):
    """Raised when a database request cannot be safely executed."""


class SQLiteAdapter:
    ALLOWED_OPERATORS = {
        "eq": "=",
        "ne": "!=",
        "lt": "<",
        "lte": "<=",
        "gt": ">",
        "gte": ">=",
        "contains": "LIKE",
        "in": "IN",
    }
    ALLOWED_METRICS = {"count", "avg", "sum", "min", "max"}
    MAX_LIMIT = 100

    def __init__(self, db_path=DB_PATH):
        self.db_path = Path(db_path)

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self):
        query = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        conn = self.connect()
        try:
            rows = conn.execute(query).fetchall()
        finally:
            conn.close()
        return [row["name"] for row in rows]

    def get_table_schema(self, table):
        self.validate_table(table)
        conn = self.connect()
        try:
            rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        finally:
            conn.close()
        return [
            {
                "name": row["name"],
                "type": row["type"],
                "notnull": bool(row["notnull"]),
                "default": row["dflt_value"],
                "pk": bool(row["pk"]),
            }
            for row in rows
        ]

    def get_database_schema(self):
        return {
            table: self.get_table_schema(table)
            for table in self.list_tables()
        }

    def validate_table(self, table):
        if table not in self.list_tables():
            raise ValidationError(f"Unknown table: {table}")
        return table

    def table_columns(self, table):
        return {column["name"] for column in self.get_table_schema(table)}

    def validate_column(self, table, column):
        if column not in self.table_columns(table):
            raise ValidationError(f"Unknown column for table '{table}': {column}")
        return column

    def validate_columns(self, table, columns):
        if not columns:
            return ["*"]
        if not isinstance(columns, list):
            raise ValidationError("columns must be a list of column names")
        for column in columns:
            self.validate_column(table, column)
        return columns

    def normalize_limit(self, limit):
        try:
            limit = int(limit)
        except (TypeError, ValueError) as exc:
            raise ValidationError("limit must be an integer") from exc
        if limit < 1:
            raise ValidationError("limit must be at least 1")
        return min(limit, self.MAX_LIMIT)

    def normalize_offset(self, offset):
        try:
            offset = int(offset)
        except (TypeError, ValueError) as exc:
            raise ValidationError("offset must be an integer") from exc
        if offset < 0:
            raise ValidationError("offset must be non-negative")
        return offset

    def normalize_filters(self, filters):
        if isinstance(filters, dict):
            return [
                {"column": column, "op": "eq", "value": value}
                for column, value in filters.items()
            ]
        if isinstance(filters, list):
            for item in filters:
                if not isinstance(item, dict) or "column" not in item:
                    raise ValidationError(
                        "Each filter must be an object with column, op, and value"
                    )
            return filters
        raise ValidationError("filters must be a dict or a list of filter objects")

    def build_where_clause(self, table, filters):
        if not filters:
            return "", []

        normalized = self.normalize_filters(filters)
        clauses = []
        params = []

        for item in normalized:
            column = item["column"]
            op = item.get("op", "eq")
            value = item.get("value")

            self.validate_column(table, column)
            if op not in self.ALLOWED_OPERATORS:
                raise ValidationError(f"Unsupported filter operator: {op}")

            sql_op = self.ALLOWED_OPERATORS[op]
            if op == "contains":
                clauses.append(f"{column} {sql_op} ?")
                params.append(f"%{value}%")
            elif op == "in":
                if not isinstance(value, list) or not value:
                    raise ValidationError("'in' filter value must be a non-empty list")
                placeholders = ", ".join("?" for _ in value)
                clauses.append(f"{column} IN ({placeholders})")
                params.extend(value)
            else:
                clauses.append(f"{column} {sql_op} ?")
                params.append(value)

        return " WHERE " + " AND ".join(clauses), params

    def search(
        self,
        table,
        columns=None,
        filters=None,
        limit=20,
        offset=0,
        order_by=None,
        descending=False,
    ):
        self.validate_table(table)
        selected_columns = self.validate_columns(table, columns)
        where_sql, params = self.build_where_clause(table, filters)
        limit = self.normalize_limit(limit)
        offset = self.normalize_offset(offset)

        column_sql = "*" if selected_columns == ["*"] else ", ".join(selected_columns)
        query = f"SELECT {column_sql} FROM {table}{where_sql}"

        if order_by:
            self.validate_column(table, order_by)
            direction = "DESC" if descending else "ASC"
            query += f" ORDER BY {order_by} {direction}"

        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        conn = self.connect()
        try:
            rows = [dict(row) for row in conn.execute(query, params).fetchall()]
        finally:
            conn.close()

        return {
            "table": table,
            "rows": rows,
            "count": len(rows),
            "limit": limit,
            "offset": offset,
        }

    def insert(self, table, values):
        self.validate_table(table)
        if not isinstance(values, dict) or not values:
            raise ValidationError("values must be a non-empty object")

        for column in values:
            self.validate_column(table, column)

        columns = list(values.keys())
        placeholders = ", ".join("?" for _ in columns)
        column_sql = ", ".join(columns)
        params = [values[column] for column in columns]
        query = f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})"

        conn = self.connect()
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            row_id = cursor.lastrowid
        finally:
            conn.close()

        inserted = {"id": row_id, **values}
        return {"table": table, "inserted": inserted}

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        self.validate_table(table)
        metric = str(metric).lower()
        if metric not in self.ALLOWED_METRICS:
            raise ValidationError(f"Unsupported aggregate metric: {metric}")

        if metric == "count" and column is None:
            target = "*"
        else:
            if column is None:
                raise ValidationError(f"metric '{metric}' requires a column")
            self.validate_column(table, column)
            target = column

        select_parts = []
        group_by_columns = []
        if group_by:
            group_by_columns = group_by if isinstance(group_by, list) else [group_by]
            for group_column in group_by_columns:
                self.validate_column(table, group_column)
            select_parts.extend(group_by_columns)

        select_parts.append(f"{metric.upper()}({target}) AS value")
        where_sql, params = self.build_where_clause(table, filters)
        query = f"SELECT {', '.join(select_parts)} FROM {table}{where_sql}"

        if group_by_columns:
            query += " GROUP BY " + ", ".join(group_by_columns)

        conn = self.connect()
        try:
            rows = [dict(row) for row in conn.execute(query, params).fetchall()]
        finally:
            conn.close()

        return {
            "table": table,
            "metric": metric,
            "column": column,
            "group_by": group_by_columns,
            "rows": rows,
        }
