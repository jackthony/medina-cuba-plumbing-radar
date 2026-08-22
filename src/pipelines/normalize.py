from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional

from src.models.project_signal import ProjectSignal


def parse_arcgis_date(value: Any) -> Optional[date]:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, tz=timezone.utc).date()
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(text[:19], fmt).date()
        except ValueError:
            pass
    return None


def parse_number(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    cleaned = re.sub(r"[^0-9.\-]", "", str(value).replace(",", ""))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def normalize_fort_worth(raw: Dict[str, Any], layer_url: str) -> ProjectSignal:
    permit_no = str(raw.get("Permit_No") or raw.get("Unique_ID") or raw.get("ObjectId") or "unknown")
    address_parts = [raw.get("Addr_No"), raw.get("Direction"), raw.get("Street_Name"), raw.get("Street_Suffix"), raw.get("Street_Suffix_Dir")]
    constructed_address = " ".join(str(part).strip() for part in address_parts if part not in (None, ""))
    address = str(raw.get("Full_Street_Address") or constructed_address or "").strip()
    special = str(raw.get("B1_SPECIAL_TEXT") or "").strip()
    work = str(raw.get("B1_WORK_DESC") or "").strip()
    if work.upper() == "B1_WORK_DESC":
        work = ""
    use = " / ".join(filter(None, [str(raw.get("Use_Type") or "").strip(), str(raw.get("Specific_Use") or "").strip()]))
    useful_special = special if special.upper() not in ("METRO CODE", "B1_WORK_DESC", "NA") else ""
    fallback_label = " / ".join(filter(None, [str(raw.get("Permit_SubType") or "").strip(), use]))
    project_name = useful_special or ("{0} — {1}".format(fallback_label, address) if fallback_label and address else "Permit {0}".format(permit_no))
    builder = special if looks_like_company(special) else ""
    source_url = layer_url.rstrip("/") + "/query?" + urlencode_safe("ObjectId={0}".format(raw.get("ObjectId", "")))
    return ProjectSignal(
        source="fort_worth_arcgis_permits",
        source_project_id=permit_no,
        project_name=project_name,
        address=address,
        project_type=" / ".join(filter(None, [str(raw.get("Permit_Type") or ""), str(raw.get("Permit_SubType") or ""), use])),
        project_stage=str(raw.get("Current_Status") or ""),
        start_date=parse_arcgis_date(raw.get("File_Date")),
        estimated_value=parse_number(raw.get("JobValue")),
        owner_developer=str(raw.get("Owner_Full_Name") or "").strip(),
        general_contractor=builder,
        builder=builder,
        scope=work or use,
        square_feet=parse_number(raw.get("SqFt")),
        source_url=source_url,
        raw_payload=raw,
    )


def urlencode_safe(where: str) -> str:
    from urllib.parse import urlencode

    return urlencode({"where": where, "outFields": "*", "returnGeometry": "false", "f": "html"})


def looks_like_company(value: str) -> bool:
    text = " {0} ".format(value.upper())
    company_markers = (" LLC ", " INC ", " LTD ", " CORP ", " HOMES", "BUILDERS", "CONSTRUCTION", "CONTRACTING", "PLUMBING")
    return bool(value) and any(marker in text for marker in company_markers)
