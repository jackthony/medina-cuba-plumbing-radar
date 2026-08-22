from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

COLUMNS = ["score", "project_name", "city", "project_type", "start_date", "estimated_value", "builder_gc", "owner_developer", "plumbing_relevance", "reason_for_score", "source", "source_url"]
ACCOUNT_COLUMNS = ["target_company", "active_permits", "max_score", "total_permit_value", "latest_permit", "project_types", "example_address", "source_url"]


def export_csv(path: Path, rows: Iterable[tuple]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for row in materialized:
            writer.writerow(row[:12])
    return len(materialized)


def export_accounts_csv(path: Path, rows: Iterable[tuple]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized = list(rows)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(ACCOUNT_COLUMNS)
        writer.writerows(materialized)
    return len(materialized)
