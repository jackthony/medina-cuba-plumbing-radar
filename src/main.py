from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.dashboard import serve
from src.intelligence.deduplication import deduplicate
from src.intelligence.scoring import score_signal
from src.outputs.csv_export import export_csv
from src.pipelines.normalize import normalize_fort_worth
from src.sources.arcgis import fetch_permits
from src.storage.duckdb import save_signals, top_signals

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/market_radar.duckdb"
CSV = ROOT / "data/top_opportunities.csv"


def settings() -> dict:
    return json.loads((ROOT / "config/settings.json").read_text(encoding="utf-8"))


def collect(source: str) -> int:
    if source not in ("arcgis", "fort_worth"):
        raise SystemExit("Fuente soportada en el MVP: arcgis")
    cfg = settings()
    raw = fetch_permits(cfg)
    signals = [score_signal(normalize_fort_worth(item, cfg["source"]["layer_url"]), cfg["scoring"]) for item in raw]
    count = save_signals(DB, deduplicate(signals))
    print("Guardados {0} permisos reales en {1}".format(count, DB))
    return count


def rank(top: int) -> int:
    cfg = settings()
    rows = top_signals(DB, top, int(cfg["scoring"]["minimum_export_score"]))
    count = export_csv(CSV, rows)
    print("Exportadas {0} oportunidades a {1}".format(count, CSV))
    return count


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Medina Cuba Plumbing DFW Project Radar")
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect"); collect_parser.add_argument("--source", default="arcgis")
    rank_parser = commands.add_parser("rank"); rank_parser.add_argument("--top", type=int, default=50)
    demo_parser = commands.add_parser("demo"); demo_parser.add_argument("--port", type=int, default=8765)
    serve_parser = commands.add_parser("serve"); serve_parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "collect": collect(args.source)
    elif args.command == "rank": rank(args.top)
    elif args.command == "demo": collect("arcgis"); rank(50); serve(DB, port=args.port)
    elif args.command == "serve": serve(DB, port=args.port)


if __name__ == "__main__":
    main()

