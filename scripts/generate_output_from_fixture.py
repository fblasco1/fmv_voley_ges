#!/usr/bin/env python3
"""Genera outputs/ desde fixture de test (sin red)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fmv_voley_ges.transform import build_envelope, transform_match

FIXTURE = ROOT / "tests" / "fixtures" / "club_420_matches_page1.json"
OUT_JSON = ROOT / "outputs" / "echague" / "fixture_fmv_voley.json"


def main() -> int:
	data = json.loads(FIXTURE.read_text(encoding="utf-8"))
	partidos = []
	for raw in data["matches"]:
		item = transform_match(raw, addresses=data.get("addresses") or [])
		if item:
			partidos.append(item)
	envelope = build_envelope(partidos, generated_at="2026-08-28T20:00:00-03:00")
	OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
	OUT_JSON.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
	print(f"Wrote {len(partidos)} partidos → {OUT_JSON}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
