from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

import duckdb

from src.models.project_signal import ProjectSignal

SCHEMA = """
CREATE TABLE IF NOT EXISTS project_signals (
 source VARCHAR, source_project_id VARCHAR, project_name VARCHAR, address VARCHAR,
 city VARCHAR, county VARCHAR, state VARCHAR, project_type VARCHAR, project_stage VARCHAR,
 start_date DATE, completion_date DATE, estimated_value DOUBLE, owner_developer VARCHAR,
 general_contractor VARCHAR, builder VARCHAR, design_firm VARCHAR, scope VARCHAR,
 square_feet DOUBLE, plumbing_relevance VARCHAR, opportunity_score INTEGER,
 reason_for_score VARCHAR, source_url VARCHAR, first_seen TIMESTAMP, last_seen TIMESTAMP,
 raw_payload JSON, PRIMARY KEY(source, source_project_id)
)
"""


def save_signals(path: Path, signals: Iterable[ProjectSignal]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(signals)
    with duckdb.connect(str(path)) as db:
        db.execute(SCHEMA)
        for s in rows:
            db.execute("DELETE FROM project_signals WHERE source=? AND source_project_id=?", [s.source, s.source_project_id])
            db.execute(
                "INSERT INTO project_signals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [s.source, s.source_project_id, s.project_name, s.address, s.city, s.county, s.state,
                 s.project_type, s.project_stage, s.start_date, s.completion_date, s.estimated_value,
                 s.owner_developer, s.general_contractor, s.builder, s.design_firm, s.scope,
                 s.square_feet, s.plumbing_relevance, s.opportunity_score, s.reason_for_score,
                 s.source_url, s.first_seen, s.last_seen, json.dumps(s.raw_payload)],
            )
    return len(rows)


def top_signals(path: Path, limit: int, minimum_score: int) -> List[tuple]:
    with duckdb.connect(str(path), read_only=True) as db:
        return db.execute(
            """SELECT opportunity_score, project_name, city, project_type, start_date,
                      estimated_value, COALESCE(NULLIF(builder,''), general_contractor, ''),
                      owner_developer, plumbing_relevance, reason_for_score, source, source_url,
                      address, project_stage, square_feet
               FROM project_signals WHERE opportunity_score >= ?
               ORDER BY opportunity_score DESC, start_date DESC LIMIT ?""",
            [minimum_score, limit],
        ).fetchall()


def top_signals_for_source(path: Path, source: str, limit: int, minimum_score: int) -> List[tuple]:
    with duckdb.connect(str(path), read_only=True) as db:
        return db.execute(
            """SELECT opportunity_score, project_name, city, project_type, start_date,
                      estimated_value, COALESCE(NULLIF(builder,''), general_contractor, ''),
                      owner_developer, plumbing_relevance, reason_for_score, source, source_url,
                      address, project_stage, square_feet
               FROM project_signals WHERE opportunity_score >= ? AND source = ?
               ORDER BY opportunity_score DESC, start_date DESC LIMIT ?""",
            [minimum_score, source, limit],
        ).fetchall()


def top_accounts(path: Path, limit: int = 20, minimum_score: int = 70) -> List[tuple]:
    with duckdb.connect(str(path), read_only=True) as db:
        return db.execute(
            """SELECT COALESCE(NULLIF(builder,''), NULLIF(owner_developer,'')) AS target_company,
                      COUNT(*) AS active_permits, MAX(opportunity_score) AS max_score,
                      SUM(COALESCE(estimated_value, 0)) AS total_permit_value,
                      MAX(start_date) AS latest_permit,
                      STRING_AGG(DISTINCT project_type, ' | ') AS project_types,
                      MAX(address) AS example_address, MAX(source_url) AS source_url
               FROM project_signals
               WHERE opportunity_score >= ? AND target_company IS NOT NULL
                 AND UPPER(target_company) NOT IN ('CITY OF FORT WORTH', 'FORT WORTH ISD', 'TARRANT COUNTY')
               GROUP BY target_company
               ORDER BY active_permits DESC, max_score DESC, total_permit_value DESC
               LIMIT ?""",
            [minimum_score, limit],
        ).fetchall()


def radar_summary(path: Path) -> tuple:
    """Return presentation-safe counts without inferring annual production."""
    with duckdb.connect(str(path), read_only=True) as db:
        return db.execute(
            """SELECT COUNT(*) AS signal_count,
                      COUNT(DISTINCT source) AS source_count,
                      SUM(CASE WHEN project_type ILIKE '%Residential Building Permit / New / Single Family Residence%'
                               THEN 1 ELSE 0 END) AS new_single_family_permits
               FROM project_signals"""
        ).fetchone()


def source_coverage(path: Path) -> List[tuple]:
    """Describe the exact observed date window for every municipal source."""
    with duckdb.connect(str(path), read_only=True) as db:
        return db.execute(
            """SELECT source, COUNT(*) AS signal_count, MIN(start_date), MAX(start_date)
               FROM project_signals
               GROUP BY source
               ORDER BY source"""
        ).fetchall()
