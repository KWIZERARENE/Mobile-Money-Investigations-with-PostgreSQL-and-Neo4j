"""Draws the two diagrams for review set C from live data (matplotlib only).
Needs: results/full/Q6-C.json and Q3-C.json and the PostgreSQL service running.
Output: results\diagram_cycle_C.png and results\diagram_devices_C.png"""
import datetime, json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
from db import run_pg

R = os.environ.get("P2_RESULTS", r"C:\assignement\results")
CAT = datetime.timezone(datetime.timedelta(hours=2))
SET = os.environ.get("P2_SET", "C")


def load(name):
    return json.load(open(os.path.join(R, "full", name + ".json")))


def hms(ts):
    return datetime.datetime.fromtimestamp(int(ts), CAT).strftime("%H:%M:%S")


q6 = load(f"Q6-{SET}")["pg"]
q3 = load(f"Q3-{SET}")["pg"]
review = load(f"Q1-{SET}")["params"]["acc"]
ids = [int(i) for i in q6[0][0]]
rows = run_pg("SELECT transfer_id, sender_id, receiver_id, occurred_at, amount_rwf "
              "FROM transfers WHERE transfer_id = ANY(%(ids)s) ORDER BY occurred_at, transfer_id",
              dict(ids=ids))
loop = [r[1] for r in rows]                     # accounts in sending order
n = len(loop)

# ---------- diagram 1: the cycle ----------
fig, ax = plt.subplots(figsize=(9, 9))
pos = {}
for i, a in enumerate(loop):
    ang = math.pi / 2 - 2 * math.pi * i / n
    pos[a] = (math.cos(ang), math.sin(ang))
for a, (x, y) in pos.items():
    col = "#d95f02" if a == review else "#1f77b4"
    ax.add_patch(Circle((x, y), 0.11, color=col, zorder=3))
    ax.text(x * 1.2, y * 1.2, str(a), ha="center", va="center", fontsize=11, weight="bold")
for k, (t, s, r, ts, amt) in enumerate(rows):
    (x1, y1), (x2, y2) = pos[s], pos[r]
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), connectionstyle="arc3,rad=-0.18",
                                 arrowstyle="-|>", mutation_scale=18, lw=1.8,
                                 color="#444444", shrinkA=16, shrinkB=16, zorder=2))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mx * 0.78, my * 0.78, f"{k + 1}. {amt:,} RWF\n{hms(ts)} CAT",
            ha="center", va="center", fontsize=8.5,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbbbbb"))
ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_aspect("equal"); ax.axis("off")
back = rows[-1][4] / rows[0][4]
ax.set_title(f"Set {SET}: {n}-transfer cycle from account {review} ({datetime.datetime.fromtimestamp(rows[0][3], CAT):%d %b %Y})\n"
             f"{rows[0][4]:,} RWF leaves, {rows[-1][4]:,} RWF returns ({back:.1%}); orange = review account",
             fontsize=11)
out1 = os.path.join(R, f"diagram_cycle_{SET}.png")
fig.savefig(out1, dpi=160, bbox_inches="tight")
plt.close(fig)
print("saved", out1)

# ---------- diagram 2: ownership / shared devices ----------
devs = {}
for r in q3:
    devs.setdefault(r[1], []).append((r[0], r[3], r[4]))
fig, ax = plt.subplots(figsize=(11, 7))
ax.add_patch(Circle((0, 0), 0.35, color="#d95f02", zorder=3))
ax.text(0, 0, str(review), ha="center", va="center", color="white", weight="bold", fontsize=10, zorder=4)
dl = sorted(devs)
for j, d in enumerate(dl):
    ang = math.pi / 2 + math.pi * (j - (len(dl) - 1) / 2) * 1.0 + (math.pi if len(dl) == 1 else 0)
    ang = math.pi * (0.5 + j * 1.0) if len(dl) == 2 else ang
    dx, dy = 3.2 * math.cos(ang), 2.3 * math.sin(ang) * 0 + 0.0
    dx = -3.4 if j == 0 else 3.4
    ax.add_patch(Rectangle((dx - 0.5, -0.3), 1.0, 0.6, color="#7f7f7f", zorder=3))
    ax.text(dx, 0, f"device\n{d}", ha="center", va="center", color="white", fontsize=9, zorder=4)
    ax.add_patch(FancyArrowPatch((0.35, 0) if dx > 0 else (-0.35, 0), (dx - 0.5 if dx > 0 else dx + 0.5, 0),
                                 arrowstyle="-", lw=1.5, color="#888888", zorder=1))
    members = sorted(devs[d], key=lambda m: m[0])
    for i, (acc, s0, e0) in enumerate(members):
        yy = (len(members) - 1) / 2 * 0.9 - i * 0.9
        xx = dx + (2.0 if dx > 0 else -2.0)
        in_loop = acc in loop
        ax.add_patch(Circle((xx, yy), 0.28, color="#1f77b4" if in_loop else "#c7c7c7", zorder=3))
        ax.text(xx, yy, str(acc), ha="center", va="center", fontsize=8,
                color="white" if in_loop else "black", zorder=4)
        ax.text(xx + (0.4 if dx > 0 else -0.4), yy, f"days {s0} to {e0}", fontsize=7.5,
                ha="left" if dx > 0 else "right", va="center", color="#555555")
        ax.add_patch(FancyArrowPatch((dx + (0.5 if dx > 0 else -0.5), 0), (xx + (-0.28 if dx > 0 else 0.28), yy),
                                     arrowstyle="-", lw=1, color="#bbbbbb", zorder=1))
ax.set_xlim(-6.8, 6.8); ax.set_ylim(-3, 3); ax.axis("off")
ax.set_title(f"Set {SET}: accounts sharing a device with {review} (Q3)\n"
             "blue = also in the cycle, grey = not in the cycle; overlap shown as day numbers", fontsize=11)
out2 = os.path.join(R, f"diagram_devices_{SET}.png")
fig.savefig(out2, dpi=160, bbox_inches="tight")
plt.close(fig)
print("saved", out2)

