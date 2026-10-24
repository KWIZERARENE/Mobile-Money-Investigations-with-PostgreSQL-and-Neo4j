import csv, os
from db import run_pg
R = os.environ.get("P2_RESULTS", r"C:\assignement\results")

print("=== PostgreSQL sizes (bytes; 1 GB = 1,000,000,000) ===")
print("database:", run_pg("SELECT pg_database_size('mobile_money')")[0][0])
for r in run_pg("SELECT c.relname, c.relkind, pg_total_relation_size(c.oid) FROM pg_class c "
                "JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relkind IN ('r','i') "
                "ORDER BY 3 DESC LIMIT 25"):
    print(" ", r)

for fn in ("timing_summary.csv", "concurrency_final.csv"):
    print("\n=== " + fn + " ===")
    p = os.path.join(R, fn)
    if os.path.exists(p):
        for row in csv.reader(open(p, newline="")):
            print(",".join(row))
    else:
        print("missing")

print("\n=== files in results that may hold load/import times ===")
for f in sorted(os.listdir(R)):
    if any(k in f.lower() for k in ("load", "import", "index", "version", "hardware", "size")):
        print(" ", f)
