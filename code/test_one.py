from db import run_pg, run_neo
from timeutil import hour_window
import queries as q

SETS = {  # review, destination, September day
    "A": (998, 24755, 6),     "B": (147228, 186823, 13), "C": (206978, 6573, 8),
    "D": (237998, 21755, 6),  "E": (144228, 183823, 13), "F": (203978, 3573, 8),
}

for name in ("A", "D", "B"):
    acc, dst, day = SETS[name]
    s, e = hour_window(day)          # adapt if your function takes different arguments
    print(name, "params:", acc, dst, day, s, e)
    print(" Q1 pg ", run_pg(q.Q1_SQL, dict(acc=acc, start=s, end=e)))
    print(" Q3 pg ", run_pg(q.Q3_SQL, dict(acc=acc)))
    print(" Q3 neo", run_neo(q.Q3_CYPHER, dict(acc=acc)))
    print(" Q4 pg ", run_pg(q.Q4_SQL, dict(acc=acc, k=4)))
    print(" Q4 neo", run_neo(q.q4_cypher(4), dict(acc=acc)))