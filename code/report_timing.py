import csv, statistics as st, sys
R = r"C:\assignement\results"

DURATION_NAMES = ["duration_ms", "elapsed_ms", "time_ms", "ms",
                  "duration_s", "elapsed_s", "time_s", "seconds", "duration", "elapsed"]


def pick(cols, *names):
    low = {c.lower(): c for c in cols}
    for n in names:
        if n in low:
            return low[n]
    return None


def is_num(x):
    try:
        float(x)
        return True
    except (TypeError, ValueError):
        return False


def load(path):
    rows = list(csv.DictReader(open(path, newline="")))
    cols = list(rows[0].keys())
    print("HEADERS", path, cols)
    case = pick(cols, "case")
    status = pick(cols, "status")
    phase = pick(cols, "phase", "kind", "stage")
    ms = pick(cols, *DURATION_NAMES)
    if ms is None:
        # fall back: numeric columns that are not obviously something else
        skip = {"run", "rep", "repeat", "rows", "row_count", "n_rows", "cat_start", "start", "end"}
        cands = [c for c in cols if c.lower() not in skip
                 and all(is_num(r[c]) for r in rows if r[c] != "")
                 and any(r[c] != "" for r in rows)]
        print("No known duration column. Numeric candidates:", cands)
        sys.exit("Tell me which column is the duration and its unit.")
    scale = 1.0 if ms.lower().endswith("ms") or ms.lower() == "ms" else 1000.0
    print("case =", case, "| duration =", ms, "| x", scale, "| status =", status, "| phase =", phase)
    d, bad = {}, {}
    for r in rows:
        if phase and r[phase].strip().lower() in ("warmup", "warm-up", "warm"):
            continue
        if status and r[status].strip().lower() != "ok":
            bad.setdefault(r[case], []).append(r[status])
            continue
        if not is_num(r[ms]):
            continue
        d.setdefault(r[case], []).append(float(r[ms]) * scale)
    return d, bad


pg, pgbad = load(rf"{R}\timing_raw_pg.csv")
ne, nebad = load(rf"{R}\timing_raw_neo.csv")
out = []
for c in pg:
    p = st.median(pg[c])
    n = st.median(ne[c]) if ne.get(c) else None
    out.append([c, len(pg[c]), round(p, 1), round(min(pg[c]), 1), round(max(pg[c]), 1),
                len(ne.get(c, [])),
                None if n is None else round(n, 1),
                None if n is None else round(min(ne[c]), 1),
                None if n is None else round(max(ne[c]), 1),
                None if not n else round(p / n, 3)])
with open(rf"{R}\timing_summary.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["case", "pg_n", "pg_med_ms", "pg_min", "pg_max",
                "neo_n", "neo_med_ms", "neo_min", "neo_max", "pg_over_neo"])
    w.writerows(out)
for r in out:
    print(r)
print("errors/timeouts PG:", pgbad, "| Neo:", nebad)
