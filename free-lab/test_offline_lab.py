import csv
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SOURCE_LAB = Path(__file__).resolve().parent


class OfflineLabTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.lab = Path(self.temp_dir.name) / "free-lab"
        shutil.copytree(SOURCE_LAB, self.lab)

    def run_lab(self):
        return subprocess.run(
            [sys.executable, str(self.lab / "run_demo.py")],
            cwd=self.lab.parent,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def test_public_command_proves_resume_without_refetch(self):
        result = self.run_lab()

        self.assertEqual(result.returncode, 0, result.stderr)
        for proof in (
            "RUN_1_EXIT=130",
            "COMPLETED_RECORDS_REFETCHED=0",
            "FINAL_RECORDS=2",
            "DUPLICATES_SKIPPED=1",
            "LAB_OK",
        ):
            self.assertIn(proof, result.stdout)

        with (self.lab / "output" / "fetch_log.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            fetches = list(csv.DictReader(handle))
        self.assertEqual(
            [row["record_id"] for row in fetches].count("sku-001"), 1
        )

    def test_second_invocation_is_deterministic(self):
        first = self.run_lab()
        self.assertEqual(first.returncode, 0, first.stderr)
        first_csv = (self.lab / "output" / "results.csv").read_bytes()

        second = self.run_lab()

        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            (self.lab / "output" / "results.csv").read_bytes(), first_csv
        )

    def test_missing_fixture_fails_helpfully(self):
        (self.lab / "fixtures" / "product_b.html").unlink()

        result = self.run_lab()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing fixture", (result.stdout + result.stderr).lower())
        self.assertNotIn("LAB_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
