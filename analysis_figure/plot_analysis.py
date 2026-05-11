"""
Plot two figures for TextWorld RL paper:
  Left : Context length (tokens) vs game steps
  Right: Cumulative % prompts solved vs game steps

Methods
-------
direct_RL, react_rl  : single record per game; full transcript lives in input+output
memory_static, ours  : one record per game step (decoupled); reward=1 marks solved
mem1 (mem1_qwen2)    : JSON list; context = q + i_{k} at each step; win_score=1 if solved

Token counts use Qwen/Qwen2.5-3B-Instruct tokenizer.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from collections import defaultdict
from scipy.ndimage import gaussian_filter1d
from transformers import AutoTokenizer

# ── Tokenizer ────────────────────────────────────────────────────────────────
print("Loading tokenizer …")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-3B-Instruct")

def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text, add_special_tokens=False))


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_standard(path):
    games = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            full_text = d["input"] + d["output"]
            parts = full_text.split("user\n")
            total_steps = len(parts) - 1
            step_tokens = []
            for k in range(1, total_steps + 1):
                ctx = "user\n".join(parts[: k + 1])
                step_tokens.append(count_tokens(ctx))
            games.append(dict(gts=d["gts"], reward=d["reward"],
                              step_tokens=step_tokens, total_steps=total_steps))
    return games


def load_decoupled(path):
    raw = defaultdict(list)
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            raw[d["gts"]].append(dict(tokens=count_tokens(d["input"]), reward=d["reward"]))
    return dict(raw)


def load_mem1(path):
    with open(path) as f:
        data = json.load(f)
    games = []
    for d in data:
        n = d["num_rounds"]
        step_tokens = [count_tokens(d["q"] + d.get(f"i{k}", "")) for k in range(n)]
        games.append(dict(step_tokens=step_tokens, num_rounds=n, win_score=int(d["win_score"])))
    return games


# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading direct_RL …")
direct = load_standard("direct_RL.jsonl")
print("Loading react_rl …")
react  = load_standard("react_rl.jsonl")
print("Loading memory_static …")
mem    = load_decoupled("memory_static.jsonl")
print("Loading Our_method …")
ours   = load_decoupled("Our_method.jsonl")
print("Loading mem1_qwen2 …")
mem1   = load_mem1("mem1_qwen2.json")

MAX_STEPS = 100


# ── Curve helpers ─────────────────────────────────────────────────────────────

def ctx_curve_standard(games, max_steps=MAX_STEPS):
    sums, counts = np.zeros(max_steps), np.zeros(max_steps)
    for g in games:
        for k, tok in enumerate(g["step_tokens"]):
            if k < max_steps:
                sums[k] += tok; counts[k] += 1
    return np.arange(1, max_steps + 1), np.where(counts > 0, sums / counts, np.nan)


def ctx_curve_decoupled(game_dict, max_steps=MAX_STEPS):
    sums, counts = np.zeros(max_steps), np.zeros(max_steps)
    for steps in game_dict.values():
        for k, s in enumerate(steps):
            if k < max_steps:
                sums[k] += s["tokens"]; counts[k] += 1
    return np.arange(1, max_steps + 1), np.where(counts > 0, sums / counts, np.nan)


def ctx_curve_mem1(games, max_steps=MAX_STEPS):
    sums, counts = np.zeros(max_steps), np.zeros(max_steps)
    for g in games:
        for k, tok in enumerate(g["step_tokens"]):
            if k < max_steps:
                sums[k] += tok; counts[k] += 1
    return np.arange(1, max_steps + 1), np.where(counts > 0, sums / counts, np.nan)


def acc_curve_standard(games, max_steps=MAX_STEPS):
    n, solved = len(games), np.zeros(max_steps)
    for g in games:
        if g["reward"] == 1:
            solved[min(g["total_steps"], max_steps) - 1] += 1
    return np.arange(1, max_steps + 1), np.cumsum(solved) / n * 100


def acc_curve_decoupled(game_dict, max_steps=MAX_STEPS):
    n, solved = len(game_dict), np.zeros(max_steps)
    for steps in game_dict.values():
        for k, s in enumerate(steps):
            if s["reward"] == 1:
                solved[min(k, max_steps - 1)] += 1; break
    return np.arange(1, max_steps + 1), np.cumsum(solved) / n * 100


def acc_curve_mem1(games, max_steps=MAX_STEPS):
    n, solved = len(games), np.zeros(max_steps)
    for g in games:
        if g["win_score"] == 1:
            solved[min(g["num_rounds"], max_steps) - 1] += 1
    return np.arange(1, max_steps + 1), np.cumsum(solved) / n * 100


def ffill(arr):
    out, last = arr.copy(), np.nan
    for i in range(len(out)):
        if not np.isnan(out[i]): last = out[i]
        elif not np.isnan(last): out[i] = last
    return out


# ── Compute ───────────────────────────────────────────────────────────────────
print("Computing curves …")
x, ctx_react  = ctx_curve_standard(react)
_, ctx_direct = ctx_curve_standard(direct)
_, ctx_mem    = ctx_curve_decoupled(mem)
_, ctx_ours   = ctx_curve_decoupled(ours)
_, ctx_mem1   = ctx_curve_mem1(mem1)

_, acc_react  = acc_curve_standard(react)
_, acc_direct = acc_curve_standard(direct)
_, acc_mem    = acc_curve_decoupled(mem)
_, acc_ours   = acc_curve_decoupled(ours)
_, acc_mem1   = acc_curve_mem1(mem1)

# Smooth all curves
SIG = 2.5
def sm(arr, sig=SIG): return gaussian_filter1d(ffill(arr).astype(float), sigma=sig)

ctx_react_s  = sm(ctx_react)
ctx_direct_s = sm(ctx_direct)
ctx_mem_s    = sm(ctx_mem,  sig=1.5)
ctx_ours_s   = sm(ctx_ours, sig=1.5)
ctx_mem1_s   = sm(ctx_mem1, sig=1.5)

acc_react_s  = sm(acc_react)
acc_direct_s = sm(acc_direct)
acc_mem_s    = sm(acc_mem,  sig=1.5)
acc_ours_s   = sm(acc_ours, sig=1.5)
acc_mem1_s   = sm(acc_mem1, sig=1.5)


# ── Publication style ─────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":        "DejaVu Sans",
    "font.size":          11,
    "axes.labelsize":     12,
    "axes.titlesize":     13,
    "axes.titleweight":   "bold",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.linewidth":     0.8,
    "xtick.labelsize":    10,
    "ytick.labelsize":    10,
    "xtick.direction":    "out",
    "ytick.direction":    "out",
    "xtick.major.size":   4,
    "ytick.major.size":   4,
    "legend.fontsize":    9.5,
    "legend.framealpha":  0.92,
    "legend.edgecolor":   "#cccccc",
    "legend.borderpad":   0.6,
    "figure.facecolor":   "white",
    "axes.facecolor":     "#fafafa",
})

# Wong colorblind-safe palette (modified)
C = {
    "react":  "#D55E00",   # vermillion
    "direct": "#0072B2",   # sky blue
    "mem1":   "#CC79A7",   # reddish purple
    "mem":    "#009E73",   # green
    "ours":   "#E69F00",   # amber / gold
}
STYLES = {
    "react":  dict(ls="-", lw=2.0, color=C["react"]),
    "direct": dict(ls="-", lw=2.0, color=C["direct"]),
    "mem1":   dict(ls="-", lw=2.0, color=C["mem1"]),
    "mem":    dict(ls="-", lw=2.0, color=C["mem"]),
    "ours":   dict(ls="-", lw=3.2, color=C["ours"]),
}
NAMES = {
    "react":  "ReAct",
    "direct": "Direct RL",
    "mem1":   "Mem-1",
    "mem":    "Summary-Belief",
    "ours":   "Ours",
}

CONTEXT_MAX = 10_000

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(12, 4.2),
                                   gridspec_kw={"wspace": 0.22})

# ═══════════════════════════════════════════════════════════════════════════════
# LEFT – Context length
# ═══════════════════════════════════════════════════════════════════════════════
ax = ax_l

# Danger-zone shading above context limit
ax.axhspan(CONTEXT_MAX, 16_384, color="#FFCCCC", alpha=0.45, zorder=0, lw=0)
ax.axhline(CONTEXT_MAX, color="#CC0000", ls="--", lw=1.3, alpha=0.7, zorder=1)
ax.text(1.5, CONTEXT_MAX * 1.08, "Context limit (10K)", fontsize=8.5,
        color="#CC0000", va="bottom", alpha=0.85)

# Method curves
ax.plot(x, ctx_react_s,  **STYLES["react"],  zorder=3, label=NAMES["react"])
ax.plot(x, ctx_direct_s, **STYLES["direct"], zorder=3, label=NAMES["direct"])
ax.plot(x, ctx_mem1_s,   **STYLES["mem1"],   zorder=3, label=NAMES["mem1"])
ax.plot(x, ctx_mem_s,    **STYLES["mem"],    zorder=3, label=NAMES["mem"])
ax.plot(x, ctx_ours_s,   **STYLES["ours"],   zorder=4, label=NAMES["ours"])


ax.set_yscale("log", base=2)
ax.set_xlim(0, MAX_STEPS)
ax.set_ylim(256, 16_384)          # 2^8 … 2^14
ax.set_xlabel("Game Steps", labelpad=6)
ax.set_ylabel("Context Length (tokens, log₂)", labelpad=6)
ax.set_title("Context Length vs. Steps")
ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
# Power-of-2 ticks: 256, 512, 1K, 2K, 4K, 8K, 16K
pow2_ticks = [2**k for k in range(8, 15)]   # 256 → 16384
ax.set_yticks(pow2_ticks)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda v, _: f"{int(v/1000)}K" if v >= 1000 else str(int(v))))
ax.grid(True, which="major", ls="--", lw=0.5, alpha=0.4, color="#888888")
ax.grid(True, which="minor", ls=":",  lw=0.3, alpha=0.2, color="#aaaaaa")

# End-of-curve dots for high-context methods
for key, arr in [("react", ctx_react_s), ("direct", ctx_direct_s)]:
    last_idx = np.where(arr > 0)[0][-1]
    ax.plot(x[last_idx], arr[last_idx], "o", ms=4, color=C[key], zorder=5)

# ═══════════════════════════════════════════════════════════════════════════════
# RIGHT – Cumulative accuracy
# ═══════════════════════════════════════════════════════════════════════════════
ax = ax_r

ax.plot(x, acc_react_s,  **STYLES["react"],  zorder=3, label=NAMES["react"])
ax.plot(x, acc_direct_s, **STYLES["direct"], zorder=3, label=NAMES["direct"])
ax.plot(x, acc_mem1_s,   **STYLES["mem1"],   zorder=3, label=NAMES["mem1"])
ax.plot(x, acc_mem_s,    **STYLES["mem"],    zorder=3, label=NAMES["mem"])
ax.plot(x, acc_ours_s,   **STYLES["ours"],   zorder=4, label=NAMES["ours"])

# End-of-curve accuracy labels — stagger to avoid overlap
# Sort by smoothed final value to assign vertical positions cleanly
entries = [
    ("react",  acc_react_s,  acc_react),
    ("direct", acc_direct_s, acc_direct),
    ("mem1",   acc_mem1_s,   acc_mem1),
    ("mem",    acc_mem_s,    acc_mem),
    ("ours",   acc_ours_s,   acc_ours),
]
entries_sorted = sorted(entries, key=lambda e: e[1][-1])
MIN_GAP = 4.0   # minimum vertical gap between labels (percent points)
label_y = []
for key, arr_s, arr_raw in entries_sorted:
    y_raw = arr_s[-1]
    if label_y and y_raw - label_y[-1] < MIN_GAP:
        y_raw = label_y[-1] + MIN_GAP
    label_y.append(y_raw)

for (key, arr_s, arr_raw), ly in zip(entries_sorted, label_y):
    final_val = ffill(arr_raw)[-1]
    ax.text(MAX_STEPS + 2, ly,
            f"{final_val:.0f}%",
            fontsize=9, color=C[key], fontweight="bold", va="center")
    # Connector dot at curve end
    ax.plot(MAX_STEPS, arr_s[-1], "o", ms=4, color=C[key], zorder=5)

ax.set_xlim(0, MAX_STEPS + 11)
ax.set_ylim(0, 90)
ax.set_xlabel("Game Steps", labelpad=6)
ax.set_ylabel("Prompts Solved (%)", labelpad=6)
ax.set_title("Cumulative Solve Rate vs. Steps")
ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
ax.yaxis.set_major_locator(mticker.MultipleLocator(20))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v)}%"))
ax.grid(True, which="major", ls="--", lw=0.5, alpha=0.4, color="#888888")

# Shared horizontal legend below both subplots
handles, labels = ax_l.get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=5,
           frameon=False, handlelength=2.2, columnspacing=1.2,
           fontsize=10, bbox_to_anchor=(0.5, -0.08))

plt.savefig("analysis_plot.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.savefig("analysis_plot.pdf", bbox_inches="tight", facecolor="white")
print("Saved → analysis_plot.png / .pdf")

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n=== Final accuracy ===")
for name, arr in [("ReAct", acc_react), ("Direct", acc_direct),
                  ("Mem1", acc_mem1), ("Summary-Belief", acc_mem), ("Ours", acc_ours)]:
    print(f"  {name:12s}: {ffill(arr)[-1]:.1f}%")

print("\n=== Context at step 1 / 20 / 50 (tokens) ===")
for name, arr in [("ReAct", ctx_react), ("Direct", ctx_direct),
                  ("Mem1", ctx_mem1), ("Summary-Belief", ctx_mem), ("Ours", ctx_ours)]:
    def v(a, i): return f"{a[i]:.0f}" if not np.isnan(a[i]) else "—"
    print(f"  {name:12s}: step1={v(arr,0):>6}  step20={v(arr,19):>6}  step50={v(arr,49):>6}")
