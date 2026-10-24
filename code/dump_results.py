import json, os
from db import run_pg, run_neo
from run_all import build_cases

OUT = r"C:\assignement\results\full"
os.makedirs(OUT, exist_ok=True)

for qn, s, params, sql, cyp in build_cases():
    k = params.get("k", "")
    label = f"{qn}-{s}" + (f"-k{k}" if k != "" else "")
    pg = [list(r) for r in run_pg(sql, params)]
    neo = [list(r) for r in run_neo(cyp, params)]
    with open(os.path.join(OUT, label + ".json"), "w") as f:
        json.dump(dict(case=label, params=params, pg=pg, neo=neo), f, default=str, indent=1)
    print(label, len(pg), len(neo))