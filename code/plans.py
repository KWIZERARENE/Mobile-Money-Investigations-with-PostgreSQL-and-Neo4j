import json, psycopg
from neo4j import GraphDatabase
from cases import SETS
import queries as q

R = r"C:\assignement\results"
pg = psycopg.connect(host="127.0.0.1", dbname="mobile_money", user="postgres",
                     password="password", autocommit=True)
neo = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))
B = SETS["B"]

CASES = {
    "Q2":       (q.Q2_SQL, {}, q.Q2_CYPHER, {}),
    "Q4_B_k10": (q.Q4_SQL, dict(acc=B["acc"], k=10), q.q4_cypher(10), dict(acc=B["acc"])),
    "Q7_B_k6":  (q.Q7_SQL, dict(src=B["acc"], dst=B["dst"], k=6), q.q7_cypher(6),
                 dict(src=B["acc"], dst=B["dst"])),
}


def dump(n, depth, out):
    args = n.get("args", {}) or {}
    out.append("  " * depth + f'{n.get("operatorType")}  rows={n.get("rows", args.get("Rows"))}  '
               f'dbHits={n.get("dbHits", args.get("DbHits"))}  '
               f'time={args.get("Time", args.get("time"))}')
    for c in n.get("children", []) or []:
        dump(c, depth + 1, out)


for name, (sql, sp, cyp, cp) in CASES.items():
    print("running", name, flush=True)
    with pg.cursor() as cur:
        cur.execute("EXPLAIN (ANALYZE, BUFFERS) " + sql, sp)
        open(rf"{R}\plan_pg_{name}.txt", "w", encoding="utf-8").write("\n".join(r[0] for r in cur.fetchall()))
    with neo.session(database="neo4j") as s:
        prof = s.run("PROFILE " + cyp, cp).consume().profile
        lines = []
        dump(prof, 0, lines)
        open(rf"{R}\plan_neo_{name}.txt", "w", encoding="utf-8").write("\n".join(lines))
        open(rf"{R}\plan_neo_{name}.json", "w", encoding="utf-8").write(json.dumps(prof, default=str, indent=1))
    print("done", name, flush=True)
