#!/usr/bin/env python3
"""
Materialize the fixture repositories used by tests/run_tests.py.

Fixtures are tiny but structurally real: each carries the primary markers a
platform-detection pass should key on, a set of *seeded* defects with known
locations, and — critically — seeded *negatives*: code that superficially looks
dangerous but is not, so a detector that pattern-matches on names fails the suite.

The clean fixture has no seeded defects at all. An auditor that reports findings
there is not trustworthy, and the suite treats that as a failure.
"""
from __future__ import annotations

import json
import os
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def w(path: str, content: str) -> None:
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(content.lstrip("\n"))


def expect(fixture: str, data: dict) -> None:
    w(f"{fixture}/.expected/expectations.json", json.dumps(data, indent=2) + "\n")


# ---------------------------------------------------------------- web-spa
def web_spa() -> None:
    f = "web-spa"
    w(f"{f}/package.json", """
{
  "name": "fixture-web-spa",
  "private": true,
  "dependencies": { "react": "18.2.0", "react-dom": "18.2.0" },
  "devDependencies": { "vite": "5.0.0", "typescript": "5.3.0" }
}
""")
    w(f"{f}/vite.config.ts", """
import { defineConfig } from 'vite';
export default defineConfig({ build: { sourcemap: true } });
""")
    w(f"{f}/index.html", """
<!doctype html>
<html><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>
""")
    # SEEDED-WEB-1 (line 7): unsanitized innerHTML sink reachable from a URL param.
    w(f"{f}/src/Comment.tsx", """
import React from 'react';

export function Comment({ raw }: { raw: string }) {
  // renders user-submitted comment bodies
  return (
    <div
      dangerouslySetInnerHTML={{ __html: raw }}
    />
  );
}

export function SafeComment({ text }: { text: string }) {
  // NEGATIVE: escaped by React, must not be reported
  return <div>{text}</div>;
}
""")
    # SEEDED-WEB-2 (line 4): session token in localStorage.
    w(f"{f}/src/auth.ts", """
export function persistSession(token: string) {
  // token survives any XSS on this origin
  localStorage.setItem('session_token', token);
}

export function readTheme(): string | null {
  // NEGATIVE: non-sensitive value in localStorage is fine
  return localStorage.getItem('ui_theme');
}
""")
    w(f"{f}/src/main.tsx", """
import { Comment } from './Comment';
import { persistSession } from './auth';

const params = new URLSearchParams(window.location.search);
export function boot(token: string) {
  persistSession(token);
  return Comment({ raw: params.get('c') ?? '' });
}
""")
    expect(f, {
        "fixture": "web-spa",
        "expected_platforms": ["web-frontend"],
        "forbidden_platforms": ["mobile-android", "mobile-ios", "embedded-iot"],
        "expected_markers": ["vite.config.ts", "index.html", "package.json"],
        "expected_standards": ["OWASP Top 10:2025", "OWASP ASVS", "WCAG 2.2"],
        "seeded_defects": [
            {"id": "SEEDED-WEB-1", "marker": 'dangerouslySetInnerHTML', "file": "src/Comment.tsx", "line": 7,
             "finding_class": "security", "cwe": "CWE-79",
             "description": "dangerouslySetInnerHTML fed from a URL parameter"},
            {"id": "SEEDED-WEB-2", "marker": 'localStorage.setItem', "file": "src/auth.ts", "line": 3,
             "finding_class": "security", "cwe": "CWE-922",
             "description": "session token stored in localStorage"},
        ],
        "seeded_negatives": [
            {"file": "src/Comment.tsx", "symbol": "SafeComment",
             "why": "React escapes interpolated text"},
            {"file": "src/auth.ts", "symbol": "readTheme",
             "why": "non-sensitive value in web storage"},
        ],
    })


