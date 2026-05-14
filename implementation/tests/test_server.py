import sys
import unittest
from pathlib import Path


IMPLEMENTATION_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(IMPLEMENTATION_DIR))

from db import SQLiteAdapter, ValidationError  # noqa: E402
from init_db import create_database  # noqa: E402


class SQLiteAdapterTests(unittest.TestCase):
    def setUp(self):
        self.db_path = IMPLEMENTATION_DIR / "test_lab.db"
        create_database(self.db_path)
        self.adapter = SQLiteAdapter(self.db_path)

    def tearDown(self):
        if self.db_path.exists():
            self.db_path.unlink()

    def test_list_tables(self):
        self.assertEqual(
            self.adapter.list_tables(),
            ["courses", "enrollments", "students"],
        )

    def test_search_with_filter_order_and_pagination(self):
        result = self.adapter.search(
            "students",
            filters={"cohort": "A1"},
            columns=["name", "score"],
            order_by="score",
            descending=True,
            limit=2,
        )
        self.assertEqual(result["count"], 2)
        self.assertGreaterEqual(result["rows"][0]["score"], result["rows"][1]["score"])

    def test_insert_returns_payload(self):
        result = self.adapter.insert(
            "students",
            {"name": "New Student", "cohort": "C3", "score": 79.0},
        )
        self.assertEqual(result["inserted"]["name"], "New Student")
        self.assertIsInstance(result["inserted"]["id"], int)

    def test_aggregate_count_and_grouped_avg(self):
        count_result = self.adapter.aggregate("students", "count")
        self.assertEqual(count_result["rows"][0]["value"], 5)

        avg_result = self.adapter.aggregate("students", "avg", "score", group_by="cohort")
        self.assertTrue(any(row["cohort"] == "A1" for row in avg_result["rows"]))

    def test_invalid_table_column_and_operator_are_rejected(self):
        with self.assertRaises(ValidationError):
            self.adapter.search("missing")
        with self.assertRaises(ValidationError):
            self.adapter.search("students", columns=["missing"])
        with self.assertRaises(ValidationError):
            self.adapter.search(
                "students",
                filters=[{"column": "cohort", "op": "starts_with", "value": "A"}],
            )


if __name__ == "__main__":
    unittest.main()
