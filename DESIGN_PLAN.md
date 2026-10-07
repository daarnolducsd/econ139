# Textbook redesign plan

Last updated: October 4, 2026.

## Objective and scope

Give the ECON 139 textbook a coherent editorial design while preserving its existing teaching content, evidence, and economic interpretation. Work chapter by chapter, with reviewable figure previews before replacing the originals.

The vermilion page design is implemented and published. Chapters 1–6 now use the approved dark green and rust figure palette locally; the restoration and shared-palette refactor are local and not yet published. Later chapters require a separate review before reconstruction or recoloring. Chapter 7 already has recreated figures, but is outside this palette update.

## Decisions already made

### Pages

- Pure white background `#FFFFFF`; Georgia prose at 18 px with 1.7 line spacing and an approximately 680 px reading column.
- Heavy sans-serif chapter titles in normal title case, bold sans-serif section headings, and sans-serif navigation/captions.
- Warm vermilion `#DF5145` for graphic accents, chapter numbers, and the introduction title. Darker red `#B8322B` for links and small accent text.
- Introduction title: **Labor Economics**, with the existing author/date metadata. No cover image or duplicate course label/author block.
- Chapter numbers sit alongside chapter titles. The latest inline-number adjustment is local, not yet published.
- Expanded chapter navigation on the left and **In this chapter** on the right. No extra All Chapters heading.
- Curious Detours have a thin vermilion border around the entire passage, white interior, square corners, 24 px padding (18 px on phones), a red uppercase label, and a bold sans-serif specific title.
- Preserve prose and teaching content except for necessary corrections to literal figure-color descriptions. In student-facing prose, call the accent **red**, not vermilion; reserve the precise color name and hex values for design documentation and code.

### Figures — approved dark green and rust palette

David chose to restore the original dark green/rust figure palette after reviewing red-led and sage/ochre alternatives. This decision supersedes those previews and their archived instructions. Page headings and rules retain the warm red accents. The shared helper retains the original supporting colors and series assignments.

| Role | Color | Hex |
| --- | --- | --- |
| Principal relationship, labor demand / MRP | Dark green | `#3D6155` |
| Main comparison, labor supply | Rust | `#A36F49` |
| Third series, marginal factor cost | Sage | `#758C7F` |
| Fourth series | Muted ochre | `#B39B61` |
| Reference/annotation | Dark ink | `#2B302D` |

- Shared definitions live in `code/figures/figure_style.py`; import these for future chapter renderers instead of repeating color literals.
- White backgrounds, dark ink `#2B302D`, muted labels `#616962`, and light-gray grids `#E1E5DF`.
- Education mapping: dropout taupe `#827568`; high-school graduate muted green `#6F887A`; some college gray-green `#66726B`; bachelor's degree rust; graduate degree dark green. Keep the existing line patterns and endpoint labels.
- Related demand/supply/MFC diagrams use the role mapping above. Chapter 2 individual cafes use sage and rust; their aggregate demand is dark green.
- Chapter 6 region mapping: Africa dark green, Asia rust, Europe ochre, Americas sage.
- Ordered map categories use rust tints (`#A36F49`, `#C49A77`, `#E5D4BD`, white), retaining the existing category thresholds, no-data treatment, and source geography. Do not substitute categorical hues for ordered values.
- Preserve all source data, coordinates, estimates, uncertainty, line styles, markers, annotations, captions, and figure IDs. Update prose when it explicitly names a changed color.
- Prefer transparent SVGs and direct labels; retain legends where needed. Figures with many series must use line patterns/markers as well as color.
- Preserve photographs, historical illustrations, and survey screenshots in their original colors. Existing documented map/diagram reconstructions retain their scientific limitations.
- The active book has one white theme. Existing dark companions remain legacy exports with their original palette; they are not the design target for this update.
- This pass covers the recreated figures in Chapters 1–6 only. Preview new reconstructions for later chapters before integrating them.

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

Chapters 1–6 have approved reconstructions and now share the palette above. For later chapters, review the inventory and existing reconstruction status first; do not redo completed work unnecessarily.

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

Produce a new figure in an output directory and show it alongside the original. Use the approved style and preserve the plotted quantities. Target the active white HTML theme. Retain existing legacy dark assets where the maintained renderer already produces them; both variants must share the same data and geometry.

Review the candidate at the actual book reading width. Check text size, direct-label collisions, line distinction, plot whitespace, caption fit, and consistency with the other figures in its chapter. Check zoom and narrow-screen behavior where relevant.

### 5. Review and integrate

Review the chapter's proposed figures with David. After a style and construction method are chosen, replace the relevant source references or plotting code with small, targeted edits. Preserve figure IDs, cross-references, and existing captions unless a specific correction is agreed.

