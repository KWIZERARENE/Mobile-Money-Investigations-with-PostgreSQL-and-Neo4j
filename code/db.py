import psycopg
from neo4j import GraphDatabase

PG = dict(host="127.0.0.1", dbname="mobile_money", user="postgres", password="password")
_pg = None
_neo = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "password"))

def pg_conn():
    global _pg
    if _pg is None or _pg.closed:
        _pg = psycopg.connect(**PG, autocommit=True)
    return _pg

def norm(v):
    if isinstance(v, bool): return v
    if isinstance(v, (list, tuple)): return tuple(norm(x) for x in v)
    if isinstance(v, (int, float)) and float(v) == int(v): return int(v)
    if hasattr(v, "iso_format"): return v.iso_format()[:10]   # neo4j Date
    if hasattr(v, "isoformat"): return v.isoformat()[:10]     # python date
    return v

def run_pg(query, params=None):
    with pg_conn().cursor() as cur:
        cur.execute(query, params or {})
        return [tuple(norm(x) for x in r) for r in cur.fetchall()]

def run_neo(query, params=None):
    with _neo.session(database="neo4j") as s:
        res = s.run(query, params or {})
        return [tuple(norm(x) for x in r.values()) for r in res]