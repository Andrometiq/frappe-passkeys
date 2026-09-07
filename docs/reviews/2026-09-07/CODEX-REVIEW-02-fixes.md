> File links were made relative to this report for publication. Review text and verdict are unchanged.

No unresolved material correctness or security defect was found in the six corrections or retained compatibility changes.

## Disposition of original findings

1. **Core-login dispatch confusion — Resolved.**  
   Truthy `cmd` now takes precedence and must equal literal `login`; otherwise only the exact canonical path qualifies. Sudo classification and OTP consumption share the predicate ([passkeys/session.py:136](../../../passkeys/session.py#L136), [passkeys/auth_hooks.py:128](../../../passkeys/auth_hooks.py#L128)). Regression coverage includes exact positive/negative shapes, preserved OTP markers, and the real v15 sequence of successful password login followed by diverted email-key dispatch. The enrolled target receives weak sudo and cannot use weak bootstrap for registration or management ([passkeys/tests/test_second_factor.py:415](../../../passkeys/tests/test_second_factor.py#L415), [passkeys/tests/test_second_factor.py:431](../../../passkeys/tests/test_second_factor.py#L431), [passkeys/tests/test_sudo_window.py:93](../../../passkeys/tests/test_sudo_window.py#L93)).

2. **Registration fallback serialization — Resolved.**  
   The dedicated serializer prefers native `toJSON`, otherwise preserves registration fields, extensions, attachment, and optional transports while excluding assertion-only fields ([passkeys/public/js/passkey_common.bundle.js:124](../../../passkeys/public/js/passkey_common.bundle.js#L124)). All three creation paths use it ([passkeys/public/js/passkey_headless.bundle.js:101](../../../passkeys/public/js/passkey_headless.bundle.js#L101), [passkeys/public/js/passkey_desk.bundle.js:144](../../../passkeys/public/js/passkey_desk.bundle.js#L144), [passkeys/public/js/passkey_desk.bundle.js:733](../../../passkeys/public/js/passkey_desk.bundle.js#L733)). Unit wiring and Chromium virtual-authenticator coverage exercise native serialization disabled through actual begin/create/verify flows.

3. **Enablement importability validation — Resolved.**  
   Off→on transitions run a fixed, shell-free, 30-second child-process import of the full engine using the current interpreter; stderr is bounded and every start, timeout, or nonzero failure refuses the save ([passkeys/policy.py:28](../../../passkeys/policy.py#L28), [passkeys/passkeys/doctype/passkey_settings/passkey_settings.py:50](../../../passkeys/passkeys/doctype/passkey_settings/passkey_settings.py#L50)). Existing enabled saves and disables do not probe. Tests cover each transition, genuine discoverable-but-broken dependencies, failure classes, and parent-process crypto-module hygiene ([passkeys/tests/test_dependency_probe.py:56](../../../passkeys/tests/test_dependency_probe.py#L56), [passkeys/tests/test_dependency_probe.py:93](../../../passkeys/tests/test_dependency_probe.py#L93), [passkeys/tests/test_dependency_probe.py:147](../../../passkeys/tests/test_dependency_probe.py#L147)).

4. **Server enforcement verdict — Resolved.**  
   Unknown events are rejected before evaluation. Current settings and enabled-credential count feed the canonical verdict before defer claims or enforcement mutations; ineligible events return unchanged state. Default Degrade produces neither the advisory nor its audit event, while applicable Block + Notify reports remain ([passkeys/passkey.py:930](../../../passkeys/passkey.py#L930), [passkeys/tests/test_enforcement.py:257](../../../passkeys/tests/test_enforcement.py#L257), [passkeys/tests/test_enforcement.py:327](../../../passkeys/tests/test_enforcement.py#L327)).

5. **Incapable-advisory concurrency — Resolved.**  
   Delivery locks the durable User row, then performs a locking marker read before enqueueing and marking ([passkeys/notifications.py:137](../../../passkeys/notifications.py#L137), [passkeys/notifications.py:175](../../../passkeys/notifications.py#L175)). The checked Frappe v15 queued-mail path does not commit between those operations, so the lock remains effective. Separate-connection coverage establishes stale snapshots and confirms one send; failure and recipient absence remain retryable ([passkeys/tests/test_notification_concurrency.py:44](../../../passkeys/tests/test_notification_concurrency.py#L44)). Recovery copy now names the implemented per-user exemption and grace reset controls.

6. **Translation cache partitioning — Resolved.**  
   Versioned and unversioned responses use `private, no-store`, and the browser explicitly requests `cache: "no-store"` while retaining merge behavior ([passkeys/passkey.py:855](../../../passkeys/passkey.py#L855), [passkeys/public/js/passkey_login.bundle.js:84](../../../passkeys/public/js/passkey_login.bundle.js#L84)). Tests cover both endpoint forms, changed languages on the same URL, and the published loader request.

## Retained candidate changes

The README’s v15.108 minimum remains consistent with the package constraint and install guard ([README.md:90](../../../README.md#L90), [pyproject.toml:23](../../../pyproject.toml#L23), [passkeys/install.py:21](../../../passkeys/install.py#L21)). Removed throttle helpers have no remaining callers; tests now use the production claim/counter contract. Tuple normalization preserves the exact POST-only assertion, and the revised Cypress selectors target visible modal and form-submit controls without weakening the tested browser behavior.

## Scope and limitations

Reviewed the current tracked diff from `d66001c`, the new untracked regression files, the preserved initial report, affected contracts/documentation, production callers, and relevant Python, Node, and Cypress test source. I did not repeat the untouched whole-code survey.

No tests, browser gates, bench operations, imports gates, remote access, or mutable commands were run. The orchestrator’s reported Node results and pending integrated gates are not claimed as independently verified. This is a scoped source-review verdict, not a production-readiness attestation.

GO — no unresolved material correctness or security defect was found in the scoped corrections.