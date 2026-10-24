import csv
from db import run_pg, run_neo

# 1. Audit totals computed straight from the CSV (independent of both databases)
n = s = 0
lo = hi = None
with open(r"C:\assignement\data\transfers.csv", newline="") as f:
    for r in csv.DictReader(f):
        n += 1
        s += int(r["amount_rwf"])
        t = int(r["occurred_at"])
        lo = t if lo is None or t < lo else lo
        hi = t if hi is None or t > hi else hi
print("CSV   ", n, s, lo, hi)

# 2. PostgreSQL
print("PG transfers", run_pg("SELECT count(*), sum(amount_rwf), min(occurred_at), max(occurred_at) FROM transfers", {}))
for t in ("customers", "accounts", "devices", "account_devices"):
    print("PG", t, run_pg(f"SELECT count(*) FROM {t}", {}))
print("PG roles", run_pg("SELECT role, count(*) FROM accounts GROUP BY role ORDER BY 1", {}))

# 3. Neo4j
print("NEO transfers", run_neo("MATCH ()-[t:TRANSFER]->() RETURN count(t), sum(t.amount_rwf), min(t.occurred_at), max(t.occurred_at)", {}))
print("NEO nodes", run_neo("MATCH (n) RETURN labels(n)[0] AS l, count(*) ORDER BY l", {}))
print("NEO rels ", run_neo("MATCH ()-[r]->() RETURN type(r) AS t, count(*) ORDER BY t", {}))
print("NEO roles", run_neo("MATCH (a:Account) RETURN a.role, count(*) ORDER BY 1", {}))
print("NEO accounts without exactly one owner", run_neo("MATCH (a:Account) OPTIONAL MATCH (c:Customer)-[:OWNS]->(a) WITH a, count(c) AS k WHERE k <> 1 RETURN count(a)", {}))
print("NEO distinct transfer_id", run_neo("MATCH ()-[t:TRANSFER]->() RETURN count(DISTINCT t.transfer_id)", {}))