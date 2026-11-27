#!/usr/bin/env python3
"""Small standard-library example; results describe simulated observations only."""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "需求历史.csv"

with DATA.open(encoding="utf-8-sig", newline="") as stream:
    rows = list(csv.DictReader(stream))

observed = []
for row in rows:
    if not row["units"].strip():
        continue
    observed.append((datetime.strptime(row["week_start"], "%Y/%m/%d").date(), int(row["units"])))

by_year = defaultdict(list)
for day, units in observed:
    by_year[day.year].append(units)

print("Annual descriptive summary (simulated weekly units)")
for year in sorted(by_year):
    values = by_year[year]
    print(f"{year}: weeks={len(values)}, total={sum(values)}, mean={sum(values)/len(values):.2f}")

# Time-ordered holdout: last 12 observed weeks. Baseline predicts the prior 4-week mean.
actual = [units for _, units in observed]
if len(actual) >= 17:
    start = len(actual) - 12
    errors = []
    for index in range(start, len(actual)):
        prediction = sum(actual[index - 4:index]) / 4
        errors.append(abs(actual[index] - prediction))
    print(f"Last-12-week rolling baseline MAE: {sum(errors)/len(errors):.2f} units")
    print("This is an illustrative baseline, not a validated real-world forecast.")
