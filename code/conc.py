"""Concurrency test (Section 7): one engine per run.
   python conc.py --engine pg  --q7 v2
   python conc.py --engine neo
Passwords come from the environment (PGPASSWORD, NEO4J_PASSWORD), never from this file."""
import argparse, csv, json, math, os, statistics as st, sys, time
import multiprocessing as mp

R = os.environ.get("P2_RESULTS", r"C:\assignement\results")
CYCLE = ("A", "B", "C")
TIMEOUT_S = 60


def norm(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, (list, tuple)):
        return tuple(norm(x) for x in v)
    if isinstance(v, float) and v == int(v):
        return int(v)
    if hasattr(v, "iso_format"):
        return v.iso_format()[:10]
    if hasattr(v, "isoformat"):
        return v.isoformat()[:10]
    return v


def canon(workload, rows):
    rows = [tuple(norm(x) for x in r) for r in rows]
    if workload == "Q7":                       # SQL gives (None,) for "no path", Cypher gives no row
        rows = [r for r in rows if r != (None,)]
    return repr(sorted(rows, key=repr))


def make_job(engine, workload, version, s):
    import queries as q
    from cases import SETS
    p = SETS[s]
    if workload == "Q4":
        prm = dict(acc=p["acc"], k=10)
        text = q.Q4_SQL if engine == "pg" else q.q4_cypher(10)
    else:
        prm = dict(src=p["acc"], dst=p["dst"], k=6)
        if engine == "pg":
            text = q.Q7_SQL_V2 if version == "v2" else q.Q7_SQL
        else:
            text = q.q7_cypher(6)
    return text, prm


def connect(engine):
    """One persistent connection per process. Returns run(text, params) -> list of rows."""
    if engine == "pg":
        import psycopg
        c = psycopg.connect(host="127.0.0.1", dbname="mobile_money",
                            user=os.environ.get("PGUSER", "postgres"),
                            password=os.environ.get("PGPASSWORD"),
                            autocommit=True,
                            options=f"-c statement_timeout={TIMEOUT_S * 1000}")

        def run(text, prm):
            with c.cursor() as cur:
                cur.execute(text, prm)
                return cur.fetchall()
        return run
    from neo4j import GraphDatabase, Query
    d = GraphDatabase.driver("bolt://127.0.0.1:7687",
                             auth=("neo4j", os.environ.get("NEO4J_PASSWORD")))

    def run(text, prm):
        with d.session(database="neo4j") as s:
            return [tuple(r.values()) for r in s.run(Query(text, timeout=TIMEOUT_S), prm)]
    return run


def classify(e, latency):
    m = str(e).lower()
    if "timeout" in m or "timed out" in m or "canceling statement" in m or latency >= TIMEOUT_S:
        return "timeout"
    return "error"


def worker(engine, workload, version, idx, b1, b2, start, duration, out_q):
    try:
        run = connect(engine)
        jobs = {s: make_job(engine, workload, version, s) for s in CYCLE}
        for s in CYCLE:                                  # each client warms up A-B-C once
            try:
                run(*jobs[s])
            except Exception:
                pass
        i = b1.wait(900)                                 # barrier release
        if i == 0:
            start.value = time.time()                    # common start time
        b2.wait(900)
        t0 = start.value
        deadline = t0 + duration                         # common deadline
        recs, cyc = [], 0
        while time.time() < deadline:                    # start a new cycle only before the deadline
            for s in CYCLE:                              # a started cycle is always finished
                a = time.perf_counter()
                try:
                    rows = run(*jobs[s])
                    b = time.perf_counter()
                    end_off = time.time() - t0
                    status, res = "ok", canon(workload, rows)
                except Exception as e:
                    b = time.perf_counter()
                    end_off = time.time() - t0
                    status, res = classify(e, b - a), str(e)[:120]
                recs.append((idx, cyc, s, end_off, b - a, status, res))
            cyc += 1
        out_q.put(("ok", idx, recs))
    except BaseException as e:
        for bar in (b1, b2):
            try:
                bar.abort()
            except Exception:
                pass
        import traceback
        traceback.print_exc()
        out_q.put(("fail", idx, repr(e)[:300]))


