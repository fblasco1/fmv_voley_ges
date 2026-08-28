"""Descarga paginada del fixture de club en metrovoley.com.ar."""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlencode

import requests

from fmv_voley_ges.inertia import extract_matches_props, parse_inertia_html
from fmv_voley_ges.transform import ECHAGUE_CLUB_ID, build_envelope, transform_match

BASE_URL = "https://metrovoley.com.ar"
USER_AGENT = (
	"fmv-voley-ges/0.1 (+https://github.com/fblasco1/fmv_voley_ges; fixture ICDPE)"
)
REQUEST_TIMEOUT_SEC = 60
PAGE_DELAY_SEC = 0.35


def club_matches_url(club_id: int, *, page: int = 1, scope: str | None = None) -> str:
	path = f"/clubs/{club_id}/matches"
	params: dict[str, str | int] = {}
	if page > 1:
		params["page"] = page
	if scope and scope not in ("proximos", ""):
		params["scope"] = scope
	if not params:
		return f"{BASE_URL}{path}"
	return f"{BASE_URL}{path}?{urlencode(params)}"


def fetch_html(url: str, *, session: requests.Session | None = None) -> str:
	client = session or requests
	response = client.get(
		url,
		headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
		timeout=REQUEST_TIMEOUT_SEC,
	)
	response.raise_for_status()
	return response.text


def fetch_club_matches_page(
	club_id: int,
	*,
	page: int = 1,
	scope: str | None = None,
	session: requests.Session | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
	url = club_matches_url(club_id, page=page, scope=scope)
	html = fetch_html(url, session=session)
	inertia = parse_inertia_html(html)
	return extract_matches_props(inertia)


def scrape_club_upcoming_matches(
	club_id: int = ECHAGUE_CLUB_ID,
	*,
	scope: str | None = None,
	only_local: bool = False,
	session: requests.Session | None = None,
) -> list[dict[str, Any]]:
	"""Recorre todas las páginas y devuelve partidos normalizados."""
	session = session or requests.Session()
	all_raw: list[dict[str, Any]] = []
	addresses: list[dict[str, Any]] = []
	page = 1
	last_page = 1

	while page <= last_page:
		matches, pagination, page_addresses = fetch_club_matches_page(
			club_id,
			page=page,
			scope=scope,
			session=session,
		)
		if page_addresses and not addresses:
			addresses = page_addresses
		all_raw.extend(matches)
		last_page = int(pagination.get("lastPage") or 1)
		page += 1
		if page <= last_page:
			time.sleep(PAGE_DELAY_SEC)

	seen_ids: set[str] = set()
	partidos: list[dict[str, Any]] = []
	for raw in all_raw:
		match_id = str(raw.get("id") or "")
		if match_id and match_id in seen_ids:
			continue
		if match_id:
			seen_ids.add(match_id)
		item = transform_match(raw, addresses=addresses)
		if not item:
			continue
		if only_local and item.get("localia") != "Local":
			continue
		partidos.append(item)

	partidos.sort(key=lambda p: (p.get("fecha") or "", p.get("hora") or ""))
	return partidos


def scrape_fixture_envelope(
	club_id: int = ECHAGUE_CLUB_ID,
	*,
	only_local: bool = False,
) -> dict[str, Any]:
	partidos = scrape_club_upcoming_matches(club_id, only_local=only_local)
	return build_envelope(partidos, club_id=club_id)
