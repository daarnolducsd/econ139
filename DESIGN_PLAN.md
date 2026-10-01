# Textbook redesign plan

Last updated: October 1, 2026.

## Objective and scope

Give the ECON 139 textbook a coherent editorial design while preserving its existing teaching content, evidence, and economic interpretation. Work chapter by chapter, with reviewable figure previews before replacing the originals.

The page design is implemented and published. Figure reconstruction is the next phase. No figures are being replaced as part of the inventory and planning step.

## Decisions already made

### Pages

- Georgia serif prose; system sans-serif headings, navigation, captions, and figure labels.
- Approximately 720 px reading width, 18 px desktop prose, and generous line spacing.
- Light background `#FAFAF7`, sidebar `#F0F0EC`, ink `#2B302D`, muted text `#616962`, borders `#D6D9D3`.
- Dark background `#202522`, sidebar `#1B201D`, ink `#E5EBE6`, muted text `#B6C0B8`, borders `#414942`.
- Green links and accents: `#3D6155` in light mode and `#ACC9BB` in dark mode.
- One wide existing industrial-robot photograph on the title page.
- Chapter navigation on the left, a quiet section outline on the right, and responsive navigation on narrow screens.
- Restrained dividers, left-aligned muted captions, consistent tables, and generous equation spacing.
- The feature label is **Curious Detours**, above the existing specific feature title. These features remain fully visible, have no emojis, and are not marked optional.
- Preserve the existing prose. Do not add learning goals, motivating questions, or new teaching content during the visual redesign.

### Figures

- Use the approved **Style A** inequality preview as the starting reference.
- Base colors: green `#3D6155` and rust `#A36F49`.
- Match the book's sans-serif typography, simplify axes, and use quiet horizontal grids where helpful.
- Prefer direct labels when they are readable. Keep a compact legend when direct labels would overlap or obscure evidence.
- Prefer vector output for charts and diagrams, with backgrounds that integrate with the page.
- Use line patterns, meaningful markers, and supporting neutral colors when a figure has more than two series. Decide the extension for the five education series before implementing that figure.
- Preserve color meanings across related figures. Choose mappings for each related set before drawing it.
- Keep confidence intervals, uncertainty bands, sample-size markers, zero lines, cutoffs, and other economically meaningful annotations.
- Use appropriate visual forms for maps, timelines, histograms, scatter plots, conceptual diagrams, and interactive widgets. They share typography and colors without needing identical geometry.
- Keep photographs, historical illustrations, and survey screenshots in their original colors; integrate them through sizing and placement.

## Inventory and starting point

The current configured book contains **110 charts, diagrams, and interactive chart entries**, plus **8 illustrations** and **9 table/survey screenshots**: **127 visual entries** in total. A numbered composite can contain several images; it is counted once. The Roman-edicts hover image is included, as is the ACS earnings widget. Native text/code-generated tables are outside the figure inventory.

Inventory files, relative to this textbook directory:

- `../outputs/textbook-figure-inventory/figure-list.md`: complete chapter-by-chapter checklist.
- `../outputs/textbook-figure-inventory/index.html`: detailed source and reconstruction assessment.
- `../outputs/textbook-figure-inventory/inventory.json`: structured records.
- `../outputs/textbook-figure-style-preview/`: earlier approved Style A comparison.

The source audit classifies 63 chart entries as having local plotting code or coordinates, 10 as needing a small local setup, 5 as needing reconstruction or specification recovery, and 32 as having matching plotting data not yet located. These are feasibility assessments, not verified successful reruns of all analyses.

The inventory reflects the current local book sources. Existing unpublished chapter edits remain local; publication work must preserve them and stage the requested changes deliberately.

## Figure code organization and documentation

All code used to recreate figures must be **clear, concise, and organized** in the maintained `textbook/code/figures/` directory. Use descriptive chapter filenames, factor repeated styling into shared helpers when useful, and keep data preparation separate from rendering. Avoid exploratory code, stale paths, and duplicate implementations in the maintained scripts.

Each chapter's code must document its inputs and provenance, calculations and assumptions, output assets, dependencies, and exact rebuild commands in `code/figures/README.md` or a clearly linked chapter README. Keep public plotted-series snapshots under `code/figures/data/` when needed for a standalone textbook checkout. Raw course inputs remain read-only; derived artifacts and review previews belong in output directories. Commit the maintained code and documentation with the corresponding approved figures.

## Chapter-by-chapter workflow

### 1. Agree on the chapter's figure plan

Review the complete chapter list and decide which figures to redraw first. For each figure, identify its teaching purpose, its relationship to neighboring figures, and its current caption/reference ID. Record any choices about color mappings, panels, labels, or legends before implementation.

Start with Chapters 1 and 2: Chapter 1 has local replication inputs for its four charts; Chapter 2 has six conceptual charts with embedded plotting code. Chapter 1's education chart needs more than two distinguishable series.

### 2. Establish the source of truth

Find the actual plotting code and data, or the deterministic coordinates/summary values used by the current figure. Record the input paths, original paper or source, sample, weights, units, time period, transformations, and any estimation choices that matter.

Distinguish:

- **Embedded conceptual code:** preserve coordinates, intersections, and annotations.
- **Embedded summary values:** redraw those values without claiming to replicate the underlying empirical study.
- **Local empirical replication:** verify sample and calculations before styling.
- **Imported paper figure:** recover plotted series or a replication package before claiming an exact reproduction.
- **Illustration or screenshot:** improve integration; a table conversion needs transcription and verification.

When exact data are unavailable, keep the original while deciding how to obtain them. Do not silently trace curves, invent observations, drop uncertainty, or substitute a different measure.

