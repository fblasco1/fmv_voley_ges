"""Parseo de páginas Inertia.js (Laravel + SportsFlow) en metrovoley.com.ar."""

from __future__ import annotations

import html
import json
import re
from typing import Any

_INERTIA_ATTR_RE = re.compile(r'data-page="([^"]+)"', re.DOTALL)


def parse_inertia_html(page_html: str) -> dict[str, Any]:
	"""Extrae el objeto JSON embebido en el atributo ``data-page``."""
	match = _INERTIA_ATTR_RE.search(page_html)
	if not match:
		raise ValueError("No se encontró atributo data-page (Inertia) en el HTML")
	raw = html.unescape(match.group(1))
	data = json.loads(raw)
	if not isinstance(data, dict):
		raise ValueError("data-page no es un objeto JSON")
	return data


def extract_matches_props(inertia: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
	"""Devuelve (matches, pagination, addresses) desde props Inertia."""
	props = inertia.get("props") or {}
	matches = props.get("matches") or []
	pagination = props.get("pagination") or {}
	addresses = props.get("addresses") or []
	if not isinstance(matches, list):
		raise ValueError("props.matches no es una lista")
	return matches, pagination, addresses
