"""Render the approved Chapter 1 charts from committed plotted-series snapshots.
See README.md for provenance, calculations, verification, and regeneration commands.
This renderer reads data only and writes to --output-dir (default: book figure assets).
"""
from pathlib import Path
from figure_style import palette
import argparse, os, tempfile

SCRIPT = Path(__file__).resolve().parent
BOOK = SCRIPT.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-dir", type=Path, default=BOOK / "images/01_images/editorial"
)
parser.add_argument(
    "--proofs", action="store_true", help="Also export PDF and themed PNG proofs"
)
args = parser.parse_args()
OUTPUT = args.output_dir.resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
cache = Path(tempfile.gettempdir()) / "econ139-figure-cache"
cache.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

DATA = SCRIPT / "data/chapter01"
ineq = pd.read_csv(DATA / "inequality.csv").sort_values(["group", "year"])
labor = pd.read_csv(DATA / "labor-share.csv")
lfp = pd.read_csv(DATA / "participation.csv")
means = pd.read_csv(DATA / "education.csv")
means["change"] = means.change.astype(np.float32)
assert len(ineq) == 214 and len(labor) == 70 and len(lfp) == 156 and len(means) == 275
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "axes.linewidth": 0.65,
        "lines.solid_capstyle": "round",
        "font.weight": "normal",
    }
)
for mode in ["light", "dark"]:
    dark = mode == "dark"
    p = palette(mode)
    paper = p["paper"]
    ink = p["ink"]
    muted = p["muted"]
    grid = p["grid"]
    primary = p["primary"]
    comparison = p["comparison"]

    def canvas(label, height=4.2, right=0.99, bottom=0.19):
        fig, ax = plt.subplots(figsize=(7.2, height))
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        fig.subplots_adjust(left=0.08, right=right, top=0.88, bottom=bottom)
        for edge in ["left", "right", "top"]:
            ax.spines[edge].set_visible(False)
        ax.spines["bottom"].set_color(grid)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color=grid, lw=0.65)
        ax.tick_params(axis="both", labelsize=9.5, labelcolor=muted, color=grid)
        ax.tick_params(axis="y", length=0, pad=8)
        ax.tick_params(axis="x", length=3, pad=7)
        ax.set_xlabel("Year", color=muted, labelpad=9, fontsize=10)
        ax.text(
            0, 1.06, label, transform=ax.transAxes, fontsize=10, color=muted, ha="left"
        )
        return fig, ax

    def save(fig, name):
        fig.savefig(OUTPUT / f"{name}-{mode}.svg", transparent=True)
        if args.proofs:
            fig.savefig(OUTPUT / f"{name}-{mode}.pdf", transparent=True)
            fig.patch.set_alpha(1)
            fig.savefig(
                OUTPUT / f"{name}-{mode}.png",
                facecolor=paper,
                transparent=False,
                dpi=180,
            )
        plt.close(fig)

    # Approved Style A: same layout and color/line assignments as prior sample.
    fig, ax = canvas("Share of total income")
    for group, color, line, label in [
        ("p99p100", comparison, "-", "Top 1%"),
        ("p0p50", primary, "--", "Bottom 50%"),
    ]:
        d = ineq[ineq.group == group]
        ax.plot(d.year, d.share, color=color, lw=2, ls=line)
        ax.scatter(d.year.iloc[-1], d.share.iloc[-1], s=15, color=color, zorder=3)
        ax.text(2026, d.share.iloc[-1], label, va="center", fontsize=9.5, color=color)
    ax.set(
        xlim=(1917, 2045),
        ylim=(0.045, 0.255),
        xticks=[1920, 1940, 1960, 1980, 2000, 2020],
        yticks=[0.05, 0.1, 0.15, 0.2, 0.25],
    )
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))
    save(fig, "inequality")

    fig, ax = canvas(
        "Change in mean log weekly wage, men (1963 = 0)", height=4.8, right=0.76
    )
    colors = [
        p["education_dropout"],
        p["education_highschool"],
        p["education_somecollege"],
        comparison,
        primary,
    ]
    patterns = ["-", (0, (5, 2)), (0, (1, 2)), (0, (6, 2, 1, 2)), (0, (3, 1.5))]
    labels = [
        "High school dropout",
        "High school graduate",
        "Some college",
        "Bachelor’s degree",
        "Graduate degree",
    ]
    labelbounds = []
    for cat, color, pattern, label in zip(range(1, 6), colors, patterns, labels):
        d = means[means.edcat == cat]
        ax.plot(d.year, d.change, color=color, lw=1.8, ls=pattern)
        y = float(d.change.iloc[-1])
        ax.scatter(2017, y, s=13, color=color, zorder=3)
        text = ax.annotate(
            label,
            xy=(2017, y),
            xytext=(1.025, y),
            xycoords="data",
            textcoords=("axes fraction", "data"),
            va="center",
            ha="left",
            fontsize=9.2,
            color=color,
            annotation_clip=False,
        )
        labelbounds.append(text)
    ax.set(
        xlim=(1963, 2019),
        ylim=(-0.12, 0.82),
        xticks=[1963, 1972, 1981, 1990, 1999, 2008, 2017],
        yticks=[0, 0.2, 0.4, 0.6, 0.8],
    )
    ax.axhline(0, color=muted, lw=0.8, zorder=1)
    fig.canvas.draw()
    boxes = [t.get_window_extent() for t in labelbounds]
    assert not any(
        a.overlaps(b) for i, a in enumerate(boxes) for b in boxes[i + 1 :]
    ), "Education label collision"
    assert all(b.x1 <= fig.bbox.x1 for b in boxes), "Education label outside canvas"
    save(fig, "education")

    fig, ax = canvas("Labor share of income", height=4.4, right=0.96)
    ax.plot(labor.year, labor.share, color=primary, lw=2)
    ax.set(
        xlim=(1945, 2020),
        ylim=(50, 70),
        xticks=[1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
        yticks=[50, 55, 60, 65, 70],
    )
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    events = [
        (1961, 65.2, 67, "Kaldor’s paper"),
        (1973, 63.5, 60, "Oil shocks"),
        (1987, 63.2, 67, "Stock market crash"),
        (1995, 60.6, 56.8, "Dot com boom"),
    ]
    for year, target, position, label in events:
        ax.annotate(
            label,
            xy=(year, target),
            xytext=(year, position),
            ha="center",
            va="bottom" if position > target else "top",
            fontsize=9,
            color=muted,
            arrowprops={
                "arrowstyle": "->",
                "color": muted,
                "lw": 0.9,
                "shrinkA": 4,
                "shrinkB": 3,
            },
        )
    save(fig, "labor-share")

    fig, ax = canvas("Labor force participation rate")
    for group, color, line, label in [
        ("men", comparison, "-", "Men"),
        ("women", primary, "--", "Women"),
    ]:
        d = lfp[lfp.group == group]
        ax.plot(d.year, d.rate, color=color, lw=2, ls=line)
        ax.scatter(2025, d.rate.iloc[-1], s=15, color=color, zorder=3)
        ax.text(2028, d.rate.iloc[-1], label, va="center", fontsize=9.5, color=color)
    ax.set(
        xlim=(1945, 2040),
        ylim=(28, 92),
        xticks=[1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020],
        yticks=[30, 40, 50, 60, 70, 80, 90],
    )
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=0))
    save(fig, "participation")

print("Rendered Chapter 1 light/dark charts to", OUTPUT)