# ------------------------------------------------------------ backend-api
def backend_api() -> None:
    f = "backend-api"
    w(f"{f}/package.json", """
{
  "name": "fixture-backend-api",
  "private": true,
  "main": "src/server.js",
  "dependencies": { "express": "4.18.2", "sqlite3": "5.1.6" }
}
""")
    # SEEDED-API-1 (line 9): SQL built by concatenation.
    # SEEDED-API-2 (line 16): missing ownership check (BOLA).
    w(f"{f}/src/server.js", """
const express = require('express');
const db = require('./db');
const app = express();

app.get('/search', (req, res) => {
  const term = req.query.q;
  db.all(
    "SELECT id, title FROM notes WHERE title LIKE '%" + term + "%'",
    (err, rows) => res.json(rows)
  );
});

app.get('/notes/:id', requireAuth, (req, res) => {
  // no check that req.user owns this note
  db.get('SELECT * FROM notes WHERE id = ?', [req.params.id],
    (err, row) => res.json(row));
});

app.get('/my/notes', requireAuth, (req, res) => {
  // NEGATIVE: scoped by the authenticated user, parameterised
  db.all('SELECT * FROM notes WHERE owner_id = ?', [req.user.id],
    (err, rows) => res.json(rows));
});

function requireAuth(req, res, next) {
  if (!req.headers.authorization) return res.status(401).end();
  req.user = { id: 1 };
  next();
}

module.exports = app;
""")
    w(f"{f}/src/db.js", """
const sqlite3 = require('sqlite3');
module.exports = new sqlite3.Database(process.env.DB_PATH || ':memory:');
""")
    w(f"{f}/.env.example", """
DB_PATH=./data.sqlite
SESSION_SECRET=<set-me>
""")
    expect(f, {
        "fixture": "backend-api",
        "expected_platforms": ["backend-api"],
        "forbidden_platforms": ["mobile-android", "desktop", "embedded-iot"],
        "expected_markers": ["package.json"],
        "expected_output_tokens": ["express"],
        "expected_standards": ["OWASP ASVS", "OWASP API Security Top 10"],
        "seeded_defects": [
            {"id": "SEEDED-API-1", "marker": 'LIKE', "file": "src/server.js", "line": 8,
             "finding_class": "security", "cwe": "CWE-89",
             "description": "SQL string concatenation from req.query"},
            {"id": "SEEDED-API-2", "marker": 'no check that req.user owns', "file": "src/server.js", "line": 14,
             "finding_class": "security", "cwe": "CWE-639",
             "description": "object-level authorization missing on /notes/:id"},
        ],
        "seeded_negatives": [
            {"file": "src/server.js", "symbol": "/my/notes",
             "why": "parameterised and scoped to the authenticated user"},
            {"file": ".env.example", "symbol": "SESSION_SECRET",
             "why": "placeholder in an example file, not a real secret"},
        ],
    })


# ----------------------------------------------------------- android-app
def android_app() -> None:
    f = "android-app"
    # SEEDED-AND-1 (line 5): allowBackup + cleartext. SEEDED-AND-2 (line 9): exported activity.
    w(f"{f}/app/src/main/AndroidManifest.xml", """
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  <uses-permission android:name="android.permission.INTERNET" />
  <application
      android:allowBackup="true"
      android:usesCleartextTraffic="true"
      android:label="Fixture">
    <activity android:name=".MainActivity" android:exported="true">
      <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
      </intent-filter>
    </activity>
    <activity android:name=".SettingsActivity" android:exported="false" />
  </application>
</manifest>
""")
    w(f"{f}/app/build.gradle.kts", """
plugins { id("com.android.application") }
android {
    namespace = "com.example.fixture"
    compileSdk = 34
    defaultConfig { minSdk = 24; targetSdk = 34 }
    buildTypes { release { isMinifyEnabled = false } }
}
""")
    # SEEDED-AND-3 (line 6): auth token in plain SharedPreferences.
    w(f"{f}/app/src/main/java/com/example/fixture/TokenStore.kt", """
package com.example.fixture

import android.content.Context

class TokenStore(private val ctx: Context) {
    fun save(token: String) {
        ctx.getSharedPreferences("auth", Context.MODE_PRIVATE)
            .edit().putString("bearer", token).apply()
    }

    // NEGATIVE: non-sensitive UI state in SharedPreferences is fine
    fun saveLastTab(index: Int) {
        ctx.getSharedPreferences("ui", Context.MODE_PRIVATE)
            .edit().putInt("last_tab", index).apply()
    }
}
""")
    expect(f, {
        "fixture": "android-app",
        "expected_platforms": ["mobile-android"],
        "forbidden_platforms": ["web-frontend", "embedded-iot"],
        "expected_markers": ["AndroidManifest.xml", "build.gradle.kts"],
        "expected_standards": ["OWASP MASVS", "MASWE", "MASTG"],
        "seeded_defects": [
            {"id": "SEEDED-AND-1", "marker": 'usesCleartextTraffic', "file": "app/src/main/AndroidManifest.xml", "line": 6,
             "finding_class": "security", "cwe": "CWE-319",
             "description": "usesCleartextTraffic enabled"},
            {"id": "SEEDED-AND-2", "marker": 'allowBackup', "file": "app/src/main/AndroidManifest.xml", "line": 5,
             "finding_class": "security", "cwe": "CWE-530",
             "description": "allowBackup true exposes app data to adb backup"},
            {"id": "SEEDED-AND-3", "marker": 'putString("bearer"',
             "file": "app/src/main/java/com/example/fixture/TokenStore.kt", "line": 8,
             "finding_class": "security", "cwe": "CWE-922",
             "description": "bearer token in unencrypted SharedPreferences"},
        ],
        "seeded_negatives": [
            {"file": "app/src/main/AndroidManifest.xml", "symbol": "SettingsActivity",
             "why": "explicitly not exported"},
            {"file": "app/src/main/java/com/example/fixture/TokenStore.kt",
             "symbol": "saveLastTab", "why": "non-sensitive UI state"},
        ],
    })


