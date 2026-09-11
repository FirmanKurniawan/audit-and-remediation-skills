#!/usr/bin/env node
// Minimal stdio MCP server for the audit-and-remediation repo.
//
// Protocol: JSON-RPC 2.0 over newline-delimited JSON on stdin/stdout.
// Methods implemented:
//   - initialize
//   - tools/list
//   - tools/call   (4 validator wrappers)
//
// Usage:
//   Claude Code CLI:    claude mcp add audit-and-remediation -- node /path/to/repo/mcp/server.js
//   Claude Desktop:     { "mcpServers": { "audit-and-remediation": { "command": "node", "args": ["/path/to/repo/mcp/server.js"] }}}
//   Cursor / Continue:  same shape as Claude Desktop, in their respective mcp.json
//   Direct stdio:       node /path/to/repo/mcp/server.js   (then feed JSON-RPC on stdin)
//
// This server is intentionally thin. Audit orchestration remains with the
// agent via the SKILL.md files; this server only exposes the deterministic
// Python validators so external processes (editor extensions, CI helpers,
// scripts) can invoke them without launching the full agent.

'use strict';

const path  = require('path');
const fs    = require('fs');
const { spawnSync } = require('child_process');

// ---- locate audit-skill scripts -----------------------------------------
//
// The audit skill's Python validators live in a sibling directory. The
// server supports three layouts so the same script works whether it lives
// inside the MiniMax Code plugin, the GitHub repo, or a custom install:
//
//   1) <root>/skills/universal-audit-skill/scripts/   (MiniMax plugin layout)
//   2) <root>/universal-audit-skill/scripts/         (GitHub-repo flat layout)
//   3) <root>/scripts/                              (legacy / single-skill installs)
//
// We walk upward from __dirname until we find one of these containing the
// validate-findings.py script. That dir becomes AUDIT_SCRIPTS.

