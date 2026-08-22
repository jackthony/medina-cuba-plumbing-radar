from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

LOGGER = logging.getLogger(__name__)


class FriscoSourceError(RuntimeError):
    pass


def fetch_active_permits(settings: Dict[str, Any]) -> List[Dict[str, Any]]:
    source = settings["frisco_source"]
    params = {
        "where": "Status = 'ISSUED'",
        "outFields": "*",
        "returnGeometry": "false",
        "orderByFields": "OBJECTID DESC",
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
                raise FriscoSourceError(str(payload["error"]))
            records = [feature["attributes"] for feature in payload.get("features", [])]
            LOGGER.info("Frisco ArcGIS returned %d active permits", len(records))
            return records
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, FriscoSourceError) as exc:
            error = exc
            LOGGER.warning("Frisco attempt %d failed: %s", attempt + 1, exc)
    raise FriscoSourceError("Frisco ArcGIS failed after retries: {0}".format(error))

