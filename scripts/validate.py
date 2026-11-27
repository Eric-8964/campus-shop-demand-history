#!/usr/bin/env python3
"""Validate the teaching dataset's structure and report its current profile."""
from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "需求历史.csv"
FIELDS = ("week_start", "units", "lead_weeks", "term_start", "exam_week", "club_fair", "is_open", "stockout")
FLAGS = ("term_start", "exam_week", "club_fair", "is_open", "stockout")


def main() -> None:
    errors = []
    with DATA.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise SystemExit(f"Unexpected header: {reader.fieldnames!r}")
        rows = list(reader)

    seen = set()
    dates = []
    missing = Counter()
    flag_ones = Counter()
    for line_number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            errors.append(f"line {line_number}: malformed column count")
            continue
        try:
            day = datetime.strptime(row["week_start"], "%Y/%m/%d").date()
            if day.weekday() != 0:
                errors.append(f"line {line_number}: week_start is not Monday")
            if day in seen:
                errors.append(f"line {line_number}: duplicate date")
            seen.add(day)
            dates.append(day)
        except ValueError:
            errors.append(f"line {line_number}: invalid date")
        for name in ("units", "lead_weeks"):
            value = row[name].strip()
            if not value:
                missing[name] += 1
                continue
            try:
                number = int(value) if name == "units" else float(value)
                if number < 0:
                    raise ValueError()
            except ValueError:
                errors.append(f"line {line_number}: invalid {name}")
        for name in FLAGS:
            if row[name] not in ("0", "1"):
                errors.append(f"line {line_number}: invalid {name}")
            else:
                flag_ones[name] += int(row[name])

    for previous, current in zip(dates, dates[1:]):
        if (current - previous).days != 7:
            errors.append(f"week gap/order: {previous} -> {current}")

    print(f"file: {DATA.name}")
    print(f"rows: {len(rows)}")
    print(f"date range: {min(dates) if dates else 'n/a'} .. {max(dates) if dates else 'n/a'}")
    print(f"missing: {dict(missing)}")
    print(f"flag counts (1): {dict(flag_ones)}")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("structure: PASS (this does not verify real-world provenance)")


if __name__ == "__main__":
    main()
