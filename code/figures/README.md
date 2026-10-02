# Textbook figure construction

This directory contains the maintained code for the approved figure redesign. The files under the course's `outputs/` directory are review artifacts; the renderer here is the source for the book's redesigned assets.

## Chapter 1

### Files and responsibilities

- `chapter01.py`: draws the four approved charts in both themes from committed plotted-series CSVs.
- `replicate_chapter01.py`: reconstructs those plotted series from the original local course inputs and verifies their calculations. It writes derived files only.
- `data/chapter01/*.csv`: public, aggregated plotted-series snapshots. These allow rendering from a standalone textbook checkout without the larger course tree.
- `data/chapter01/verification.json`: counts, periods, independent calculation checks, and hashes of the original inputs and figures at review time.
- `../../images/01_images/editorial/*.svg`: the eight book assets (four charts × two themes).
- `../../01.qmd`: figure references and existing captions. Each pair has one figure ID and caption.
- `../../styles.css`: hides the alternate theme image. The light and dark SVGs share the same data and geometry; only colors differ.

### Render the committed series

From the `textbook/` directory, with Python 3 and the packages listed in `requirements.txt`:

```bash
python3 code/figures/chapter01.py
```

This regenerates the SVGs in `images/01_images/editorial/`. For an isolated review with PNG/PDF proofs:

```bash
python3 code/figures/chapter01.py --output-dir ../outputs/textbook-chapter01-rebuild --proofs
```

The Python available on David's computer with these packages is:

```bash
/Applications/Anaconda-Navigator.app/Contents/MacOS/python code/figures/chapter01.py
```

Do not run a renderer under a Python environment without its plotting dependencies. The original default Quarto Python kernel did not have matplotlib installed.

### Reconstruct from original inputs

From `textbook/`, with the full ECON139 course tree available:

```bash
python3 code/figures/replicate_chapter01.py
```

By default, this reads the sibling `code/textbook/01/` inputs and writes to `../outputs/textbook-chapter01-replication/`. To use a different location:

```bash
python3 code/figures/replicate_chapter01.py --course-root /path/to/ECON139 --output-dir /path/to/derived-output
```

Review the generated `verification.json` and compare its CSVs with `data/chapter01/` before deliberately refreshing the committed snapshots. The script never overwrites its input files. Stata's original plotting scripts remain the reference for the calculations; their stale paths and exports were not edited.

### Data and transformations

| Asset stem / figure ID | Original input and reference code | Preserved calculation |
| --- | --- | --- |
| `inequality` / `fig-piketty-saez` | `code/textbook/01/data/inequality1.csv`; `code/textbook/01/code/saez.do` | Top 1% and bottom 50% income shares, 1917–2023; 107 observations per series; share stored as a fraction and displayed as percent |
| `education` / `fig-autor-income` | `code/textbook/01/code/autor/wages.dta`; `wage_change_plot.do` in that directory | Men, five education groups, 1963–2017; analytic-weighted mean of log real weekly wages (`rplnwkw`, weight `avlswt`), normalized by subtracting the group's 1963 mean; original Stata float storage retained |
| `labor-share` / `fig-laborshare` | `code/textbook/01/data/labor_share.csv`; `code/textbook/01/code/labor_share.do` | Annual arithmetic mean of quarterly percentages, 1947–2016; final year has three quarters; original event dates and arrow targets preserved |
| `participation` / `fig-lfpr` | `code/textbook/01/data/LFP_men.csv`, `LFP_women.csv`; `code/textbook/01/code/lfp.do` | Annual arithmetic mean of monthly percentages, 1948–2025; final year includes January–May |

Original input/reference paths in this table are relative to the **ECON139 course root**, rather than the textbook root. These local plotted inputs are not the complete underlying replication packages for the cited papers.

The education y-axis shows changes in **mean log wages**, not ordinary percentage changes or the log of arithmetic mean wages. No smoothing, extrapolation, new observations, or endpoint extension is applied. Independent scalar calculations agree with the plotted series, including the float-normalized education values. See the verification record.

### Appearance and review

The four previews were approved before integration. They use Arial/system-compatible sans-serif labels, quiet horizontal grids, transparent SVGs, and the approved green/rust palette. The education chart adds three muted supporting colors and distinct line patterns. Men/top-income shares retain rust, women/bottom-income shares retain green; related series are labeled directly. Labor share retains its four historical annotations.

`--proofs` produces themed background PNGs and transparent PDFs for inspection. Published HTML uses the paired SVGs. The PDF edition of the book has not been redesigned or verified as part of this release.

### Book verification and publication