### 3. Reproduce the existing figure before redesigning it

Repair stale paths in isolated working code. Check the baseline against the current figure: observations, axes, trends, annotations, summary values, and estimates. Investigate discrepancies before choosing a new appearance.

Keep raw data read-only. Write derived data, figures, and logs to output directories. Prefer Stata for empirical course workflows; use Python or R for suitable rendering tasks. Document a fixed seed if any random generation is required.

### 4. Create a reviewable candidate

Produce a new figure in an output directory and show it alongside the original. Use the approved style and preserve the plotted quantities. Make light and dark versions legible; separate theme-specific assets may be needed for labels on externally embedded SVGs. Both variants must share the same data and geometry.

Review the candidate at the actual book reading width. Check text size, direct-label collisions, line distinction, plot whitespace, caption fit, and consistency with the other figures in its chapter. Check zoom and narrow-screen behavior where relevant.

### 5. Review and integrate

Review the chapter's proposed figures with David. After a style and construction method are chosen, replace the relevant source references or plotting code with small, targeted edits. Preserve figure IDs, cross-references, and existing captions unless a specific correction is agreed.

Keep the reconstruction script and provenance alongside the maintained source. Use the original code/template for generated assets; avoid hand-editing rendered HTML or generated figures.

### 6. Verify and publish

Render the affected chapter, then verify the book's navigation and cross-references as needed. Check light and dark modes, local asset links, figure/caption pairing, and any scientific invariants established in the baseline. Preserve unrelated working-tree changes.

Publish only when requested. Inspect the publication file set; exclude private/student materials. Verify the live output after deployment. Report the figures changed, source method, checks performed, and remaining limitations.

## Suggested sequence

1. **Chapter 1:** lock the line-chart template and resolve the five-series education palette.
2. **Chapter 2:** establish the conceptual diagram template, including discrete worker quantities, steps, intersections, and guide lines.
3. **Chapters 3–5:** apply those templates to local code; separately review imported evidence and diagrams.
4. **Chapters 6–8:** rebuild local charts and recover missing published series, map inputs, and uncertainty information.
5. **Chapter 9:** use a consistent template for budget constraints, preferences, tangencies, and decompositions.
6. **Chapter 10:** preserve country/group mappings, trade units, and empirical specifications.
7. **Dataset chapters:** integrate CPS/ACS/O*NET charts, screenshots, tables where agreed, and the interactive widget.

This sequence is a starting point. Each chapter review determines its exact implementation order.

## Choices still to make during figure reviews

- Exact fonts and label sizes for figures at the book's reading width.
- Additional series colors and line patterns beyond green/rust.
- Which figures need separate light/dark exports and how to maintain them from one source.
- Direct labels versus legends for dense or multi-series charts.
- Panel layouts for imported multi-panel evidence.
- Which screenshot tables merit conversion to native tables.
- Specifications and source packages for figures without a verified exact replication.
- Whether/when to extend the redesign to the PDF edition; the current page redesign targets HTML.

## Per-figure record

For each completed figure, retain:

- Chapter, caption, and figure ID.
- Current asset and replacement asset(s).
- Script and input files; data vintage and source attribution.
- Baseline reproduction checks and any discrepancy resolution.
- Color/line/panel decisions and light/dark output strategy.
- Review status, implementation status, and publication status.

Use explicit statuses such as **inventoried**, **source verified**, **preview ready**, **reviewed**, **integrated**, and **published**. Do not mark a figure complete solely because a plausible image has been generated.

## Chapter 1 implementation record

Four candidate charts are available in `../outputs/textbook-chapter01-figures/index.html`, with an in-chapter preview in `pages/01.html` inside that directory. Current status: **reviewed, integrated, and published**. David approved all four previews and requested commitment and publication.

- **1.1 Income inequality:** all 214 input observations retained, 1917–2023; approved Style A extended to paired light/dark assets.
- **1.2 Education wages:** five male education groups, 1963–2017; preserve analytic weighting, mean-log definition, 1963 normalization, and original float storage. The supporting colors and line patterns were approved with the four-chart preview.
- **1.3 Labor share:** annual mean of the original quarterly values, 1947–2016; preserve all four event annotations and their arrow targets. Final year has three quarters.
- **1.4 Participation:** original annual averages for men and women, 1948–2025; final year includes January–May.

Stata's installed license was expired during this exercise. Python calculations were independently checked against scalar implementations of the source formulas; details and hashes are in the candidate directory's `verification.json`. This verifies the local plotted calculations, rather than the original papers' complete underlying empirical analyses.

The maintained Chapter 1 renderer is `code/figures/chapter01.py`; raw-input reconstruction is `code/figures/replicate_chapter01.py`. See `code/figures/README.md` for reproducibility and asset documentation.

## Chapter 2 implementation record

Six figures are **reviewed and approved** in `../outputs/textbook-chapter02-figures/index.html`, with an in-chapter view in `pages/02.html` inside that directory. Maintained code is `code/figures/chapter02.py`; captured deterministic inputs and original curve coordinates are in `code/figures/data/chapter02/models.json`.

All principal x/y coordinates were checked against the original plotting code. Discrete worker quantities, production/MRP values, curve shapes, markers, the $15 cost line, eight-worker hiring point, and 12-worker/$20 market equilibrium are retained. Cafe comparison colors remain consistent between the two-cafe and aggregation charts. The aggregation figure uses labels beside its curves, with short leaders to interior points to distinguish the cafes despite their shared endpoint. Chapter 2 source integration and publication were requested after review. Existing captions and IDs are preserved; prose color references are aligned with the approved palette. The original plotting cells remain available in Git history.
