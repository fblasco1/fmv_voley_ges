#!/usr/bin/env python3
"""Sincroniza fixture FMV Echagüe → JSON (y CSV opcional) para SICLUB."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
	sys.path.insert(0, str(ROOT))

from fmv_voley_ges.scrape import scrape_fixture_envelope

DEFAULT_JSON = ROOT / "outputs" / "echague" / "fixture_fmv_voley.json"
DEFAULT_CSV = ROOT / "outputs" / "echague" / "fixture_fmv_voley.csv"


def write_json(path: Path, envelope: dict) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, envelope: dict) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	rows = envelope.get("partidos") or []
	fieldnames = [
		"external_id",
		"numero_partido",
		"fecha",
		"hora",
		"categoria",
		"tira",
		"equipo",
		"rival",
		"localia",
		"espacio",
		"direccion",
		"venue",
		"status_label",
	]
	with path.open("w", encoding="utf-8", newline="") as fh:
		writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
		writer.writeheader()
		for row in rows:
			writer.writerow(row)


def main() -> int:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--json", type=Path, default=DEFAULT_JSON, help="Ruta salida JSON")
	parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Ruta salida CSV")
	parser.add_argument("--solo-local", action="store_true", help="Solo partidos con localía Local")
	parser.add_argument("--no-csv", action="store_true", help="No escribir CSV")
	args = parser.parse_args()

	envelope = scrape_fixture_envelope(only_local=args.solo_local)
	write_json(args.json, envelope)
	if not args.no_csv:
		write_csv(args.csv, envelope)

	local = sum(1 for p in envelope["partidos"] if p.get("localia") == "Local")
	print(
		f"OK: {len(envelope['partidos'])} partidos ({local} locales) → {args.json}",
		file=sys.stderr,
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
