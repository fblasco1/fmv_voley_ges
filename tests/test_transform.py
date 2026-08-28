from __future__ import annotations

import json
from pathlib import Path

import pytest

from fmv_voley_ges.espacio import resolve_espacio_local
from fmv_voley_ges.inertia import parse_inertia_html
from fmv_voley_ges.transform import build_envelope, transform_match

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def inertia_matches() -> dict:
	data = json.loads((FIXTURES / "club_420_matches_page1.json").read_text(encoding="utf-8"))
	return data


def test_resolve_espacio_superior_echague_cancha_1() -> None:
	assert resolve_espacio_local(categoria="Superiores", team_name="ECHAGÜE") == "Cancha 1"


def test_resolve_espacio_superior_echague_b_cancha_2() -> None:
	assert resolve_espacio_local(categoria="Superiores", team_name="ECHAGÜE B") == "Cancha 2"


def test_resolve_espacio_sub15_default_cancha_2() -> None:
	assert resolve_espacio_local(categoria="Sub 15", team_name="ECHAGÜE") == "Cancha 2"


def test_transform_local_superior_b(inertia_matches: dict) -> None:
	raw = next(m for m in inertia_matches["matches"] if m["number"] == 57434)
	item = transform_match(raw, addresses=inertia_matches["addresses"])
	assert item is not None
	assert item["localia"] == "Local"
	assert item["espacio"] == "Cancha 2"
	assert item["equipo"] == "Superiores ECHAGÜE B"
	assert item["rival"] == "GELP B"
	assert item["fecha"] == "2026-09-03"
	assert item["hora"] == "21:30"


def test_transform_visitante_sub11(inertia_matches: dict) -> None:
	raw = next(m for m in inertia_matches["matches"] if m["number"] == 741209)
	item = transform_match(raw, addresses=inertia_matches["addresses"])
	assert item is not None
	assert item["localia"] == "Visitante"
	assert item["espacio"] is None
	assert item["rival"] == "UBA"


def test_transform_local_superior_principal(inertia_matches: dict) -> None:
	raw = next(m for m in inertia_matches["matches"] if m["number"] == 53142)
	item = transform_match(raw, addresses=inertia_matches["addresses"])
	assert item is not None
	assert item["localia"] == "Local"
	assert item["equipo"] == "Superiores ECHAGÜE"
	assert item["espacio"] == "Cancha 1"


def test_parse_inertia_html_minimal() -> None:
	html = (FIXTURES / "minimal_inertia.html").read_text(encoding="utf-8")
	data = parse_inertia_html(html)
	assert data["props"]["matches"][0]["number"] == 57434


def test_build_envelope_contract() -> None:
	env = build_envelope([], generated_at="2026-08-28T20:00:00-03:00")
	assert env["version"] == 1
	assert env["source"] == "fmv_voley"
	assert env["club_id_fmv"] == 420
