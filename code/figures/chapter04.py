"""Render Chapter 4 previews from the original deterministic plotting models.

All curve coordinates and deadweight-loss polygons are checked against source.
See README.md for reconstruction details and the source's MFC conventions.
"""
from pathlib import Path
from figure_style import palette
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
    default=BOOK / "images/04_images/editorial",
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
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

models = json.loads((SCRIPT / "data/chapter04/models.json").read_text())
plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "lines.solid_capstyle": "round",
    }
)
checks = []


def label(x, y, text, color, **kwargs):
    return ax.text(x, y, text, color=color, fontsize=9.5, va="center", **kwargs)


def leader(point, position, text, color, ha="left"):
    return ax.annotate(
        text,
        xy=point,
        xytext=position,
        color=color,
        fontsize=9.5,
        ha=ha,
        va="center",
        linespacing=1.5,
        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8},
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
    third = p["third"]
    for model in models:
        ident, v = model["id"], model["values"]
        fig, ax = plt.subplots(figsize=(7.2, 4.7))
        fig.patch.set_alpha(0)
        ax.patch.set_alpha(0)
        fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.19)
        for edge in ["left", "right", "top"]:
            ax.spines[edge].set_visible(False)
        ax.spines["bottom"].set_color(grid)
        ax.set_axisbelow(True)
        ax.grid(axis="y", color=grid, lw=0.65)
        ax.tick_params(axis="y", length=0, pad=8, labelcolor=muted)
        ax.tick_params(
            axis="x", length=3, pad=7, color=grid, labelcolor=muted, labelsize=9.5
        )
        ax.text(
            0,
            1.06,
            "Hourly wage / marginal value ($)",
            transform=ax.transAxes,
            color=muted,
            fontsize=10,
        )
        ax.set_xlabel("Number of baristas", color=muted, labelpad=10)
        ax.set(
            xlim=(0.5, 11.8),
            xticks=range(1, 11),
            ylim=(0, 110),
            yticks=range(0, 101, 20),
        )
        ax.yaxis.set_major_formatter(StrMethodFormatter("${x:.0f}"))
        principal_count = (
            1 if ident == "fig-labor-supply" else 2 if ident == "fig-mfc-curve" else 3
        )
        curves = model["original_curves"][:principal_count]
        colors = [comparison, third, primary]
        if ident == "fig-labor-supply":
            ax.set(ylim=(0, 55), yticks=range(0, 51, 10))
            ax.texts[0].set_text("Hourly wage ($)")
        principal = []
        for i, original in enumerate(curves):
            (line,) = ax.plot(
                original["x"],
                original["y"],
                color=colors[i],
                lw=2.3 if i == 2 else 1.9,
                marker=original["marker"],
                markersize=4.5,
                ls=original["linestyle"],
            )
            principal.append(line)

        if ident == "fig-labor-supply":
            label(6.4, 48, "Labor supply", comparison)
        elif ident == "fig-mfc-curve":
            label(6.7, 94, "Marginal factor cost", third)
            label(7.0, 54, "Labor supply", comparison)
        else:
            flat = ident == "fig-monopsony-flat-supply"
            minimum = ident in ["fig-minimum-wage-mfc", "fig-minimum-wage-too-high"]
            if flat:
                q, w, marginal = (
                    v["optimal_workers_flat"],
                    v["optimal_wage_flat"],
                    v["optimal_mfc_flat"],
                )
            elif minimum:
                high = ident == "fig-minimum-wage-too-high"
                suffix = "_high" if high else ""
                q = v["new_optimal_workers" + suffix]
                w = v["new_optimal_wage" + suffix]
                marginal = v["new_optimal_mfc" + suffix]
            else:
                q, w, marginal = (
                    v["optimal_workers"],
                    v["optimal_wage"],
                    v["optimal_mfc"],
                )
            assert q in [4, 5, 6, 7]
            assert w == (
                50
                if ident == "fig-minimum-wage-too-high"
                else 35
                if ident == "fig-minimum-wage-mfc"
                else q + 28
                if flat
                else 5 * q
            )
            # Stop guides at the economically relevant point, rather than spanning
            # the whole panel. Original discrete equilibrium quantities retained.
            ax.plot([q, q], [0, max(marginal, w)], color=muted, ls=":", lw=1)
            ax.plot([0.5, q], [w, w], color=muted, ls=":", lw=1)
            for value in sorted(set([w, marginal])):
                ax.scatter(q, value, s=30, color=ink, zorder=6)
            label(1.5, 66, "Marginal revenue product", primary)
            if flat:
                leader((10, 48), (8.7, 57), "Marginal factor cost", third)
                leader((10, 38), (9.3, 34), "Labor supply", comparison)
            elif ident == "fig-minimum-wage-mfc":
                label(8.2, 52, "Labor supply", comparison)
                leader((4, 35), (1.7, 27), "MFC: $35", third)
                leader((9, 85), (6.7, 103), "MFC with minimum wage", third)
            elif ident == "fig-minimum-wage-too-high":
                label(9.3, 42, "Labor supply", comparison)
                label(6.7, 57, "MFC with minimum wage: $50", third)
            else:
                label(6.7, 94, "Marginal factor cost", third)
                label(8.2, 52, "Labor supply", comparison)

            # Original shaded polygons are generated from their exact source
            # bounds, with no changes to the units or the employment interval.
            shade = None
            if ident == "fig-monopsony-deadweight-loss":
                shade = ax.fill_between(
                    v["x_dwl"], v["wage_dwl"], v["mrp_dwl"], color=comparison, alpha=0.22
                )
                leader((6, 35), (6.5, 19), "Deadweight\nloss", comparison, ha="center").set_bbox(
                    {"facecolor": paper, "edgecolor": "none", "pad": 1.5}
                )
            elif flat:
                shade = ax.fill_between(
                    v["x_dwl_flat"],
                    v["wage_dwl_flat"],
                    v["mrp_dwl_flat"],
                    color=comparison,
                    alpha=0.22,
                )
                leader((6.4, 36), (6.5, 12), "Deadweight\nloss", comparison, ha="center").set_bbox(
                    {"facecolor": paper, "edgecolor": "none", "pad": 1.5}
                )
            if shade is not None:
                for path, original in zip(
                    shade.get_paths(), model["original_fill_vertices"]
                ):
                    assert np.array_equal(path.vertices, original), ident
                efficient = (
                    v["efficient_employment_flat"]
                    if flat
                    else v["efficient_employment"]
                )
                efficient_wage = 35
                assert efficient == 7
                ax.plot(
                    [efficient, efficient],
                    [0, efficient_wage],
                    color=muted,
                    ls=":",
                    lw=1,
                )
                # Distinct leaders keep the wage, loss area, and efficient quantity
                # readable despite the nearby intersections.
                leader(
                    (efficient, efficient_wage),
                    (7.7, 7),
                    "Efficient employment: 7",
                    muted,
                )
            if minimum:
                position = (6.0, 84) if high else (q + 0.4, 12)
                leader((q, w), position, f"New employment: {q}\nWage paid: ${w}", ink)
            else:
                position = (2.1, 14) if flat else (2.5, 6.5)
                leader(
                    (q, w), position, f"Monopsony: {q} workers\nWage paid: ${w}", ink
                )
            # Verify the discrete hiring decision for the source's steep supply.
            if not flat and not minimum:
                assert 10 * q - 5 == 70 - 5 * q and 10 * (q + 1) - 5 > 70 - 5 * (q + 1)

        for line, original in zip(principal, curves):
            assert np.array_equal(line.get_xdata(), original["x"]), ident
            assert np.array_equal(line.get_ydata(), original["y"]), ident
            assert line.get_marker() == original["marker"], ident
        checks.append(
            {
                "id": ident,
                "theme": mode,
                "source_curves_and_markers_unchanged": True,
                "source_shaded_polygon_unchanged": bool(
                    model["original_fill_vertices"]
                ),
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
    "Rendered seven Chapter 4 figures in both themes; original curves, markers, and shaded polygons verified."
)
