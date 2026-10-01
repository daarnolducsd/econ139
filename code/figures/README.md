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
