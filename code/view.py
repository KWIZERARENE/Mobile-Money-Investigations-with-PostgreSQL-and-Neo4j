from itertools import islice
import mobile_money_generator as g

print("g.dataset_info():")
print(g.dataset_info())
print("\ng.FIELDS:")
print(g.FIELDS)

streams = {
    "customers": g.iter_customers,
    "accounts": g.iter_accounts,
    "devices": g.iter_devices,
    "account_devices": g.iter_account_devices,
    "transfers": g.iter_transfers,
}

for name, fn in streams.items():
    print(f"\n--- {name}: first 10 rows (islice) ---")
    for row in islice(fn(), 10):
        print(row)