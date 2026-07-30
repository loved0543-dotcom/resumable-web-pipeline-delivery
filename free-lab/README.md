# Free fixed-fixture resume lab

This small public lab proves one narrow claim: after a real process stop, a new
process can skip a durably completed record before fetching it again.

Requirements: Python 3.10 or newer. The lab makes no network request and uses no
third-party package.

From the repository root:

```text
python free-lab/run_demo.py
```

Windows PowerShell alternative:

```text
powershell -ExecutionPolicy Bypass -File free-lab/run_demo.ps1
```

Expected proof:

```text
RUN_1_EXIT=130
COMPLETED_RECORDS_REFETCHED=0
FINAL_RECORDS=2
DUPLICATES_SKIPPED=1
LAB_OK
```

Generated evidence is written under `free-lab/output/`. The script deliberately
terminates worker 1 with exit code 130 after the first durable record. Worker 2
loads the checkpoint, skips that record before reading its fixture, processes
the remaining record, and skips one duplicate input.

## Deliberate limits

This is a fixed local demonstration, not a configurable scraper or a throughput
claim for arbitrary websites. The paid Field Manual explains the failure model,
crash windows, evidence reading, and production checklist. The Pipeline Kit
contains the configurable Playwright collection source, retry policy, logs,
report, and full tests.