def run_combo(ctx, mgr, engine, workload, version, n, duration, refs):
    b1, b2 = mgr.Barrier(n), mgr.Barrier(n)
    start = mgr.Value("d", 0.0)
    out_q = mgr.Queue()
    ps = [ctx.Process(target=worker,
                      args=(engine, workload, version, i, b1, b2, start, duration, out_q))
          for i in range(n)]
    for p in ps:
        p.start()
    results = [out_q.get(timeout=1800) for _ in range(n)]
    for p in ps:
        p.join()
    fails = [r for r in results if r[0] == "fail"]
    if fails:
        real = [f for f in fails if "BrokenBarrier" not in f[2]] or fails
        raise RuntimeError(f"worker failed: {real[0][2]}")
    raw, lats = [], []
    n_ok = n_bad = n_to = n_err = 0
    first_err = ""
    last_end = 0.0
    for _, idx, recs in results:
        for (c, cyc, s, end_off, lat, status, res) in recs:
            correct = status == "ok" and res == refs[(workload, s)]
            if status == "ok" and not correct:
                n_bad += 1
            if correct:
                n_ok += 1
                lats.append(lat)
            elif status == "timeout":
                n_to += 1
            elif status == "error":
                n_err += 1
            if status != "ok" and not first_err:
                first_err = status + ": " + res
            last_end = max(last_end, end_off)
            raw.append((c, cyc, s, round(end_off, 3), round(lat * 1000, 1), status, int(correct)))
    lats.sort()
    k = len(lats)
    return dict(
        completions=n_ok, elapsed_s=round(last_end, 3),
        throughput_per_s=round(n_ok / last_end, 3) if last_end else 0.0,
        median_ms=round(st.median(lats) * 1000, 1) if k else None,
        p95_ms=round(lats[math.ceil(0.95 * k) - 1] * 1000, 1) if k else None,
        errors=n_err, timeouts=n_to, incorrect=n_bad, first_error=first_err), raw


def load_refs(workloads):
    refs = {}
    for w in workloads:
        for s in CYCLE:
            name = f"Q4-{s}-k10" if w == "Q4" else f"Q7-{s}-k6"
            path = os.path.join(R, "full", name + ".json")
            rec = json.load(open(path))
            if not rec.get("match"):
                sys.exit(f"{name}: engines disagreed in save_all.py, fix that first")
            refs[(w, s)] = canon(w, [tuple(r) for r in rec["pg"]])
    return refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["pg", "neo"], required=True)
    ap.add_argument("--q7", choices=["v1", "v2"], default="v2")
    ap.add_argument("--workload", default="Q4,Q7")
    ap.add_argument("--clients", default="1,4,8,16")
    ap.add_argument("--reps", type=int, default=3)
    ap.add_argument("--duration", type=float, default=15.0)
    ap.add_argument("--tag", default=None, help="file suffix; use e.g. smoke_pg for trial runs")
    a = ap.parse_args()
    tag = a.tag or a.engine
    workloads = a.workload.split(",")
    clients = [int(x) for x in a.clients.split(",")]
    refs = load_refs(workloads)
    ctx = mp.get_context("spawn")
    mgr = ctx.Manager()
    os.makedirs(R, exist_ok=True)
    reps_path = os.path.join(R, f"concurrency_reps_{tag}.csv")
    raw_path = os.path.join(R, f"concurrency_raw_{tag}.csv")
    rep_cols = ["engine", "q7_version", "workload", "clients", "rep", "completions", "elapsed_s",
                "throughput_per_s", "median_ms", "p95_ms", "errors", "timeouts", "incorrect"]
    allrows = []
    with open(reps_path, "w", newline="") as fr, open(raw_path, "w", newline="") as fw:
        wr, ww = csv.writer(fr), csv.writer(fw)
        wr.writerow(rep_cols)
        ww.writerow(["engine", "q7_version", "workload", "clients", "rep", "client", "cycle",
                     "set", "end_s", "latency_ms", "status", "correct"])
        for w in workloads:
            for n in clients:
                for rep in range(1, a.reps + 1):
                    m, raw = run_combo(ctx, mgr, a.engine, w, a.q7, n, a.duration, refs)
                    row = [a.engine, a.q7 if a.engine == "pg" else "-", w, n, rep] + \
                          [m[c] for c in rep_cols[5:]]
                    wr.writerow(row)
                    fr.flush()
                    for r in raw:
                        ww.writerow([a.engine, row[1], w, n, rep, *r])
                    fw.flush()
                    allrows.append(dict(zip(rep_cols, row)))
                    print(w, "clients", n, "rep", rep, m, flush=True)
                    time.sleep(3)
    summ = os.path.join(R, f"concurrency_summary_{tag}.csv")
    keys = ["throughput_per_s", "median_ms", "p95_ms", "errors", "timeouts", "incorrect"]
    with open(summ, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["engine", "q7_version", "workload", "clients", "reps"] + [f"{k}_median" for k in keys])
        for w in workloads:
            for n in clients:
                grp = [r for r in allrows if r["workload"] == w and r["clients"] == n]
                vals = []
                for k in keys:
                    xs = [r[k] for r in grp if r[k] is not None]
                    vals.append(round(st.median(xs), 3) if xs else None)
                wr.writerow([a.engine, grp[0]["q7_version"], w, n, len(grp)] + vals)
    print("saved", reps_path, raw_path, summ)


if __name__ == "__main__":
    main()