Render the affected chapter with Quarto and inspect it in both themes. Preserve its four figure IDs, caption text, and all unrelated local edits. Check SVG resources, theme visibility, cross-references, and existing hover/lightbox behavior.

Source changes and GitHub Pages output are committed separately in this repository's existing `main` and `gh-pages` workflow. Render in an isolated publication checkout when the working tree contains unrelated unpublished chapter changes. Push only when David requests publication and verify the deployed files afterward.

The installed Stata SE license was expired during this exercise; a successful Stata rerun is **not** claimed. The documented Python reconstruction was checked against separate scalar implementations of the source formulas.

## Chapter 2

`chapter02.py` renders the six approved figures from `data/chapter02/models.json`. This JSON contains the deterministic plotted values, original curve coordinates, and hashes of the six original plotting cells. The original cells remain in Git history at commit `be15918`, in `02.qmd`. No external empirical dataset is needed.

From `textbook/`:

```bash
python3 code/figures/chapter02.py
```

This writes paired light/dark SVGs and a coordinate verification record to `images/02_images/editorial/`. For isolated PNG/PDF review proofs:

```bash
python3 code/figures/chapter02.py --output-dir ../outputs/textbook-chapter02-rebuild --proofs
```

The renderer checks every principal curve against the original coordinates. It also verifies the $15 cost level, eight-worker hiring marker, market-demand aggregation, and equilibrium at 12 workers and $20. Discrete quantities, plotted markers, and the original connecting segments are retained. The market figures label every second integer tick for readability; no data points are removed.

All series use labels beside their curves. The aggregation figure uses short leaders to interior points because both cafes share their last point. Its cafe colors match the preceding two-cafe figure. Labor demand is green; labor supply and the cost comparison are rust.

`02.qmd` references one SVG pair per figure with its original caption and ID. Its two native tables are retained. Prose color descriptions are aligned with sage green and rust; no economic claims or quantities were changed. As with Chapter 1, this release targets HTML; PDF book output has not been redesigned or verified.

## Chapter 3 — approved figures

David requested removal of the historical-opinions composite and its adjacent timeline. Their figure blocks and references are removed from `03.qmd`; their old asset files are retained. The eleven remaining figures are reviewed and approved for integration and publication.

### Rebuild the previews

From `textbook/` with the dependencies in `requirements.txt`:

```bash
python3 code/figures/chapter03.py --proofs
```

The default output is `images/03_images/editorial/`. To rebuild the review proofs, pass `--output-dir ../outputs/textbook-chapter03-figures/figures`. Use `--output-dir /path/to/output` for another destination; omit `--proofs` for SVG-only output. Each figure has one light and one dark SVG. `manifest.json` lists IDs and captions; output `verification.json` records the rendering checks. The renderer reads only the aggregate files below and requires no local microdata.

### Inputs and preserved definitions

- `data/chapter03/models.json`: values, original line coordinates, histogram bars, and source-cell hashes for the eight remaining Python figures in `03.qmd`. Captured from the local source after removal of the two opening visuals; a full pre-change source backup is in the preview directory. The Card–Krueger figure uses the chapter's typed summary values, not a new microdata replication. Five employment diagrams share green New Jersey, rust Pennsylvania, original markers, and dashed counterfactual lines.
- `data/chapter03/inequality.csv`: eleven annual 90/10 ratios, 1979–1989. Reconstruction follows `code/03_code/min_wage_erosion.do` in the course root: no weights or extra sample filters; double-precision wage/GDP calculation stored back to float; Stata's default order-statistic percentiles, averaged when N*p/100 is integer; final ratio stored as float. Reference formula: [Stata percentile documentation](https://www.stata.com/manuals/dpctile.pdf). The rendered curve agrees with the shape and endpoints of the existing image; no successful Stata execution is claimed.
- `data/chapter03/histograms.csv`: original and counterfactual sample counts for the 1989 distributions. Preserve the chapter's Python float arithmetic `hr_wage * (1 / gdp)`, missing-value exclusion, unweighted frequencies, complete 50-cent bins, visible $0–$40 range, actual $3.35 minimum, and counterfactual $4.77 floor. Both distributions contain 168,438 observations. The renderer compares every bin edge and count to the original matplotlib artists; the two-panel comparison retains a common y-axis scale.
- `data/chapter03/verification.json`: raw input hashes, observation counts, independent percentile and histogram calculations, and read-only input confirmation.