# -------------------------------------------------------- desktop-electron
def desktop_electron() -> None:
    f = "desktop-electron"
    w(f"{f}/package.json", """
{
  "name": "fixture-desktop",
  "private": true,
  "main": "main.js",
  "devDependencies": { "electron": "28.0.0", "electron-builder": "24.9.1" }
}
""")
    # SEEDED-DSK-1 (line 8): nodeIntegration on + contextIsolation off.
    w(f"{f}/main.js", """
const { app, BrowserWindow } = require('electron');

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  win.loadURL('https://example.com/app');
}

app.whenReady().then(createWindow);
""")
    # NEGATIVE: a correctly configured second window.
    w(f"{f}/help-window.js", """
const { BrowserWindow } = require('electron');
const path = require('path');

// NEGATIVE: isolated, sandboxed, local content only
module.exports = function helpWindow() {
  return new BrowserWindow({
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });
};
""")
    w(f"{f}/electron-builder.yml", """
appId: com.example.fixture
directories:
  output: dist
""")
    expect(f, {
        "fixture": "desktop-electron",
        "expected_platforms": ["desktop"],
        "forbidden_platforms": ["mobile-android", "embedded-iot"],
        "expected_markers": ["electron-builder.yml", "package.json"],
        "expected_standards": ["OWASP Desktop App Security Top 10"],
        "seeded_defects": [
            {"id": "SEEDED-DSK-1", "marker": 'nodeIntegration: true', "file": "main.js", "line": 8,
             "finding_class": "security", "cwe": "CWE-693",
             "description": "nodeIntegration enabled with contextIsolation disabled on a window "
                            "that loads remote content"},
        ],
        "seeded_negatives": [
            {"file": "help-window.js", "symbol": "helpWindow",
             "why": "isolated, sandboxed, local preload"},
        ],
    })


# ------------------------------------------------------------ embedded-c
def embedded_c() -> None:
    f = "embedded-c"
    w(f"{f}/platformio.ini", """
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
""")
    # SEEDED-EMB-1 (line 10): memcpy with attacker-controlled length.
    # SEEDED-EMB-2 (line 24): watchdog fed unconditionally from a timer.
    w(f"{f}/src/protocol.c", """
#include <string.h>
#include <stdint.h>

#define MAX_PAYLOAD 64

struct frame { uint8_t len; uint8_t data[MAX_PAYLOAD]; };

void parse_frame(const uint8_t *wire, struct frame *out) {
    out->len = wire[0];
    memcpy(out->data, wire + 1, out->len);
}

/* NEGATIVE: bounds-checked variant, must not be reported */
int parse_frame_checked(const uint8_t *wire, size_t wire_len, struct frame *out) {
    if (wire_len < 1) return -1;
    if (wire[0] > MAX_PAYLOAD || (size_t)wire[0] + 1 > wire_len) return -1;
    out->len = wire[0];
    memcpy(out->data, wire + 1, out->len);
    return 0;
}
""")
    w(f"{f}/src/watchdog.c", """
#include <stdbool.h>

extern void wdt_reset(void);
extern bool control_loop_healthy(void);

/* fires every 100 ms regardless of whether the control loop is alive */
void timer_isr(void) {
    wdt_reset();
}

/* NEGATIVE: the correct pattern, conditional on liveness */
void supervisor_task(void) {
    if (control_loop_healthy()) {
        wdt_reset();
    }
}
""")
    expect(f, {
        "fixture": "embedded-c",
        "expected_platforms": ["embedded-iot"],
        "forbidden_platforms": ["web-frontend", "backend-api"],
        "expected_markers": ["platformio.ini"],
        "expected_standards": ["SEI CERT", "CWE Top 25"],
        "seeded_defects": [
            {"id": "SEEDED-EMB-1", "marker": 'memcpy(out->data', "file": "src/protocol.c", "line": 10,
             "finding_class": "security", "cwe": "CWE-787",
             "description": "memcpy length taken from the wire without bounds check"},
            {"id": "SEEDED-EMB-2", "marker": 'wdt_reset();', "file": "src/watchdog.c", "line": 8,
             "finding_class": "reliability", "cwe": None,
             "description": "watchdog fed from a timer ISR independent of task liveness"},
        ],
        "seeded_negatives": [
            {"file": "src/protocol.c", "symbol": "parse_frame_checked",
             "why": "length validated against the buffer and the wire length"},
            {"file": "src/watchdog.c", "symbol": "supervisor_task",
             "why": "feed is conditional on liveness"},
        ],
    })


