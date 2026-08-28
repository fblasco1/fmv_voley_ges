"""Normalización de partidos FMV al contrato JSON consumido por SICLUB."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fmv_voley_ges.espacio import build_equipo_label, resolve_espacio_local

SOURCE = "fmv_voley"
ECHAGUE_CLUB_ID = 420


def is_echague_team(team: dict[str, Any] | None) -> bool:
	if not team:
		return False
	if team.get("clubId") == ECHAGUE_CLUB_ID:
		return True
	name = (team.get("name") or "").upper()
	return "ECHAG" in name


def resolve_direccion(venue: str, addresses: list[dict[str, Any]]) -> str:
	venue_upper = (venue or "").upper()
	for addr in addresses:
		name = (addr.get("name") or "").upper()
		address = (addr.get("address") or "").strip()
		city = (addr.get("city") or "").strip()
		if "OLÍMPICO" in venue_upper or "OLIMPICO" in venue_upper:
			if "OLÍMPICO" in name or "OLIMPICO" in name:
				return ", ".join(p for p in (address, city) if p)
		if "ECHAG" in venue_upper and ("ECHAG" in name or "PEDRO" in name):
			return ", ".join(p for p in (address, city) if p)
	for addr in addresses:
		name = (addr.get("name") or "").upper()
		if "ECHAG" in name or "PEDRO" in name:
			address = (addr.get("address") or "").strip()
			city = (addr.get("city") or "").strip()
			return ", ".join(p for p in (address, city) if p)
	return "Portela 836, Capital Federal"


def parse_scheduled(scheduled_at: str) -> tuple[str, str]:
	"""Convierte ``2026-08-29T09:00:00`` a (fecha ISO, hora HH:MM)."""
	text = (scheduled_at or "").strip()
	if not text:
		raise ValueError("scheduledAt vacío")
	# FMV a veces manda fecha UTC en detalle; en listado suele venir hora local sin Z.
	dt = datetime.fromisoformat(text.replace("Z", "+00:00").split(".")[0])
	return dt.date().isoformat(), dt.strftime("%H:%M")


def transform_match(
	raw: dict[str, Any],
	*,
	addresses: list[dict[str, Any]] | None = None,
) -> dict[str, Any] | None:
	home = raw.get("homeTeam") or {}
	away = raw.get("awayTeam") or {}
	addresses = addresses or []

	if is_echague_team(home):
		localia = "Local"
		echague_team = home.get("name") or ""
		rival = away.get("name") or ""
	elif is_echague_team(away):
		localia = "Visitante"
		echague_team = away.get("name") or ""
		rival = home.get("name") or ""
	else:
		return None

	fecha, hora = parse_scheduled(str(raw.get("scheduledAt") or ""))
	categoria = str(raw.get("categoryName") or "").strip()
	division = str(raw.get("divisionName") or "").strip()
	equipo = build_equipo_label(categoria, echague_team)
	venue = str(raw.get("venue") or "").strip()

	espacio: str | None = None
	if localia == "Local":
		espacio = resolve_espacio_local(categoria=categoria, team_name=echague_team)

	return {
		"source": SOURCE,
		"external_id": str(raw.get("id") or raw.get("number") or ""),
		"fecha": fecha,
		"hora": hora,
		"categoria": categoria,
		"tira": division,
		"equipo": equipo,
		"rival": rival,
		"localia": localia,
		"direccion": resolve_direccion(venue, addresses),
		"espacio": espacio,
		"venue": venue,
		"numero_partido": raw.get("number"),
		"status_label": raw.get("statusLabel"),
	}


def build_envelope(
	partidos: list[dict[str, Any]],
	*,
	club_id: int = ECHAGUE_CLUB_ID,
	club_name: str = "PEDRO ECHAGUE",
	generated_at: str | None = None,
) -> dict[str, Any]:
	from datetime import datetime, timezone, timedelta

	if generated_at is None:
		# ART (UTC-3) sin depender de zoneinfo en runtime mínimo
		art = timezone(timedelta(hours=-3))
		generated_at = datetime.now(tz=art).replace(microsecond=0).isoformat()

	return {
		"version": 1,
		"source": SOURCE,
		"generated_at": generated_at,
		"club": club_name,
		"club_id_fmv": club_id,
		"partidos": partidos,
	}
