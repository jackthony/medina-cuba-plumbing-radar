from __future__ import annotations

from typing import Iterable, List

from src.models.project_signal import ProjectSignal


def deduplicate(signals: Iterable[ProjectSignal]) -> List[ProjectSignal]:
    unique = {}
    for signal in signals:
        key = (signal.source, signal.source_project_id.strip().lower())
        current = unique.get(key)
        if current is None or signal.last_seen > current.last_seen:
            unique[key] = signal
    return list(unique.values())

