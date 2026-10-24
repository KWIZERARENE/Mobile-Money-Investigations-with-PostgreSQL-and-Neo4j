"""Builds the final concurrency table (median across repetitions) and the chart for Section 7.2."""
import csv, os, statistics as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = os.environ.get("P2_RESULTS", r"C:\assignement\results")
# (engine, workload, reps file). The pg file also holds failed Q7 rows from the run before
# q7_v2 existed, so only the wanted workload is read from each file.
SRC = [("pg", "Q4", "concurrency_reps_pg.csv"),
       ("pg", "Q7", "concurrency_reps_pg_q7.csv"),
       ("neo", "Q4", "concurrency_reps_neo_q4_all.csv"),
       ("neo", "Q7", "concurrency_reps_neo_q7.csv")]
METRICS = ["throughput_per_s", "median_ms", "p95_ms", "errors", "timeouts", "incorrect"]


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


final = {}      # (engine, workload, clients) -> dict
for engine, wl, fn in SRC:
    path = os.path.join(R, fn)
    rows = [r for r in csv.DictReader(open(path, newline="")) if r["workload"] == wl and r["engine"] == engine]
    for n in sorted({int(r["clients"]) for r in rows}):
        grp = [r for r in rows if int(r["clients"]) == n]
        d = {"reps": len(grp), "q7_version": grp[0]["q7_version"]}
        for m in METRICS:
            xs = [num(r[m]) for r in grp if num(r[m]) is not None]
            d[m] = round(st.median(xs), 3) if xs else None
        final[(engine, wl, n)] = d

out = os.path.join(R, "concurrency_final.csv")
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["engine", "workload", "q7_version", "clients", "reps"] + [m + "_median" for m in METRICS])
    for (e, wl, n), d in sorted(final.items(), key=lambda kv: (kv[0][1], kv[0][0], kv[0][2])):
        w.writerow([e, wl, d["q7_version"], n, d["reps"]] + [d[m] for m in METRICS])
print("saved", out)

print("\nworkload clients | pg thr  neo thr  neo/pg | pg p95 ms  neo p95 ms")
for wl in ("Q4", "Q7"):
    for n in (1, 4, 8, 16):
        p, q = final.get(("pg", wl, n)), final.get(("neo", wl, n))
        if p and q:
            print(f"{wl}  {n:>2} | {p['throughput_per_s']:>8} {q['throughput_per_s']:>8} "
                  f"{q['throughput_per_s'] / p['throughput_per_s']:>7.1f} | {p['p95_ms']:>9} {q['p95_ms']:>9}")

titles = {"Q4": "Q4: ownership/device network, depth 10", "Q7": "Q7: shortest connection, bound 6 (length only)"}
colors = {"pg": "#1f77b4", "neo": "#d95f02"}
labels = {"pg": "PostgreSQL", "neo": "Neo4j"}
fig, axes = plt.subplots(2, 2, figsize=(11, 8))
for c, wl in enumerate(("Q4", "Q7")):
    for r, (m, yl) in enumerate([("throughput_per_s", "Throughput (completed requests per second)"),
                                 ("p95_ms", "p95 latency (ms)")]):
        ax = axes[r][c]
        for e in ("pg", "neo"):
            pts = sorted((n, d[m]) for (ee, ww, n), d in final.items() if ee == e and ww == wl and d[m] is not None)
            if pts:
                lab = labels[e] + (" (Q7 v2)" if (e == "pg" and wl == "Q7") else "")
                ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", color=colors[e], label=lab)
        ax.set_xscale("log", base=2)
        ax.set_xticks([1, 4, 8, 16])
        ax.set_xticklabels(["1", "4", "8", "16"])
        ax.set_yscale("log")
        ax.set_xlabel("Concurrent clients")
        ax.set_ylabel(yl)
        ax.set_title(titles[wl] if r == 0 else "")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
fig.suptitle("Concurrency: median of 3 repetitions per point (log scales)")
fig.tight_layout()
png = os.path.join(R, "concurrency_plot.png")
fig.savefig(png, dpi=150)
print("saved", png)
