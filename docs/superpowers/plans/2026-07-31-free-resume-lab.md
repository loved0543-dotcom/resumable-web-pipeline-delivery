# Free Resume Lab Implementation Plan

> **실행 에이전트용:** 이 계획을 태스크 단위로 구현할 때
> implementation-planning의 executing-plans 절차를 쓴다. 이 변경은 한
> 저장소의 짧고 강하게 연결된 작업이므로 인라인 실행을 선택한다.

**Goal:** Publish a free, one-command, fixed-fixture interruption proof in the
existing public evidence repository.

**Architecture:** `free-lab/run_demo.py` owns a small parent/worker process
boundary and derives proof from CSV and JSON files under `free-lab/output/`.
Black-box tests invoke only the public command. The root README and CI workflow
make the lab discoverable and reproducible without exposing paid product scope.

**Tech Stack:** Python 3.10+ standard library, `unittest`, GitHub Actions

## Global Constraints

- Public command: `python free-lab/run_demo.py`.
- No network requests or third-party Python packages.
- Print exactly the five required proof lines ending in `LAB_OK`.
- Fixed fixtures only; no configurable selectors, URLs, or paid product source.
- Do not add unrelated existing untracked files to a commit.

---

### Task 1: Public black-box contract

**Files:**
- Create: `free-lab/test_offline_lab.py`
- Create: `free-lab/input.csv`
- Create: `free-lab/fixtures/product_a.html`
- Create: `free-lab/fixtures/product_b.html`

**Interfaces:**
- Consumes: `python free-lab/run_demo.py`
- Produces: three `unittest` cases for success proof, deterministic reruns, and
  missing-fixture failure

- [ ] **Step 1: Write the failing public-command test**

```python
result = subprocess.run(
    [sys.executable, str(lab / "run_demo.py")],
    cwd=lab.parent,
    capture_output=True,
    text=True,
)
self.assertEqual(result.returncode, 0, result.stderr)
self.assertIn("RUN_1_EXIT=130", result.stdout)
self.assertIn("COMPLETED_RECORDS_REFETCHED=0", result.stdout)
self.assertIn("FINAL_RECORDS=2", result.stdout)
self.assertIn("DUPLICATES_SKIPPED=1", result.stdout)
self.assertIn("LAB_OK", result.stdout)
```

- [ ] **Step 2: Confirm RED**

Run: `python -m unittest free-lab/test_offline_lab.py -v`

Expected: FAIL because `free-lab/run_demo.py` does not exist.

- [ ] **Step 3: Add fixed input and fixtures**

`input.csv` contains `sku-001`, `sku-002`, and a second `sku-002`. Each fixture
contains one `data-field="title"` and one `data-field="price"` value.

- [ ] **Step 4: Keep the test red**

Run: `python -m unittest free-lab/test_offline_lab.py -v`

Expected: FAIL because the public runner still does not exist.

### Task 2: Minimal public runner

**Files:**
- Create: `free-lab/run_demo.py`
- Create: `free-lab/run_demo.ps1`
- Create: `free-lab/README.md`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `free-lab/input.csv` and `free-lab/fixtures/*.html`
- Produces: `free-lab/output/results.csv`, `state.json`, `fetch_log.csv`,
  `run_log.csv`, and five proof lines

- [ ] **Step 1: Implement the process boundary**

```python
run_1 = subprocess.run(command + ["--run", "1", "--stop-after", "1"])
run_2 = subprocess.run(command + ["--run", "2"])
```

Worker 1 atomically writes results first and state second, then calls
`os._exit(130)`. Worker 2 checks completed IDs before `fetch_fixture`.

- [ ] **Step 2: Implement proof verification**

```python
print(f"RUN_1_EXIT={run_1_exit}")
print(f"COMPLETED_RECORDS_REFETCHED={completed_refetched}")
print(f"FINAL_RECORDS={len(results)}")
print(f"DUPLICATES_SKIPPED={duplicates_skipped}")
print("LAB_OK")
```

- [ ] **Step 3: Add buyer instructions and generated-output ignore**

The README gives the Python command first and PowerShell alternative second.
`.gitignore` excludes `free-lab/output/` and `__pycache__/`.

- [ ] **Step 4: Confirm GREEN**

Run: `python -m unittest free-lab/test_offline_lab.py -v`

Expected: `Ran 3 tests ... OK`.

Run: `python free-lab/run_demo.py`

Expected: exit 0 and all five proof lines.

- [ ] **Step 5: Commit**

```text
git add .gitignore free-lab
git commit -m "feat: publish free interruption proof lab"
```

### Task 3: Discovery, CI, and public verification

**Files:**
- Modify: `README.md`
- Create: `.github/workflows/free-lab.yml`

**Interfaces:**
- Consumes: the verified `free-lab/` public contract
- Produces: root discovery copy, commercial-scope boundary, and CI execution on
  Python 3.10 and 3.12

- [ ] **Step 1: Add a root README section**

The section includes the buyer command, five expected lines, a link to
`free-lab/README.md`, and a three-way boundary: free proof lab, $9 manual, and
configurable Pipeline Kit.

- [ ] **Step 2: Add GitHub Actions**

```yaml
strategy:
  matrix:
    python-version: ["3.10", "3.12"]
steps:
  - uses: actions/checkout@v4
  - uses: actions/setup-python@v5
    with:
      python-version: ${{ matrix.python-version }}
  - run: python -m unittest free-lab/test_offline_lab.py -v
  - run: python free-lab/run_demo.py
```

- [ ] **Step 3: Run local final verification**

Run: `python -m unittest free-lab/test_offline_lab.py -v`

Expected: `Ran 3 tests ... OK`.

Run: `python free-lab/run_demo.py`

Expected: exit 0 and all five proof lines.

Run: `git diff --check`

Expected: no errors.

- [ ] **Step 4: Commit**

```text
git add README.md .github/workflows/free-lab.yml
git commit -m "docs: expose free resume proof"
```

- [ ] **Step 5: Push and verify public state**

Run: `git push origin main`

Expected: the remote accepts both commits. Verify the public README contains
`python free-lab/run_demo.py`, the public workflow file exists, and the CI run
reaches a terminal state before claiming it passed.
