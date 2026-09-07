#!/usr/bin/env bash
# Fail closed when a Frappe test runner prints failure but exits successfully.

set -euo pipefail

if [[ $# -ne 1 || -z "$1" ]]; then
	echo "usage: $0 <site>" >&2
	exit 2
fi

site=$1
output_file=$(mktemp)
trap 'rm -f "$output_file"' EXIT

if bench --site "$site" run-tests --app passkeys 2>&1 | tee "$output_file"; then
	bench_status=0
else
	bench_status=$?
fi

if (( bench_status != 0 )); then
	echo "server tests: bench exited with status $bench_status" >&2
	exit "$bench_status"
fi

python - "$output_file" <<'PY'
import re
import sys
from pathlib import Path

ANSI_ESCAPE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
RUN_SUMMARY = re.compile(r"^Ran ([0-9]+) tests? in [^\r\n]+$", re.MULTILINE)
FINAL_SUMMARY = re.compile(r"\s*(OK|FAILED)(?: \([^\r\n]*\))?\s*(?:\r?\n|$)")

output = ANSI_ESCAPE.sub("", Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace"))
runs = list(RUN_SUMMARY.finditer(output))
if not runs:
	raise SystemExit("server tests: missing or unrecognized unittest run summary")

last_run = runs[-1]
if int(last_run.group(1)) == 0:
	raise SystemExit("server tests: unittest ran zero tests")
summary = FINAL_SUMMARY.match(output, last_run.end())
if not summary:
	raise SystemExit("server tests: missing successful final unittest summary")
if summary.group(1) == "FAILED":
	raise SystemExit("server tests: unittest reported a FAILED final summary")
PY
