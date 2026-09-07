# Lens audit disposition

Reviewed against d66001c and the accompanying corrections. Finding numbers refer to the
audit's Critical, Warning, and Info sections. The executive summary's categories and counts
do not consistently match its detailed findings; the detailed claims were checked individually.

No critical defect was confirmed in the supplied findings. This is a disposition of that
report, not a production-readiness attestation or a substitute for the separate whole-code review.

## Accepted changes

- **Info 50–51, partial:** remove the obsolete `record_password_failure` and
  `is_password_throttled` helpers. They still had test callers, but production already uses
  atomic `claim_password_attempt`. Update the endpoint tests to use that production primitive,
  retaining the threshold, correct-password rejection, session, and UV-state assertions.
- **Separately identified documentation mismatch:** align README's v15 minimum with the
  v15.108.0 floor already enforced by `install.py` and documented in `docs/install.md`.

## Findings requiring no change

| Findings | Reason |
| --- | --- |
| Critical 1, 3: guest writes | Login completion must remain reachable before session creation. `verify_second_factor` verifies a single-use, binder-bound ceremony, credential ownership and assertion, then rechecks password version and enabled account before updating. `complete_uv_setup` requires a previously verified UV assertion, binder, password, atomic setup consumption and locked credential checks. Removing guest access would break authentication. |
| Critical 2: controller lacks tests | `test_passkey.py` exercises real document validation and saves; `test_management_p6.py` exercises last-credential deletion/disable guards and lifecycle notifications. Frappe loads the controller dynamically; a colocated duplicate test file adds no coverage. |
| Warning 1: silent advisory exception | `_advise_dormant_once` is explicitly a best-effort diagnostic on every-request hooks after native core takes over. Redis or diagnostic failures must not break login. Adding a second unguarded logging call would violate this contract. |
| Warning 2: global state | `_CORE_NATIVE` caches a process-wide code capability, not site configuration or user authorization. Moving it to a class would not improve concurrency or state ownership. |
| Warning 3: read-only get_doc | The loaded User document is used to add/remove roles, not just read fields. |
| Warning 4; Info 19–23, 62–63: permission bypasses | Admin changes are System Manager gated; credential operations derive the owner from the session and enforce ownership, sudo or action grants. Registration verifies bound ceremonies before credential insertion. Install deletions target the app's own metadata; notification writes create server-authored audit records. These narrow paths intentionally bypass broad DocType permissions. |
| Warning 5–6: commit without catch | These are operator-only recovery/import functions. Failures propagate and command teardown closes the transaction. Wrapping only `commit` does not address earlier faults; a blanket rollback also affects the caller's unrelated transaction work. No partial committed write defect was demonstrated. |
| Info 1–9, 11, 18, 24–26, 54: commented code | All flagged snippets are explanatory prose, including security and bundle-order rationale. |
| Info 10, 27–34, 40–43, 59: unused classes | These are live exception bases/subclasses, verification result objects, wire-contract exceptions, and action policies, with actual raises, construction, or inheritance. |
| Info 12–15, 55–58: print | These are operator CLI messages: backup paths, restore instructions, rejected-row summaries and recovery results. Background logs would hide the expected command output. |
| Info 16–17: parameter count | Explicit keyword-only crypto/policy inputs are useful here. Packing them into dictionaries would not fix a demonstrated problem. |
| Info 35–39, 44–49, 52–53, 60–61: unused functions | Calls exist through decorators, callable arguments, documented console APIs, Frappe page conventions, or tests of stored counters. Retain the `get_counter` primitive. |
| Info 67: missing digest index | `credential_id_sha256` already has `unique: 1`, which creates a unique database index. The user field also explicitly has `search_index: 1`. Another index would be redundant. |

The summary's unenumerated claims about 19 endpoints and unrestricted `get_all` calls were also
checked against the production surface. Owner endpoints use server-derived session identity;
administrator/settings endpoints use explicit role gates; guest authentication and public
metadata endpoints have purpose-specific contracts. The reported three `flags.ignore_permissions`
assignments in `enforcement_admin.py` are actually one, reached through the administrator gate.

## Deferred suggestions

**Info 64–66:** shared private helpers and large wire/lifecycle modules are real observations,
but the proposed module splits demonstrate no functional defect and conflict with the current
core-adoption layout. Changing endpoint or documented console import paths adds compatibility
cost. Revisit when a concrete change requires new boundaries, not to meet a size heuristic.

## Second opinion and subsequent test corrections

Claude Fable 5.1 (`claude-fable-5-1`) reviewed these judgment calls with tools disabled and returned
GO. It received the complete install/recovery sources and distilled evidence for the other
decisions; it did not perform the whole-code review. Its cautions were to preserve exact throttle
thresholds and ensure updated button selectors still drive actual operations.

Separate upstream-drift investigation identified test assumptions rather than authentication
failures: Frappe now stores allowed HTTP methods as tuples and uses new dialog/login button
classes. The corrections normalize only the sequence representation and locate the corresponding
buttons across versions. Method/guest restrictions, real clicks, resulting database changes,
login status, redirects, and session assertions remain enforced.
