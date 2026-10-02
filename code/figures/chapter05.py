"""Render Chapter 5 figure candidates in the approved green/rust style.

Seven models retain the current chapter's plotted coordinates. Imported charts
have separate, explicit provenance: printed values, approximate pixel readings,
and a raster category recoloring (not a geographic/data replication).
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import tempfile
from statistics import NormalDist

SCRIPT = Path(__file__).resolve().parent
BOOK = SCRIPT.parents[1]
DATA = SCRIPT / "data/chapter05"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-dir", type=Path, default=BOOK / "images/05_images/editorial"
)
parser.add_argument("--proofs", action="store_true")
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
cache = Path(tempfile.gettempdir()) / "econ139-figure-cache"
os.environ.setdefault("MPLCONFIGDIR", str(cache / "matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(cache))
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from PIL import Image

plt.rcParams.update(
    {
        "font.family": "Arial",
        "font.size": 10.5,
        "svg.fonttype": "none",
        "lines.solid_capstyle": "round",
    }
)
models = json.loads((DATA / "models.json").read_text())
imports = json.loads((DATA / "imports.json").read_text())
noncompetes = json.loads((DATA / "noncompetes-approximate.json").read_text())
decomposition = json.loads((DATA / "decomposition.json").read_text())
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
    )


def panel(p, unit, size=(7.2, 4.9), bottom=0.19):
    fig, ax = plt.subplots(figsize=size)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.87, bottom=bottom)
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


def leader(ax, point, position, text, color, ha="left"):
    return ax.annotate(
        text,
        xy=point,
        xytext=position,
        color=color,
        fontsize=9.5,
        ha=ha,
        va="center",
        arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8},
    )


def save(fig, ident, mode, p):
    fig.savefig(OUT / f"{ident}-{mode}.svg", transparent=True)
    if args.proofs:
        fig.savefig(OUT / f"{ident}-{mode}.pdf", transparent=True)
        fig.patch.set_alpha(1)
        fig.savefig(OUT / f"{ident}-{mode}.png", facecolor=p["paper"], dpi=180)
    plt.close(fig)


def firm_diagram(model, index, p):
    fig, ax = panel(p, "Annual wage / marginal value ($)")
    ax.set(
        xlim=(50, 150),
        ylim=(25000, 275000),
        xticks=range(50, 151, 25),
        yticks=range(25000, 275001, 25000),
    )
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"${y / 1000:.0f}K"))
    ax.set_xlabel("Number of employees", color=p["muted"], labelpad=10)
    if index < 2:
        ax.texts[0].set_text("Annual wage ($)")
    count = [0, 1, 4, 6, 6][index]
    colors = (
        [p["rust"]]
        if count == 1
        else (
            [p["rust"], p["sage"], p["green"], p["green"]]
            if count == 4
            else [p["rust"]] * 2 + [p["sage"]] * 2 + [p["green"]] * 2
        )
    )
    for source, color in zip(model["curves"][:count], colors):
        (line,) = ax.plot(
            source["x"], source["y"], color=color, lw=1.9, ls=source["linestyle"]
        )
        assert np.array_equal(line.get_xdata(), source["x"])
        assert np.array_equal(line.get_ydata(), source["y"])
    for i, points in enumerate(model["scatter"]):
        xy = np.asarray(points)
        artist = ax.scatter(
            xy[:, 0],
            xy[:, 1],
            s=32,
            marker="o" if i == 0 else "s",
            color=p["ink"],
            zorder=6,
        )
        assert np.array_equal(artist.get_offsets(), xy)
    for year, x, y in zip(["2023", "2024"], [100, 120], [100000, 110000]):
        ax.annotate(
            year,
            (x, y),
            xytext=(-9, -17),
            textcoords="offset points",
            color=p["ink"],
            fontsize=9.5,
            ha="right",
        )
    if index >= 2:
        points = model["scatter"][1]
        for (x, w), (_, marginal) in zip(model["scatter"][0], points):
            ax.plot([x, x], [w, marginal], color=p["muted"], ls=":", lw=0.9)
    if index == 1:
        leader(ax, (135, 117500), (133, 151000), "Labor supply", p["rust"], "right")
    elif index == 2:
        labels = [
            (0, 135, (133, 67000), "Labor supply", "right"),
            (1, 65, (57, 61000), "Marginal factor cost", "left"),
            (2, 68, (57, 202000), "MRP 2023", "left"),
            (3, 68, (57, 246000), "MRP 2024", "left"),
        ]
        add_curve_labels(ax, model, labels, colors)
    elif index == 3:
        labels = [
            (0, 138, (146, 65000), "Labor supply 2023", "right"),
            (1, 138, (125, 76000), "Labor supply 2024", "right"),
            (2, 138, (145, 123000), "MFC 2023", "right"),
            (3, 138, (145, 157000), "MFC 2024", "right"),
            (4, 62, (56, 211000), "MRP 2023", "left"),
            (5, 62, (56, 240000), "MRP 2024", "left"),
        ]
        add_curve_labels(ax, model, labels, colors)
    elif index == 4:
        labels = [
            (0, 138, (145, 101000), "Labor supply 2023", "right"),
            (1, 138, (126, 70000), "Labor supply 2024", "right"),
            (2, 65, (58, 163000), "MFC 2023", "left"),
            (3, 65, (56, 91000), "MFC 2024", "left"),
            (4, 64, (56, 204000), "MRP 2023", "left"),
            (5, 90, (108, 265000), "MRP 2024", "left"),
        ]
        add_curve_labels(ax, model, labels, colors)
    return fig


def add_curve_labels(ax, model, labels, colors):
    for i, x, position, text, ha in labels:
        curve = model["curves"][i]
        y = float(np.interp(x, curve["x"], curve["y"]))
        leader(ax, (x, y), position, text, colors[i], ha)


def density(model, p):
    fig, ax = panel(p, "Density", bottom=0.24)
    v = model["values"]
    x, y = np.asarray(v["x"]), np.asarray(v["y"])
    normal = NormalDist(0, 0.2)
    assert np.isclose(v["p25"], normal.inv_cdf(0.25))
    assert np.isclose(v["p75"], normal.inv_cdf(0.75))
    assert v["median"] == 0
    assert np.allclose(y, np.exp(-0.5 * (x / 0.2) ** 2) / (0.2 * np.sqrt(2 * np.pi)))
    ax.plot(x, y, color=p["green"], lw=2)
    ax.fill_between(x, y, color=p["green"], alpha=0.13)
    ax.set(
        xlim=(-0.6, 0.6),
        ylim=(0, 2.65),
        xticks=np.arange(-0.6, 0.7, 0.2),
        yticks=np.arange(0, 2.1, 0.5),
    )
    ax.set_xlabel("Log wage premium (firm effect)", color=p["muted"], labelpad=10)
    for q, text, side in [
        (v["p25"], "25th percentile\n(−0.135)", -1),
        (v["median"], "Median (average firm)\n(0.000)", 0),
        (v["p75"], "75th percentile\n(0.135)", 1),
    ]:
        ax.axvline(q, color=p["rust"] if side else p["sage"], lw=1.1, ls="--")
        ax.text(
            q if not side else side * 0.38,
            2.35,
            text,
            color=p["ink"],
            ha="center",
            va="center",
            fontsize=9.5,
        )
        if side:
            leader(
                ax,
                (q, 1.4),
                (side * 0.39, 1.2),
                "25% of firms pay\n"
                + ("less than this" if side < 0 else "more than this"),
                p["muted"],
                "center",
            )
    ax.text(
        0.98,
        -0.27,
        "Standard deviation: 0.2",
        transform=ax.transAxes,
        ha="right",
        fontsize=9,
        color=p["muted"],
    )
    return fig


def merger(model, p):
    fig, ax = panel(p, "Change in earnings (%)", bottom=0.24)
    v = model["values"]
    effects = v["earnings_impact"]
    bars = ax.bar(range(3), effects, width=0.58, color=p["rust"])
    assert [b.get_height() for b in bars] == effects
    ax.axhline(0, color=p["muted"], lw=1)
    ax.set(
        ylim=(-4, 0.5),
        yticks=np.arange(-4, 0.6, 0.5),
        xticks=range(3),
        xticklabels=v["merger_types"],
    )
    for x, value in enumerate(effects):
        ax.text(x, value - 0.16, f"{value:.1f}%", ha="center", va="top", color=p["ink"])
    return fig


def noncompete(model, p):
    fig, ax = panel(
        p, "Probability of having a non-compete", size=(8, 5.7), bottom=0.31
    )
    n = len(model["means"])
    xs = np.arange(n)
    ax.set(
        xlim=(-0.65, n - 0.35),
        ylim=(0, 0.64),
        yticks=np.arange(0, 0.61, 0.1),
        xticks=xs,
        xticklabels=model["categories"],
    )
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.1f}"))
    for x, bounds, lo_ci, hi_ci in zip(
        xs, model["bounds"], model["lower_ci"], model["upper_ci"]
    ):
        lo, hi = bounds
        ax.add_patch(
            Rectangle(
                (x - 0.36, lo),
                0.72,
                hi - lo,
                fill=False,
                edgecolor=p["sage"],
                linewidth=0.9,
                alpha=0.7,
            )
        )
        for ci in [lo_ci, hi_ci]:
            ax.plot([x + 0.10, x + 0.10], ci, color=p["sage"], lw=0.8, alpha=0.7)
            ax.plot([x + 0.075, x + 0.125], [ci[0]] * 2, color=p["sage"], lw=0.8)
            ax.plot([x + 0.075, x + 0.125], [ci[1]] * 2, color=p["sage"], lw=0.8)
    means = np.asarray(model["means"])
    intervals = np.asarray(model["mean_ci"])
    ax.errorbar(
        xs,
        means,
        yerr=[means - intervals[:, 0], intervals[:, 1] - means],
        fmt="o",
        color=p["green"],
        ms=4.7,
        capsize=2,
        lw=1.1,
        zorder=5,
    )
    for x, value in zip(xs, means):
        ax.annotate(
            f"{value:.2f}",
            (x, value),
            xytext=(6, 4),
            textcoords="offset points",
            color=p["ink"],
            fontsize=9,
        )
    ax.axhline(model["overall"], color=p["rust"], ls="--", lw=1.2)
    ax.set_xlabel(
        "Annual earnings in $1,000s" if n == 8 else "Non-compete enforceability level",
        color=p["muted"],
        labelpad=10,
    )
    handles = [
        Patch(
            facecolor="none",
            edgecolor=p["sage"],
            label="Upper–lower bounds of incidence",
        ),
        Line2D(
            [],
            [],
            color=p["green"],
            marker="o",
            lw=0,
            label="Multiple-imputation incidence estimate",
        ),
        Line2D([], [], color=p["sage"], marker="|", lw=1, label="95% CI"),
        Line2D(
            [],
            [],
            color=p["rust"],
            ls="--",
            lw=1.2,
            label="Overall multiple-imputation incidence",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.28),
        ncol=2,
        frameon=False,
        fontsize=8.5,
        labelcolor=p["muted"],
        columnspacing=1.2,
    )
    return fig


def inequality(p):
    fig, ax = panel(p, "Change in log 90/10 ratio", bottom=0.27)
    a = np.asarray(decomposition["log90_50"])
    b = np.asarray(decomposition["log50_10"])
    ax.bar(range(3), a, width=0.58, color=p["green"])
    ax.bar(range(3), b, bottom=a, width=0.58, color=p["rust"])
    ax.axhline(0, color=p["muted"], lw=1)
    ax.set(
        ylim=(-0.3, 0.35),
        yticks=np.arange(-0.3, 0.351, 0.05),
        xticks=range(3),
        xticklabels=decomposition["categories"],
    )
    for x in range(3):
        if abs(a[x]) < 0.04:
            leader(ax, (x, a[x] / 2), (x, 0.045), f"{a[x]:.3f}", p["green"], "center")
        else:
            ax.text(
                x,
                a[x] / 2,
                f"{a[x]:.3f}",
                color=p["paper"],
                ha="center",
                va="center",
                fontsize=9.5,
            )
        ax.text(
            x,
            a[x] + b[x] / 2,
            f"{b[x]:.3f}",
            color=p["paper"],
            ha="center",
            va="center",
            fontsize=9.5,
        )
    ax.legend(
        handles=[
            Patch(color=p["green"], label="log 90/50 ratio"),
            Patch(color=p["rust"], label="log 50/10 ratio"),
        ],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.24),
        ncol=2,
        frameon=False,
        fontsize=9.5,
        labelcolor=p["muted"],
    )
    return fig


def concentration(p):
    """Recolor the source map's pixels, preserving its geography and artifacts.

    This is a raster style preview. It does not infer CZ data, repair striping,
    interpolate a concentration value, or substitute a different map vintage.
    """
    original = BOOK / "images/05_images/concentration.png"
    source = next(m for m in imports if m["id"] == "fig-concentration")
    assert hashlib.sha256(original.read_bytes()).hexdigest() == source["sha256"]
    # Crop only the source map; its embedded legend is replaced by native text.
    rgb = np.asarray(Image.open(original).convert("RGB"))[80:800, 95:1305].copy()
    # Legend occupies this lower-right region; it is outside all mapped land.
    rgb[580:, 970:] = 255
    # Nearest source colors distinguish the four ordered categories, no-data,
    # white areas, and black boundaries. Antialiasing is kept as ink blending.
    source_colors = np.array(
        [
            [188, 30, 43],
            [229, 151, 173],
            [241, 201, 214],
            [255, 255, 255],
            [190, 190, 190],
            [0, 0, 0],
        ]
    )
    distances = ((rgb.astype(float)[:, :, None, :] - source_colors) ** 2).sum(axis=3)
    classes = distances.argmin(axis=2)
    from matplotlib.colors import to_rgb

    colors = ["#A36F49", "#C49A77", "#E5D4BD", p["paper"], p["grid"], p["muted"]]
    if p["paper"] == "#202522":
        colors[:3] = ["#D9A278", "#A77957", "#685440"]
    image = np.array([to_rgb(c) for c in colors])[classes]
    # Outside-white is the page color. Low-HHI white uses the same page color,
    # retaining the source's boundaries and category classification.
    fig, ax = plt.subplots(figsize=(8, 5.6))
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.13)
    ax.imshow(image, interpolation="nearest")
    ax.axis("off")
    handles = [
        Patch(facecolor=c, edgecolor=p["muted"], lw=0.5, label=t)
        for c, t in zip(
            colors[:5],
            [
                "Very high (5,000–10,000)",
                "High (2,500–5,000)",
                "Moderate (1,500–2,500)",
                "Low (0–1,500)",
                "No data",
            ],
        )
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=3,
        frameon=False,
        fontsize=8.8,
        labelcolor=p["muted"],
        title="HHI concentration category",
        title_fontsize=9.5,
    )
    fig.legends[0].get_title().set_color(p["muted"])
    return fig


manifest = models[:6] + imports[:3] + [models[6], imports[3]]
for mode in ["light", "dark"]:
    p = palette(mode)
    for index, model in enumerate(models):
        fig = (
            firm_diagram(model, index, p)
            if index < 5
            else density(model, p)
            if index == 5
            else merger(model, p)
        )
        save(fig, model["id"], mode, p)
        checks.append(
            {
                "id": model["id"],
                "theme": mode,
                "provenance": "current local 05.qmd",
                "source_model_preserved": True,
            }
        )
    for model in noncompetes:
        save(noncompete(model, p), model["id"], mode, p)
        checks.append(
            {
                "id": model["id"],
                "theme": mode,
                "approximate_intervals": True,
                "printed_means_preserved": True,
            }
        )
    save(inequality(p), "fig-inequality-decomp", mode, p)
    save(concentration(p), "fig-concentration", mode, p)
    checks.extend(
        [
            {
                "id": "fig-inequality-decomp",
                "theme": mode,
                "printed_rounded_values_preserved": True,
            },
            {"id": "fig-concentration", "theme": mode, "raster_recolor_only": True},
        ]
    )
(OUT / "manifest.json").write_text(
    json.dumps([{"id": m["id"], "caption": m["caption"]} for m in manifest], indent=2)
)
(OUT / "verification.json").write_text(json.dumps(checks, indent=2))
print(
    "Rendered eleven candidates in light and dark; imported approximations explicitly recorded."
)
