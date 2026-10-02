"""Reconstruct the four ACS figure aggregates from read-only local inputs.

Follow code/acs/mincer.do: ages 18–65, positive nonmissing earnings, unweighted
means, and observation-count marker weights. No student or course roster data.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

SCRIPT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--course-root", type=Path, default=SCRIPT.parents[2])
parser.add_argument("--output-dir", type=Path)
args = parser.parse_args()
root = args.course_root.resolve()
out = (args.output_dir or root / "outputs/textbook-chapter06-replication").resolve()
out.mkdir(parents=True, exist_ok=True)
raw = root / "data/acs/acs_clean.dta"
before = hashlib.sha256(raw.read_bytes()).hexdigest()
df = pd.read_stata(
    raw,
    columns=["age", "incwage", "exper", "edu_yrs", "year"],
    convert_categoricals=False,
)
years = sorted(df.year.dropna().unique().astype(int).tolist())
df = df.loc[df.age.between(18, 65) & (df.incwage > 0) & df.incwage.notna()].copy()
# Stata's `gen log_wage = log(incwage)` creates a float by default.
df["log_wage"] = np.log(df.incwage.astype("float64")).astype("float32")
df["obs_count"] = 1
checks = []
for variable, filename in [("exper", "experience.csv"), ("edu_yrs", "schooling.csv")]:
    grouped = (
        df.groupby(variable, dropna=False)
        .agg(
            incwage=("incwage", "mean"),
            log_wage=("log_wage", "mean"),
            obs_count=("obs_count", "sum"),
        )
        .reset_index()
    )
    # Independent integer-group accumulation checks pandas aggregation.
    valid = df[variable].notna()
    x = df.loc[valid, variable].to_numpy().astype(int)
    count = np.bincount(x)
    for outcome in ["incwage", "log_wage"]:
        total = np.bincount(x, weights=df.loc[valid, outcome].to_numpy().astype(float))
        for _, row in grouped.loc[grouped[variable].notna()].iterrows():
            key = int(row[variable])
            assert int(row.obs_count) == count[key]
            assert np.isclose(
                row[outcome], total[key] / count[key], rtol=1e-7, atol=1e-6
            )
    grouped.to_csv(out / filename, index=False, float_format="%.12g")
    checks.append(
        {
            "file": filename,
            "groups": len(grouped),
            "sample_count": int(grouped.obs_count.sum()),
            "independent_bincount_check": True,
        }
    )
assert hashlib.sha256(raw.read_bytes()).hexdigest() == before
(out / "verification.json").write_text(
    json.dumps(
        {
            "input": "data/acs/acs_clean.dta",
            "input_sha256": before,
            "raw_input_unchanged": True,
            "years": years,
            "source_script": "code/acs/mincer.do",
            "sample_size": len(df),
            "means": "unweighted; Stata-default float log wages",
            "marker_weights": "observation counts, not survey weights",
            "checks": checks,
        },
        indent=2,
    )
)
print(
    f"Reconstructed four ACS series from {len(df):,} observations; years {years}; raw input unchanged."
)
