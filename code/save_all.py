import csv, json, os, time
from db import run_pg, run_neo
from run_all import build_cases

OUT = r"C:\assignement\results\full"
os.makedirs(OUT, exist_ok=True)
summary, report = [], []


def clean(qn, rows):
    """Convert rows to lists. For Q7, SQL returns [None] when no path exists
    while Cypher returns no row, so drop that encoding difference only."""
    rows = [list(r) for r in rows]
    if qn == "Q7":
        rows = [r for r in rows if r != [None]]
    return rows


def key(rows):
    return sorted(map(repr, rows))


for qn, s, params, sql, cyp in build_cases():
    k = params.get("k", "")
    label = qn if s == "-" else f"{qn}-{s}"
    if k != "":
        label += f"-k{k}"
    rec = dict(case=label, params=params)
    try:
        t = time.perf_counter()
        pg = clean(qn, run_pg(sql, params))
        rec["pg_s"] = round(time.perf_counter() - t, 3)

        t = time.perf_counter()
        neo = clean(qn, run_neo(cyp, params))
        rec["neo_s"] = round(time.perf_counter() - t, 3)

        rec.update(pg_rows=len(pg), neo_rows=len(neo),
                   match=key(pg) == key(neo), pg=pg, neo=neo, status="ok")
    except Exception as e:
        rec.update(status="error", err=str(e)[:300], match=False)

    with open(os.path.join(OUT, label + ".json"), "w") as f:
        json.dump(rec, f, default=str, indent=1)

    summary.append({k2: rec.get(k2) for k2 in
                    ("case", "pg_rows", "neo_rows", "match", "status", "pg_s", "neo_s")})
    report.append(
        f"=== {label} | params={params} | pg={rec.get('pg_rows')} "
        f"neo={rec.get('neo_rows')} match={rec.get('match')}\n"
        f"PG : {str(rec.get('pg'))[:1500]}\n"
        f"NEO: {str(rec.get('neo'))[:1500]}\n")
    print(label, rec.get("pg_rows"), rec.get("neo_rows"), rec.get("match"), rec.get("status"))

with open(r"C:\assignement\results\summary.csv", "w", newline="") as f:
    w = csv.DictWriter(f, summary[0].keys())
    w.writeheader()
    w.writerows(summary)

with open(r"C:\assignement\results\all_answers.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(report))

bad = [r["case"] for r in summary if not r["match"] or r["status"] != "ok"]
print(f"\n{len(summary)} cases saved, {len(bad)} mismatches or errors", bad if bad else "")
print("Files in C:\\assignement\\results")

