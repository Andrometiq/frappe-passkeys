> File links were made repository-relative for publication. Review text and verdict are unchanged.

## Demonstrated findings

1. **High — spoofable dispatch identity upgrades weak login and can bypass the OTP/passkey veto.**  
   [session.py:136](../../../passkeys/session.py#L136) treats the `/api/method/login` path alone as proof of password authentication. [auth_hooks.py:136](../../../passkeys/auth_hooks.py#L136) similarly accepts an OTP fallback when either the path or `cmd` resembles core login. Frappe processes client-controlled `form_dict.cmd` before the URL route; the app already recognizes this at [auth_hooks.py:176](../../../passkeys/auth_hooks.py#L176).

   - Trigger: redeem a valid email-login key through `/api/method/login?cmd=frappe.www.login.login_via_key&key=…`. The resulting email-link session is classified as password-grade and receives management sudo. For an enrolled second-factor user, a pending app-issued OTP marker plus this diverted request and any non-empty `otp` also satisfies the final veto without core verifying that OTP.
   - Impact: a one-time weak login can add or remove passkeys and become persistent credential access. A password plus alternate-login link can bypass the configured passkey/OTP second factor.
   - Smallest correction: centralize an exact core-login dispatch predicate: accept `cmd=="login"`, or the canonical login path only when `cmd` is absent or `"login"`. Use it in both locations.
   - Regression coverage: test the login path with `cmd=frappe.www.login.login_via_key`; assert a `weak` sudo window, management refusal, OTP-veto failure, and that the unused OTP marker remains intact. Add an end-to-end email-link variant.

2. **Medium — registration fallback serializes attestations as authentication assertions.**  
   [passkey_headless.bundle.js:109](../../../passkeys/public/js/passkey_headless.bundle.js#L109), [passkey_desk.bundle.js:144](../../../passkeys/public/js/passkey_desk.bundle.js#L144), and [passkey_desk.bundle.js:733](../../../passkeys/public/js/passkey_desk.bundle.js#L733) fall back to [authAssertionToJSON](../../../passkeys/public/js/passkey_common.bundle.js#L100) when `credential.toJSON` is unavailable.

   - Trigger: a WebAuthn-capable browser supports `navigator.credentials.create()` but lacks the newer `PublicKeyCredential.toJSON()`. The fallback emits `authenticatorData`, `signature`, and `userHandle`, but omits required registration fields `attestationObject` and transports.
   - Impact: explicit enrollment, portal/headless enrollment, and conditional creation all fail server verification on that supported fallback path.
   - Smallest correction: add a dedicated registration serializer emitting `clientDataJSON`, `attestationObject`, `transports`, `rawId`, attachment, and extension results; use it at all three creation sites.
   - Regression coverage: pass a live-style attestation object without `toJSON` through the browser wiring and assert the exact `RegistrationResponseJSON` submitted to `verify_registration`.

3. **Medium — enablement checks module discoverability, not the documented importability.**  
   [policy.py:20](../../../passkeys/policy.py#L20) uses only `find_spec("webauthn")`, while [passkey_settings.py:50](../../../passkeys/passkeys/doctype/passkey_settings/passkey_settings.py#L50) and [install.md:32](../../../docs/install.md#L32) promise refusal when WebAuthn is not importable.

   - Trigger: `webauthn` has a discoverable package but importing it or an engine dependency such as `cbor2`/`cryptography` raises.
   - Impact: settings can enable an unusable authentication mode; ceremonies then fail during lazy import. Existing passkey-only users can be stranded until operator repair.
   - Smallest correction: perform an actual lazy import of the ceremony engine or required WebAuthn symbols during enablement validation, catch import failures, and preserve the current import-clean hook paths.
   - Regression coverage: simulate a present spec whose loader raises and assert that saving enabled settings is rejected.

4. **Low — enforcement reporting does not enforce the server-owned verdict.**  
   [passkey.py:941](../../../passkeys/passkey.py#L941) mutates grace state or reports incapability without calling [build_enforcement](../../../passkeys/boot.py#L233).

   - Trigger: an authenticated user who is out of scope, exempt, already enrolled, or on an Off/Nudge policy directly posts `defer` or `incapable`.
   - Impact: the user can prematurely consume future grace; a retained Block-and-Notify setting can create false audit events and manager alerts. This is not a cross-account or authentication bypass.
   - Smallest correction: calculate the current verdict and credential count before claiming the session event. Accept defer only for an unenrolled in-scope user with grace remaining, and incapable reporting only for the applicable in-scope policy.
   - Regression coverage: exercise Off, Nudge, exempt, out-of-role, enrolled, blocking, and valid-grace cases.
   - Documentation also conflicts at [configuration.md:83](../../../docs/configuration.md#L83), which says the default Degrade policy emails administrators although the implementation does not.

5. **Low — incapable-device email deduplication is non-atomic.**  
   [notifications.py:153](../../../passkeys/notifications.py#L153) checks the marker, sends, and only then records it at [notifications.py:167](../../../passkeys/notifications.py#L167).

   - Trigger: parallel first reports for one user all read an absent marker before any writes it.
   - Impact: multiple administrator emails violate the documented once-per-user-per-24-hour guarantee.
   - Smallest correction: serialize this section with a per-user distributed lock or atomic idempotency claim, preserving retry after dispatch failure.
   - Regression coverage: race concurrent reports and assert exactly one send. Also assert corrected recovery copy—the current email recommends a nonexistent role-wide exempt list at [notifications.py:160](../../../passkeys/notifications.py#L160).

6. **Low — guest translation caching is not keyed by language or the claimed version.**  
   [passkey_login.bundle.js:90](../../../passkeys/public/js/passkey_login.bundle.js#L90) always fetches the same unversioned URL, despite the immutable/version contract in [passkey.py:877](../../../passkeys/passkey.py#L877).

   - Trigger: change `preferred_language` in the same browser within the five-minute private cache lifetime.
   - Impact: the cached catalog can render the previous language; the claimed versioned cache-busting path is never used.
   - Smallest correction: key the request URL by app version and request language, or use appropriate `Vary`/no-cache semantics.
   - Regression coverage: switch languages within the cache window and verify a correctly partitioned request and label.

## Scope and limitations

Reviewed base `d66001c7` plus all nine tracked working-tree modifications across server endpoints, WebAuthn engine, state, hooks, DocTypes, install/migration/recovery, browser bundles, CI, documentation, and relevant Python/Node/Cypress tests. The untracked `docs/reviews/` directory was excluded. Binary screenshots and logos were inventoried but not visually assessed.

The candidate diff itself introduced no identified defect: its version-floor correction is consistent, removed throttle wrappers have no callers, and the test compatibility/selector updates preserve their contracts.

Read-only validation completed:

- All 11 JavaScript unit files passed.
- Every tracked JavaScript file passed `node --check`.
- All tracked JSON parsed successfully.
- All 73 tracked Python files passed AST parsing.
- `git diff --check` was clean, and Git state remained unchanged.

Per instruction, I did not run mutable bench integration tests, Cypress/browser ceremonies, live DB/Redis/mail tests, or contact remotes. Ruff was unavailable. Exact pinned CI Frappe revisions were not fetched; dispatcher precedence was corroborated against locally available Frappe trees and the application’s own documented assumptions.

The documented post-login nature of enrollment enforcement, restricted weak first enrollment, and non-`__Host-` binder policy were treated as accepted policy—not defects. Guest writes were traced through their ceremony, origin, binder, session, ownership, and transaction gates.

NO-GO — the dispatch-confusion vulnerability and broken registration fallback are unresolved material security and correctness defects.