The two Clemens schematics are redrawn from the chapter's supplied images. Their construction is explicitly commented in `chapter03.py`: normalized D1=10−L and S=L, equilibrium L1=5/w1=5, new minimum wage=7, and D2=11.5−L for price pass-through. These values are illustration coordinates, not measured observations or exact image digitization. Both versions retain the source's symbolic labels, wage increase, unemployment bracket, and employment decline; pass-through moves L2 from 3 to 4.5, still below L1. The chapter's existing citation remains in the in-context preview.

### Reconstruct aggregates from local inputs

```bash
python3 code/figures/replicate_chapter03.py
```

This reads `../data/03_data/morg_cleaned_1979.dta` through `morg_cleaned_1989.dta` and writes derived CSVs and verification metadata to `../outputs/textbook-chapter03-replication/`. Flags `--course-root` and `--output-dir` select alternate locations. Raw files are never modified. Percentiles are independently checked using partial selection rather than sorting; histogram counts are independently checked using bin assignments. Deliberately compare output to the committed plotted snapshots before refreshing snapshots. Raw CPS microdata remain outside the textbook repository.

### Review artifacts

- `../outputs/textbook-chapter03-figures/index.html`: original/candidate comparisons, both modes, reading-width toggle.
- `../outputs/textbook-chapter03-figures/render/_book/03.html`: Quarto-rendered chapter context with both requested removals and renumbered figures.
- `../outputs/textbook-chapter03-figures/03-preview.qmd`: candidate source references. Only necessary prose color descriptions are aligned with the new palette; captions and remaining figure IDs are retained.

All eleven replacements were approved, including the raised employment-decline labels and the single arrow from the actual to counterfactual minimum wage with its label nearby. The approved chapter preview also retains its existing Before/After wording and date corrections. Publish only when requested. This workflow targets HTML; no PDF book redesign is claimed.

## Chapter 4 — approved figures

`chapter04.py` renders seven deterministic charts from `data/chapter04/models.json`. The JSON captures each original source cell's values, line coordinates, marker shapes, shaded polygon vertices, caption, ID, and code hash. No external empirical data are required. The original cells are in `04.qmd` at Git commit `829959b`; the one pre-existing local change in this chapter wraps the Adam Smith illustration and does not change its plotting code.

From `textbook/`:

```bash
python3 code/figures/chapter04.py --proofs
```

This writes paired SVGs, optional PNG/PDF proofs, a manifest, and verification metadata to `images/04_images/editorial/`. For isolated review proofs, pass `--output-dir ../outputs/textbook-chapter04-figures/figures`. Use `--output-dir` for a different output directory; omit `--proofs` for SVGs only.

### Preserved construction

| Figures | Definition / source values retained |
| --- | --- |
| Labor supply, MFC comparison, equilibrium, steep-supply loss | Ten discrete worker quantities 1–10; wage=5L; discrete MFC=10L−5; MRP=70−5L; employment=5 and wage=$25 |
| Steep-supply deadweight loss | Original continuous shading bounds 5–7; lower bound 5L, upper bound 70−5L; all 50 source points retained |
| Flatter supply | Wage=L+28; source uses continuous MFC=2L+28; employment=6, wage=$34, efficient employment=7; exact 6–7 shaded polygon retained |
| $35 minimum wage | MFC=$35 at workers 1–7, then 10L−5 at 8–10; original connecting segments preserved; equilibrium=7 workers, $35 |
| $50 minimum wage | MFC=$50 over the displayed ten quantities; equilibrium=4 workers, $50 |

The original chapter uses a discrete cost increment for steep supply and a continuous derivative for the flatter-supply panel. Both conventions and their original values are retained for this styling review. The renderer does not silently change the underlying economic construction. In particular, it does not turn the source's straight segments between discrete minimum-wage MFC points into a different step curve.

Labor supply is rust, MFC is muted sage with its original line patterns, and MRP is green. Original markers distinguish the series. Direct labels replace legends, and equilibrium/efficiency guides stop at their relevant plotted values. Original equilibrium quantities and wages are identified beside their points; loss regions use transparent rust shading. The multiseries panels share a $0–$110 scale with quieter major ticks; the single supply chart uses $0–$55. The renderer checks all principal coordinates, markers, and loss polygons against the captured originals.

Review `../outputs/textbook-chapter04-figures/index.html` for side-by-side comparisons and light/dark/reading-width controls, or `render/_book/04.html` inside that directory for chapter context. All seven figures are approved and integrated into `04.qmd` with their existing captions and IDs. The final deadweight-loss labels in 4.4 and 4.5 are centered at 6.5 workers and split over two lines to separate them from the efficient-employment labels. David requested commitment and publication. No PDF book redesign is claimed.
