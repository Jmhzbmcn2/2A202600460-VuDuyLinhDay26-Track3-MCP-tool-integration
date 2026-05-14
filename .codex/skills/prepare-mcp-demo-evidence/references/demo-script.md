# Day26 Demo Evidence Script

## Screenshot Checklist

Recommended filenames:

- `01-verify-server-passed.png`
- `02-unit-tests-ok.png`
- `03-codex-mcp-list-sqlite-lab.png`
- `04-tools-resources-discovered.png`
- `05-valid-search-result.png`
- `06-invalid-request-error.png`

Minimum acceptable evidence:

- one terminal screenshot showing `python implementation\verify_server.py` and `Verification passed`
- one terminal screenshot showing unit tests passing
- one screenshot showing Codex MCP client configured with `sqlite_lab`
- one screenshot from Codex or MCP Inspector showing tools/resources or a successful tool call

## Two-Minute Video Outline

0:00-0:15 - Show project structure:

```powershell
Get-ChildItem implementation
```

Say: "This project implements a FastMCP SQLite server with database logic, server logic, verification, and tests."

0:15-0:35 - Show database initialization:

```powershell
python implementation\init_db.py
```

Say: "The SQLite database is reproducible and seeded with students, courses, and enrollments."

0:35-0:55 - Show verification:

```powershell
python implementation\verify_server.py
```

Point out the valid search, insert, aggregate, and invalid-table check.

0:55-1:10 - Show tests:

```powershell
python -m unittest discover -s implementation\tests
```

Say: "The tests cover search, insert, aggregate, and validation errors."

1:10-1:30 - Show Codex MCP configuration:

```powershell
codex mcp list
```

Point out `sqlite_lab` is enabled and points to `implementation\mcp_server.py`.

1:30-2:00 - Show one MCP client interaction:

Use Codex or MCP Inspector to demonstrate:

- read `schema://database`
- call `search` on `students` with cohort `A1`
- call `aggregate` with average `score` grouped by `cohort`
- call an invalid table and show the clear error

## Codex Prompt

```text
Use the sqlite_lab MCP server. Read schema://database, then search for students in cohort A1 ordered by score descending. Then compute average score by cohort. Finally, show an invalid request for a missing table and explain the error.
```

## Submission Note Template

Use this in the README, assignment comment, or video description:

```text
The implementation uses FastMCP with SQLite and exposes search, insert, aggregate, schema://database, and schema://table/{table_name}. I verified it with implementation/verify_server.py, unit tests, and Codex MCP client configuration named sqlite_lab.
```
