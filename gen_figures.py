import json, os
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIGDIR = "paper/figures"
os.makedirs(FIGDIR, exist_ok=True)
GEMMA = "experiments/ablation_google_gemma-4-26b-a4b-it__google_gemma-4-31b-it.json"
D = json.load(open(GEMMA))
A = D["A_full"]
E = D["E_always_large"]
F = D["F_always_small"]

# ---- E2: cost by price regime (actual Gemma-4 vs frontier) ----
L_IN, L_OUT, S_IN, S_OUT = 0.12, 0.35, 0.06, 0.33


def cost(rec, large):
    pin, pout = (L_IN, L_OUT) if large else (S_IN, S_OUT)
    return rec["prompt_tokens"] / 1e6 * pin + rec["completion_tokens"] / 1e6 * pout


a_act = sum(cost(r, r["model"] == "google/gemma-4-31b-it") for r in A["records"])
e_act = sum(cost(r, True) for r in E["records"])
f_act = sum(cost(r, False) for r in F["records"])
FL_IN, FL_OUT, FS_IN, FS_OUT = 10.0, 30.0, 0.10, 0.30


def costf(rec, large):
    pin, pout = (FL_IN, FL_OUT) if large else (FS_IN, FS_OUT)
    return rec["prompt_tokens"] / 1e6 * pin + rec["completion_tokens"] / 1e6 * pout


a_fr = sum(costf(r, r["model"] == "google/gemma-4-31b-it") for r in A["records"])
e_fr = sum(costf(r, True) for r in E["records"])
f_fr = sum(costf(r, False) for r in F["records"])

fig, ax = plt.subplots(figsize=(5, 3))
cats = ["Always-Large", "Always-Small", "HydraRoute(fix)"]
x = np.arange(3)
w = 0.35
b1 = ax.bar(x - w / 2, [e_act, f_act, a_act], w, label="Actual Gemma-4")
b2 = ax.bar(x + w / 2, [e_fr, f_fr, a_fr], w, label="Frontier gap")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels(cats)
ax.set_ylabel("USD / 67 tasks (log)")
ax.legend()
ax.set_title("E2: cost by price regime (measured routing)")
for b in list(b1) + list(b2):
    ax.annotate(
        f"${b.get_height():.4f}",
        (b.get_x() + b.get_width() / 2, b.get_height()),
        ha="center",
        va="bottom",
        fontsize=7,
    )
fig.tight_layout()
fig.savefig(f"{FIGDIR}/e2_cost_frontier.png", dpi=150)
plt.close(fig)
print("e2_cost_frontier.png")


# ---- ablation_tokens: total tokens per config (A,E,F,D) ----
def _tot(v):
    tt = v.get("total_tokens")
    if tt:
        return tt
    recs = v.get("records") or []
    return sum(r.get("total_tokens", 0) for r in recs)


cfgs = [
    ("A (fix)", _tot(A)),
    ("E always-large", _tot(E)),
    ("F always-small", _tot(F)),
    ("D no-sympy", _tot(D)),
]
fig, ax = plt.subplots(figsize=(5, 3))
labels = [c[0] for c in cfgs]
vals = [c[1] for c in cfgs]
bars = ax.bar(labels, vals, color=["#2ca02c", "#1f77b4", "#ff7f0e", "#9467bd"])
ax.set_ylabel("total tokens")
ax.set_title("E1: total tokens by configuration (Gemma-4)")
for b in bars:
    ax.annotate(
        str(b.get_height()),
        (b.get_x() + b.get_width() / 2, b.get_height()),
        ha="center",
        va="bottom",
        fontsize=8,
    )
plt.xticks(rotation=15, ha="right")
fig.tight_layout()
fig.savefig(f"{FIGDIR}/ablation_tokens.png", dpi=150)
plt.close(fig)
print("ablation_tokens.png")


# ---- ablation_cost: token cost vs accuracy (actual pricing) ----
def acc(v):
    return v.get("passed", 0) / v.get("total_tasks", 1)


fig, ax = plt.subplots(figsize=(5, 3))
pts = [
    ("A (fix)", a_act, acc(A)),
    ("E always-large", e_act, acc(E)),
    ("F always-small", f_act, acc(F)),
    ("D no-sympy", _tot(D) * 0.0, acc(D)),
]
xs = [p[1] for p in pts]
ys = [p[2] for p in pts]
ax.scatter(xs, ys, s=60, color=["#2ca02c", "#1f77b4", "#ff7f0e", "#9467bd"])
for p in pts:
    ax.annotate(
        p[0], (p[1], p[2]), fontsize=7, xytext=(3, 3), textcoords="offset points"
    )
ax.set_xlabel("cost (USD, actual Gemma-4)")
ax.set_ylabel("pass@67 accuracy")
ax.set_title("E1: cost vs accuracy (higher-left better)")
fig.tight_layout()
fig.savefig(f"{FIGDIR}/ablation_cost.png", dpi=150)
plt.close(fig)
print("ablation_cost.png")

# ---- tier0_coverage: pie of route breakdown in A ----
from collections import Counter

rc = Counter(r["route"] for r in A["records"])
fig, ax = plt.subplots(figsize=(4, 4))
ax.pie(
    [rc.get("tier0", 0), rc.get("api", 0), rc.get("sympy", 0)],
    labels=[
        f"Tier-0 free ({rc.get('tier0', 0)})",
        f"API ({rc.get('api', 0)})",
        f"SymPy ({rc.get('sympy', 0)})",
    ],
    autopct="%1.0f%%",
    colors=["#2ca02c", "#1f77b4", "#9467bd"],
)
ax.set_title("Tier-0 coverage in config A (data-driven fix)")
fig.tight_layout()
fig.savefig(f"{FIGDIR}/tier0_coverage.png", dpi=150)
plt.close(fig)
print("tier0_coverage.png")
print("DONE figures")
