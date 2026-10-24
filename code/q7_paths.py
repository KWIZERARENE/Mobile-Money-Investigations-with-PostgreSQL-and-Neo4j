from db import run_pg, run_neo
from cases import SETS

CY = """
MATCH (s:Account {account_id: $src, role: 'person'}), (d:Account {account_id: $dst, role: 'person'})
MATCH p = SHORTEST 1 (s) ( ()-[:TRANSFER]->(:Account {role: 'person'}) ){1,6} (d)
RETURN [n IN nodes(p) | n.account_id] AS accounts,
       [r IN relationships(p) | r.transfer_id] AS transfer_ids, length(p) AS hops
"""

for name, p in SETS.items():
    rows = run_neo(CY, dict(src=p["acc"], dst=p["dst"]))
    if not rows:
        print(name, "no route within 6"); continue
    accs, tids, hops = rows[0]
    tr = run_pg("SELECT transfer_id, sender_id, receiver_id FROM transfers WHERE transfer_id = ANY(%(i)s)", dict(i=list(tids)))
    by_id = {t[0]: t for t in tr}
    ok_dir = all(by_id.get(t) and by_id[t][1] == accs[i] and by_id[t][2] == accs[i + 1] for i, t in enumerate(tids))
    roles = run_pg("SELECT role FROM accounts WHERE account_id = ANY(%(a)s)", dict(a=list(accs)))
    ok_roles = all(r[0] == "person" for r in roles) and len(roles) == len(set(accs))
    print(name, accs, tids, hops, "direction/existence ok:", ok_dir, "roles ok:", ok_roles, "length ok:", hops == len(tids))