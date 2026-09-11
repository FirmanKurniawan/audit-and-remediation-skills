# Playbook — Desktop

Covers Electron, Tauri, Qt, WPF/WinForms, JavaFX/Swing, GTK, PySide/PyQt/Tkinter,
AppKit. Standards: OWASP Desktop App Security Top 10, ASVS for any embedded web
surface, CWE Top 25, plus OS hardening guidance.

## Process model and isolation
- **Electron**: `nodeIntegration` disabled, `contextIsolation` enabled,
  `sandbox` on, `webSecurity` not disabled, `contextBridge` exposing a minimal
  typed API rather than `ipcRenderer` wholesale
- IPC channel handlers validating sender, channel, and payload shape
- `will-navigate` / `new-window` / `setWindowOpenHandler` restricting navigation
- Remote content loaded into a privileged window
- **Tauri**: allowlist scope, command argument validation, `dangerousRemoteDomain`
- Native UI frameworks: privilege of the process, elevation prompts, service
  components running as SYSTEM/root

## Local attack surface
- File permissions on config, cache, logs, and the data directory
  (world-readable secrets on a shared machine)
- Credentials in plaintext config vs OS credential store (DPAPI, Keychain,
  libsecret/kwallet)
- Named pipes, Unix sockets, local HTTP servers: are they authenticated? bound to
  loopback? is the port predictable?
- Registry/plist permissions; writable install directory enabling binary planting
- DLL/dylib search-order hijacking; unquoted service paths
- Custom URI scheme handlers accepting arbitrary parameters
- Drag-and-drop and file-open handlers parsing untrusted files

## Update and integrity
- Update channel over TLS with signature verification of the payload
- Downgrade protection; update server pinning
- Code signing and notarization present for the shipped artifact
- Whether an attacker with local write access can replace the updater

## Data and persistence
- Local database encryption and key location (a key next to the ciphertext is not
  encryption)
- Crash dumps, temp files, and logs containing sensitive data
- Multi-user machines: per-user isolation of app data
- Sync conflict resolution and offline queue integrity

## Reliability and resources
- Long-running process: memory growth over days, handle/descriptor leaks
- Background threads blocking the UI thread
- Unbounded log growth, no rotation
- Behaviour on sleep/wake, network change, display change, OS update
- Multi-instance handling; single-instance lock correctness
- Graceful shutdown saving state; recovery from an unclean exit

## Packaging and distribution
- Bundled runtime and dependency versions (an old Electron/Chromium is a
  vulnerability inventory, not just a version string)
- Installer privileges and what it writes outside the app directory
- Uninstall completeness
- Telemetry defaults and opt-out

## Accessibility and UX
- Keyboard navigation, screen reader support (UIA, NSAccessibility, AT-SPI)
- High-contrast and OS theme respect; scaling on HiDPI and mixed-DPI setups
- Window state restore on multi-monitor setups
- Destructive actions requiring confirmation and offering undo
