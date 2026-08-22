from __future__ import annotations

import json
import logging
import time
from datetime import date, timedelta
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LOGGER = logging.getLogger(__name__)


class ArcGISSourceError(RuntimeError):
    pass


def fetch_permits(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = settings["source"]
    since = date.today() - timedelta(days=int(source["lookback_days"]))
    where = (
        "File_Date >= DATE '{since}' AND "
        "Permit_Type IN ('Residential Building Permit','Commercial Building Permit')"
    ).format(since=since.isoformat())
    params = {
        "where": where,
        "outFields": "*",
        "returnGeometry": "false",
        "orderByFields": "File_Date DESC",
        "resultRecordCount": str(source["record_limit"]),
        "f": "json",
    }
    url = source["layer_url"].rstrip("/") + "/query?" + urlencode(params)
    request = Request(url, headers={"User-Agent": "MedinaCubaMarketRadar/0.1"})

    error: Optional[Exception] = None
    for attempt in range(int(source["max_retries"])):
        try:
            if attempt:
                time.sleep(float(source["rate_limit_seconds"]) * (2**attempt))
            with urlopen(request, timeout=float(source["timeout_seconds"])) as response:
                payload = json.load(response)
            if payload.get("error"):
                raise ArcGISSourceError(str(payload["error"]))
            records = [feature["attributes"] for feature in payload.get("features", [])]
            LOGGER.info("ArcGIS returned %d permits since %s", len(records), since)
            return records
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, ArcGISSourceError) as exc:
            error = exc
            LOGGER.warning("ArcGIS attempt %d failed: %s", attempt + 1, exc)
    raise ArcGISSourceError("ArcGIS failed after retries: {0}".format(error))
