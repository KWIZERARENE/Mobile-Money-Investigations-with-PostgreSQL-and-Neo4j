SETS = {
       "A": dict(acc=998,    dst=24755,  day=6),
       "B": dict(acc=147228, dst=186823, day=13),
       "C": dict(acc=206978, dst=6573,   day=8),
       "D": dict(acc=237998, dst=21755,  day=6),
       "E": dict(acc=144228, dst=183823, day=13),
       "F": dict(acc=203978, dst=3573,   day=8),
   }

# Guard so placeholders can never silently pass again
for _k, _v in SETS.items():
    assert _v["acc"] > 0 and 1 <= _v["day"] <= 30 and _v["dst"] > 0, f"set {_k} not filled in"