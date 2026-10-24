import time, statistics as st
from db import run_pg
import queries as q
from cases import SETS

bad = 0
for s, p in SETS.items():
    for k in (4, 6):
        prm = dict(src=p["acc"], dst=p["dst"], k=k)
        a, b = run_pg(q.Q7_SQL, prm), run_pg(q.Q7_SQL_V2, prm)
        ok = a == b
        bad += not ok
        print(s, k, "v1", a, "v2", b, ok, flush=True)
print("12 cases,", bad, "mismatches", flush=True)

for s in ("B", "E"):
    for k in (4, 6):
        p = SETS[s]
        prm = dict(src=p["acc"], dst=p["dst"], k=k)
        for _ in range(3):
            run_pg(q.Q7_SQL_V2, prm)
        ts = []
        for _ in range(5):
            t = time.perf_counter()
            run_pg(q.Q7_SQL_V2, prm)
            ts.append((time.perf_counter() - t) * 1000)
        print(f"Q7-{s}-k{k} v2 median ms {st.median(ts):.1f}  min {min(ts):.1f}  max {max(ts):.1f}", flush=True)
