import csv, os

SRC, DST = r"C:\assignement\data", r"C:\assignement\import_tmp"
os.makedirs(DST, exist_ok=True)

def rewrite(src, dst, in_cols, header):
    n = 0
    with open(os.path.join(SRC, src), newline="") as f, \
         open(os.path.join(DST, dst), "w", newline="") as o:
        r, w = csv.DictReader(f), csv.writer(o)
        w.writerow(header)
        for row in r:
            w.writerow([row[c] for c in in_cols])
            n += 1
    print(dst, n)

# nodes: keep every property column; only retype the header
def retype_nodes(src, dst, id_col, label, types):
    with open(os.path.join(SRC, src), newline="") as f:
        cols = next(csv.reader(f))
    header = []
    for c in cols:
        if c == id_col:
            header.append(f"{c}:ID({label})")
        else:
            header.append(f"{c}:{types.get(c, 'string')}")
    rewrite(src, dst, cols, header)

retype_nodes("customers.csv", "customers.csv", "customer_id", "Customer", {})
retype_nodes("devices.csv", "devices.csv", "device_id", "Device", {})

# accounts: account_id:ID(Account), customer_id ignored, role string
rewrite("accounts.csv", "accounts.csv",
        ["account_id", "customer_id", "role"],
        ["account_id:ID(Account)", ":IGNORE", "role:string"])

# owns.csv derived from accounts in customer_id, account_id order
with open(os.path.join(SRC, "accounts.csv"), newline="") as f:
    pairs = sorted((int(r["customer_id"]), int(r["account_id"])) for r in csv.DictReader(f))
with open(os.path.join(DST, "owns.csv"), "w", newline="") as o:
    w = csv.writer(o)
    w.writerow([":START_ID(Customer)", ":END_ID(Account)"])
    w.writerows(pairs)
print("owns.csv", len(pairs))

rewrite("account_devices.csv", "used_device.csv",
        ["account_id", "device_id", "first_day", "last_day", "observations"],
        [":START_ID(Account)", ":END_ID(Device)", "first_day:int", "last_day:int", "observations:int"])

rewrite("transfers.csv", "transfers.csv",
        ["sender_id", "receiver_id", "transfer_id", "occurred_at", "amount_rwf"],
        [":START_ID(Account)", ":END_ID(Account)", "transfer_id:long", "occurred_at:long", "amount_rwf:int"])