# Final CI-gate review

The six application findings remain resolved per CODEX-REVIEW-02-fixes.md. Review only the small
CI correction and final test-harness changes below; do not repeat the application survey.

Real local evidence showed the v15 bench command exiting zero despite a final unittest FAILED
summary. The workflow previously trusted only that exit code. It now invokes
`.github/helper/run_server_tests.sh`, which preserves combined output and process status, then
requires a recognized nonempty final unittest run with an adjacent successful summary. The
standalone fake-process tests run in CI and cover zero-exit failures, nonzero exits, missing/empty/
interrupted results, earlier success followed by failure, ANSI output, and argument forwarding.
The orchestrator also replayed the actual passing and failing server logs through this wrapper:
the passing log was accepted and the failing log rejected.

Review the wrapper, `.github/helper/test_server_test_gate.py`, workflow wiring, and corresponding
CONTRIBUTING/agent-guide instructions for false-green paths or accidental failure masking.
Existing matrix, pinned inputs, and upstream-drift policy are unchanged.

Also note final harness corrections: sudo tests reset their request path; the routing regression
restores its previous weak-bootstrap setting; and the new fallback Cypress spec asserts boolean
prototype presence instead of passing a native prototype to Cypress's object serializer.
The complete final runs passed 542 server tests, 182 JS tests on Node 18/24, and 66 browser tests
with zero skips/retries. Import isolation, build, and lint passed. These are orchestrator results,
not tests you ran. A prior browser transport failure coincided with the bench supervisor receiving
SIGTERM; restarting it restored the unchanged session-race tests.

Stay read-only: no file/Git changes, runtime tests, remote access, or external messages. Use
repository-relative file references. Report only concrete material defects; otherwise return GO
for these final changes. Preserve the limits of the preceding source review.

Your FINAL line must begin with GO or NO-GO.
