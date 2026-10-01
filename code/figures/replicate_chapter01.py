"""Chapter 1 candidate figures. Read-only original inputs; outputs stay here.
See README.md for commands and original input locations.
Weighted log-wage means follow the existing Stata script, including float storage.
"""
from pathlib import Path
import os, csv, json, hashlib, math

SCRIPT = Path(__file__).resolve().parent
COURSE = SCRIPT.parents[2]
import argparse

parser = argparse.ArgumentParser(
    description="Reconstruct Chapter 1 plotted series from the original local inputs"
)
parser.add_argument(
    "--course-root",
    type=Path,
    default=COURSE,
    help="Root of the local ECON139 course tree",
)
parser.add_argument(
    "--output-dir", type=Path, default=COURSE / "outputs/textbook-chapter01-replication"
)
args = parser.parse_args()
COURSE = args.course_root.resolve()
ROOT = args.output_dir.resolve()
ROOT.mkdir(parents=True, exist_ok=True)
(ROOT / "data").mkdir(exist_ok=True)
import numpy as np
import pandas as pd

DATA = COURSE / "code/textbook/01/data"
AUTOR = COURSE / "code/textbook/01/code/autor"
inputs = [
    DATA / p
    for p in ["inequality1.csv", "labor_share.csv", "LFP_men.csv", "LFP_women.csv"]
] + [AUTOR / "wages.dta"]
originals = [
    COURSE / "textbook/images/01_images" / p
    for p in [
        "income_inequality.png",
        "autor_fig.png",
        "labor_share.png",
        "lfp_full.png",
    ]
]
before = {
    str(p.relative_to(COURSE)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in inputs + originals
}
report = {
    "checks": {},
    "inputs_sha256": before,
    "stata": "Installed Stata SE license expired; Stata replication could not run. Python independently checks calculations against scalar implementations of the source formulas.",
}


def record(name, n, error, **extra):
    report["checks"][name] = {
        "plotted_observations": int(n),
        "independent_calculation_max_error": float(error),
        **extra,
    }


ineq = pd.read_csv(
    DATA / "inequality1.csv", sep=";", header=None, names=["group", "year", "share"]
)
ineq = ineq.loc[
    (ineq.year >= 1917) & ineq.group.isin(["p99p100", "p0p50"])
].sort_values(["group", "year"])
assert (
    ineq.groupby("group").size().tolist() == [107, 107]
    and not ineq[["year", "share"]].isna().any().any()
)
ineq.to_csv(ROOT / "data/inequality.csv", index=False)
record("inequality", len(ineq), 0, first_year=1917, last_year=2023)

raw = pd.read_csv(DATA / "labor_share.csv")
raw["year"] = raw.Quarter.str[-4:].astype(int)
raw["share"] = raw["Labor share"].str.replace("%", "", regex=False).astype(float)
labor = raw.groupby("year", as_index=False).agg(
    share=("share", "mean"), quarters=("share", "count")
)
ref = {y: math.fsum(float(x) for x in g.share) / len(g) for y, g in raw.groupby("year")}
error = max(abs(row.share - ref[row.year]) for row in labor.itertuples())
assert error < 1e-12
assert len(labor) == 70 and labor.iloc[-1].year == 2016 and labor.iloc[-1].quarters == 3
labor.to_csv(ROOT / "data/labor-share.csv", index=False)
record(
    "labor_share",
    len(labor),
    error,
    first_year=1947,
    last_year=2016,
    last_year_quarters=3,
)

lfp = []
for sex in ["men", "women"]:
    raw = pd.read_csv(DATA / f"LFP_{sex}.csv")
    raw["year"] = raw.observation_date.str.rsplit("/", n=1).str[-1].astype(int)
    raw["year"] = np.where(raw.year <= 25, raw.year + 2000, raw.year + 1900)
    col = f"LFP_{sex}"
    annual = raw.groupby("year", as_index=False).agg(
        rate=(col, "mean"), months=(col, "count")
    )
    annual["group"] = sex
    ref = {
        y: math.fsum(float(x) for x in g[col]) / len(g) for y, g in raw.groupby("year")
    }
    error = max(abs(row.rate - ref[row.year]) for row in annual.itertuples())
    assert error < 1e-12
    assert len(annual) == 78 and annual.iloc[-1].months == 5
    lfp.append(annual)
    record(
        "participation_" + sex,
        len(annual),
        error,
        first_year=1948,
        last_year=2025,
        last_year_months=5,
    )
lfp = pd.concat(lfp)
lfp.to_csv(ROOT / "data/participation.csv", index=False)

raw = pd.read_stata(AUTOR / "wages.dta", convert_categoricals=False)
raw = raw[(raw.female == 0) & raw.year.between(1963, 2017)].copy()
assert not raw[["rplnwkw", "avlswt"]].isna().any().any() and (raw.avlswt > 0).all()
raw["avlswt"] = raw.avlswt.astype(float)
raw["weighted"] = raw.rplnwkw.astype(float) * raw.avlswt
means = raw.groupby(["edcat", "year"], as_index=False).agg(
    weighted=("weighted", "sum"), weight=("avlswt", "sum")
)
means["mean_log_wage"] = (means.weighted / means.weight).astype(np.float32)
means["baseline"] = means.groupby("edcat").mean_log_wage.transform("first")
means["change"] = (means.mean_log_wage - means.baseline).astype(np.float32)
refs = {}
for (cat, year), group in raw.groupby(["edcat", "year"]):
    refs[(int(cat), int(year))] = np.float32(
        math.fsum(float(x) * float(w) for x, w in zip(group.rplnwkw, group.avlswt))
        / math.fsum(float(w) for w in group.avlswt)
    )
errors = []
for row in means.itertuples():
    v = np.float32(refs[(int(row.edcat), int(row.year))] - refs[(int(row.edcat), 1963)])
    errors.append(abs(float(v) - float(row.change)))
assert (
    max(errors) < 1e-6
    and len(means) == 275
    and (means[means.year == 1963].change == 0).all()
)
means[["edcat", "year", "mean_log_wage", "change"]].to_csv(
    ROOT / "data/education.csv", index=False
)
record(
    "education",
    len(means),
    max(errors),
    first_year=1963,
    last_year=2017,
    groups=5,
    definition="Analytic-weighted mean log real weekly wages of men, minus 1963 mean; float storage follows original Stata script.",
)


report["originals_unchanged"] = before == {
    str(p.relative_to(COURSE)): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in inputs + originals
}
assert report["originals_unchanged"]
(ROOT / "verification.json").write_text(json.dumps(report, indent=2))
print("Reconstructed and verified plotted series in", ROOT / "data")
