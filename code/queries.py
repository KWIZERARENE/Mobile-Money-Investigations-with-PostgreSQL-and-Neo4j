# queries.py: parameterized SQL (psycopg, %(name)s) and Cypher ($name) pairs for Q1-Q7.
# Parameters used:
#   acc, start, end  -> review account and hour window (epoch seconds, CAT boundaries computed in Python)
#   k                -> depth / bound (Q4: 4,6,8,10; Q7: 4,6)
#   src, dst         -> Q7 source and destination accounts

# ---------- Q1: account activity (outgoing count and RWF in the hour) ----------
Q1_SQL = """
SELECT count(*) AS n, COALESCE(sum(amount_rwf), 0)::bigint AS total_rwf
FROM transfers
WHERE sender_id = %(acc)s AND occurred_at >= %(start)s AND occurred_at < %(end)s;
"""

Q1_CYPHER = """
MATCH (a:Account {account_id: $acc})
OPTIONAL MATCH (a)-[t:TRANSFER]->()
  WHERE t.occurred_at >= $start AND t.occurred_at < $end
RETURN count(t) AS n, coalesce(sum(t.amount_rwf), 0) AS total_rwf;
"""

# ---------- Q2: daily activity over the whole month (CAT days) ----------
Q2_SQL = """
SELECT (to_timestamp(occurred_at) AT TIME ZONE 'Africa/Kigali')::date AS day,
       count(*) AS n, sum(amount_rwf)::bigint AS total_rwf
FROM transfers GROUP BY 1 ORDER BY 1;
"""

Q2_CYPHER = """
MATCH ()-[t:TRANSFER]->()
WITH date(datetime({epochSeconds: t.occurred_at, timezone: 'Africa/Kigali'})) AS day, t
RETURN day, count(*) AS n, sum(t.amount_rwf) AS total_rwf ORDER BY day;
"""

# ---------- Q3: shared devices with overlapping day intervals ----------
Q3_SQL = """
SELECT b.account_id AS other_account, a.device_id, d.access_type,
       GREATEST(a.first_day, b.first_day) AS overlap_start,
       LEAST(a.last_day, b.last_day)      AS overlap_end
FROM account_devices a
JOIN account_devices b ON b.device_id = a.device_id AND b.account_id <> a.account_id
JOIN devices d ON d.device_id = a.device_id
WHERE a.account_id = %(acc)s
  AND GREATEST(a.first_day, b.first_day) <= LEAST(a.last_day, b.last_day)
ORDER BY b.account_id, a.device_id;
"""

Q3_CYPHER = """
MATCH (r:Account {account_id: $acc})-[u1:USED_DEVICE]->(d:Device)<-[u2:USED_DEVICE]-(o:Account)
WHERE o <> r
WITH o, d,
     CASE WHEN u1.first_day > u2.first_day THEN u1.first_day ELSE u2.first_day END AS s,
     CASE WHEN u1.last_day  < u2.last_day  THEN u1.last_day  ELSE u2.last_day  END AS e
WHERE s <= e
RETURN o.account_id AS other_account, d.device_id AS device_id, d.access_type AS access_type,
       s AS overlap_start, e AS overlap_end
ORDER BY other_account, device_id;
"""

# ---------- Q4: ownership and device network, grouped by owner region ----------
# Node kind is carried with every ID so Customer 7 differs from Account 7.
# UNION (not UNION ALL) in the recursive step removes repeated states and lets the walk terminate.
Q4_SQL = """
WITH RECURSIVE edges(ak, aid, bk, bid) AS (
    SELECT 'C', customer_id, 'A', account_id FROM accounts
    UNION ALL SELECT 'A', account_id, 'C', customer_id FROM accounts
    UNION ALL SELECT 'A', account_id, 'D', device_id  FROM account_devices
    UNION ALL SELECT 'D', device_id,  'A', account_id FROM account_devices
), reach(kind, id, depth) AS (
    SELECT 'A', %(acc)s::int, 0
    UNION
    SELECT e.bk, e.bid, r.depth + 1
    FROM reach r JOIN edges e ON e.ak = r.kind AND e.aid = r.id
    WHERE r.depth < %(k)s
)
SELECT c.region, count(*) AS accounts
FROM (SELECT DISTINCT id FROM reach WHERE kind = 'A' AND id <> %(acc)s) x
JOIN accounts a ON a.account_id = x.id
JOIN customers c ON c.customer_id = a.customer_id
GROUP BY c.region ORDER BY c.region;
"""

