"""Render the approved Chapter 2 figures from their deterministic source models.
See README.md for inputs, construction, verification, and rebuild commands.
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
    default=BOOK / "images/02_images/editorial",
)
parser.add_argument(
    "--proofs", action="store_true", help="Also export PNG and PDF proofs"
)
args = parser.parse_args()
OUTPUT = args.output_dir.resolve()
OUTPUT.mkdir(parents=True, exist_ok=True)
cache = Path(tempfile.gettempdir()) / "econ139-figure-cache"
cache.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

models = json.loads((SCRIPT / "data/chapter02/models.json").read_text())
# Confirm that market demand is the sum of the two discrete cafe schedules.
for model in models:
    values = model["values"]
    if "market_quantities" in values:
        recomputed = [
            sum(mrp >= wage for mrp in values["mrp_cafe1"])
            + sum(mrp >= wage for mrp in values["mrp_cafe2"])
            for wage in values["wage_levels"]
        ]
        assert recomputed == values["market_quantities"]

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "lines.solid_capstyle": "round",
    }
)
checks = []

for mode in ["light", "dark"]:
    dark = mode == "dark"
    paper = "#202522" if dark else "#FAFAF7"
    ink = "#E5EBE6" if dark else "#2B302D"
    muted = "#B6C0B8" if dark else "#616962"
    grid = "#414942" if dark else "#E1E5DF"
    green = "#ACC9BB" if dark else "#3D6155"
    rust = "#D9A278" if dark else "#A36F49"
    sage = "#C0CFC5" if dark else "#758C7F"

    for model in models:
        ident = model["id"]
        v = model["values"]
        fig, ax = plt.subplots(figsize=(7.2, 4.5))
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        fig.subplots_adjust(left=0.09, right=0.97, top=0.88, bottom=0.19)
        for edge in ["left", "right", "top"]:
            ax.spines[edge].set_visible(False)
        ax.spines["bottom"].set_color(grid)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color=grid, lw=0.65)
        ax.tick_params(axis="y", length=0, pad=8, labelcolor=muted)
        ax.tick_params(
            axis="x", length=3, pad=7, color=grid, labelcolor=muted, labelsize=9.5
        )
        ax.set_xlabel("Number of baristas", color=muted, labelpad=10)
        unit = "Hourly wage ($)"
        if ident == "fig-production-function":
            unit = "Lattes produced per hour"
        elif ident in ["fig-mrp-vs-cost", "fig-two-cafes-mrp"]:
            unit = "Marginal revenue product ($)"
        ax.text(0, 1.06, unit, transform=ax.transAxes, fontsize=10, color=muted)
        ax.set(
            ylim=(0, 55),
            yticks=[0, 10, 20, 30, 40, 50],
            xlim=(0.5, 10.5),
            xticks=range(1, 11),
        )
        if ident != "fig-production-function":
            ax.yaxis.set_major_formatter(StrMethodFormatter("${x:.0f}"))
        principal = []

        def curve(x, y, color, marker="o", ls="-", lw=2):
            (line,) = ax.plot(
                x,
                y,
                color=color,
                lw=lw,
                ls=ls,
                marker=marker,
                markersize=4,
                markeredgewidth=0.8,
            )
            principal.append(line)
            return line

        def label(x, y, text, color, **kwargs):
            return ax.text(
                x, y, text, color=color, fontsize=9.5, ha="left", va="center", **kwargs
            )

        if ident == "fig-production-function":
            curve(v["baristas"], v["lattes"], green)
            ax.set(ylim=(0, 60), yticks=[0, 10, 20, 30, 40, 50, 60])

        elif ident == "fig-mrp-vs-cost":
            curve(v["workers"], v["marginal_revenue_product"], green)
            wage = v["cost_per_worker"]
            n = v["intersection_worker"]
            ax.axhline(wage, color=rust, ls="--", lw=1.7)
            ax.plot([n, n], [0, wage], color=muted, ls=":", lw=1)
            ax.scatter(n, wage, s=38, color=ink, zorder=5)
            label(2.3, 46, "Marginal revenue product", green)
            label(1.3, 18, f"Cost per worker: ${wage}", rust)
            ax.annotate(
                "Optimal hiring point",
                xy=(n, wage),
                xytext=(7.4, 28),
                fontsize=9.5,
                color=ink,
                arrowprops={"arrowstyle": "->", "color": muted, "lw": 0.9},
            )

        elif ident == "fig-labor-demand-curve":
            curve(v["workers_hired"], v["wage_levels"], green)
            label(5.7, 32, "Labor demand", green)

        elif ident == "fig-two-cafes-mrp":
            curve(v["workers"], v["mrp_cafe1"], sage)
            curve(v["workers"], v["mrp_cafe2"], rust, marker="s", ls="--")
            label(5.4, 32, "Cafe 1", sage)
            label(5.3, 12, "Cafe 2", rust)

        elif ident == "fig-market-demand":
            curve(v["workers"], v["mrp_cafe1"], sage, lw=1.6)
            curve(v["workers"], v["mrp_cafe2"], rust, marker="s", ls="--", lw=1.6)
            curve(v["market_quantities"], v["wage_levels"], green, marker="D", lw=2.5)
            ax.set(xlim=(0, 21), xticks=range(0, 21, 2))
            ax.set_xticks(range(0, 22), minor=True)
            ax.tick_params(axis="x", which="minor", color=grid, length=2)
            # Label interior segments because the cafes share their last point.
            for text, point, position, color in [
                ("Cafe 1", (7, 20), (8.2, 20), sage),
                ("Cafe 2", (6, 16), (4.2, 16), rust),
                ("Market demand", (14, 15), (15.2, 17), green),
            ]:
                ax.annotate(
                    text,
                    xy=point,
                    xytext=position,
                    fontsize=9.5,
                    color=color,
                    ha="left",
                    va="center",
                    arrowprops={
                        "arrowstyle": "-",
                        "color": color,
                        "lw": 0.8,
                        "shrinkA": 3,
                        "shrinkB": 3,
                    },
                )

        elif ident == "fig-market-equilibrium":
            curve(v["market_quantities"], v["wage_levels"], green, marker="D", lw=2.5)
            curve(v["supply_quantities"], v["supply_wages"], rust, ls="--", lw=2.2)
            q, w = v["equilibrium_workers"], v["equilibrium_wage"]
            ax.set(xlim=(0, 21), xticks=range(0, 21, 2))
            ax.set_xticks(range(0, 22), minor=True)
            ax.tick_params(axis="x", which="minor", color=grid, length=2)
            ax.plot([0, q], [w, w], color=muted, ls=":", lw=1)
            ax.plot([q, q], [0, w], color=muted, ls=":", lw=1)
            ax.scatter(q, w, s=42, color=ink, zorder=6)
            label(3.4, 43, "Labor demand", green)
            label(15.7, 31, "Labor supply", rust)
            ax.annotate(
                f"Equilibrium\n{q} workers, ${w}",
                xy=(q, w),
                xytext=(13.7, 40),
                fontsize=9.5,
                color=ink,
                arrowprops={"arrowstyle": "->", "color": muted, "lw": 0.9},
                linespacing=1.5,
            )
            assert w == 8 + q
            assert dict(zip(v["market_quantities"], v["wage_levels"]))[q] == w

        # Compare the economically meaningful curves with the exact source artists.
        original = model["original_curves"]
        if ident == "fig-mrp-vs-cost":
            originals = [original[0]]
            assert original[1]["y"] == [v["cost_per_worker"]] * 2
            assert original[3]["x"] == [v["intersection_worker"]]
        else:
            originals = original[: len(principal)]
        for candidate, baseline in zip(principal, originals):
            assert np.array_equal(candidate.get_xdata(), baseline["x"]), ident
            assert np.array_equal(candidate.get_ydata(), baseline["y"]), ident
        checks.append(
            {
                "id": ident,
                "theme": mode,
                "principal_curves": len(principal),
                "source_coordinates_unchanged": True,
            }
        )
        fig.savefig(OUTPUT / f"{ident}-{mode}.svg", transparent=True)
        if args.proofs:
            fig.savefig(OUTPUT / f"{ident}-{mode}.pdf", transparent=True)
            fig.patch.set_alpha(1)
            fig.savefig(
                OUTPUT / f"{ident}-{mode}.png",
                facecolor=paper,
                transparent=False,
                dpi=180,
            )
        plt.close(fig)

(OUTPUT / "verification.json").write_text(json.dumps(checks, indent=2))
print(
    "Rendered six Chapter 2 figures in both themes; source curve coordinates verified"
)
