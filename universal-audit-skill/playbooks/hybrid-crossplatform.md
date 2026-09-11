# Playbook — Hybrid and Cross-Platform

For products spanning several surfaces (React Native, Flutter, Capacitor/Cordova,
MAUI/Xamarin, Kotlin Multiplatform, Rust core + FFI, shared TypeScript domain,
Electron + mobile companion).

## Audit strategy
1. Audit the **shared core** once against the strictest applicable standard set.
2. Audit **each shell** for its platform-specific surface: permissions, storage,
   IPC, packaging, store policy, accessibility.
3. Audit the **bridge** — this is where hybrid-specific defects concentrate.

Keep the component name on every finding. "The app validates input" is meaningless
when there are three clients and one of them does not.

## Bridge and FFI boundary
- What can the web/managed layer invoke in the native layer, and is that surface
  minimal? An unrestricted bridge turns any XSS into native code execution.
- Argument validation on the native side (never trust the JS/managed caller)
- Serialization across the boundary: type confusion, integer width, nullability,
  string encoding, ownership of buffers
- Error propagation across the boundary: exceptions swallowed, error codes ignored
- Threading model across the boundary: which side owns the thread, callbacks
  delivered on the wrong thread
- Memory ownership in FFI: who frees, double-free, leak on the error path

## Web-content shells (Capacitor, Cordova, embedded webview)
- Remote content in a privileged webview
- Plugin allowlist and per-plugin permissions
- CSP inside the webview
- Local file access from the web layer
- Deep link → webview navigation without validation

## Consistency defects (the classic hybrid bug class)
- Validation implemented on one platform only
- Divergent state machines: the iOS client and the Android client disagree about
  connection or session state
- Feature flags evaluated differently per shell
- Different crypto or storage implementations per platform for the same data
- Different permission-denial handling
- Number, date, and locale formatting divergence
- Version skew: shells shipping different core versions against one backend

## Shared-core specifics
- Platform-conditional code (`expect`/`actual`, `#if`, platform channels) —
  audit every branch, not just the one you can read most easily
- Test coverage that exercises the core only on one platform
- Dependency injection differing per platform, changing behaviour silently

## Build and release
- One version scheme across shells, or an explicit compatibility matrix
- Backward compatibility with older shells still in the field
- Forced-update mechanism, and what happens to a client that cannot update
- Per-platform signing and provenance
