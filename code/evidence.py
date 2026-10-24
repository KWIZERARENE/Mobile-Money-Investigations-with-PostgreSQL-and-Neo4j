"""Collects the Q1-Q7 evidence for sets A-F from results\\full\\*.json (saved by save_all.py).
For the first Q5 chain and first Q6 cycle of each set it also reads the transfer rows
from PostgreSQL (needs the PostgreSQL service running) so times appear in CAT."""
import datetime, json, os

R = os.environ.get("P2_RESULTS", r"C:\assignement\results")
FULL = os.path.join(R, "full")
CAT = datetime.timezone(datetime.timedelta(hours=2))


def cat(ts):
    return datetime.datetime.fromtimestamp(int(ts), CAT).strftime("%d %b %H:%M:%S")


def load(name):
    p = os.path.join(FULL, name + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


try:
    from db import run_pg
    run_pg("SELECT 1")
    HAVE_PG = True
except Exception as e:
    HAVE_PG = False
    PG_ERR = str(e)[:120]

out = []


def P(s=""):
    out.append(s)
    print(s)


def tr_details(ids):
    rows = run_pg("SELECT transfer_id, sender_id, receiver_id, occurred_at, amount_rwf "
                  "FROM transfers WHERE transfer_id = ANY(%(ids)s) ORDER BY occurred_at, transfer_id",
                  dict(ids=[int(i) for i in ids]))
    for t, s, r, ts, a in rows:
        P(f"      transfer {t}: {s} -> {r}  {a:,} RWF  at {cat(ts)} CAT")


for s in "ABCDEF":
    P(f"===== SET {s} =====")
    q1 = load(f"Q1-{s}")
    if q1:
        pr = q1["params"]
        P(f"review account {pr['acc']}; hour window {cat(pr['start'])} to {cat(pr['end'])} CAT")
        P(f"Q1 outgoing in hour (count, RWF): {q1['pg']}")
    q3 = load(f"Q3-{s}")
    if q3:
        rows = q3["pg"]
        P(f"Q3 shared-device overlaps: {len(rows)} rows, {len({r[0] for r in rows})} other accounts, "
          f"{len({r[1] for r in rows})} devices")
        for r in rows[:12]:
            P(f"      Q3 row: {r}")
    for k in (4, 6, 8, 10):
        q4 = load(f"Q4-{s}-k{k}")
        if q4:
            P(f"Q4 k={k}: " + ", ".join(f"{r[0]}={r[1]}" for r in q4["pg"]) +
              f"  (total {sum(r[1] for r in q4['pg'])})")
    q5 = load(f"Q5-{s}")
    if q5:
        rows = q5["pg"]
        P(f"Q5 rapid onward chains: {len(rows)}")
        for r in rows[:3]:
            P(f"      transfers {r[0]},{r[1]},{r[2]}; accounts {r[3]}->{r[4]}->{r[5]}->{r[6]}; "
              f"amounts {r[7]:,}, {r[8]:,}, {r[9]:,} RWF")
        if rows and HAVE_PG:
            P("   detail of first chain:")
            tr_details(rows[0][:3])
    q6 = load(f"Q6-{s}")
    if q6:
        rows = q6["pg"]
        P(f"Q6 cycles: {len(rows)}")
        for r in rows[:3]:
            P(f"      transfers {r[0]} ({r[1]} transfers), first {cat(r[2])}, last {cat(r[3])} CAT")
        if rows and HAVE_PG:
            P("   detail of first cycle:")
            tr_details(rows[0][0])
    l4, l6 = load(f"Q7-{s}-k4"), load(f"Q7-{s}-k6")
    P("Q7 shortest connection: bound 4 = " + (str(l4["pg"][0][0]) if l4 and l4["pg"] else "no path") +
      ", bound 6 = " + (str(l6["pg"][0][0]) if l6 and l6["pg"] else "no path"))
    P()

if not HAVE_PG:
    P(f"(PostgreSQL details skipped: {PG_ERR})")
path = os.path.join(R, "evidence_summary.txt")
open(path, "w", encoding="utf-8").write("\n".join(out))
print("saved", path)

