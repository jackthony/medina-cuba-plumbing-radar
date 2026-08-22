from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional


@dataclass
class ProjectSignal:
    source: str
    source_project_id: str
    project_name: str
    address: str = ""
    city: str = "Fort Worth"
    county: str = "Tarrant"
    state: str = "TX"
    project_type: str = ""
    project_stage: str = ""
    start_date: Optional[date] = None
    completion_date: Optional[date] = None
    estimated_value: Optional[float] = None
    owner_developer: str = ""
    general_contractor: str = ""
    builder: str = ""
    design_firm: str = ""
    scope: str = ""
    square_feet: Optional[float] = None
    plumbing_relevance: str = "unknown"
    opportunity_score: int = 0
    reason_for_score: str = ""
    source_url: str = ""
    first_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_payload: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)

