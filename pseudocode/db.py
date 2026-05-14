import sqlite3

class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""


class SQLiteAdapter:
    """
    Pseudocode responsibilities:
    - open SQLite connections
    - list tables
    - inspect schemas
    - execute search queries
    - execute inserts
    - execute aggregates
    - validate identifiers before building SQL
    """
    def __init__(self, db_path="lab.db"):
        self.db_path = db_path  

    def connect(self):
        # return sqlite connection with row_factory enabled
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def list_tables(self):
        # query sqlite_master and return non-internal tables
        query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
        ORDER BY NAME 
        """
        with self.connect() as conn:
                rows = conn.execute(query).fetchall()
        
        return [row["name"] for row in rows]


    def get_table_schema(self, table):
        # run PRAGMA table_info(table) and normalize result
        if table not in self.list_tables():
            raise ValidationError(f"Unknown table: {table}")

        query = f"PRAGMA table_info({table})"
        with self.connect() as conn:
            rows = conn.execute(query).fetchall()

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



    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        """
        Pseudocode:
        - validate identifiers
        - build WHERE clause from supported operators
        - build ORDER BY if requested
        - append LIMIT and OFFSET
        - execute with bound parameters
        """
        pass

    def insert(self, table, values):
        """
        Pseudocode:
        - validate table and columns
        - build INSERT statement with placeholders
        - commit transaction
        - return inserted payload
        """
        pass

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        """
        Pseudocode:
        - validate metric
        - validate identifiers
        - build SELECT metric(column) AS value
        - optionally add GROUP BY
        - execute and return rows
        """
        pass
