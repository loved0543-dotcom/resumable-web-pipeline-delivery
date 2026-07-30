"""Build and verify the one-click free-lab release archive."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
DIST = REPO / "free-lab" / "dist"
ARCHIVE = DIST / "Free_Resume_Lab_v1.0.0.zip"
ARCHIVE_PATHS = (
    "free-lab/README.md",
    "free-lab/run_demo.py",
    "free-lab/run_demo.ps1",
    "free-lab/input.csv",
    "free-lab/fixtures/product_a.html",
    "free-lab/fixtures/product_b.html",
    "free-lab/test_offline_lab.py",
)
PROOF_LINES = (
    "RUN_1_EXIT=130",
    "COMPLETED_RECORDS_REFETCHED=0",
    "FINAL_RECORDS=2",
    "DUPLICATES_SKIPPED=1",
    "LAB_OK",
)
ZIP_TIMESTAMP = (2026, 7, 31, 0, 0, 0)


class PackageError(RuntimeError):
    pass


def build_archive() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as packaged:
        for relative in ARCHIVE_PATHS:
            source = REPO / relative
            if not source.is_file():
                raise PackageError(f"missing release source: {relative}")
            info = zipfile.ZipInfo(relative, date_time=ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            packaged.writestr(info, source.read_bytes(), compresslevel=9)


def verify_archive() -> str:
    with zipfile.ZipFile(ARCHIVE) as packaged:
        if tuple(packaged.namelist()) != ARCHIVE_PATHS:
            raise PackageError("archive entry contract mismatch")
        with tempfile.TemporaryDirectory() as temp_dir:
            packaged.extractall(temp_dir)
            buyer = subprocess.run(
                [sys.executable, "free-lab/run_demo.py"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
    if buyer.returncode != 0:
        detail = buyer.stderr.strip() or buyer.stdout.strip()
        raise PackageError(f"buyer command failed: {detail}")
    missing = [proof for proof in PROOF_LINES if proof not in buyer.stdout]
    if missing:
        raise PackageError(f"buyer proof missing: {', '.join(missing)}")
    return buyer.stdout.strip()


def main() -> int:
    try:
        build_archive()
        proof = verify_archive()
        digest = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest().upper()
        print(proof)
        print(f"ARCHIVE={ARCHIVE.relative_to(REPO).as_posix()}")
        print(f"BYTES={ARCHIVE.stat().st_size}")
        print(f"SHA256={digest}")
        print("PACKAGE_OK")
        return 0
    except (OSError, PackageError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        print(f"PACKAGE_ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
