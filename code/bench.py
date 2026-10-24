import sys, csv, os, statistics, time
from time import perf_counter
from datetime import datetime
from zoneinfo import ZoneInfo
import queries as q
from cases import SETS
from timeutil import hour_window

engine = sys.argv[1]                     # "pg" or "neo"
PG_DSN = "host=127.0.0.1 dbname=mobile_money user=postgres password=password"
NEO_URI, NEO_AUTH = "bolt://127.0.0.1:7687", ("neo4j", "password")     # <-- fill
OUT = r"C:\assignement\results"

def build():
    cs = []
    for s in "BE":
        p = SETS[s]; st, en = hour_window(p["day"]); w = dict(acc=p["acc"], start=st, end=en)
        cs += [(f"Q1-{s}", w, q.Q1_SQL, q.Q1_CYPHER), (f"Q3-{s}", dict(acc=p["acc"]), q.Q3_SQL, q.Q3_CYPHER),
               (f"Q5-{s}", w, q.Q5_SQL, q.Q5_CYPHER), (f"Q6-{s}", w, q.Q6_SQL, q.Q6_CYPHER)]
        cs += [(f"Q4-{s}-k{k}", dict(acc=p["acc"], k=k), q.Q4_SQL, q.q4_cypher(k)) for k in (4, 6, 8, 10)]
        cs += [(f"Q7-{s}-k{k}", dict(src=p["acc"], dst=p["dst"], k=k), q.Q7_SQL, q.q7_cypher(k)) for k in (4, 6)]
    cs.append(("Q2", {}, q.Q2_SQL, q.Q2_CYPHER))
    assert len(cs) == 21
    return cs

if engine == "pg":
    import psycopg
    conn = psycopg.connect(PG_DSN, autocommit=True)          # one persistent connection
    conn.execute("SET TIME ZONE 'Africa/Kigali'")
    def call(sql, cyp, params, timeout):
        conn.execute(f"SET statement_timeout = {timeout * 1000}")
        return conn.execute(sql, params).fetchall()          # consume every row
    is_timeout = lambda e: "statement timeout" in str(e).lower() or "canceling" in str(e).lower()
else:
    import neo4j
    driver = neo4j.GraphDatabase.driver(NEO_URI, auth=NEO_AUTH)
    sess = driver.session()                                  # one persistent session
    def call(sql, cyp, params, timeout):
        return list(sess.run(neo4j.Query(cyp, timeout=timeout), params))
    is_timeout = lambda e: "timed" in str(e).lower() or "timeout" in str(e).lower()

raw = []
for case, params, sql, cyp in build():
    stamp = datetime.now(ZoneInfo("Africa/Kigali")).isoformat(timespec="seconds")
    status = "ok"
    for _ in range(3):                                       # untimed warm-ups, 180 s limit
        try: call(sql, cyp, params, 180)
        except Exception as e:
            status = "timeout" if is_timeout(e) else "error"; err = str(e)[:150]; break
    if status != "ok":
        raw.append(dict(case=case, engine=engine, params=str(params), start_cat=stamp, run=0,
                        seconds="", rows="", status=status)); print(case, status, err); continue
    for i in range(1, 6):                                    # 5 measured runs, 60 s limit
        t0 = perf_counter()
        try:
            rows = call(sql, cyp, params, 60); dt = perf_counter() - t0; st = "ok"
        except Exception as e:
            dt = ""; rows = []; st = "timeout" if is_timeout(e) else "error"
        raw.append(dict(case=case, engine=engine, params=str(params), start_cat=stamp, run=i,
                        seconds=round(dt, 4) if dt != "" else "", rows=len(rows), status=st))
    ok = [r["seconds"] * 1000 for r in raw if r["case"] == case and r["status"] == "ok"]
    print(case, "median ms:", round(statistics.median(ok), 1) if ok else "n/a", "| min/max:",
          (round(min(ok), 1), round(max(ok), 1)) if ok else "n/a")

path = os.path.join(OUT, f"timing_raw_{engine}.csv")
with open(path, "w", newline="") as f:
    w = csv.DictWriter(f, raw[0].keys()); w.writeheader(); w.writerows(raw)
print("saved", path)