# Free Lab Release Implementation Plan

> **실행 에이전트용:** 이 계획을 태스크 단위로 구현할 때 dynamic-workflow-orchestrator(태스크별 fresh subagent 디스패치, 권장) 또는 이 스킬의 executing-plans 절차(`references/executing-plans.md`)를 쓴다. 스텝은 체크박스(`- [ ]`) 문법으로 추적한다.

**Goal:** Publish the existing fixed-fixture lab as a verified one-click GitHub release ZIP and make that asset the primary Gumroad download link.

**Architecture:** A standard-library packaging script owns the exact archive allowlist, reproducible ZIP metadata, SHA-256 reporting, and extracted buyer-command verification. A black-box contract test proves the archive contents and output before the artifact is published as a non-latest GitHub release. Gumroad is changed only after a fresh public download passes the same hash and execution checks.

**Tech Stack:** Python 3.10+ standard library, `unittest`, Git/GitHub CLI, existing Chrome session for Gumroad.

## Global Constraints

- Tag `free-lab-v1.0.0`, title `Free Resume Lab v1.0.0`, asset `Free_Resume_Lab_v1.0.0.zip`.
- The free release must not become GitHub's latest release; paid Pipeline Kit `v1.0.1` remains latest.
- The ZIP contains exactly the seven paths in the approved design and no paid source, generated output, or bytecode.
- The extracted command is `python free-lab/run_demo.py` and must emit all five approved proof lines with exit zero.
- Packaging and lab execution use Python 3.10+ standard library only and require no network during the lab run.
- Existing paid Gumroad ZIP, price, other products, license, and unrelated untracked files remain unchanged.
- Existing tag or release means inspect and stop; never overwrite it.
- Gumroad links change only after the public asset hash and extracted execution match the local verified artifact.
- Execution mode: inline, because this is a short release-critical chain with strong state continuity and the user requested autonomous continuation.

---

### Task 1: Lock the release-package contract

**Files:**
- Create: `free-lab/test_release_package.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: future command `python free-lab/package_release.py`
- Produces: black-box assertions for archive path, exact entry names, proof output, SHA-256, and `PACKAGE_OK`

- [ ] **Step 1: Write the failing black-box test**

```python
EXPECTED = [
    "free-lab/README.md",
    "free-lab/run_demo.py",
    "free-lab/run_demo.ps1",
    "free-lab/input.csv",
    "free-lab/fixtures/product_a.html",
    "free-lab/fixtures/product_b.html",
    "free-lab/test_offline_lab.py",
]

def test_package_release_contract(self):
    completed = subprocess.run(
        [sys.executable, str(self.repo / "free-lab" / "package_release.py")],
        cwd=self.repo, text=True, capture_output=True
    )
    self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
    self.assertIn("PACKAGE_OK", completed.stdout)
    with zipfile.ZipFile(self.archive) as zipped:
        self.assertEqual(zipped.namelist(), EXPECTED)
