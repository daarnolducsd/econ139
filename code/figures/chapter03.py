"""Render Chapter 3 previews from documented models and public aggregate CSVs.

No raw microdata are needed for rendering. See README.md for reconstruction.
"""
from pathlib import Path
import argparse
import json
import os
import tempfile

SCRIPT = Path(__file__).resolve().parent
BOOK = SCRIPT.parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-dir",
    type=Path,
    default=BOOK / "images/03_images/editorial",
)
parser.add_argument("--proofs", action="store_true")
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
cache = Path(tempfile.gettempdir()) / "econ139-figure-cache"
cache.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

DATA = SCRIPT / "data/chapter03"
models = json.loads((DATA / "models.json").read_text())
extra = [
    {"id": "fig-clemens0", "caption": "Textbook Minimum Wage Analysis"},
    {"id": "fig-clemens1", "caption": "Partial Offset Through Price Pass-Through"},
    {"id": "fig-90-10", "caption": "90-10 Ratio Over Time"},
]
models[6:6] = extra
hist = pd.read_csv(DATA / "histograms.csv")
inequality = pd.read_csv(DATA / "inequality.csv")
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "lines.solid_capstyle": "round",
    }
)
checks = []


def style(ax, unit, xlabel, gridlines=True):
    ax.patch.set_alpha(0)
    for edge in ["left", "right", "top"]:
        ax.spines[edge].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    ax.set_axisbelow(True)
    if gridlines:
        ax.grid(axis="y", color=grid, lw=0.65)
    ax.tick_params(axis="y", length=0, pad=8, labelcolor=muted)
    ax.tick_params(
        axis="x", length=3, pad=7, color=grid, labelcolor=muted, labelsize=9.5
    )
    ax.text(0, 1.06, unit, transform=ax.transAxes, color=muted, fontsize=10)
    ax.set_xlabel(xlabel, color=muted, labelpad=10)


def label(ax, x, y, text, color, **kwargs):
    return ax.text(x, y, text, color=color, fontsize=9.5, va="center", **kwargs)


def leader(ax, point, position, text, color):
    ax.annotate(
        text,
        xy=point,
        xytext=position,
        fontsize=9.5,
        color=color,
        va="center",
        linespacing=1.5,
        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8},
    )


def bracket(ax, left, right, y, text, label_offset=0.3):
    ax.annotate(
        "",
        xy=(left, y),
        xytext=(right, y),
        arrowprops={"arrowstyle": "|-|", "lw": 1, "color": ink},
    )
    label(ax, (left + right) / 2, y + label_offset, text, ink, ha="center")


def histogram_panel(ax, counter=False, maximum=None):
    counts = hist.counterfactual if counter else hist.actual
    bars = ax.bar(
        hist.left,
        counts,
        width=hist.right - hist.left,
        align="edge",
        color=green,
        alpha=0.85,
        edgecolor=paper,
        linewidth=0.35,
    )
    assert np.array_equal([bar.get_height() for bar in bars], counts)
    maximum = maximum or max(hist.actual) * 1.365
    ax.set(xlim=(0, 40), ylim=(0, maximum), xticks=range(0, 41, 5))
    ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    style(ax, "Frequency", "Hourly wage ($)")
    if not counter:
        ax.axvline(3.35, color=rust, ls="--", lw=1.5)
        leader(
            ax,
            (3.35, maximum * 0.75),
            (10, maximum * 0.82),
            "Actual minimum wage: $3.35",
            rust,
        )
    ax.axvline(4.77, color=ink, ls=":", lw=1.5)
    leader(
        ax,
        (4.77, maximum * 0.60),
        (10, maximum * 0.66),
        "Counterfactual minimum wage: $4.77",
        ink,
    )
    return bars


