#!/usr/bin/env python3
"""
NeurIPS-style 2-panel belief calibration figure.

Panel (a) — Brier Score vs Agentic Step
Panel (b) — Certainty Marker Distribution (stacked bars) + Brier overlay

uv run python scripts/plot_neurips.py \
    --jsonl scripts/belief_brier_350.jsonl \
    --out   scripts/neurips_belief.pdf \
    --min-episodes 10 --max-step 15
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ---------------------------------------------------------------------------
# NeurIPS style — matches their LaTeX body text (10pt), column width ~3.25in
# ---------------------------------------------------------------------------
NEURIPS_RC = {
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "Times", "DejaVu Serif"],
    "font.size":          9,
    "axes.titlesize":     9,
    "axes.labelsize":     9,
    "xtick.labelsize":    8,
    "ytick.labelsize":    8,
    "legend.fontsize":    7.5,
    "legend.framealpha":  0.9,
    "legend.edgecolor":   "#cccccc",
    "axes.linewidth":     0.8,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":          True,
    "grid.alpha":         0.20,
    "grid.linewidth":     0.5,
    "grid.linestyle":     "--",
    "lines.linewidth":    1.5,
    "lines.markersize":   4,
    "xtick.major.width":  0.8,
    "ytick.major.width":  0.8,
    "figure.dpi":         200,
    "savefig.dpi":        300,
    "savefig.bbox":       "tight",
    "savefig.pad_inches": 0.02,
    "pdf.fonttype":       42,   # embeds fonts for camera-ready
    "ps.fonttype":        42,
}
plt.rcParams.update(NEURIPS_RC)

# Certainty scale colours — colourblind-safe (Wong palette adapted)
# ordered: low confidence → high confidence
MARKERS = [
    (0.0,  "unknown",      "#d55e00"),   # vermillion
    (0.1,  "doubtful",       "#e69f00"),   # orange
    (0.5,  "possible",       "#f0e442"),   # yellow
    (0.75, "probable",       "#56b4e9"),   # sky blue
    (0.9,  "almost certain", "#009e73"),   # bluish green
    (1.0,  "confirmed",      "#0072b2"),   # blue
]
PRIMARY = "#0072b2"    # blue — main metric colour


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_jsonl(path: Path) -> List[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def aggregate(rows: List[dict]) -> Dict[int, dict]:
    data: Dict[int, dict] = defaultdict(lambda: {
        "brier": [], "markers": defaultdict(int), "n_ep": set(),
    })
    for row in rows:
        idx = row.get("trajectory_segment_index")
        if idx is None:
            continue
        data[idx]["n_ep"].add(row["gts"])
        for b in row.get("bullets", []):
            pm = b.get("p_model")
            br = b.get("brier")
            if pm is not None and pm == pm:
                data[idx]["markers"][round(pm, 2)] += 1
            if br is not None and br == br:
                data[idx]["brier"].append(br)
    return dict(data)


def filtered_steps(data: Dict[int, dict], min_ep: int, max_step: int) -> List[int]:
    return [s for s in sorted(data)
            if len(data[s]["n_ep"]) >= min_ep and s <= max_step]


def brier_series(
    data: Dict[int, dict], min_ep: int, max_step: int
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    steps, means, sems = [], [], []
    for s in filtered_steps(data, min_ep, max_step):
        vals = data[s]["brier"]
        if vals:
            steps.append(s)
            means.append(float(np.mean(vals)))
            sems.append(float(np.std(vals) / np.sqrt(len(vals))))  # SEM not std
    return np.array(steps), np.array(means), np.array(sems)


# ---------------------------------------------------------------------------
# Panel A — Brier score
# ---------------------------------------------------------------------------

def draw_panel_a(ax: plt.Axes, data, min_ep, max_step, label, n_ep):
    steps, mean, sem = brier_series(data, min_ep, max_step)

    ax.fill_between(steps,
                    np.clip(mean - sem, 0, 1),
                    np.clip(mean + sem, 0, 1),
                    alpha=0.18, color=PRIMARY, linewidth=0)
    ax.plot(steps, mean, color=PRIMARY, marker="o", markersize=3.5,
            label=f"Brier score (n={n_ep})", zorder=3)
    ax.axhline(0.25, color="#999999", linestyle=":", linewidth=1.0,
               label="Baseline (random, p=0.5)")

    # annotate drop
    if len(steps) >= 6:
        drop = mean[0] - mean[5]
        ax.annotate(
            f"−{drop:.2f}",
            xy=(steps[5], mean[5]),
            xytext=(steps[5] + 1.2, mean[5] + 0.06),
            arrowprops=dict(arrowstyle="->", color="#333333",
                            lw=0.9, mutation_scale=10),
            fontsize=8, color="#333333",
        )

    ax.set_xlim(-0.5, max_step + 0.5)
    ax.set_ylim(0, 0.55)
    ax.set_xlabel("Agentic Step")
    ax.set_ylabel("Mean Brier Score")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=8))
    # ax.set_title("(a)", loc="left", fontweight="bold", pad=3)


# ---------------------------------------------------------------------------
# Panel B — Stacked bars + Brier overlay
# ---------------------------------------------------------------------------

def draw_panel_b(ax: plt.Axes, data, min_ep, max_step):
    valid_steps = filtered_steps(data, min_ep, max_step)
    xs = np.array(valid_steps)

    # compute fractions
    fracs = {pv: [] for pv, *_ in MARKERS}
    for s in valid_steps:
        total = sum(data[s]["markers"].values()) or 1
        for pv, *_ in MARKERS:
            fracs[pv].append(data[s]["markers"].get(pv, 0) / total)

    # stacked bars
    bottoms = np.zeros(len(xs))
    for pv, name, color in MARKERS:
        ys = np.array(fracs[pv])
        ax.bar(xs, ys, bottom=bottoms, width=0.72,
               color=color, label=name, edgecolor="none", alpha=0.92)
        bottoms += ys

    ax.set_ylim(0, 1.0)
    ax.set_ylabel("Fraction of WEPs Count")
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0, decimals=0))

    # Brier line — right axis
    ax2 = ax.twinx()
    ax2.spines["right"].set_visible(True)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_linewidth(0.8)

    steps_b, mean_b, sem_b = brier_series(data, min_ep, max_step)
    ax2.fill_between(steps_b,
                     np.clip(mean_b - sem_b, 0, 1),
                     np.clip(mean_b + sem_b, 0, 1),
                     alpha=0.15, color="black", linewidth=0)
    ax2.plot(steps_b, mean_b, color="black", marker="o", markersize=3.5,
             linewidth=1.6, zorder=5, label="Brier score")
    ax2.axhline(0.25, color="#666666", linestyle=":", linewidth=0.9,
                zorder=4, label="Baseline BS=0.25")
    ax2.set_ylim(0, 0.65)
    ax2.set_ylabel("Brier Score (↓)", fontsize=8.5)
    ax2.tick_params(axis="y", labelsize=8)

    if len(steps_b) >= 6:
        drop = mean_b[0] - mean_b[5]
        ax2.annotate(
            f"−{drop:.2f}",
            xy=(steps_b[5], mean_b[5]),
            xytext=(steps_b[5] + 1.5, mean_b[5] + 0.10),
            arrowprops=dict(arrowstyle="->", color="#111111",
                            lw=1.0, mutation_scale=10),
            fontsize=8, color="#111111", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.95, ec="#aaaaaa"),
        )

    ax.set_xlim(-0.5, max_step + 0.5)
    ax2.set_xlim(-0.5, max_step + 0.5)
    ax.set_xlabel("Agentic Step")
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True, nbins=8))

    # annotation — confirmed shift
    fc0 = fracs[1.0][0]
    fc5 = fracs[1.0][min(5, len(fracs[1.0]) - 1)]
    ax.annotate(
        f"'confirmed': {fc0*100:.0f}% → {fc5*100:.0f}%",
        xy=(5, 1.0),
        xytext=(7, 1.12),
        xycoords="data", textcoords="data",
        arrowprops=dict(arrowstyle="->", color="#333333", lw=1.1),
        fontsize=8, color="#333333", fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.9, ec="#cccccc"),
        annotation_clip=False,
    )

    # ax.set_title("(b)", loc="left", fontweight="bold", pad=3)

    return ax2


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--jsonl", type=Path, required=True)
    p.add_argument("--out",   type=Path, default=Path("neurips_belief.png"))
    p.add_argument("--min-episodes", type=int, default=10)
    p.add_argument("--max-step",     type=int, default=15)
    p.add_argument("--label", type=str, default="")
    args = p.parse_args()

    rows  = load_jsonl(args.jsonl)
    data  = aggregate(rows)
    label = args.label or args.jsonl.stem
    n_ep  = len(set(r["gts"] for r in rows))

    # NeurIPS wrapfigure: ~half text width so text wraps alongside
    fig, ax_b = plt.subplots(1, 1, figsize=(3.25, 2.6))

    ax2 = draw_panel_b(ax_b, data, args.min_episodes, args.max_step)

    # ---- single shared legend centred below the panel ----
    bar_h, bar_l = ax_b.get_legend_handles_labels()
    line_h, line_l = ax2.get_legend_handles_labels()

    all_handles = bar_h[::-1] + line_h
    all_labels  = bar_l[::-1] + line_l

    fig.legend(
        all_handles, all_labels,
        loc="lower center",
        ncol=4,
        fontsize=7.0,
        handlelength=1.0,
        handletextpad=0.3,
        columnspacing=0.7,
        frameon=False,
        bbox_to_anchor=(0.5, -0.02),
    )

    fig.tight_layout()
    fig.subplots_adjust(bottom=0.30)
    fig.savefig(args.out)
    print(f"Saved → {args.out}")


if __name__ == "__main__":
    main()
