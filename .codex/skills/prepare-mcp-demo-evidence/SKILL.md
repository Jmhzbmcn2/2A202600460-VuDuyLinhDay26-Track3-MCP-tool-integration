---
name: prepare-mcp-demo-evidence
description: Prepare submission evidence for the Day26 FastMCP SQLite lab. Use when Codex needs to help create or review demo screenshots, a short demo video script, MCP Inspector evidence, Codex MCP client evidence, terminal verification output, or a rubric-aligned proof package showing the SQLite MCP server tools and schema resources working.
---

# Prepare MCP Demo Evidence

## Workflow

Use this skill after the Day26 implementation is complete and the user needs proof for submission.

1. Re-run verification commands before capturing evidence:

```powershell
python implementation\init_db.py
python implementation\verify_server.py
python -m unittest discover -s implementation\tests
codex mcp list
```

2. Confirm Codex lists `sqlite_lab` as enabled. If not, configure it:

```powershell
codex mcp add sqlite_lab -- python C:\Users\VUDUYLINH\PycharmProjects\VinAI\Day26\Day26-Track3-MCP-tool-integration\implementation\mcp_server.py
```

3. Capture at least four screenshots:

- terminal verification output showing `Verification passed`
- unit test output showing `OK`
- Codex MCP list showing `sqlite_lab ... enabled`
- Codex or Inspector output showing tools/resources and one valid query result

4. Prepare a 2-minute video using the sequence in `references/demo-script.md`.

5. Check the final evidence against the rubric:

- tools are discoverable: `search`, `insert`, `aggregate`
- resources are discoverable: `schema://database`, `schema://table/{table_name}`
- valid call succeeds
- invalid call returns a clear error
- Codex is configured as the client

## Codex Demo Prompt

Use this prompt in a fresh Codex session after `sqlite_lab` is configured:

```text
Use the sqlite_lab MCP server. Read schema://database, then search for students in cohort A1 ordered by score descending. After that, call aggregate to compute average score by cohort, and show one invalid request for a missing table.
```

If Codex cannot access resources directly in that UI, use MCP Inspector for the resource screenshot and keep Codex evidence for client configuration.

## Output Guidance

When helping the user assemble evidence, produce a short checklist with:

- exact file or screenshot names to submit
- exact command outputs already verified
- what remains manual, such as recording the screen
- any caveat, such as local dependency conflicts or missing Inspector screenshots

Do not claim a video exists unless it has actually been recorded or provided by the user.

## Reference

Read `references/demo-script.md` for the timed video outline and screenshot checklist.
