import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "free-lab" / "dist" / "Free_Resume_Lab_v1.0.0.zip"
EXPECTED_PATHS = [
    "free-lab/README.md",
    "free-lab/run_demo.py",
    "free-lab/run_demo.ps1",
    "free-lab/input.csv",
    "free-lab/fixtures/product_a.html",
    "free-lab/fixtures/product_b.html",
    "free-lab/test_offline_lab.py",
]
PROOF_LINES = [
    "RUN_1_EXIT=130",
    "COMPLETED_RECORDS_REFETCHED=0",
    "FINAL_RECORDS=2",
    "DUPLICATES_SKIPPED=1",
    "LAB_OK",
]


class ReleasePackageTests(unittest.TestCase):
    def test_public_package_command_builds_verified_buyer_zip(self):
        shutil.rmtree(ARCHIVE.parent, ignore_errors=True)

        result = subprocess.run(
            [sys.executable, str(REPO / "free-lab" / "package_release.py")],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PACKAGE_OK", result.stdout)
        self.assertRegex(result.stdout, r"SHA256=[0-9A-F]{64}\b")
        self.assertRegex(result.stdout, r"BYTES=[1-9][0-9]*\b")
        self.assertTrue(ARCHIVE.is_file())
        with zipfile.ZipFile(ARCHIVE) as packaged:
            self.assertEqual(packaged.namelist(), EXPECTED_PATHS)

        with tempfile.TemporaryDirectory() as temp_dir:
            with zipfile.ZipFile(ARCHIVE) as packaged:
                packaged.extractall(temp_dir)
            buyer = subprocess.run(
                [sys.executable, "free-lab/run_demo.py"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
        self.assertEqual(buyer.returncode, 0, buyer.stdout + buyer.stderr)
        for proof in PROOF_LINES:
            self.assertIn(proof, buyer.stdout)

        reported_hash = re.search(
            r"SHA256=([0-9A-F]{64})\b", result.stdout
        )
        self.assertIsNotNone(reported_hash)


if __name__ == "__main__":
    unittest.main()
