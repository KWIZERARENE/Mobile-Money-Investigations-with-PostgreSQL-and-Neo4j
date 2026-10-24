import csv, json, sys, time, os
from db import run_pg, run_neo
from timeutil import hour_window
import queries as q
from cases import SETS

OUT = r"C:\assignement\results"
os.makedirs(OUT, exist_ok=True)

def build_cases():
    cs = []
    for s, p in SETS.items():
        st, en = hour_window(p["day"])
        w = dict(acc=p["acc"], start=st, end=en)
        cs.append(("Q1", s, w, q.Q1_SQL, q.Q1_CYPHER))
        cs.append(("Q3", s, dict(acc=p["acc"]), q.Q3_SQL, q.Q3_CYPHER))
        cs.append(("Q5", s, w, q.Q5_SQL, q.Q5_CYPHER))
        cs.append(("Q6", s, w, q.Q6_SQL, q.Q6_CYPHER))
        for k in (4, 6, 8, 10):
            cs.append(("Q4", s, dict(acc=p["acc"], k=k), q.Q4_SQL, q.q4_cypher(k)))
        for k in (4, 6):
            cs.append(("Q7", s, dict(src=p["acc"], dst=p["dst"], k=k), q.Q7_SQL, q.q7_cypher(k)))
    cs.append(("Q2", "-", {}, q.Q2_SQL, q.Q2_CYPHER))
    return cs

def clean(qn, rows):
    if qn == "Q7":                      # SQL returns (None,) when no path; Cypher returns no row
        rows = [r for r in rows if r != (None,)]
    return sorted(rows, key=repr)

def main(only=None):
    cases = build_cases()
    assert len(cases) == 61, len(cases)
    out, bad = [], 0
    for qn, s, params, sql, cyp in cases:
        label = f"{qn}-{s}-" + ",".join(f"{k}={v}" for k, v in params.items() if k in ("k",))
        if only and qn not in only: continue
        rec = dict(case=label, q=qn, set=s, params=json.dumps(params))
        try:
            t = time.perf_counter(); a = clean(qn, run_pg(sql, params)); rec["pg_s"] = round(time.perf_counter() - t, 3)
            t = time.perf_counter(); b = clean(qn, run_neo(cyp, params)); rec["neo_s"] = round(time.perf_counter() - t, 3)
            rec.update(pg_rows=len(a), neo_rows=len(b), match=(a == b), status="ok")
            if a != b:
                bad += 1
                print("MISMATCH", label, "pg:", a[:3], "neo:", b[:3])
        except Exception as e:
            rec.update(status="error", err=str(e)[:200], match=False); bad += 1
            print("ERROR", label, str(e)[:150])
        print(label, rec.get("pg_rows"), rec.get("neo_rows"), rec.get("match"))
        out.append(rec)
    keys = ["case", "q", "set", "params", "pg_rows", "neo_rows", "match", "status", "pg_s", "neo_s", "err"]
    with open(os.path.join(OUT, "comparison.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, keys, extrasaction="ignore"); w.writeheader(); w.writerows(out)
    print(f"\n{len(out)} cases run, {bad} mismatches or errors")

if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)