# Playbook — Web Frontend

Standards: OWASP Top 10:2025, ASVS 5.0 (client-relevant chapters), WCAG 2.2,
Core Web Vitals.

## Rendering and injection
- `dangerouslySetInnerHTML`, `v-html`, `innerHTML`, `document.write`, and any
  template that interpolates unescaped user content
- Sanitizer presence, configuration, and whether it runs before or after
  transformation
- `javascript:` and `data:` URLs reaching `href`/`src`
- Dynamic `eval`, `new Function`, dynamic `import()` of user-influenced paths
- Client-side template injection in i18n strings and CMS content
- CSP: present? `unsafe-inline`/`unsafe-eval`? nonce or hash strategy? reported?

## Auth and session in the browser
- Token storage: `localStorage` (readable by any XSS) vs cookies with
  `HttpOnly`+`Secure`+`SameSite`
- Refresh flow: race on concurrent 401s, silent-refresh loops, token in URL
- Logout: does it clear memory, storage, service-worker cache, and IndexedDB?
- OAuth/OIDC: PKCE, `state`, nonce validation, redirect-URI allowlist,
  implicit flow still in use
- Authorization decided client-side only (hidden buttons, route guards) with no
  server enforcement

## Data handling
- Secrets in bundle: API keys, private endpoints, feature-flag payloads
  (`grep` the built output, not just the source)
- Sourcemaps published to production
- PII in `localStorage`, URL params, analytics events, or console logs
- Third-party scripts: what they can read, SRI, whether they run before consent

## Network
- CORS reliance for authorization (it is not an authorization mechanism)
- Mixed content, missing HSTS, absolute `http://` URLs
- Unbounded retry loops, no timeout on `fetch`, no abort on unmount
- WebSocket auth and origin checking
- Error responses rendered raw into the DOM

## State and correctness
- Stale closures capturing old props/state
- Effects without cleanup; subscriptions leaking on route change
- Race conditions between concurrent requests updating shared state
  (no request-id or abort → last-response-wins)
- Optimistic updates with no reconciliation on failure
- Derived state duplicated instead of computed
- Key collisions in lists causing wrong-row actions

## Performance
- Bundle size and code splitting; largest chunk contents
- Render-blocking resources, unoptimized images, missing `loading="lazy"`
- LCP/INP/CLS budgets and what breaks them
- Long tasks on the main thread; expensive work in render
- Memory growth on long-lived SPA sessions

## Accessibility (WCAG 2.2 AA)
- Keyboard operability of every interactive element; focus order and visible focus
- Semantic elements vs `div` with a click handler
- Labels, `aria-*` correctness, live regions for async status
- Contrast ratios, target size, motion preferences
- Form errors: identified, described, programmatically associated
- Automated pass with an axe-style tool plus a manual keyboard-only walkthrough

## Build and delivery
- Environment variable leakage into the client bundle
- Dev-only code, mock servers, or debug panels shipped
- Cache headers and cache-busting for the entry document
- Service worker: stale content trap, no update path, caching authenticated responses