function findAuditScripts(startDir) {
  let dir = path.resolve(startDir);
  for (let i = 0; i < 6; i++) {
    const candidates = [
      path.join(dir, 'skills', 'universal-audit-skill', 'scripts'),
      path.join(dir, 'universal-audit-skill', 'scripts'),
      path.join(dir, 'scripts'),
    ];
    for (const c of candidates) {
      try {
        if (fs.existsSync(path.join(c, 'validate-findings.py'))) return c;
      } catch (_) { /* EACCES, etc. — keep walking */ }
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;        // reached filesystem root
    dir = parent;
  }
  return null;
}

const AUDIT_SCRIPTS = findAuditScripts(__dirname);

// ---- helpers -------------------------------------------------------------

function pickPythonLauncher() {
  // Python scripts in the skill use a `python3` shebang. On POSIX we honor
  // that name. On Windows we prefer the `py` launcher (which on first-use
  // dispatches to whichever Python version Windows carries).
  if (process.platform === 'win32') return 'py';
  return 'python3';
}

function runScript(scriptRelPath, args) {
  if (!AUDIT_SCRIPTS) {
    return {
      ok: false,
      exitCode: -1,
      stdout: '',
      stderr: 'audit-skill scripts directory not found near this server; ensure the repo is intact',
      verdict: 'BLOCKED',
      errors: [{ kind: 'missing_dependency', message: 'universal-audit-skill/scripts/' }],
    };
  }
  const scriptAbs = path.join(AUDIT_SCRIPTS, scriptRelPath);
  if (!fs.existsSync(scriptAbs)) {
    return {
      ok: false,
      exitCode: -1,
      stdout: '',
      stderr: `script not found in audit-skill: ${scriptRelPath}`,
      verdict: 'BLOCKED',
      errors: [{ kind: 'missing_dependency', message: scriptRelPath }],
    };
  }

  const launcher = pickPythonLauncher();
  const result   = spawnSync(launcher, [scriptAbs, ...args], {
    cwd: path.dirname(AUDIT_SCRIPTS),
    encoding: 'utf8',
    timeout: 60000,
    windowsHide: true,
  });

  const exit = result.status == null ? -1 : result.status;
  return {
    ok: exit === 0,
    exitCode: exit,
    stdout: result.stdout || '',
    stderr: result.stderr || '',
    verdict: exit === 0 ? 'PASS' : 'FAIL_VALIDATION',
  };
}

function rejectPathTraversal(p) {
  // Caller-supplied paths must be non-empty strings without null bytes.
  if (!p || typeof p !== 'string') return { ok: false, reason: 'path required' };
  if (p.includes('\0'))            return { ok: false, reason: 'null byte in path' };
  return { ok: true };
}

// ---- tool definitions ----------------------------------------------------

const TOOLS = [
  {
    name: 'audit_list_components',
    description: 'List the components and validators shipped in this package. Use this to confirm what is locally available before calling a validator.',
    inputSchema: {
      type: 'object',
      properties: {},
      additionalProperties: false,
    },
  },
  {
    name: 'audit_validate_findings',
    description: 'Run validate-findings.py on a findings.jsonl file. Returns ok=false on schema errors, ok=true on a clean ledger. Does not modify the file.',
    inputSchema: {
      type: 'object',
      properties: {
        findings_path: { type: 'string', description: 'Absolute or repo-relative path to a findings.jsonl ledger.' },
      },
      required: ['findings_path'],
      additionalProperties: false,
    },
  },
  {
    name: 'audit_validate_manifest',
    description: 'Run validate-manifest.py on an audit manifest. Returns ok=false on manifest errors, ok=true on a clean manifest.',
    inputSchema: {
      type: 'object',
      properties: {
        manifest_path: { type: 'string', description: 'Absolute or repo-relative path to a manifest.json file.' },
      },
      required: ['manifest_path'],
      additionalProperties: false,
    },
  },
  {
    name: 'audit_quality_gate',
    description: 'Run the end-to-end quality gate against an .audit/ directory. Writes validation-result.json next to the findings. Returns the gate verdict (PASS / PASS_WITH_LIMITATIONS / FAIL_VALIDATION / BLOCKED).',
    inputSchema: {
      type: 'object',
      properties: {
        audit_dir: { type: 'string', description: 'Absolute or repo-relative path to the .audit/ directory.' },
      },
      required: ['audit_dir'],
      additionalProperties: false,
    },
  },
];

function toolListComponents(_args) {
  return {
    ok: true,
    audit_skill_scripts: AUDIT_SCRIPTS,
    validators: AUDIT_SCRIPTS
      ? ['validate-findings.py', 'validate-manifest.py', 'quality-gate.py']
      : [],
    pythonLauncher: pickPythonLauncher(),
  };
}

function toolCall(name, args) {
  switch (name) {
    case 'audit_list_components':
      return toolListComponents(args);

    case 'audit_validate_findings': {
      const reject = rejectPathTraversal(args.findings_path);
      if (!reject.ok) return { ok: false, reason: reject.reason };
      return runScript('validate-findings.py', ['--findings', args.findings_path]);
    }

    case 'audit_validate_manifest': {
      const reject = rejectPathTraversal(args.manifest_path);
      if (!reject.ok) return { ok: false, reason: reject.reason };
      return runScript('validate-manifest.py', ['--manifest', args.manifest_path]);
    }

    case 'audit_quality_gate': {
      const reject = rejectPathTraversal(args.audit_dir);
      if (!reject.ok) return { ok: false, reason: reject.reason };
      return runScript('quality-gate.py', ['--audit-dir', args.audit_dir]);
    }

    default:
      return { ok: false, reason: `unknown tool: ${name}` };
  }
}

// ---- JSON-RPC plumbing ---------------------------------------------------

function sendMessage(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

function sendResult(id, result) {
  sendMessage({ jsonrpc: '2.0', id, result });
}

function sendError(id, code, message) {
  sendMessage({ jsonrpc: '2.0', id, error: { code, message } });
}

function handleLine(line) {
  let msg;
  try { msg = JSON.parse(line); }
  catch (_) { return; }
  if (typeof msg !== 'object' || msg === null) return;
  const id = Object.prototype.hasOwnProperty.call(msg, 'id') ? msg.id : null;
  if (id === null) return;                             // notification: ignore

  switch (msg.method) {
    case 'initialize':
      sendResult(id, {
        protocolVersion: '2024-11-05',
        serverInfo: { name: 'audit-and-remediation', version: '1.0.0' },
        capabilities: { tools: {} },
      });
      return;

    case 'tools/list':
      sendResult(id, { tools: TOOLS });
      return;

    case 'tools/call': {
      const toolName = msg.params && msg.params.name;
      const toolArgs = (msg.params && msg.params.arguments) || {};
      const handled  = toolCall(toolName, toolArgs);
      sendResult(id, {
        content: [{ type: 'text', text: JSON.stringify(handled, null, 2) }],
        isError: handled.ok === false,
      });
      return;
    }

    default:
      sendError(id, -32601, `method not found: ${msg.method}`);
  }
}

// ---- main loop -----------------------------------------------------------

let buffer = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => {
  buffer += chunk;
  let nl;
  while ((nl = buffer.indexOf('\n')) !== -1) {
    const line = buffer.slice(0, nl).trim();
    buffer = buffer.slice(nl + 1);
    if (line) handleLine(line);
  }
});
process.stdin.on('end', () => process.exit(0));
