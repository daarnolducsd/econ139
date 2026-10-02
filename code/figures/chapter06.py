"""Render Chapter 6 review figures, preserving source/provenance distinctions.

ACS plots use reconstructed aggregates; the Mincer curve uses its original
formula. RD curves are approximate pixel digitizations. Gapminder bubbles use
vector traces of visible source silhouettes, not reconstructed country data.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile

SCRIPT = Path(__file__).resolve().parent
BOOK = SCRIPT.parents[1]
DATA = SCRIPT / "data/chapter06"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-dir", type=Path, default=BOOK / "images/06_images/editorial"
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
from matplotlib.patches import Patch, PathPatch
from matplotlib.path import Path as PlotPath
from matplotlib.ticker import FuncFormatter
from matplotlib.colors import to_rgb

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "lines.solid_capstyle": "round",
    }
)
imports = json.loads((DATA / "imports.json").read_text())
rds = json.loads((DATA / "rd-approximate.json").read_text())
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


def panel(p, unit, height=4.7, bottom=0.19):
    fig, ax = plt.subplots(figsize=(7.2, height))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.86, bottom=bottom)
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


def save(fig, ident, mode, p):
    fig.savefig(OUT / f"{ident}-{mode}.svg", transparent=True)
    if args.proofs:
        fig.savefig(OUT / f"{ident}-{mode}.pdf", transparent=True)
        fig.patch.set_alpha(1)
        fig.savefig(OUT / f"{ident}-{mode}.png", facecolor=p["paper"], dpi=180)
    plt.close(fig)


def mincer(p):
    fig, ax = panel(p, "Log earnings")
    x = np.linspace(0, 25, 100)
    y = 10 + 0.02 * x - 0.0005 * x**2
    source = json.loads((DATA / "mincer.json").read_text())
    assert np.array_equal(x, source["experience"])
    assert np.array_equal(y, source["log_earnings"])
    (curve,) = ax.plot(x, y, color=p["green"], lw=2)
    assert np.array_equal(curve.get_ydata(), y)
    ax.set(
        xlim=(0, 25),
        ylim=(9.99, 10.22),
        xticks=range(0, 26, 5),
        yticks=np.arange(10, 10.201, 0.05),
    )
    ax.set_xlabel("Years of experience", color=p["muted"], labelpad=10)
    ax.text(12, 10.11, "Log earnings", color=p["green"], fontsize=9.5)
    return fig


def acs(ident, p):
    experience = "experience" in ident
    logged = ident.endswith("-log")
    d = pd.read_csv(DATA / ("experience.csv" if experience else "schooling.csv"))
    variable = "exper" if experience else "edu_yrs"
    if experience:
        d = d.loc[d.exper <= 40]
    d = d.dropna(subset=[variable])
    value = "log_wage" if logged else "incwage"
    unit = "Log annual wage income" if logged else "Annual wage income ($)"
    fig, ax = panel(p, unit)
    areas = 220 * d.obs_count / d.obs_count.max()
    dots = ax.scatter(
        d[variable],
        d[value],
        s=areas,
        color=p["green"],
        alpha=0.45,
        linewidth=0.65,
        edgecolor=p["green"],
    )
    assert np.allclose(dots.get_offsets(), np.column_stack([d[variable], d[value]]))
    assert np.allclose(dots.get_sizes() / d.obs_count, 220 / d.obs_count.max())
    if experience:
        ax.set(
            xlim=(-1, 41),
            xticks=range(0, 41, 10),
            ylim=(8.7, 11.5) if logged else (0, 100000),
            yticks=np.arange(9, 11.51, 0.5) if logged else range(0, 100001, 20000),
        )
    else:
        ax.set(
            xlim=(-0.7, 20.7),
            xticks=range(0, 21, 5),
            ylim=(9.3, 11.6) if logged else (0, 140000),
            yticks=np.arange(9.5, 11.51, 0.5) if logged else range(0, 140001, 20000),
        )
    if not logged:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y/1000:.0f}K"))
    ax.set_xlabel(
        "Years of experience" if experience else "Years of schooling",
        color=p["muted"],
        labelpad=10,
    )
    return fig


def rd(model, p):
    ident = model["id"]
    gpa = ident.startswith("fig-ec-")
    units = {
        "fig-scholarship-prob": "Probability of receiving scholarship",
        "fig-college-attendance": "Probability of college attendance",
        "fig-future-earnings": "Earnings / monthly minimum wage",
        "fig-ec-deg-prob": "Economics degree (%)",
        "fig-ec-sat": "SAT score",
        "fig-ec-earnings": "Annual earnings ($)",
    }
    fig, ax = panel(
        p, units[ident], height=5.0, bottom=0.25 if "note" in model else 0.19
    )
    points = np.asarray(model["points"])
    cutoff = model.get("cutoff", 0)
    # Keep each side's fitted segment separate; never connect across treatment.
    for i, line in enumerate(model["fits"]):
        xy = np.asarray(line)
        ax.plot(xy[:, 0], xy[:, 1], color=p["green"], lw=1.8)
        band = model["left_band"] if i == 0 else model["right_band"]
        if band:
            upper, lower = np.asarray(band[0]), np.asarray(band[1])
            ax.fill_between(
                upper[:, 0], lower[:, 1], upper[:, 1], color=p["green"], alpha=0.15
            )
    if gpa:
        areas = np.asarray(model["relative_areas"], float)
        areas = 900 * areas / areas.max()
        ax.scatter(
            points[:, 0],
            points[:, 1],
            s=areas,
            facecolors="none",
            edgecolor=p["green"],
            lw=1.2,
            zorder=3,
        )
        limits = (
            (0, 100)
            if ident.endswith("deg-prob")
            else (1480, 1920)
            if ident.endswith("sat")
            else (39000, 71000)
        )
        ticks = (
            range(0, 101, 20)
            if ident.endswith("deg-prob")
            else range(1500, 1901, 100)
            if ident.endswith("sat")
            else range(40000, 70001, 10000)
        )
        ax.set(xlim=(1.55, 4.3), ylim=limits, xticks=[2, 2.5, 3, 3.5, 4], yticks=ticks)
        if ident.endswith("earnings"):
            ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y/1000:.0f}K"))
        for i, text in enumerate(model["stats"]):
            ax.text(
                0.98,
                0.055 + 0.095 * (len(model["stats"]) - i - 1),
                text,
                transform=ax.transAxes,
                ha="right",
                color=p["ink"],
                fontsize=13,
            )
        ax.set_xlabel("Average GPA in Economics 1 and 2", color=p["muted"], labelpad=10)
    else:
        ax.scatter(points[:, 0], points[:, 1], s=13, color=p["green"], zorder=3)
        earnings = ident == "fig-future-earnings"
        ax.set(
            xlim=(-52, 52) if not earnings else (-41, 41),
            ylim=(-0.03, 1.04) if not earnings else (-0.04, 2.04),
            xticks=[-40, -20, 0, 20, 40],
            yticks=np.arange(0, 1.01, 0.2) if not earnings else np.arange(0, 2.01, 0.4),
        )
        ax.set_xlabel("Distance to SABER 11 cutoff", color=p["muted"], labelpad=10)
    ax.axvline(cutoff, color=p["rust"], ls="--", lw=1.2)
    if "note" in model:
        note = (
            "Sample restricted to SISBEN-eligible individuals"
            if model["note"] == "SISBEN-eligible individuals"
            else model["note"]
        )
        ax.text(0, -0.32, note, transform=ax.transAxes, color=p["muted"], fontsize=9)
    return fig


def scores(p):
    model = json.loads((DATA / "scores-approximate.json").read_text())
    xy = np.asarray(model["bars"])
    fig, ax = panel(p, "Percentage")
    ax.bar(
        xy[:, 0],
        xy[:, 1],
        width=model["bar_width"],
        color=p["green"],
        alpha=0.7,
        edgecolor=p["paper"],
        lw=0.2,
    )
    ax.axvline(310, color=p["rust"], lw=1.3)
    ax.text(
        325, 4.6, "SPP eligibility\n(~ top 9%)", color=p["rust"], fontsize=9.5, va="top"
    )
    ax.set(
        xlim=(-10, 510), ylim=(0, 5.1), xticks=range(0, 501, 100), yticks=range(0, 6)
    )
    ax.set_xlabel("SABER 11 test score", color=p["muted"], labelpad=10)
    return fig


def popularity(p):
    m = json.loads((DATA / "rdd-popularity-approximate.json").read_text())
    xy = np.asarray(m["series"])
    fig, ax = panel(p, "Number of studies mentioning RDD", bottom=0.26)
    ax.plot(xy[:, 0], xy[:, 1], color=p["green"], lw=2)
    ax.axvline(1999, color=p["rust"], ls="--", lw=1)
    ax.set(
        xlim=(1960, 2020),
        ylim=(0, 6200),
        xticks=[1960, 1980, 2000, 2020],
        yticks=[0, 2000, 4000, 6000],
    )
    ax.set_xlabel("Year", color=p["muted"], labelpad=10)
    ax.text(
        0,
        -0.33,
        "Vertical bar: Angrist and Lavy (1999) and Black (1999)",
        transform=ax.transAxes,
        color=p["muted"],
        fontsize=9,
    )
    return fig


def gap(model, p):
    # Preserve the source's visible bubbles and overlaps as scalable paths.
    # Axis calibration is in resized-source pixels (2048 px width).
    source = BOOK / "images/06_images" / model["file"]
    assert hashlib.sha256(source.read_bytes()).hexdigest() == model["sha256"]
    traces = json.loads((DATA / "bubble-traces.json").read_text())
    trace = next(t for t in traces if t["file"] == model["file"])
    assert trace["source_sha256"] == model["sha256"]
    men = model["file"] == "gap1.png"
    bounds = trace["bounds_display_pixels"]
    width, height = trace["crop_size"]
    colors = [p["green"], p["rust"], p["ochre"], p["sage"]]
    # GDP uses log2 coordinates so equal pixel spacings still represent doublings.
    xtick = 436 if men else 203
    x_at_tick = 2 if men else 0
    x_step = 120.75
    xmin = x_at_tick + (bounds[0] - xtick) / x_step
    xmax = x_at_tick + (bounds[2] - xtick) / x_step
    y500 = 760 if men else 617
    ystep = 70.2 if men else 55.7
    ymin = np.log2(500) + (y500 - bounds[3]) / ystep
    ymax = np.log2(500) + (y500 - bounds[1]) / ystep
    plot_height = 6.192 / (width / height)
    fig_height = plot_height / 0.60
    fig, ax = panel(
        p,
        "GDP per capita (PPP$2017, price/inflation adjusted)",
        height=fig_height,
        bottom=0.26,
    )
    # Native SVG paths keep the visible source silhouettes sharp at any zoom.
    # Preserve overlaps; do not invent fully occluded circles or country records.
    for group, color in zip(trace["groups"], colors):
        vertices, codes = [], []
        for source_path in group["paths"]:
            path = np.asarray(source_path)
            x = xmin + path[:, 0] * (xmax - xmin) / width
            y = ymax - path[:, 1] * (ymax - ymin) / height
            vertices.extend(np.column_stack([x, y]))
            codes.extend(
                [PlotPath.MOVETO]
                + [PlotPath.LINETO] * (len(path) - 2)
                + [PlotPath.CLOSEPOLY]
            )
        if vertices:
            patch = PathPatch(
                PlotPath(vertices, codes),
                facecolor=(*to_rgb(color), 0.72),
                edgecolor=p["muted"],
                lw=0.40,
                zorder=3,
                joinstyle="round",
                capstyle="round",
            )
            ax.add_patch(patch)
    ticks = np.array([500, 1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000])
    ax.set(
        xlim=(xmin, xmax),
        ylim=(ymin, ymax),
        xticks=range(0, 15, 2),
        yticks=np.log2(ticks),
        yticklabels=["500", "1K", "2K", "4K", "8K", "16K", "32K", "64K", "128K"],
    )
    ax.set_xlabel(
        "Mean years of schooling, "
        + ("men" if men else "women")
        + " 25 years and older",
        color=p["muted"],
        labelpad=10,
    )
    ax.legend(
        handles=[
            Patch(color=c, label=l)
            for c, l in zip(colors, ["Africa", "Asia", "Europe", "Americas"])
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=4,
        frameon=False,
        fontsize=9.5,
        labelcolor=p["muted"],
    )
    return fig


manifest = (
    imports[:2]
    + [
        {
            "id": "mincer-experience-model",
            "caption": "Relationship Between Experience and Log Earnings (Mincer Equation)",
            "unnumbered": True,
        }
    ]
    + imports[2:]
)
for mode in ["light", "dark"]:
    p = palette(mode)
    for m in manifest:
        ident = m["id"]
        if ident == "mincer-experience-model":
            fig = mincer(p)
            kind = "original deterministic model"
        elif ident.startswith("fig-edu-gdp"):
            fig = gap(m, p)
            kind = "vector source silhouette tracing; approximate image reconstruction"
        elif ident.startswith(("fig-experience-", "fig-school-")):
            fig = acs(ident, p)
            kind = "local ACS reconstruction"
        elif ident == "fig-rdd-papers":
            fig = popularity(p)
            kind = "approximate source curve digitization"
        elif ident == "fig-saber-scores":
            fig = scores(p)
            kind = "approximate source histogram digitization"
        else:
            fig = rd(next(x for x in rds if x["id"] == ident), p)
            kind = "approximate RD source digitization"
        save(fig, ident, mode, p)
        checks.append({"id": ident, "theme": mode, "construction": kind})
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
(OUT / "verification.json").write_text(json.dumps(checks, indent=2))
print(
    "Rendered 15 Chapter 6 candidates in light/dark; construction status documented for each."
)