def q4_cypher(k):
    return f"""
MATCH (r:Account {{account_id: $acc}})-[:OWNS|USED_DEVICE*1..{int(k)}]-(a:Account)
WHERE a <> r
WITH DISTINCT a
MATCH (c:Customer)-[:OWNS]->(a)
RETURN c.region AS region, count(a) AS accounts ORDER BY region;
"""

# ---------- Q5: rapid onward payments (3 transfers, 4 distinct accounts) ----------
Q5_SQL = """
SELECT t1.transfer_id, t2.transfer_id, t3.transfer_id,
       t1.sender_id, t1.receiver_id, t2.receiver_id, t3.receiver_id,
       t1.amount_rwf, t2.amount_rwf, t3.amount_rwf
FROM transfers t1
JOIN transfers t2 ON t2.sender_id = t1.receiver_id
 AND t2.occurred_at >  t1.occurred_at AND t2.occurred_at <= t1.occurred_at + 600
 AND 90::bigint * t1.amount_rwf <= 100::bigint * t2.amount_rwf
 AND 100::bigint * t2.amount_rwf <= 105::bigint * t1.amount_rwf
JOIN transfers t3 ON t3.sender_id = t2.receiver_id
 AND t3.occurred_at >  t2.occurred_at AND t3.occurred_at <= t2.occurred_at + 600
 AND 90::bigint * t2.amount_rwf <= 100::bigint * t3.amount_rwf
 AND 100::bigint * t3.amount_rwf <= 105::bigint * t2.amount_rwf
WHERE t1.sender_id = %(acc)s AND t1.occurred_at >= %(start)s AND t1.occurred_at < %(end)s
  AND t1.receiver_id <> t1.sender_id
  AND t2.receiver_id NOT IN (t1.sender_id, t1.receiver_id)
  AND t3.receiver_id NOT IN (t1.sender_id, t1.receiver_id, t2.receiver_id)
ORDER BY 1, 2, 3;
"""

Q5_CYPHER = """
MATCH (a:Account {account_id: $acc})-[t1:TRANSFER]->(b:Account)-[t2:TRANSFER]->(c:Account)-[t3:TRANSFER]->(d:Account)
WHERE t1.occurred_at >= $start AND t1.occurred_at < $end
  AND a <> b AND a <> c AND a <> d AND b <> c AND b <> d AND c <> d
  AND t2.occurred_at > t1.occurred_at AND t2.occurred_at <= t1.occurred_at + 600
  AND t3.occurred_at > t2.occurred_at AND t3.occurred_at <= t2.occurred_at + 600
  AND 90 * t1.amount_rwf <= 100 * t2.amount_rwf AND 100 * t2.amount_rwf <= 105 * t1.amount_rwf
  AND 90 * t2.amount_rwf <= 100 * t3.amount_rwf AND 100 * t3.amount_rwf <= 105 * t2.amount_rwf
RETURN t1.transfer_id, t2.transfer_id, t3.transfer_id,
       a.account_id, b.account_id, c.account_id, d.account_id,
       t1.amount_rwf, t2.amount_rwf, t3.amount_rwf
ORDER BY 1, 2, 3;
"""

# ---------- Q6: circular payments (3 to 8 transfers, back to the review account) ----------
# Rules: all events inside the hour, strictly increasing time, span <= 1800 s, Q5 amount rule
# on each consecutive pair, stop at the first return, other accounts may repeat.
Q6_SQL = """
WITH RECURSIVE walk(cur, ids, n, t_first, t_last, amt) AS (
    SELECT receiver_id, ARRAY[transfer_id], 1, occurred_at, occurred_at, amount_rwf
    FROM transfers
    WHERE sender_id = %(acc)s AND occurred_at >= %(start)s AND occurred_at < %(end)s
  UNION ALL
    SELECT t.receiver_id, w.ids || t.transfer_id, w.n + 1, w.t_first, t.occurred_at, t.amount_rwf
    FROM walk w JOIN transfers t ON t.sender_id = w.cur
    WHERE w.cur <> %(acc)s AND w.n < 8
      AND t.occurred_at > w.t_last AND t.occurred_at < %(end)s
      AND t.occurred_at - w.t_first <= 1800
      AND 90::bigint * w.amt <= 100::bigint * t.amount_rwf
      AND 100::bigint * t.amount_rwf <= 105::bigint * w.amt
)
SELECT ids, n, t_first, t_last FROM walk
WHERE cur = %(acc)s AND n BETWEEN 3 AND 8
ORDER BY ids;
"""

