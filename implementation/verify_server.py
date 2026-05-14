import json

from db import DB_PATH, SQLiteAdapter, ValidationError
from init_db import create_database


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    create_database(DB_PATH)
    adapter = SQLiteAdapter(DB_PATH)

    tables = adapter.list_tables()
    assert_true(tables == ["courses", "enrollments", "students"], "tables mismatch")

    schema = adapter.get_database_schema()
    assert_true("students" in schema, "students schema missing")

    search_result = adapter.search(
        "students",
        filters={"cohort": "A1"},
        order_by="score",
        descending=True,
    )
    assert_true(search_result["count"] >= 1, "search returned no A1 students")

    insert_result = adapter.insert(
        "students",
        {"name": "Test Student", "cohort": "T1", "score": 82.0},
    )
    assert_true(insert_result["inserted"]["id"] is not None, "insert did not return id")

    aggregate_result = adapter.aggregate("students", "avg", "score", group_by="cohort")
    assert_true(aggregate_result["rows"], "aggregate returned no rows")

    try:
        adapter.search("missing_table")
    except ValidationError:
        invalid_error_ok = True
    else:
        invalid_error_ok = False
    assert_true(invalid_error_ok, "invalid table was not rejected")

    report = {
        "database": str(DB_PATH),
        "tables": tables,
        "sample_search": search_result,
        "sample_insert": insert_result,
        "sample_aggregate": aggregate_result,
        "invalid_error_ok": invalid_error_ok,
    }
    print(json.dumps(report, indent=2))
    print("Verification passed.")


if __name__ == "__main__":
    main()
