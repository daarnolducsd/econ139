"""Rebuild Chapter 3's public plotted aggregates from read-only local CPS inputs."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--course-root", type=Path, default=Path(__file__).resolve().parents[3]
)
parser.add_argument("--output-dir", type=Path)
args = parser.parse_args()
course = args.course_root.resolve()
out = args.output_dir or course / "outputs/textbook-chapter03-replication"
out.mkdir(parents=True, exist_ok=True)
inputs = [
    course / f"data/03_data/morg_cleaned_{year}.dta" for year in range(1979, 1990)
]
hashes = {
    str(p.relative_to(course)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in inputs
}


def stata_percentile(values, percent):
    """Default Stata percentile: order statistic, averaging at integer N*p/100.

    Reference: https://www.stata.com/manuals/dpctile.pdf (Methods and formulas).
    """
    ordered = np.sort(values)
    rank = len(ordered) * percent / 100
    if rank.is_integer():
        i = int(rank)
        return (float(ordered[i - 1]) + float(ordered[i])) / 2
    return float(ordered[math.ceil(rank) - 1])


rows = []
for year, path in zip(range(1979, 1990), inputs):
    raw = pd.read_stata(path, columns=["hr_wage", "gdp"])
    # Stata evaluates expressions in double precision, then stores replace in
    # the existing float variable. No weights or additional filters in source.
    nominal = (
        (raw.hr_wage.astype("float64") / raw.gdp.astype("float64"))
        .astype("float32")
        .dropna()
        .to_numpy()
    )
    p10, p90 = [stata_percentile(nominal, p) for p in (10, 90)]
    # Independent partial-selection implementation (no complete sort).
    reference = []
    for p in (10, 90):
        rank = len(nominal) * p / 100
        indices = (
            [int(rank) - 1, int(rank)] if rank.is_integer() else [math.ceil(rank) - 1]
        )
        selected = np.partition(nominal.astype("float64"), indices)
        reference.append(sum(selected[i] for i in indices) / len(indices))
    assert np.array_equal(reference, [p10, p90])
    rows.append(
        {
            "year": year,
            "p10": p10,
            "p90": p90,
            "ratio": float(np.float32(p90 / p10)),
            "observations": len(nominal),
        }
    )
pd.DataFrame(rows).to_csv(out / "inequality.csv", index=False)

# Keep the chapter's Python expression exactly, including float32 arithmetic.
# These are unweighted sample frequencies, not weighted population estimates.
raw = pd.read_stata(inputs[-1], columns=["hr_wage", "gdp"])
actual = (raw.hr_wage * (1 / raw.gdp)).dropna().to_numpy()
counterfactual = actual.copy()
counterfactual[counterfactual < 4.77] = 4.77
edges = np.arange(0, actual.max() + 0.5, 0.5)
counts, _ = np.histogram(actual, edges)
counter_counts, _ = np.histogram(counterfactual, edges)
# Independent count construction confirms every bin, including final endpoint.
for values, expected in [(actual, counts), (counterfactual, counter_counts)]:
    index = np.searchsorted(edges, values, side="right") - 1
    index[values == edges[-1]] = len(edges) - 2
    reference = np.bincount(index, minlength=len(edges) - 1)
    assert np.array_equal(reference, expected)
assert counts.sum() == counter_counts.sum() == len(actual)
pd.DataFrame(
    {
        "left": edges[:-1],
        "right": edges[1:],
        "actual": counts,
        "counterfactual": counter_counts,
    }
).to_csv(out / "histograms.csv", index=False)
assert all(
    hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p.relative_to(course))]
    for p in inputs
)
report = {
    "inputs_sha256": hashes,
    "inequality_years": [1979, 1989],
    "histogram_observations": len(actual),
    "histogram_bins": len(counts),
    "bin_width": 0.5,
    "counts_preserved": True,
    "independent_percentiles_match": True,
    "independent_histogram_counts_match": True,
    "raw_inputs_unchanged": True,
    "stata": "Python implementation of the source formulas; no successful Stata rerun is claimed.",
}
(out / "verification.json").write_text(json.dumps(report, indent=2))
print(
    f"Wrote 11 annual ratios and two histograms ({len(actual):,} observations) to {out}"
)
