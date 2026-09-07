# Copyright (c) 2026, Frappe Passkeys Contributors
# License: MIT. See LICENSE

"""Process-boundary tests for the fail-closed server-test wrapper."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / ".github" / "helper" / "run_server_tests.sh"


class ServerTestGateTest(unittest.TestCase):
	def setUp(self):
		self.directory = tempfile.TemporaryDirectory()
		self.addCleanup(self.directory.cleanup)
		self.bin_directory = Path(self.directory.name)
		self.args_file = self.bin_directory / "args.json"
		bench = self.bin_directory / "bench"
		bench.write_text(
			"""#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

Path(os.environ["FAKE_BENCH_ARGS"]).write_text(json.dumps(sys.argv[1:]), encoding="utf-8")
sys.stdout.write(os.environ.get("FAKE_BENCH_OUTPUT", ""))
raise SystemExit(int(os.environ.get("FAKE_BENCH_STATUS", "0")))
""",
			encoding="utf-8",
		)
		bench.chmod(0o755)

	def run_gate(self, output: str, status: int = 0):
		environment = os.environ.copy()
		environment.update(
			{
				"PATH": str(self.bin_directory) + os.pathsep + environment["PATH"],
				"FAKE_BENCH_ARGS": str(self.args_file),
				"FAKE_BENCH_OUTPUT": output,
				"FAKE_BENCH_STATUS": str(status),
			}
		)
		return subprocess.run(
			["bash", str(GATE), "test_site"],
			cwd=ROOT,
			env=environment,
			capture_output=True,
			text=True,
			check=False,
		)

	def assert_rejected(self, output: str, status: int = 0):
		result = self.run_gate(output, status)
		self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

	def test_passing_nonempty_run_is_accepted_and_forwarded_exactly(self):
		output = (
			"expected nested-runner log\nFAILED (failures=1)\n"
			"RuntimeError: expected\nRan 3 tests in 0.100s\n\nOK\n"
		)
		result = self.run_gate(output)
		self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
		self.assertEqual(
			json.loads(self.args_file.read_text()), ["--site", "test_site", "run-tests", "--app", "passkeys"]
		)
		self.assertEqual(result.stdout, output)

	def test_failed_summary_is_rejected_even_when_bench_exits_zero(self):
		self.assert_rejected("Ran 2 tests in 0.100s\n\nFAILED (failures=1)\n")

	def test_nonzero_bench_status_is_propagated_despite_ok_summary(self):
		result = self.run_gate("Ran 2 tests in 0.100s\n\nOK\n", status=7)
		self.assertEqual(result.returncode, 7, result.stdout + result.stderr)

	def test_zero_tests_is_rejected(self):
		self.assert_rejected("Ran 0 tests in 0.000s\n\nOK\n")

	def test_missing_summary_is_rejected(self):
		self.assert_rejected("test output stopped before its runner summary\n")

	def test_earlier_ok_does_not_hide_later_failure(self):
		self.assert_rejected("Ran 1 test in 0.010s\n\nOK\nRan 1 test in 0.010s\n\nFAILED (errors=1)\n")

	def test_ansi_colored_success_is_accepted(self):
		result = self.run_gate("\x1b[32mRan 4 tests in 0.100s\x1b[0m\n\n\x1b[32mOK\x1b[0m\n")
		self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

	def test_interrupted_or_unrecognized_final_summary_is_rejected(self):
		for summary in ("", "unrecognized result\n"):
			with self.subTest(summary=summary):
				self.assert_rejected("Ran 1 test in 0.010s\n\nOK\nRan 2 tests in 0.100s\n\n" + summary)


if __name__ == "__main__":
	unittest.main()
