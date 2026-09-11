# Phase 1 — Platform Detection

**Goal:** determine what kind of software this is, from artifacts on disk — never
from the repository name, the README's claims, or the user's description alone.

Run `scripts/detect-stack.sh` for a first pass, then verify by hand. The script
is a hint generator, not an oracle.

## 1.1 Fingerprints

A platform is **detected** only when at least one *primary* marker is present.
Secondary markers raise confidence but never establish detection alone.

### Web frontend
Primary: `index.html` + a bundler config (`vite.config.*`, `webpack.config.*`,
`next.config.*`, `nuxt.config.*`, `angular.json`, `svelte.config.js`,
`remix.config.*`, `astro.config.*`), or `public/index.html` with a JS framework
dependency.
Secondary: `.jsx`/`.tsx`/`.vue`/`.svelte` files, `tailwind.config.*`, `postcss.config.*`,
service worker, `manifest.webmanifest`.

### Backend / API service
Primary: a server framework dependency (Express, Fastify, NestJS, Spring Boot,
Django, Flask, FastAPI, Rails, Laravel, Gin, Echo, Actix, ASP.NET Core), or an
OpenAPI/GraphQL schema, or a `Dockerfile` exposing a port with an app entrypoint.
Secondary: migrations directory, ORM config, `docker-compose.yml`, k8s manifests,
queue/broker clients.

### Mobile — Android
Primary: `AndroidManifest.xml`, `build.gradle(.kts)` with `com.android.application`.
Secondary: `gradle/libs.versions.toml`, `proguard-rules.pro`, `res/` tree, `.kt`/`.java` under `app/src`.

### Mobile — iOS
Primary: `*.xcodeproj`, `*.xcworkspace`, `Package.swift` with an iOS target, `Info.plist` with iOS keys.
Secondary: `Podfile`, `*.swift`, `*.xcassets`, `PrivacyInfo.xcprivacy`.

### Mobile — cross-platform
Primary: `pubspec.yaml` (Flutter), React Native (`react-native` dependency +
`android/` and `ios/`), `.csproj` with MAUI/Xamarin targets, Capacitor/Cordova
config, Kotlin Multiplatform `shared/` module with `androidMain`/`iosMain`.

### Desktop
Primary: Electron (`electron` dependency + `main`/`preload` entry), Tauri
(`src-tauri/tauri.conf.json`), Qt (`*.pro`, `CMakeLists.txt` with Qt),
WPF/WinForms `.csproj`, JavaFX/Swing entrypoint, GTK bindings, PySide/PyQt/Tkinter
main window, macOS AppKit target.
Secondary: installer config (`electron-builder.yml`, NSIS, `.deb`/`.rpm` packaging,
`Info.plist` for macOS), auto-updater config, tray/menu code.

### CLI / library / SDK
Primary: a published-package manifest with `bin`/entry points and no UI or server
surface; `setup.py`/`pyproject.toml` with console_scripts; `Cargo.toml` `[[bin]]`.

### Embedded / IoT / edge
Primary: `platformio.ini`, Zephyr/`prj.conf`, ESP-IDF `sdkconfig`, Yocto layers,
Buildroot config, bare-metal linker scripts, `device tree` files, systemd units +
GPIO/serial/hardware libraries.
Secondary: cross-compile toolchain config, `udev` rules, watchdog usage.

### Data / ML / AI
Primary: training/inference pipeline code with a framework dependency (PyTorch,
TensorFlow, scikit-learn, JAX), notebooks driving production artifacts, model
registry config, DAG definitions (Airflow, Dagster, Prefect), LLM orchestration
(prompt templates, agent frameworks, vector store clients).

### Infrastructure / DevOps
Primary: Terraform/Pulumi/CloudFormation, Helm charts, Kubernetes manifests,
Ansible playbooks as the main deliverable.

### Game
Primary: Unity `ProjectSettings/`, Unreal `.uproject`, Godot `project.godot`.

## 1.2 Hybrid and monorepo resolution

Multi-platform is the norm, not the exception. Classify explicitly:

- **Hybrid product** — one product, several surfaces (e.g. React web + Android app + Node API).
- **Monorepo** — several independent products or packages in one tree.
- **Shared-core** — one core library consumed by several platform shells (KMP, Rust core + FFI, shared TypeScript domain).
- **Full-stack single deployable** — server-rendered app where frontend and backend ship together (Next.js, Rails, Laravel, Django).

For each detected component record: path, platform class, language(s), build
system, entry point, deploy target, and whether it is in audit scope for the
chosen tier.

## 1.3 Output format

Write to `.audit/manifest.json` and reproduce in the report:

| Component | Path | Platform | Primary marker (evidence) | Confidence | In scope |
|---|---|---|---|---|---|
| web-admin | `apps/admin` | Web frontend (React/Vite) | `apps/admin/vite.config.ts` | Confirmed | Yes |
| api | `services/api` | Backend API (FastAPI) | `services/api/pyproject.toml:22` | Confirmed | Yes |
| mobile | `apps/mobile` | Android (Kotlin) | `apps/mobile/AndroidManifest.xml` | Confirmed | Yes (T2 sampled) |

Confidence values: `Confirmed` (primary marker seen), `Likely` (secondary only),
`Uncertain` (ambiguous — state what would resolve it).

## 1.4 Anti-patterns

- Do not infer platform from folder names (`mobile/` may hold a web PWA).
- Do not trust the README over the build files.
- Do not treat a stale `ios/` directory as an active platform without checking
  whether it is referenced by the build, CI, or recent commits.
- Do not silently drop a detected platform because you lack expertise in it —
  declare it in scope-limitations instead.

## Exit gate

- [ ] Every component classified with a primary-marker citation
- [ ] Hybrid/monorepo relationship described
- [ ] Deploy targets and runtime environments listed
- [ ] Out-of-scope components explicitly named
