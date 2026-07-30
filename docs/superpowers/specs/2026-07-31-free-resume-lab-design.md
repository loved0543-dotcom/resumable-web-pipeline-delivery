# Free Resume Lab Design

## Goal

Give a buyer one public, runnable proof that the interruption claim is real
before purchase, without publishing the configurable Pipeline Kit or the paid
Field Manual's explanation and production checklist.

## Approaches considered

1. **Add `free-lab/` to the existing evidence repository — selected.**
   The product proof, test history, purchase links, and runnable sample remain
   in one trusted location.
2. Create a separate repository. This gives the lab a clean name but splits the
   small amount of existing traffic and trust.
3. Publish only a ZIP or Gist. This is quick but weakens code review,
   reproducible testing, and release provenance.

## Public contract

After cloning or downloading the repository, a visitor runs:

```text
python free-lab/run_demo.py
```

Python 3.10 or newer is the only requirement. The command makes no network
request and installs no package. It must print:

```text
RUN_1_EXIT=130
COMPLETED_RECORDS_REFETCHED=0
FINAL_RECORDS=2
DUPLICATES_SKIPPED=1
LAB_OK
```

## Included scope

- One fixed three-row input containing two unique IDs and one duplicate
- Two local HTML fixtures
- One standard-library Python runner
- One PowerShell launcher
- Black-box tests for the buyer command, deterministic reruns, and a missing
  fixture error
- A GitHub Actions workflow that runs the public tests on supported Python
  versions

## Excluded scope

- Configurable selectors, arbitrary URLs, Playwright, network collection,
  production retry policy, reporting UI, or reusable Pipeline Kit internals
- The Field Manual PDF, its explanatory chapters, or its production checklist
- Any claim that the fixed fixture proves performance on an arbitrary website

## Runtime behavior

The parent command removes only its own `free-lab/output/` directory. Worker 1
writes `results.csv` first, writes `state.json` second, records the event, and
terminates with exit code 130. Worker 2 reads the checkpoint, skips `sku-001`
before opening its fixture, processes `sku-002`, and records one duplicate
skip. Verification derives the five proof lines from the generated files.

## Error handling

A missing or malformed fixture exits nonzero with a `LAB_ERROR` message and
never prints `LAB_OK`. Output replacement is atomic and limited to the lab's
own directory.

## Evidence and release

The local black-box tests and the direct buyer command must pass before commit.
The commit must contain only the new lab, its workflow, the README change, and
this design/plan; unrelated untracked repository files remain untouched.
After push, the public GitHub README and workflow state must be read back.

## Commercial boundary

The README explicitly says the free lab proves one fixed interruption path.
The $9 manual sells the reasoning, crash-window analysis, and operating
checklist. The Pipeline Kit sells configurable collection source, retry,
logging, reporting, and tests.
