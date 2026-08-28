"""Reglas de mapeo cancha FMV → SICLUB (acordadas con Coordinación)."""

from __future__ import annotations

CANCHA_1 = "Cancha 1"
CANCHA_2 = "Cancha 2"


def normalize_team_name(name: str) -> str:
	return " ".join((name or "").strip().upper().split())


def build_equipo_label(categoria: str, team_name: str) -> str:
	cat = (categoria or "").strip()
	team = (team_name or "").strip()
	if cat and team:
		return f"{cat} {team}"
	return team or cat


def resolve_espacio_local(*, categoria: str, team_name: str) -> str:
	"""Solo partidos locales en Portela. Visitante devuelve None vía transform."""
	cat = (categoria or "").strip().lower()
	team = normalize_team_name(team_name)

	# SUPERIOR ECHAGÜE (equipo principal, sin sufijo B) → Cancha 1
	if cat == "superiores" and team == "ECHAGÜE":
		return CANCHA_1
	# SUPERIOR ECHAGÜE B y resto de categorías locales → Cancha 2
	return CANCHA_2