# ------------------------------------------------------------- clean-lib
def clean_lib() -> None:
    """Mandatory negative control. No seeded defects.

    Deliberately contains constructs that trip naive pattern matchers:
    the word 'password' in a docstring, an 'eval' in a comment, a variable
    called 'token' holding a parser token, and a hash used for cache keys
    rather than for credentials."""
    f = "clean-lib"
    w(f"{f}/pyproject.toml", """
[project]
name = "fixture-clean-lib"
version = "1.0.0"
requires-python = ">=3.10"

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
""")
    w(f"{f}/src/cleanlib/__init__.py", """
from .tokenizer import tokenize
from .cache import cache_key

__all__ = ["tokenize", "cache_key"]
""")
    w(f"{f}/src/cleanlib/tokenizer.py", '''
"""A tiny expression tokenizer.

Note: this module never handles a password or any credential; the word appears
here only to make sure keyword-matching scanners do not fire on documentation.
We also do not use eval() — the parser is a hand-written state machine.
"""
from __future__ import annotations

_SYMBOLS = set("+-*/()")


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    token = ""
    for ch in text:
        if ch.isspace():
            if token:
                tokens.append(token)
                token = ""
        elif ch in _SYMBOLS:
            if token:
                tokens.append(token)
                token = ""
            tokens.append(ch)
        else:
            token += ch
    if token:
        tokens.append(token)
    return tokens
''')
    w(f"{f}/src/cleanlib/cache.py", '''
"""Cache-key helper.

Uses a non-cryptographic-strength digest deliberately and only for cache
bucketing, never for authentication or integrity.
"""
from __future__ import annotations

import hashlib


def cache_key(*parts: str) -> str:
    joined = "\\u241f".join(parts)
    return hashlib.blake2b(joined.encode("utf-8"), digest_size=16).hexdigest()
''')
    w(f"{f}/tests/test_tokenizer.py", '''
from cleanlib import tokenize, cache_key


def test_tokenize_splits_symbols():
    assert tokenize("1 + 2*3") == ["1", "+", "2", "*", "3"]


def test_tokenize_empty():
    assert tokenize("") == []


def test_cache_key_is_stable():
    assert cache_key("a", "b") == cache_key("a", "b")
    assert cache_key("a", "b") != cache_key("b", "a")
''')
    expect(f, {
        "fixture": "clean-lib",
        "expected_platforms": ["cli-library"],
        "forbidden_platforms": ["mobile-android", "desktop", "embedded-iot", "web-frontend"],
        "expected_markers": ["pyproject.toml"],
        "expected_standards": ["CWE", "ISO/IEC 25010", "Sonar way"],
        "seeded_defects": [],
        "seeded_negatives": [
            {"file": "src/cleanlib/tokenizer.py", "symbol": "docstring",
             "why": "'password' and 'eval' appear only in prose"},
            {"file": "src/cleanlib/cache.py", "symbol": "cache_key",
             "why": "fast digest used for cache bucketing, not for credentials"},
        ],
        "note": "Negative control. Any Medium-or-above finding here is a false positive "
                "and fails the suite.",
    })


BUILDERS = [web_spa, backend_api, android_app, desktop_electron, embedded_c, clean_lib]


def main() -> int:
    if "--clean" in sys.argv and os.path.isdir(ROOT):
        shutil.rmtree(ROOT)
    for b in BUILDERS:
        b()
    names = sorted(d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)))
    print(f"materialized {len(names)} fixtures: {', '.join(names)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
