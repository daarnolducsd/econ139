"""Render six Chapter 7 charts with the approved green/rust editorial style.

Three occupation examples retain the chapter's typed values. Three paper
charts use public source series reconstructed by replicate_chapter07.py.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
DATA = HERE / "data/chapter07"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-dir", type=Path, default=BOOK / "images/07_images/editorial"
)
parser.add_argument("--proofs", action="store_true")
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
cache = Path(tempfile.gettempdir()) / "econ139-figure-cache"
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "lines.solid_capstyle": "round",
    }
)
MODELS = json.loads((DATA / "models.json").read_text())
checks = []


def palette(mode):
    dark = mode == "dark"
    return dict(
        paper="#202522" if dark else "#FAFAF7",
        ink="#E5EBE6" if dark else "#2B302D",
        muted="#B6C0B8" if dark else "#616962",
        grid="#414942" if dark else "#E1E5DF",
        green="#ACC9BB" if dark else "#3D6155",
        rust="#D9A278" if dark else "#A36F49",
        sage="#C0CFC5" if dark else "#758C7F",
        ochre="#D0BC8F" if dark else "#B39B61",
    )


def panel(p, unit, height=4.7, bottom=0.22, right=0.97):
    fig, ax = plt.subplots(figsize=(7.2, height))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.subplots_adjust(left=0.11, right=right, top=0.86, bottom=bottom)
    for edge in ["left", "right", "top"]:
        ax.spines[edge].set_visible(False)
    ax.spines["bottom"].set_color(p["grid"])
    ax.set_axisbelow(True)
    ax.grid(axis="y", color=p["grid"], lw=0.65)
    ax.tick_params(axis="y", length=0, pad=8, labelcolor=p["muted"])
    ax.tick_params(
        axis="x", length=3, pad=7, color=p["grid"], labelcolor=p["muted"], labelsize=9.5
    )
    ax.text(0, 1.07, unit, transform=ax.transAxes, color=p["muted"], fontsize=10)
    return fig, ax


def occupation_bars(model, p):
    values = model.get("employment_changes", model.get("percent_changes"))
    x = np.arange(len(values))
    fig, ax = panel(p, "Change in employment between 1980 and 2000 (%)", height=5.1, bottom=0.26)
    # Positive growth is green; employment declines are rust in all examples.
    colors = [p["green"] if v >= 0 else p["rust"] for v in values]
    bars = ax.bar(x, values, width=0.52, color=colors, zorder=3)
    assert np.array_equal([bar.get_height() for bar in bars], values)
    ax.axhline(0, color=p["muted"], lw=0.8)
    low = -85 if min(values) < -50 else -40
    ax.set(
        ylim=(low, 48),
        yticks=range(-80 if low == -85 else -40, 41, 20),
        xticks=x,
        xticklabels=model["occupations"],
    )
    ax.tick_params(axis="x", length=0)
    for i, v in enumerate(values):
        ax.text(
            i,
            v + (2 if v > 0 else -2),
            f"{v}%",
            ha="center",
            va="bottom" if v > 0 else "top",
            color=colors[i],
            fontsize=11,
            fontweight="bold",
        )
    # Keep the original wage information close to zero, on each bar's empty side.
    for i, (v, wage) in enumerate(zip(values, model.get("avg_wages_1980", []))):
        ax.text(
            i,
            -3 if v > 0 else 3,
            f"1980 avg wage:\n${wage:,}",
            ha="center",
            va="top" if v > 0 else "bottom",
            color=p["muted"],
            fontsize=9,
        )
    return fig


def polarization(p):
    data = pd.read_csv(DATA / "polarization.csv")
    fig, ax = panel(p, "100 × change in employment share · 1980–2005")
    (line,) = ax.plot(
        data.percentile,
        data.change_100x_share,
        color=p["green"],
        lw=2,
        marker="o",
        ms=2.3,
    )
    assert np.allclose(line.get_ydata(), data.change_100x_share, atol=0, rtol=0)
    ax.axhline(0, color=p["muted"], lw=0.8)
    ax.set(
        xlim=(0, 100),
        ylim=(-0.2, 0.4),
        xticks=range(0, 101, 20),
        yticks=np.arange(-0.2, 0.41, 0.1),
    )
    ax.set_xlabel(
        "Skill percentile (ranked by 1980 occupational mean wage)",
        color=p["muted"],
        labelpad=12,
    )
    return fig


def countries(p):
    data = pd.read_csv(DATA / "countries.csv")
    # A taller chart keeps all original countries/order with readable labels.
    fig, ax = panel(
        p, "Change in employment share · 1993–2006", height=5.9, bottom=0.34
    )
    x = np.arange(len(data))
    series = [
        ("lo", "Lowest paying third", "green"),
        ("mid", "Middle paying third", "rust"),
        ("hi", "Highest paying third", "sage"),
    ]
    for i, (col, label, color) in enumerate(series):
        bars = ax.bar(
            x + (i - 1) * 0.25,
            data[col],
            width=0.24,
            color=p[color],
            label=label,
            zorder=3,
        )
        assert np.allclose([b.get_height() for b in bars], data[col], atol=0, rtol=0)
    ax.axhline(0, color=p["muted"], lw=0.8)
    labels = data.country.replace({"European Union": "EU Average", "EU": "EU Average"})
    ax.set(
        xticks=x,
        xticklabels=labels,
        xlim=(-0.65, len(data) - 0.35),
        ylim=(-0.18, 0.22),
        yticks=np.arange(-0.15, 0.201, 0.05),
    )
    ax.tick_params(axis="x", labelrotation=90, length=0, labelsize=9)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.45),
        ncol=3,
        frameon=False,
        fontsize=8.8,
        labelcolor=p["muted"],
        handlelength=1.3,
        columnspacing=1.2,
    )
    return fig


def tasks(p):
    data = pd.read_csv(DATA / "tasks.csv")
    # Native direct labels use original occupation group names and markers.
    fig, ax = panel(p, "Employment share · males and females", height=5.0, right=0.65)
    series = [
        (
            "professional_managerial_technical",
            "Professional, managerial,\ntechnical",
            "green",
            "o",
            "-",
        ),
        ("clerical_sales", "Clerical, sales", "ochre", "s", "--"),
        ("production_operators", "Production, operators", "rust", "^", "-."),
        ("service", "Service", "sage", "D", ":"),
    ]
    for col, label, color, marker, style in series:
        (line,) = ax.plot(
            data.year, data[col], color=p[color], marker=marker, ms=4.5, lw=2, ls=style
        )
        assert np.allclose(line.get_ydata(), data[col], atol=0, rtol=0)
        ax.annotate(
            label,
            xy=(2007, data[col].iloc[-1]),
            xytext=(12, 0),
            textcoords="offset points",
            color=p[color],
            va="center",
            fontsize=9.5,
            annotation_clip=False,
        )
    ax.set(
        xlim=(1957, 2008),
        ylim=(0, 0.45),
        xticks=data.year,
        yticks=np.arange(0, 0.41, 0.1),
    )
    ax.set_xlabel("Year", color=p["muted"], labelpad=12)
    return fig


for mode in ["light", "dark"]:
    p = palette(mode)
    for model in MODELS:
        ident = model["id"]
        if "file" in model:
            assert (
                hashlib.sha256(
                    (BOOK / "images/07_images" / model["file"]).read_bytes()
                ).hexdigest()
                == model["source_sha256"]
            )
        if "occupations" in model:
            fig = occupation_bars(model, p)
        else:
            fig = {
                "fig-job-polarization": polarization,
                "fig-polarization-countries": countries,
                "fig-task-changes": tasks,
            }[ident](p)
        fig.savefig(OUT / f"{ident}-{mode}.svg", transparent=True)
        if args.proofs:
            fig.savefig(OUT / f"{ident}-{mode}.pdf", transparent=True)
            fig.patch.set_alpha(1)
            fig.savefig(OUT / f"{ident}-{mode}.png", facecolor=p["paper"], dpi=180)
        plt.close(fig)
        checks.append(dict(id=ident, theme=mode, coordinates_verified=True))
(OUT / "manifest.json").write_text(json.dumps(MODELS, indent=2) + "\n")
(OUT / "verification.json").write_text(json.dumps(checks, indent=2) + "\n")
print(f"Rendered six Chapter 7 charts in light/dark mode: {OUT}")
