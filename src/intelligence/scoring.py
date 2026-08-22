from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, List

from src.models.project_signal import ProjectSignal

RESIDENTIAL = ("residential", "single family", "multi-family", "multifamily", "townhome", "townhouse", "apartment", "duplex")
PLUMBING = ("new", "addition", "multifamily", "single family", "apartment", "townhome", "townhouse", "duplex")
SMALL_REMODEL = ("remodel", "repair", "replace", "foundation repair")
INACTIVE = ("expired", "cancel", "complete", "closed", "denied", "void")


def score_signal(signal: ProjectSignal, weights: Dict[str, Any]) -> ProjectSignal:
    text = " ".join([signal.project_name, signal.project_type, signal.scope]).lower()
    reasons: List[str] = []
    score = 0

    score += int(weights["dfw_geography"])
    reasons.append("Fort Worth/DFW +{0}".format(weights["dfw_geography"]))
    residential = any(term in text for term in RESIDENTIAL)
    new_construction = " / new" in text or text.startswith("new ") or "new building" in text or "subdivision" in text
    if residential and new_construction:
        score += int(weights["residential_fit"])
        reasons.append("construcción residencial nueva +{0}".format(weights["residential_fit"]))
        signal.plumbing_relevance = "high"
    elif residential:
        partial_fit = int(weights["residential_fit"]) // 2
        score += partial_fit
        reasons.append("fit residencial parcial +{0}".format(partial_fit))
        signal.plumbing_relevance = "medium"
    elif "commercial" in text:
        score += int(weights["residential_fit"]) // 2
        reasons.append("fit comercial selectivo +{0}".format(int(weights["residential_fit"]) // 2))
        signal.plumbing_relevance = "medium"

    if signal.start_date and signal.start_date >= date.today() - timedelta(days=120):
        score += int(weights["recent_or_upcoming"])
        reasons.append("permiso reciente +{0}".format(weights["recent_or_upcoming"]))
    if (signal.estimated_value or 0) >= 100000 or (signal.square_feet or 0) >= 5000:
        score += int(weights["attractive_value_or_size"])
        reasons.append("escala atractiva +{0}".format(weights["attractive_value_or_size"]))
    owner_is_company = any(marker in signal.owner_developer.upper() for marker in (" LLC", " INC", " LTD", " CORP", " HOMES", " DEVELOPMENT", " DEVELOPER"))
    if signal.builder or signal.general_contractor or owner_is_company:
        score += int(weights["builder_identified"])
        reasons.append("builder/GC identificado +{0}".format(weights["builder_identified"]))
    if any(term in text for term in PLUMBING):
        score += int(weights["plumbing_likelihood"])
        reasons.append("probabilidad de plumbing +{0}".format(weights["plumbing_likelihood"]))
    if signal.owner_developer and signal.address:
        score += int(weights["researchable"])
        reasons.append("investigable +{0}".format(weights["researchable"]))
    if any(term in text for term in SMALL_REMODEL):
        score += int(weights["small_remodel_penalty"])
        reasons.append("remodelación menor {0}".format(weights["small_remodel_penalty"]))
    if any(term in signal.project_stage.lower() for term in INACTIVE):
        score += int(weights["inactive_penalty"])
        reasons.append("estado inactivo {0}".format(weights["inactive_penalty"]))

    signal.opportunity_score = max(0, min(100, score))
    signal.reason_for_score = "; ".join(reasons)
    return signal