Keep the reconstruction script and provenance alongside the maintained source. Use the original code/template for generated assets; avoid hand-editing rendered HTML or generated figures.

### 6. Verify and publish

Render the affected chapter, then verify the book's navigation and cross-references as needed. Check the active white theme, local asset links, figure/caption pairing, and scientific invariants as appropriate to the requested work. Honor David's current instruction to open the book after routine style edits without screenshot or extra visual-verification passes. Preserve unrelated working-tree changes.

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
- Additional series beyond the approved five-color palette, if needed; preserve approved line patterns.
- Whether a future return to dark mode warrants redesigning the legacy companion palette.
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

## Chapter 3 implementation record

Current status: **reviewed and integrated; publication requested** for eleven remaining charts. David requested removal of the first historical-opinions composite and the adjacent major-events timeline. Both figure blocks and their references have been removed from `03.qmd`, preserving the historical discussion and all unrelated source edits. The original inventory remains a baseline snapshot; these two removals reduce its Chapter 3 count from thirteen visual entries to eleven.

Maintained code: `code/figures/chapter03.py` (rendering) and `code/figures/replicate_chapter03.py` (read-only local CPS reconstruction). Aggregate snapshots, captured source coordinates, and verification metadata are organized under `code/figures/data/chapter03/`; construction details and commands are in `code/figures/README.md`.

- Six remaining deterministic/summary-value figures: competitive minimum-wage theory and five employment/DiD diagrams; original curve values, markers, minimum wage, quantities, and DiD calculations preserved.
- Two imported Clemens diagrams: explicitly documented normalized schematics, preserving economic labels, wage increase, unemployment, employment decline, and partial offset from price pass-through. These are schematic reconstructions, not numerical empirical replications.
- Annual 90/10 ratio: eleven original annual inputs, 1979–1989, unweighted Stata percentile definition and float storage preserved.
- Two wage-distribution figures: original Python calculation, sample, 50-cent bins, unweighted counts, $3.35 actual minimum, and $4.77 counterfactual floor preserved. Independent checks and original matplotlib histogram comparisons pass.

Review page: `../outputs/textbook-chapter03-figures/index.html`. Chapter-context preview: `render/_book/03.html` inside that directory. The original review used green/rust in paired transparent SVG assets; the active light versions now use the palette above. David approved all eleven replacements and requested commitment and publication. Final revisions raise the employment-decline labels in 3.7/3.8 and use a single arrow from $3.35 to $4.77 in 3.10, with the real-value label nearby. The approved chapter context includes the existing Before/After wording and date corrections. The two requested removals are included.

## Chapter 4 implementation record

Current status: **reviewed and integrated; publication requested** for seven locally generated charts. The Adam Smith illustration is retained. All source curves, discrete quantities, markers, captions, and figure IDs are captured in `code/figures/data/chapter04/models.json`; maintained renderer and verification are in `code/figures/chapter04.py` and its outputs. `code/figures/README.md` documents the input values, original MFC conventions, equilibrium checks, shade bounds, and rebuild command.

- Labor supply and MFC comparison establish rust supply and sage MFC; MRP is dark green throughout the chapter.
- Monopsony employment and wage remain 5/$25 under steep supply and 6/$34 under flatter supply; efficient employment remains 7. Original deadweight-loss polygons are retained exactly.
- Minimum-wage figures retain the original ten discrete points and their connecting segments. The $35 floor gives 7 workers/$35; the $50 floor gives 4 workers/$50.
- The source's flatter-supply figure uses the continuous MFC derivative, while its steep-supply figure uses discrete cost increments. This existing convention is recorded and retained, not changed during styling.

Review page: `../outputs/textbook-chapter04-figures/index.html`; chapter context: `render/_book/04.html` inside that directory. Both themes use transparent SVGs, direct labels, quiet grids, and guides ending at the relevant points. All seven Chapter 4 replacements were approved and integrated. Final deadweight-loss labels in 4.4/4.5 are centered at 6.5 workers, split over two lines, and clear of the efficient-employment labels. Commitment and publication were requested. Chapter 3 was committed as `829959b` and its deployment verified live before this preview work.

## Chapter 5 implementation record

Current status: **reviewed and integrated; publication requested** for eleven
figures. David approved the review candidates and requested commitment and
publication. Maintained renderer:
`code/figures/chapter05.py`; documented inputs and approximate pixel readings:
`code/figures/data/chapter05/`; construction details: `code/figures/README.md`.

- Seven existing deterministic/summary charts preserve the current local
  chapter's curves, observed points, normal density and merger-effect values.
  Existing steep-supply corrections are preserved in the candidate source.
- Two non-compete charts retain printed means and all uncertainty layers;
  interval endpoints/bounds/overall incidence are approximate pixel readings.
  David explicitly authorized approximate redraws, documented for review.