for mode in ["light", "dark"]:
    dark = mode == "dark"
    paper = "#202522" if dark else "#FAFAF7"
    ink = "#E5EBE6" if dark else "#2B302D"
    muted = "#B6C0B8" if dark else "#616962"
    grid = "#414942" if dark else "#E1E5DF"
    green = "#ACC9BB" if dark else "#3D6155"
    rust = "#D9A278" if dark else "#A36F49"
    for model in models:
        ident = model["id"]
        v = model.get("values", {})
        paired = ident == "fig-counterfactual-wage-distribution"
        fig, axes = plt.subplots(
            2 if paired else 1, 1, figsize=(7.2, 8.6 if paired else 4.7)
        )
        fig.patch.set_alpha(0)
        fig.subplots_adjust(
            left=0.10,
            right=0.96,
            top=0.86 if paired else 0.88,
            bottom=0.13 if paired else 0.19,
            hspace=0.72,
        )
        ax = np.atleast_1d(axes)[0]
        principal = []

        def curve(x, y, color, marker=None, ls="-", lw=2):
            (line,) = ax.plot(
                x, y, color=color, lw=lw, marker=marker, markersize=4.5, ls=ls
            )
            principal.append(line)
            return line

        if ident == "fig-minimum-wage-theory":
            style(ax, "Wage ($)", "Quantity of labor", gridlines=False)
            curve(v["quantity_demand"], v["wage_demand"], green)
            curve(v["quantity_supply"], v["wage_supply"], rust)
            minimum, equilibrium = v["min_wage"], v["equilibrium_quantity"]
            qd, qs = v["q_demand_at_min_wage"], v["q_supply_at_min_wage"]
            ax.axhline(minimum, color=ink, ls="--", lw=1.4)
            for q, w in [
                (qd, minimum),
                (equilibrium, v["equilibrium_wage"]),
                (qs, minimum),
            ]:
                ax.plot([q, q], [0, w], color=muted, ls=":", lw=1)
                ax.scatter(q, w, color=ink, s=28, zorder=5)
            ax.set(
                xlim=(0, 90),
                ylim=(0, 10),
                xticks=[qd, equilibrium, qs],
                xticklabels=[r"$Q_2$", r"$Q_1$", r"$Q_3$"],
                yticks=[0, 2.5, 5, 7.25, 10],
            )
            ax.yaxis.set_major_formatter(StrMethodFormatter("${x:g}"))
            label(ax, 63, 1.3, "Labor demand", green)
            label(ax, 68, 8.5, "Labor supply", rust)
            label(ax, 3, 6.75, "Minimum wage: $7.25", ink)
            bracket(ax, qd, qs, 7.8, "Unemployment")
            assert qd == 27.5 and qs == 72.5 and equilibrium == 50

        elif ident in [
            "fig-did-illustration",
            "fig-did-growing-employment",
            "fig-card-krueger-data",
            "fig-pre-trends-violation",
            "fig-did-stable-pretrends",
        ]:
            style(
                ax,
                "Employment (number of workers)",
                "Year" if "pre" in ident else "Period",
            )
            stable = ident == "fig-did-stable-pretrends"
            x = v["years"] if stable else v["time_periods"]
            nj = v["nj_employment"] if stable else v["employment_nj"]
            pa = v["pa_employment"] if stable else v["employment_pa"]
            curve(x, nj, green, "o")
            curve(x, pa, rust, "s")
            pre = len(x) > 2
            limits = {
                "fig-did-illustration": (12, 30),
                "fig-did-growing-employment": (18, 32),
                "fig-card-krueger-data": (15, 25),
                "fig-pre-trends-violation": (16, 28),
                "fig-did-stable-pretrends": (18, 25),
            }
            ax.set(ylim=limits[ident])
            policy = 1991.5 if pre else 0.5
            ax.axvline(policy, color=muted, ls=":", lw=1)
            ax.text(
                policy,
                0.96,
                "Minimum wage change",
                transform=ax.get_xaxis_transform(),
                ha="center",
                color=muted,
                fontsize=9,
            )
            if pre:
                ax.set(xlim=(1987.8, 1994.0), xticks=x)
                # Endpoint values nearly meet; separate direct labels with leaders.
                leader(ax, (1992, pa[-1]), (1992.3, 23.0), "Pennsylvania", rust)
                leader(ax, (1992, nj[-1]), (1992.3, 20.0), "New Jersey", green)
            else:
                cf = v["employment_nj_counterfactual"]
                curve(x, cf, green, ls="--", lw=1.5)
                ax.set(
                    xlim=(-0.08, 1.90), xticks=[0, 1], xticklabels=["Before", "After"]
                )
                d1, d2 = nj[1] - nj[0], pa[1] - pa[0]
                assert np.isclose(cf[1], nj[0] + d2)
                fmt = ".2f" if ident == "fig-card-krueger-data" else ".0f"
                nj_y, pa_y, cf_y = nj[-1], pa[-1], cf[-1]
                if ident == "fig-card-krueger-data":
                    nj_y, pa_y = 20.4, 22.6
                leader(
                    ax,
                    (1, pa[-1]),
                    (1.15, pa_y),
                    f"Pennsylvania (Control)\nD2 ({d2:+{fmt}})",
                    rust,
                )
                leader(
                    ax,
                    (1, nj[-1]),
                    (1.15, nj_y),
                    f"New Jersey (Treatment)\nD1 ({d1:+{fmt}})",
                    green,
                )
                leader(
                    ax, (1, cf[-1]), (1.15, cf_y), "New Jersey\n(Counterfactual)", green
                )
                ax.annotate(
                    "",
                    xy=(0.98, nj[-1]),
                    xytext=(0.98, cf[-1]),
                    arrowprops={"arrowstyle": "<->", "color": ink, "lw": 1},
                )
                effect_y = (nj[-1] + cf[-1]) / 2
                if ident == "fig-did-illustration":
                    effect_y += 1
                label(
                    ax,
                    0.90,
                    effect_y,
                    f"ΔE ({d1-d2:+{fmt}})",
                    ink,
                    ha="right",
                )

        elif ident in ["fig-clemens0", "fig-clemens1"]:
            # Normalized schematic coordinates, not measured data or digitization.
            # D1=10-L, S=L; w1=5, w_min,2=7. Price pass-through shifts D2 to 11.5-L.
            # L2 is 3 in the standard case and 4.5 with pass-through, both < L1=5.
            shift = ident == "fig-clemens1"
            style(ax, "Wage (w)", "Labor (L)", gridlines=False)
            curve([0.5, 7.5], [9.5, 2.5], green, ls="--" if shift else "-")
            curve([0.5, 8.5], [0.5, 8.5], rust)
            if shift:
                curve([2, 8], [9.5, 3.5], green)
            l2 = 4.5 if shift else 3
            ax.set(
                xlim=(0, 13),
                ylim=(0, 11),
                xticks=[l2, 5],
                xticklabels=[r"$L_2$", r"$L_1$"],
                yticks=[5, 7],
                yticklabels=[r"$w_1$", r"$w_{\mathrm{min},2}$"],
            )
            ax.spines["left"].set_visible(True)
            ax.spines["left"].set_color(grid)
            ax.plot([0, 10.5], [5, 5], color=muted, ls=":", lw=1)
            ax.plot([0, 10.5], [7, 7], color=ink, lw=1.4)
            for q, w in [(l2, 7), (5, 5)]:
                ax.plot([q, q], [0, w], color=muted, ls=":", lw=1)
                ax.scatter(q, w, s=30, color=ink, zorder=5)
            bracket(ax, l2, 7, 7.5, "Unemployment")
            bracket(ax, l2, 5, 0.45, "Employment decline", label_offset=0.9)
            ax.annotate(
                "",
                xy=(-0.08, 7),
                xytext=(-0.08, 5),
                arrowprops={"arrowstyle": "->", "color": ink, "lw": 1},
                annotation_clip=False,
            )
            label(ax, 8.5, 9, "S(L)", rust)
            if shift:
                label(ax, 8, 2.5, r"$D_1(L)=MP(L)\times P_1$", green)
                label(ax, 8.5, 3.7, r"$D_2(L)=MP(L)\times P_2$", green)
                ax.annotate(
                    "",
                    xy=(7.2, 4.3),
                    xytext=(7.2, 2.8),
                    arrowprops={"arrowstyle": "->", "color": muted, "lw": 1},
                )
            else:
                label(ax, 8, 2.5, r"$D(L)=MP(L)\times P$", green)
            assert l2 < 5 < 7

        elif ident == "fig-90-10":
            style(ax, "90–10 wage ratio", "Year")
            curve(inequality.year, inequality.ratio, green, "o")
            principal[-1].set_markerfacecolor(paper)
            ax.set(
                xlim=(1978.8, 1989.3),
                ylim=(3.55, 4.65),
                xticks=range(1979, 1990),
                yticks=np.arange(3.6, 4.7, 0.2),
            )
            assert len(inequality) == 11

        elif ident == "fig-wage-distribution":
            histogram_panel(ax)
            maximum = ax.get_ylim()[1]
            ax.annotate(
                "",
                xy=(4.77, maximum * 0.94),
                xytext=(3.35, maximum * 0.94),
                arrowprops={"arrowstyle": "->", "color": ink, "lw": 1},
            )
            label(ax, 5.4, maximum * 0.94, "Decline in real value", ink)

        elif paired:
            maximum = max(hist.actual.max(), hist.counterfactual.max()) * 1.1
            for panel, counter in zip(axes, [False, True]):
                histogram_panel(panel, counter, maximum)
                panel.text(
                    0,
                    1.19,
                    "Counterfactual wage distribution in 1989"
                    if counter
                    else "Actual wage distribution in 1989",
                    transform=panel.transAxes,
                    color=ink,
                    fontsize=11,
                )

        if "original_curves" in model and principal:
            for line, original in zip(principal, model["original_curves"][0]):
                assert np.array_equal(line.get_xdata(), original["x"]), ident
                assert np.array_equal(line.get_ydata(), original["y"]), ident
        if ident in ["fig-wage-distribution", "fig-counterfactual-wage-distribution"]:
            baseline = model["original_curves"]
            assert baseline[0][0]["x"] == [3.35, 3.35]
            assert baseline[0][1]["x"] == [4.77, 4.77]
            for panel, original in enumerate(model["original_histograms"]):
                expected = hist.counterfactual if panel == 1 else hist.actual
                assert np.array_equal([bar["count"] for bar in original], expected)
                assert np.array_equal([bar["left"] for bar in original], hist.left)
                assert np.array_equal(
                    [bar["width"] for bar in original], hist.right - hist.left
                )
        checks.append(
            {
                "id": ident,
                "theme": mode,
                "verification": "schematic relationships and labels"
                if ident.startswith("fig-clemens")
                else "source curves or aggregate counts unchanged",
            }
        )
        fig.savefig(OUT / f"{ident}-{mode}.svg", transparent=True)
        if args.proofs:
            fig.savefig(OUT / f"{ident}-{mode}.pdf", transparent=True)
            fig.patch.set_alpha(1)
            fig.savefig(OUT / f"{ident}-{mode}.png", facecolor=paper, dpi=180)
        plt.close(fig)
(OUT / "verification.json").write_text(json.dumps(checks, indent=2))
(OUT / "manifest.json").write_text(
    json.dumps([{"id": m["id"], "caption": m["caption"]} for m in models], indent=2)
)
print(
    f"Rendered {len(models)} Chapter 3 figures in both themes; curves and counts verified."
)
