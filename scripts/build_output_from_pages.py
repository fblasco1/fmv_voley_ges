#!/usr/bin/env python3
"""Fusiona páginas crudas exportadas desde metrovoley y escribe el envelope JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fmv_voley_ges.transform import build_envelope, transform_match

PAGES_DIR = ROOT / "tests" / "fixtures" / "pages"
OUT = ROOT / "outputs" / "echague" / "fixture_fmv_voley.json"


def main() -> int:
	if not PAGES_DIR.exists():
		print(f"Falta {PAGES_DIR}", file=sys.stderr)
		return 1

	all_raw: list[dict] = []
	addresses: list[dict] = []
	seen: set[str] = set()

	for path in sorted(PAGES_DIR.glob("page*.json")):
		data = json.loads(path.read_text(encoding="utf-8"))
		if data.get("addresses") and not addresses:
			addresses = data["addresses"]
		for raw in data.get("matches") or []:
			mid = str(raw.get("id") or "")
			if mid and mid in seen:
				continue
			if mid:
				seen.add(mid)
			all_raw.append(raw)

	partidos = []
	for raw in all_raw:
		item = transform_match(raw, addresses=addresses)
		if item:
			partidos.append(item)
	partidos.sort(key=lambda p: (p.get("fecha") or "", p.get("hora") or ""))

	envelope = build_envelope(partidos)
	OUT.parent.mkdir(parents=True, exist_ok=True)
	OUT.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
	local = sum(1 for p in partidos if p.get("localia") == "Local")
	print(f"OK {len(partidos)} partidos ({local} locales) → {OUT}")
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
