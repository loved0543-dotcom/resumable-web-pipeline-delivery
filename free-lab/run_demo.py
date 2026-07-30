"""One-command, fixed-fixture crash-and-resume proof."""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
INPUT = ROOT / "input.csv"
FIXTURES = ROOT / "fixtures"
RESULTS = OUTPUT / "results.csv"
STATE = OUTPUT / "state.json"
FETCH_LOG = OUTPUT / "fetch_log.csv"
RUN_LOG = OUTPUT / "run_log.csv"
RESULT_FIELDS = ("record_id", "url", "title", "price")


class LabError(RuntimeError):
    pass


class ProductParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active: str | None = None
        self.values: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        field = dict(attrs).get("data-field")
        if field in {"title", "price"}:
            self.active = field

    def handle_data(self, data):
        if self.active:
            self.values[self.active] = (
                self.values.get(self.active, "") + data
            ).strip()

    def handle_endtag(self, tag):
        self.active = None


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def append_csv(path: Path, fields: tuple[str, ...], row: dict[str, str]) -> None:
    add_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        if add_header:
            writer.writeheader()
        writer.writerow(row)


def write_csv_atomic(
    path: Path, fields: tuple[str, ...], rows: list[dict[str, str]]
) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def write_state(completed: set[str]) -> None:
    temporary = STATE.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps({"completed": sorted(completed)}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    os.replace(temporary, STATE)


def load_state() -> set[str]:
    if not STATE.exists():
        return set()
    return set(json.loads(STATE.read_text(encoding="utf-8"))["completed"])


def fetch_fixture(record: dict[str, str], run_label: str) -> str:
    path = FIXTURES / record["fixture"]
    if not path.is_file():
        raise LabError(f"missing fixture: {path.name}")
    append_csv(
        FETCH_LOG,
        ("run", "record_id", "fixture"),
        {
            "run": run_label,
            "record_id": record["record_id"],
            "fixture": record["fixture"],
        },
    )
    return path.read_text(encoding="utf-8")


def parse_product(html: str) -> dict[str, str]:
    parser = ProductParser()
    parser.feed(html)
    missing = {"title", "price"} - parser.values.keys()
    if missing:
        raise LabError(f"fixture missing fields: {', '.join(sorted(missing))}")
    return parser.values


def input_order(records: list[dict[str, str]]) -> list[str]:
    order: list[str] = []
    for record in records:
        if record["record_id"] not in order:
            order.append(record["record_id"])
    return order


def worker(run_label: str, stop_after: int | None) -> int:
    completed = load_state()
    rows = {row["record_id"]: row for row in read_csv(RESULTS)}
    records = read_csv(INPUT)
    seen: set[str] = set()
    new_count = 0

    for record in records:
        record_id = record["record_id"]
        if record_id in seen:
            append_csv(
                RUN_LOG,
                ("run", "event", "record_id"),
                {
                    "run": run_label,
                    "event": "duplicate_skipped",
                    "record_id": record_id,
                },
            )
            continue
        seen.add(record_id)

        # This check deliberately happens before fetch_fixture.
        if record_id in completed:
            append_csv(
                RUN_LOG,
                ("run", "event", "record_id"),
                {
                    "run": run_label,
                    "event": "completed_skipped",
                    "record_id": record_id,
                },
            )
            continue

        product = parse_product(fetch_fixture(record, run_label))
        rows[record_id] = {
            "record_id": record_id,
            "url": record["url"],
            "title": product["title"],
            "price": product["price"],
        }
        ordered = [rows[key] for key in input_order(records) if key in rows]

        # Deliverable truth first, resume truth second.
        write_csv_atomic(RESULTS, RESULT_FIELDS, ordered)
        completed.add(record_id)
        write_state(completed)
        append_csv(
            RUN_LOG,
            ("run", "event", "record_id"),
            {
                "run": run_label,
                "event": "record_completed",
                "record_id": record_id,
            },
        )

        new_count += 1
        if stop_after is not None and new_count >= stop_after:
            append_csv(
                RUN_LOG,
                ("run", "event", "record_id"),
                {
                    "run": run_label,
                    "event": "process_interrupted",
                    "record_id": record_id,
                },
            )
            os._exit(130)
    return 0


def reset_output() -> None:
    resolved_root = ROOT.resolve()
    resolved_output = OUTPUT.resolve()
    if resolved_output.parent != resolved_root:
        raise LabError("unsafe output path")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir()


def verify(run_1_exit: int) -> None:
    results = read_csv(RESULTS)
    fetches = read_csv(FETCH_LOG)
    events = read_csv(RUN_LOG)
    completed = load_state()
    refetched = sum(
        1
        for row in fetches
        if row["run"] == "2" and row["record_id"] == "sku-001"
    )
    duplicates = sum(
        1 for row in events if row["event"] == "duplicate_skipped"
    )

    if run_1_exit != 130:
        raise LabError(f"expected run 1 exit 130, got {run_1_exit}")
    if [row["record_id"] for row in results] != ["sku-001", "sku-002"]:
        raise LabError("results are incomplete or out of order")
    if completed != {"sku-001", "sku-002"}:
        raise LabError("checkpoint is incomplete")
    if refetched != 0:
        raise LabError("completed record was fetched again")
    if duplicates != 1:
        raise LabError("duplicate handling proof is invalid")

    print(f"RUN_1_EXIT={run_1_exit}")
    print(f"COMPLETED_RECORDS_REFETCHED={refetched}")
    print(f"FINAL_RECORDS={len(results)}")
    print(f"DUPLICATES_SKIPPED={duplicates}")
    print("LAB_OK")


def orchestrate() -> int:
    reset_output()
    command = [sys.executable, str(Path(__file__).resolve()), "--worker"]
    first = subprocess.run(
        command + ["--run", "1", "--stop-after", "1"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    second = subprocess.run(
        command + ["--run", "2"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if second.returncode != 0:
        detail = second.stderr.strip() or second.stdout.strip()
        raise LabError(f"run 2 failed: {detail}")
    verify(first.returncode)
    return 0


def main() -> int:
    try:
        if "--worker" in sys.argv:
            run_label = sys.argv[sys.argv.index("--run") + 1]
            stop_after = None
            if "--stop-after" in sys.argv:
                stop_after = int(sys.argv[sys.argv.index("--stop-after") + 1])
            return worker(run_label, stop_after)
        return orchestrate()
    except (LabError, OSError, ValueError, KeyError, IndexError) as error:
        print(f"LAB_ERROR: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