# The time window is applied on every hop during expansion (quantified path pattern),
# so Neo4j never enumerates paths outside the hour.
Q6_CYPHER = """
MATCH p = (r:Account {account_id: $acc})
          ( ()-[t:TRANSFER]->() WHERE t.occurred_at >= $start AND t.occurred_at < $end ){3,8}
          (r)
WITH r, p, relationships(p) AS ts
WHERE all(i IN range(1, size(ts)-1) WHERE ts[i].occurred_at > ts[i-1].occurred_at
        AND 90 * ts[i-1].amount_rwf <= 100 * ts[i].amount_rwf
        AND 100 * ts[i].amount_rwf <= 105 * ts[i-1].amount_rwf)
  AND ts[size(ts)-1].occurred_at - ts[0].occurred_at <= 1800
  AND none(n IN nodes(p)[1..-1] WHERE n = r)
RETURN [x IN ts | x.transfer_id] AS ids, size(ts) AS n,
       ts[0].occurred_at AS t_first, ts[size(ts)-1].occurred_at AS t_last
ORDER BY ids;
"""

# ---------- Q7: shortest transfer connection, every account on the route a person ----------
# SQL baseline (before the Section 6.3 improvement): breadth-first walk over directed transfers,
# restricted to role = 'person' during the search.
Q7_SQL = """
WITH RECURSIVE bfs(acc, depth) AS (
    SELECT a.account_id, 0 FROM accounts a WHERE a.account_id = %(src)s AND a.role = 'person'
  UNION
    SELECT t.receiver_id, b.depth + 1
    FROM bfs b JOIN transfers t ON t.sender_id = b.acc
    JOIN accounts a ON a.account_id = t.receiver_id AND a.role = 'person'
    WHERE b.depth < %(k)s
)
SELECT min(depth) FROM bfs WHERE acc = %(dst)s;
"""

# Native shortest-path search with the person restriction inside the path pattern.
# (If your Neo4j rejects SHORTEST syntax, use q7_cypher_legacy below.)
def q7_cypher(k):
    return f"""
MATCH (s:Account {{account_id: $src, role: 'person'}}), (d:Account {{account_id: $dst, role: 'person'}})
MATCH p = SHORTEST 1 (s) ( ()-[:TRANSFER]->(:Account {{role: 'person'}}) ){{1,{int(k)}}} (d)
RETURN length(p) AS hops;
"""

def q7_cypher_legacy(k):
    return f"""
MATCH (s:Account {{account_id: $src}}), (d:Account {{account_id: $dst}})
MATCH p = shortestPath((s)-[:TRANSFER*..{int(k)}]->(d))
WHERE all(n IN nodes(p) WHERE n.role = 'person')
RETURN length(p) AS hops;
"""
Q7_SQL_V2 = """
WITH RECURSIVE bfs(acc, depth) AS (
    SELECT a.account_id, 0 FROM accounts a WHERE a.account_id = %(src)s AND a.role = 'person'
  UNION
    SELECT t.receiver_id, b.depth + 1
    FROM bfs b JOIN transfers t ON t.sender_id = b.acc
    JOIN accounts a ON a.account_id = t.receiver_id AND a.role = 'person'
    WHERE b.depth < %(k)s
      AND NOT EXISTS (SELECT 1 FROM bfs x WHERE x.acc = t.receiver_id)
)
SELECT min(depth) FROM bfs WHERE acc = %(dst)s;
"""
Q7_SQL_V2 = "SELECT q7_v2(%(src)s, %(dst)s, %(k)s);"