- The concentration map is a raster recoloring with the original categories,
  geography and artifacts, and a new native legend. It is not a data/geometry
  reconstruction; a clean vector map still requires matching source inputs.
- The inequality decomposition uses six printed, rounded bar values. These
  imply a Great Divergence total of 0.286; the current prose says 0.282. Preserve
  both and flag the discrepancy before integration.

Review page: `../outputs/textbook-chapter05-figures/index.html`; chapter context:
`render/_book/05.html` inside that directory. Both modes follow the approved
palette. Figure IDs, original captions, and existing chapter prose are retained.
Imported approximate candidates remain explicitly documented as approximations.
The 0.286/0.282 discrepancy remains unresolved; neither value was silently changed.

## Chapter 6 implementation record

Current status: **reviewed, integrated, and published** for fifteen
charts: fourteen numbered figures and the existing unnumbered Mincer model.
David approved the final revisions and requested commitment and publication. Maintained code: `code/figures/chapter06.py` and
`code/figures/replicate_chapter06.py`; plotted aggregates and digitization
coordinates: `code/figures/data/chapter06/`.

- Mincer: all 100 original formula points retained and verified. No caption or
  figure number is added to its previously unnumbered plot.
- Four ACS charts: 2023 sample, 1,370,496 observations after the source's age and
  earnings restrictions; unweighted means, float log wages, count-based marker
  areas and experience ≤40 retained. Independent aggregation checks pass and
  raw-file SHA-256 is unchanged.
- Eight imported chart redraws: explicit approximate digitizations of source
  dots/bubbles, relative bubble areas, separate RD fitted segments, confidence
  bands where originally present, histogram heights and popularity series.
  Printed statistical estimates/standard errors remain exact as displayed.
- Two Gapminder previews: visible source silhouettes traced into scalable
  paths, with native axes and legend. Original positions and overlaps remain;
  these are not country-data replications. Supporting region colors are ochre
  and sage alongside dark green/rust; prose colors are aligned with the approved palette.
- The source UCSC dashed line remains at its plotted midpoint (~2.75); the
  institutional threshold in prose remains 2.8. The Colombia attendance prose
  inconsistently says 40 and 32 percentage points; preserve both for review.

Public-source checks and approximation limits are documented in
`code/figures/README.md`. Review page:
`../outputs/textbook-chapter06-figures/index.html`; chapter context:
`render/_book/06.html` inside that directory. Preserve 6.1–6.14 numbering,
original captions/IDs and all unrelated prose. The approved replacements are
integrated in `06.qmd`; publication uses the isolated build workflow.

Chapter 6 review revisions: native vector bubble traces replace the initial
raster previews in 6.1/6.2; β/coefficient text is enlarged to 13 points in
6.12–6.14, with extra line spacing for the two estimates in 6.14.

## Chapter 7 implementation record

Current status: **reviewed and integrated; publication requested** for six
charts. David approved all figures, including the revised 1980–2000 headings
in 7.1–7.3, and requested commitment and publication. Three occupation examples retain all existing typed
employment changes and wage labels; three imported charts use recovered public
author files, with no approximate redraws. Historical illustrations remain as
supplied. Captions and IDs stay 7.1–7.6.

Maintained code: `code/figures/chapter07.py` and `replicate_chapter07.py`.
Public plotted snapshots, original source programs and small aggregate inputs
are organized under `code/figures/data/chapter07/`; rebuild commands, hashes,
calculations, aggregation checks and limits are documented in the figure README.

- 7.4 retains the 100 exact original Stata LOWESS points from the archived graph.
- 7.5 retains all 18 country/aggregate rows and the wage-tercile legend.
- 7.6 reconstructs the pooled employment shares with agriculture excluded,
  preserving the original four groups, six years and markers; direct labels
  replace the external legend.
- The 7.4 figure covers 1980–2005 but nearby prose says 1980–2000. Preserve the
  existing dates for now and flag the discrepancy for review.

Comparison: `../outputs/textbook-chapter07-figures/index.html`; chapter context:
`render/_book/07.html` within that directory. Both modes use transparent SVGs,
Arial figure text, green/rust and supporting sage/ochre. No additional prose or
learning material is added. The approved source is integrated in `07.qmd`.

Chapter 6 publication: source commit `36abaac`, Pages commit `3c4e106`.
GitHub Pages reported the deployment built, and the live `06.html` was checked
byte-for-byte against the approved deployment output.

## October 4 palette integration

Status: **approved and integrated locally**, not yet published. Chapters 1–6 render through the shared palette helper. The current page style and inline chapter-number change are preserved. Older review directories and their copied DESIGN_PLAN.md files are historical artifacts; this file is authoritative for subsequent work. Chapter 7 and later assets are unchanged by this pass. Existing reconstruction limitations and source records below remain applicable.
