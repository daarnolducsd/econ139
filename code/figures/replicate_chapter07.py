"""Recreate Chapter 7 plotted snapshots from the authors' public packages.

No download is needed: the small public input files are kept under data/chapter07/
source. The Autor–Dorn curve is read from its archived Stata graph's exact
series, avoiding a different implementation of Stata's LOWESS smoother.
"""
from pathlib import Path
import argparse
import hashlib
import json
import struct
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE / "data/chapter07"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument(
    "--output-dir",
    type=Path,
    default=HERE.parents[2] / "outputs/textbook-chapter07-replication",
)
args = parser.parse_args()
OUT = args.output_dir.resolve()
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = DATA / "source"
hashes = {
    f.name: hashlib.sha256(f.read_bytes()).hexdigest()
    for f in SOURCE.iterdir()
    if f.is_file()
}

# Figure 7.4: this specific archived graph has double pdsh0 and byte perc,
# 100 observations, 9 bytes each. Read the data block; validate against the
# graph's own series bounds and the source employment-share totals.
raw = (SOURCE / "demp-pct-1980-2005-czall-color.gph").read_bytes()
assert b'.name = `"pdsh0"\'' in raw and b'.name = `"perc"\'' in raw
start = raw.index(b"<BeginSersetData>")
end = raw.index(b"<EndSersetData>")
block = raw[start:end].removesuffix(b"\r\n")
records = list(struct.iter_unpack("<dB", block[-900:]))
curve = pd.DataFrame(records, columns=["change_100x_share", "percentile"])
assert curve.percentile.tolist() == list(range(1, 101))
assert np.isclose(curve.change_100x_share.min(), -0.0977192480332558, atol=1e-14)
assert np.isclose(curve.change_100x_share.max(), 0.2727479499544638, atol=1e-14)
emp = pd.read_stata(
    SOURCE / "emp-bypctile-1980-2005-rewt-0-czall.dta", convert_categoricals=False
)
assert np.allclose(emp.groupby("year").empshare.sum(), 100, atol=1e-5)
curve.to_csv(OUT / "polarization.csv", index=False)

# Figure 7.5: source do-file divides the already computed percentage-point
# changes by 100. Preserve all 18 countries/aggregates and their order n.
countries = pd.read_stata(
    SOURCE / "goos-manning-data.dta", convert_categoricals=False
).sort_values("n")
assert countries.n.tolist() == list(range(1, 19))
for col in ["lo", "mid", "hi"]:
    countries[col] = countries[col].astype(float) / 100
assert np.max(np.abs(countries[["lo", "mid", "hi"]].sum(axis=1))) < 0.00011
countries.to_csv(OUT / "countries.csv", index=False)

# Figure 7.6: follow the first, pooled-sex panel of plot-emp-shares-byocc.do.
# emp is an already weighted employment total, so collapse with raw sums.
cells = pd.read_stata(
    SOURCE / "census-cells-occ10-demog-1960-2008.dta", convert_categoricals=False
)
cells = cells.loc[cells.occ10 != 40].copy()  # Drop agriculture.
mapping = {11: 1, 12: 1, 13: 1, 21: 2, 22: 2, 23: 3, 31: 3, 32: 4, 33: 4, 34: 4}
cells["group"] = cells.occ10.map(mapping)
assert cells.group.notna().all()
# Stata rawsum and pandas sum ignore missing employment cells.
cells["emp"] = cells.emp.astype(float)
totals = cells.groupby(["year", "group"]).emp.sum().unstack("group")
shares = totals.div(totals.sum(axis=1), axis=0)
# Independent NumPy accumulation verifies each source group total.
for year in totals.index:
    chunk = cells.loc[cells.year == year]
    check = np.bincount(
        chunk.group.to_numpy(dtype=int),
        weights=chunk.emp.fillna(0).to_numpy(dtype=float),
        minlength=5,
    )[1:]
    assert np.allclose(check, totals.loc[year], rtol=1e-12, atol=1e-7)
assert np.allclose(shares.sum(axis=1), 1, atol=1e-12)
shares.index = shares.index.astype(int) - 1  # Original earnings-year convention.
shares.index.name = "year"
shares.columns = [
    "professional_managerial_technical",
    "clerical_sales",
    "production_operators",
    "service",
]
shares.to_csv(OUT / "tasks.csv")
assert hashes == {
    f.name: hashlib.sha256(f.read_bytes()).hexdigest()
    for f in SOURCE.iterdir()
    if f.is_file()
}
report = dict(
    source_sha256=hashes,
    polarization_points=100,
    countries=18,
    task_source_cells=len(cells),
    task_years=shares.index.tolist(),
    checks=[
        "exact archived graph bounds and percentiles",
        "source employment shares total 100",
        "country changes sum approximately zero at published precision",
        "independent task aggregation",
        "task shares sum to one",
        "source hashes unchanged",
    ],
    limitation="Reads the archived Stata LOWESS series; does not rerun raw microdata preparation or Stata LOWESS.",
)
(OUT / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
print(f"Reconstructed three imported figures from public source files: {OUT}")
