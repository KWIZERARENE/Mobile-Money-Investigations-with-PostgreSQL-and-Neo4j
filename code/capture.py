import csv, json, time
from itertools import islice
from pathlib import Path
import mobile_money_generator as g

DATA = Path(__file__).resolve().parent.parent / "data"
RESULTS = Path(__file__).resolve().parent.parent / "results"
DATA.mkdir(exist_ok=True); RESULTS.mkdir(exist_ok=True)

EXPECTED = {"customers": 228_000, "accounts": 248_000, "devices": 228_600,
            "account_devices": 285_600, "transfers": 20_003_300}
STREAMS = {"customers": g.iter_customers, "accounts": g.iter_accounts,
           "devices": g.iter_devices, "account_devices": g.iter_account_devices,
           "transfers": g.iter_transfers}

print(g.dataset_info()); print(g.FIELDS)
for name, fn in STREAMS.items():
    print(f"\n--- preview {name} ---")
    for row in islice(fn(), 10):
        print(row)

audit = {}
for name, fn in STREAMS.items():
    path = DATA / f"{name}.csv"
    consumed = written = 0
    t0 = time.perf_counter()
    stats = {"min_occurred_at": None, "max_occurred_at": None, "sum_amount_rwf": 0}
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=g.FIELDS[name], lineterminator="\n")
        w.writeheader()
        for row in fn():
            consumed += 1
            w.writerow(row); written += 1
            if name == "transfers":
                t = row["occurred_at"]
                if stats["min_occurred_at"] is None or t < stats["min_occurred_at"]:
                    stats["min_occurred_at"] = t
                if stats["max_occurred_at"] is None or t > stats["max_occurred_at"]:
                    stats["max_occurred_at"] = t
                stats["sum_amount_rwf"] += row["amount_rwf"]
                if consumed % 1_000_000 == 0:
                    print(f"transfers: {consumed:,} rows, {time.perf_counter()-t0:.0f}s", flush=True)
    secs = time.perf_counter() - t0
    audit[name] = {"consumed": consumed, "written": written,
                   "expected": EXPECTED[name], "matches_expected": written == EXPECTED[name],
                   "seconds": round(secs, 1), "csv_bytes": path.stat().st_size}
    if name == "transfers":
        audit[name].update(stats)
    print(f"{name}: {audit[name]}", flush=True)

audit["total_records"] = sum(audit[n]["written"] for n in EXPECTED)
print("TOTAL RECORDS:", audit["total_records"], "(expect 20,993,500)")
(RESULTS / "capture_audit.json").write_text(json.dumps(audit, indent=2))