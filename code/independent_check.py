import csv

# Device overlap, set A: account 998 vs others on its devices
rows = list(csv.DictReader(open(r"C:\assignement\data\account_devices.csv")))
mine = [r for r in rows if r["account_id"] == "998"]
for m in mine:
    for o in rows:
        if o["device_id"] == m["device_id"] and o["account_id"] != "998":
            s = max(int(m["first_day"]), int(o["first_day"])); e = min(int(m["last_day"]), int(o["last_day"]))
            if s <= e: print("overlap", o["account_id"], m["device_id"], s, e)

# Chain / cycle: transfers 20000001..20000004
ids = {str(i) for i in range(20000001, 20000005)}
for r in csv.DictReader(open(r"C:\assignement\data\transfers.csv")):
    if r["transfer_id"] in ids: print(r)