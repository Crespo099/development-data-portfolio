"""Small, paginated client for the World Bank Indicators API."""

from __future__ import annotations

from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_BASE_URL = "https://api.worldbank.org/v2"
PAGE_SIZE = 10_000
COUNTRY_PAGE_SIZE = 400


def create_session() -> requests.Session:
    """Create a session with bounded retries for transient GET failures."""
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": "development-data-portfolio/0.1"})
    return session


def fetch_country_regions(session: requests.Session) -> dict[str, str | None]:
    """Fetch World Bank economy-to-region metadata, including aggregate markers."""
    url = f"{API_BASE_URL}/country"
    params = {"format": "json", "per_page": COUNTRY_PAGE_SIZE, "page": 1}
    regions: dict[str, str | None] = {}

    while True:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[0], dict):
            raise ValueError("Unexpected World Bank country metadata response.")

        metadata = payload[0]
        if "message" in metadata:
            raise ValueError(f"World Bank country metadata error: {metadata['message']}")
        countries = payload[1] or []
        if not isinstance(countries, list):
            raise ValueError("Unexpected World Bank country metadata rows.")

        for country in countries:
            region = country.get("region") or {}
            regions[country["id"]] = region.get("id")

        page = int(metadata.get("page", params["page"]))
        pages = int(metadata.get("pages", page))
        if page >= pages:
            break
        params["page"] = page + 1

    return regions


def normalize_rows(
    rows: list[dict[str, Any]],
    indicator_code: str,
    region_by_economy: dict[str, str | None],
) -> list[dict[str, Any]]:
    """Keep reporting economies and map API records to the project schema."""
    normalized = []
    for row in rows:
        country = row.get("country") or {}
        economy_code = row.get("countryiso3code")
        if not economy_code:
            continue
        if economy_code not in region_by_economy:
            raise ValueError(f"No World Bank region metadata found for {economy_code}.")
        region_code = region_by_economy[economy_code]
        if region_code == "NA":
            continue

        normalized.append(
            {
                "economy_code": economy_code,
                "economy": country.get("value"),
                "region_code": region_code,
                "year": int(row["date"]),
                "indicator_code": indicator_code,
                "value": row.get("value"),
            }
        )
    return normalized


def fetch_indicator(
    session: requests.Session,
    indicator_code: str,
    start_year: int,
    end_year: int,
    region_by_economy: dict[str, str | None],
) -> tuple[list[dict[str, Any]], str | None]:
    """Fetch all pages for one indicator and return rows plus source update date."""
    if start_year < 1 or end_year < 1 or start_year > end_year:
        raise ValueError("Years must be positive and start_year must not exceed end_year.")

    url = f"{API_BASE_URL}/country/all/indicator/{indicator_code}"
    params = {
        "date": f"{start_year}:{end_year}",
        "format": "json",
        "per_page": PAGE_SIZE,
        "page": 1,
    }
    all_rows: list[dict[str, Any]] = []
    source_updated: str | None = None

    while True:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[0], dict):
            raise ValueError(f"Unexpected World Bank API response for {indicator_code}.")

        metadata = payload[0]
        if "message" in metadata:
            raise ValueError(f"World Bank API error for {indicator_code}: {metadata['message']}")
        source_updated = metadata.get("lastupdated") or source_updated
        rows = payload[1] or []
        if not isinstance(rows, list):
            raise ValueError(f"Unexpected row payload for {indicator_code}.")
        all_rows.extend(normalize_rows(rows, indicator_code, region_by_economy))

        page = int(metadata.get("page", params["page"]))
        pages = int(metadata.get("pages", page))
        if page >= pages:
            break
        params["page"] = page + 1

    return all_rows, source_updated