```

- [ ] **Step 2: Run the test and confirm RED**

Run: `python -m unittest free-lab/test_release_package.py -v`

Expected: FAIL because `free-lab/package_release.py` does not exist.

- [ ] **Step 3: Ignore generated release artifacts**

```text
free-lab/dist/
```

- [ ] **Step 4: Commit the contract**

```text
git add .gitignore free-lab/test_release_package.py
git commit -m "test: lock free lab release package"
```

### Task 2: Build and verify the exact ZIP

**Files:**
- Create: `free-lab/package_release.py`
- Test: `free-lab/test_release_package.py`

**Interfaces:**
- Consumes: the seven approved repository files
- Produces: `free-lab/dist/Free_Resume_Lab_v1.0.0.zip` plus `ARCHIVE`, `BYTES`, `SHA256`, and `PACKAGE_OK` output lines

- [ ] **Step 1: Implement the minimum package owner**

```python
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
```

Write each allowlisted file with stable ZIP metadata, reopen and reject any name mismatch, extract to a temporary directory, run `[sys.executable, "free-lab/run_demo.py"]`, require exit zero and every proof line, then print the artifact path, byte size, SHA-256, and `PACKAGE_OK`.

- [ ] **Step 2: Run package and all lab tests**

Run:

```text
python -m unittest free-lab/test_release_package.py free-lab/test_offline_lab.py -v
python free-lab/package_release.py
```

Expected: all tests PASS; package output contains five proof lines, a 64-character SHA-256, and `PACKAGE_OK`.

- [ ] **Step 3: Directly inspect the generated archive**

Run a read-only Python ZIP inspection and confirm its ordered names equal `ARCHIVE_PATHS`, no name contains `output` or `__pycache__`, and a fresh extraction runs the buyer command successfully.

- [ ] **Step 4: Commit the package owner**

```text
git add free-lab/package_release.py
git commit -m "feat: package verified free resume lab"
```

### Task 3: Publish precise buyer documentation

**Files:**
- Modify: `README.md`
- Create: `free-lab/RELEASE_NOTES_v1.0.0.md`

**Interfaces:**
- Consumes: verified local artifact SHA-256 and byte size from Task 2
- Produces: stable direct asset link, exact extraction command, checksum, requirements, and narrow scope disclosure

- [ ] **Step 1: Add one-click download details**

Add the direct URL:

```text
https://github.com/loved0543-dotcom/resumable-web-pipeline-delivery/releases/download/free-lab-v1.0.0/Free_Resume_Lab_v1.0.0.zip
```

Record the observed byte size and SHA-256 in the root README, which is outside
the ZIP, and say to extract then run `python free-lab/run_demo.py`. Keep the
included `free-lab/README.md` free of a self-referential archive checksum.

- [ ] **Step 2: Write release notes**

State Python 3.10+, no third-party package, no network during execution, fixed fixtures, and that this is neither the configurable paid Pipeline Kit nor an arbitrary-site performance claim.

- [ ] **Step 3: Repackage and confirm the external checksum**

Run `python free-lab/package_release.py`, insert its final SHA-256 and size in
the root `README.md`, then run it again and confirm the printed values exactly
match the external documentation.

- [ ] **Step 4: Run the full free-lab suite**

Run: `python -m unittest discover -s free-lab -p "test_*.py" -v`

Expected: all tests PASS.

- [ ] **Step 5: Commit buyer documentation**

```text
git add README.md free-lab/RELEASE_NOTES_v1.0.0.md docs/superpowers/plans/2026-07-31-free-lab-release.md
git commit -m "docs: add one-click free lab download"
```

### Task 4: Publish the non-latest GitHub release

**Files:**
- No tracked file changes.

**Interfaces:**
- Consumes: committed release source and verified local ZIP
- Produces: public tag, release page, and downloadable asset while preserving the paid latest release

- [ ] **Step 1: Confirm the remote identity is unused**

Run:

```text
git ls-remote --tags origin refs/tags/free-lab-v1.0.0
gh release view free-lab-v1.0.0 --repo loved0543-dotcom/resumable-web-pipeline-delivery
```

Expected: no matching remote tag and release not found. If either exists, stop and inspect.

- [ ] **Step 2: Push the exact source state**

Run `git push origin main` and record the pushed commit SHA.

- [ ] **Step 3: Create the release as non-latest**

Run:

```text
gh release create free-lab-v1.0.0 free-lab/dist/Free_Resume_Lab_v1.0.0.zip --repo loved0543-dotcom/resumable-web-pipeline-delivery --target <pushed-sha> --title "Free Resume Lab v1.0.0" --notes-file free-lab/RELEASE_NOTES_v1.0.0.md --latest=false
```

- [ ] **Step 4: Verify release metadata**

Run `gh release view free-lab-v1.0.0 --repo loved0543-dotcom/resumable-web-pipeline-delivery --json assets,isLatest,tagName,url,targetCommitish`.

Expected: one correctly named asset and `isLatest:false`.

### Task 5: Verify the public buyer path

**Files:**
- No tracked file changes.

**Interfaces:**
- Consumes: public GitHub release asset
- Produces: public download hash, exact entry list, extracted command evidence, and paid-latest preservation evidence

- [ ] **Step 1: Download into a fresh temporary directory**

Use `gh release download free-lab-v1.0.0 --pattern Free_Resume_Lab_v1.0.0.zip --dir <temp>` and never reuse the local build artifact.

- [ ] **Step 2: Compare hash, size, and contents**

Expected: public SHA-256 and bytes equal the documented/local values and the ZIP contains exactly the seven approved paths.

- [ ] **Step 3: Extract and execute the buyer command**

Run `python free-lab/run_demo.py` from the extraction root.

Expected: exit zero and all five proof lines.

- [ ] **Step 4: Verify the paid latest release remains latest**

Run `gh release list --repo loved0543-dotcom/resumable-web-pipeline-delivery --limit 10`.

Expected: Pipeline Kit `v1.0.1` is marked Latest and the free-lab release is not.

### Task 6: Point Gumroad to the verified asset and record evidence

**Files:**
- Modify: `../STATUS.md`
- Modify: `../revenue_ledger.csv`

**Interfaces:**
- Consumes: verified public direct-download URL and final public evidence
- Produces: saved Gumroad Content/public description, readback verification, metrics snapshot, and low-load browser final state

- [ ] **Step 1: Open one Chrome tab through the existing logged-in session**

Keep only the required Gumroad tab and do not create another profile or browser.

- [ ] **Step 2: Replace only the primary free-lab folder link**

In both purchase Content and public description, replace the repository-folder URL with the verified direct release-asset URL. Preserve the source-file link, current v1.0 delivery disclosure, existing paid ZIP, price, and all other product state.

- [ ] **Step 3: Save, reload, and read back both surfaces**

Expected: both surfaces contain the exact direct asset URL and retain the separate-free-lab/current-v1.0 disclosures.

- [ ] **Step 4: Capture current sales metrics**

Record current Gumroad sales, views, and revenue without claiming that views or test attempts are sales.

- [ ] **Step 5: Finalize browser and append the audit trail**

Return Chrome to exactly one `about:blank` tab. Append timestamped public URL, commit/tag, byte size, SHA-256, extracted proof, Gumroad readback, metrics, and any remaining CAPTCHA limitation to `STATUS.md` and `revenue_ledger.csv`.
