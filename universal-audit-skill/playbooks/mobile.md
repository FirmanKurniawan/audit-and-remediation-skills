# Playbook — Mobile (Android / iOS)

Standards: OWASP MASVS 2.x groups, MASWE 1.0 weakness ids, MASTG 2.0 tests, plus
store policy. Cite MASWE ids in findings — they are more actionable than MASVS
control ids alone.

## Storage (MASVS-STORAGE)
- Credentials/tokens in SharedPreferences / NSUserDefaults / plain files
- Keystore / Keychain usage: is it used, with what protection class, and does the
  key actually gate the secret?
- Database encryption; unencrypted caches; external/shared storage
- Backup inclusion: `allowBackup`, `dataExtractionRules`, iOS backup exclusion
- Logs, clipboard, screenshots and task-switcher previews, notification content
- Data cleared on logout and on account switch

## Crypto (MASVS-CRYPTO)
- Deprecated algorithms and modes (ECB, DES, MD5/SHA1 for security purposes)
- Hardcoded keys/IVs; keys derived from device-readable values
- `Random` vs `SecureRandom` / `SecRandomCopyBytes`
- Key lifecycle, rotation, and what happens on biometric enrolment change

## Auth (MASVS-AUTH)
- Local auth (biometric/PIN) used as a real gate or only as a UI curtain — is the
  protected secret actually bound to the authentication?
- Session lifetime, refresh, and revocation
- Re-authentication before sensitive operations
- Account switching leaving prior state behind

## Network (MASVS-NETWORK)
- Cleartext permitted (`usesCleartextTraffic`, ATS exceptions) — including
  "debug-only" configurations that ship in release
- Custom `TrustManager` / `hostnameVerifier` / `URLSession` delegate that accepts
  anything
- Certificate pinning: present? recoverable when the cert rotates? bypassable?
- Sensitive data in URLs; caching of authenticated responses
- Custom UDP/TCP protocols: authentication, integrity, replay protection, and
  handling of packets from unexpected peers

## Platform (MASVS-PLATFORM)
- Exported activities/services/receivers/providers and their intent handling
- Intent redirection, unsafe `PendingIntent` mutability, implicit intents with data
- Deep link and universal link validation; `assetlinks.json` / AASA correctness
- FileProvider paths; content provider permissions and `grantUriPermissions`
- WebView: `setJavaScriptEnabled`, `addJavascriptInterface`, file access,
  `WKScriptMessageHandler` bridges, loading untrusted URLs
- Permissions requested versus used; runtime permission denial and revocation
  handling; permission rationale
- iOS: URL scheme handling, app group containers, extension data sharing,
  pasteboard, required-reason API declarations, privacy manifest

## Code and resilience (MASVS-CODE / MASVS-RESILIENCE)
- Debuggable release builds, exported debug flags, test endpoints in release
- Minification/obfuscation config and whether it is actually applied to release
- Native/JNI: buffer bounds, reference leaks, thread attach/detach, ABI
- Dynamic code loading, reflection on user input
- Third-party SDK inventory and what each transmits
- Integrity/anti-tamper only where the threat model justifies it — say which

## Privacy (MASVS-PRIVACY)
- Data minimization; identifiers collected and their necessity
- Consent before collection; opt-out honoured
- Camera/mic/location indicators and background access
- Store declarations (Play Data safety, App Store privacy labels) matching reality
- Analytics and crash-report payload contents

## Lifecycle and concurrency
- Configuration change and process-death restore
- Work that outlives its scope; jobs not cancelled on teardown
- Callbacks after view/controller destruction
- Duplicate background loops after a fast reconnect or rapid navigation
- Foreground service type, notification, and restrictions on newer OS versions
- Battery optimization / background execution limits killing critical work
- Race conditions on rapid user input (double tap, quick toggle, fast switching)

## Audio / media / hardware (when present)
- Recorder and player lifecycle: init, release, re-init after route change
- Audio focus and interruption handling (call, other app)
- Bluetooth/wired route changes mid-operation
- Buffer sizing, underrun/overrun, sample-rate assumptions
- Fail-safe: can a crash or race leave capture or transmission running? Is there a
  hard timeout that stops it regardless of application state?

## Release readiness
- Target API/deployment target versus current store requirement
- Signing configuration not committed; upload key separate from app signing key
- Crash reporting configured with symbol upload
- Store policy items that block review
