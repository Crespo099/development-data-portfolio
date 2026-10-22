"""Validation and descriptive analysis for the country-year panel."""

from __future__ import annotations

from typing import Any

import pandas as pd

INDICATORS = {
    "NY.GDP.PCAP.PP.KD": "gdp_per_capita_ppp_2021_usd",
    "SP.DYN.LE00.IN": "life_expectancy_years",
    "SP.DYN.TFRT.IN": "fertility_births_per_woman",
    "SP.POP.TOTL": "population_people",
}
KEY_COLUMNS = ["economy_code", "economy", "region_code", "year"]


def build_panel(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Validate observations and pivot them into one row per economy-year."""
    if not records:
        raise ValueError("The API returned no observations for the selected period.")

    observations = pd.DataFrame.from_records(records)
    required = set(KEY_COLUMNS + ["indicator_code", "value"])
    missing = required.difference(observations.columns)
    if missing:
        raise ValueError(f"Observation fields missing: {', '.join(sorted(missing))}.")
    if observations.duplicated(KEY_COLUMNS + ["indicator_code"]).any():
        raise ValueError("Duplicate economy-year-indicator observations found.")

    observations["year"] = pd.to_numeric(observations["year"], errors="raise").astype(int)
    observations["value"] = pd.to_numeric(observations["value"], errors="coerce")
    panel = observations.pivot(
        index=KEY_COLUMNS,
        columns="indicator_code",
        values="value",
    ).reset_index()
    panel.columns.name = None

    for code, column in INDICATORS.items():
        if code not in panel:
            panel[code] = pd.NA
        panel[column] = pd.to_numeric(panel.pop(code), errors="coerce")

    return panel[KEY_COLUMNS + list(INDICATORS.values())].sort_values(
        ["year", "economy_code"], ignore_index=True
    )


def summarize_panel(
    panel: pd.DataFrame,
    source_updated: dict[str, str | None],
    accessed_at: str,
) -> dict[str, Any]:
    """Build coverage and latest-year pairwise correlation summaries."""
    if panel.empty:
        raise ValueError("Cannot summarize an empty panel.")

    metric_columns = list(INDICATORS.values())
    latest_year = int(panel["year"].max())
    latest = panel.loc[panel["year"] == latest_year, metric_columns]
    correlations = latest.corr(method="pearson")
    pairwise_counts = {
        left: {
            right: int(latest[[left, right]].dropna().shape[0])
            for right in metric_columns
        }
        for left in metric_columns
    }
    correlation_summary = {
        left: {
            right: (
                None
                if pd.isna(correlations.loc[left, right])
                else round(float(correlations.loc[left, right]), 3)
            )
            for right in metric_columns
        }
        for left in metric_columns
    }

    return {
        "source": "World Bank World Development Indicators",
        "accessed_at_utc": accessed_at,
        "source_last_updated": source_updated,
        "period": {
            "start_year": int(panel["year"].min()),
            "end_year": int(panel["year"].max()),
        },
        "panel_rows": int(len(panel)),
        "economies": int(panel["economy_code"].nunique()),
        "latest_year": latest_year,
        "latest_year_economies": int(panel.loc[panel["year"] == latest_year, "economy_code"].nunique()),
        "missing_fraction_by_indicator": {
            column: round(float(panel[column].isna().mean()), 4)
            for column in metric_columns
        },
        "latest_year_pairwise_observation_counts": pairwise_counts,
        "latest_year_pairwise_pearson_correlations": correlation_summary,
        "interpretation": "Descriptive associations only; correlations do not establish causation.",
    }