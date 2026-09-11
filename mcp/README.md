# MCP server — universal-audit-skill

A thin stdio MCP server that exposes the audit skill's deterministic
Python validators as MCP tools. The audit orchestration itself stays with
the agent via the `SKILL.md` files in `../universal-audit-skill/` and
`../universal-remediation-skill/`. This server is for external processes
that want to call the validators without launching the full agent.

## What it does

| Tool | Wraps | What you get back |
|---|---|---|
| `audit_list_components`     | (no Python call)             | List of validators + Python launcher |
| `audit_validate_findings`   | `scripts/validate-findings.py` | Structured JSON: ok, exitCode, stdout, stderr, verdict |
| `audit_validate_manifest`   | `scripts/validate-manifest.py` | Same shape |
| `audit_quality_gate`        | `scripts/quality-gate.py`      | Same shape, plus `validation-result.json` written next to the audit dir |

The server auto-detects where the audit-skill scripts live by walking
up from its own directory looking for `validate-findings.py`. That makes
the same `server.js` work whether it sits in the MiniMax Code plugin,
in a flat GitHub clone, or in a custom install layout.

## Requirements

- Node.js 18+ (uses only built-in modules)
- Python 3.x available on `PATH` as `python3` on POSIX or `py` on Windows
  (the server picks the right launcher per platform; the audit scripts
  themselves only depend on the Python 3 standard library)

## Install

### Claude Code (CLI)

```bash
# replace with the path where you cloned this repo
git clone https://github.com/FirmanKurniawan/audit-and-remediation-skills ~/src/audit-skills

claude mcp add audit-and-remediation -- node ~/src/audit-skills/mcp/server.js
```

Verify:

```bash
claude mcp list
```

### Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "audit-and-remediation": {
      "type": "stdio",
      "command": "node",
      "args": ["C:/Users/<you>/src/audit-skills/mcp/server.js"]
    }
  }
}
```

Restart Claude Desktop. The MCP server will appear in the tool list.

### Cursor / Continue / other MCP hosts

Same shape — point `command` at `node` and `args` at the absolute path to
`mcp/server.js` in your clone. See your host's MCP documentation for the
exact config location.

### Direct stdio (CI helpers, scripts)

Anything that can speak JSON-RPC 2.0 over stdin / stdout can drive this
server directly:

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"ci","version":"0"}}}
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"audit_list_components","arguments":{}}}' \
  | node /path/to/repo/mcp/server.js
```

## Why a thin server

The audit pipeline is largely agentic — the SKILL.md drives the agent to
collect evidence, classify findings, and reconcile reports. Most of that
work should not be re-implemented behind a tool surface. What *is*
deterministic and useful outside the agent is the validator gate: a
programmatic way to ask "is this findings ledger internally consistent?",
"is this manifest well-formed?", "what does the quality gate say?".
That is exactly what this server exposes.

## Limitations

- The server spawns Python from `PATH`. If a user moves the repo to a
  host without Python 3, the validator wrappers will return
  `verdict: BLOCKED` with a `missing_dependency` error rather than fail
  silently. `audit_list_components` will return an empty `validators`
  array in the same situation.
- The MCP server does not invoke the remediation skill. Remediation is
  an agent task because it modifies source code; gating that behind an
  MCP tool would let untrusted callers rewrite repositories without
  consent.
