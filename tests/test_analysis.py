import pandas as pd
import pytest

from development_portfolio.analysis import build_panel, summarize_panel
from development_portfolio.api import normalize_rows


def test_normalize_rows_excludes_aggregates_and_keeps_nulls():
    rows = [
        {
            "countryiso3code": "USA",
            "country": {"id": "US", "value": "United States"},
            "date": "2020",
            "value": None,
        },
        {
            "countryiso3code": "AFE",
            "country": {"id": "ZH", "value": "Africa Eastern and Southern"},
            "date": "2020",
            "value": 1.0,
        },
    ]

    records = normalize_rows(rows, "SP.DYN.LE00.IN", {"USA": "NAC", "AFE": "NA"})

    assert len(records) == 1
    assert records[0]["economy_code"] == "USA"
    assert records[0]["value"] is None


def test_build_panel_pivots_values_and_preserves_missing_data():
    records = [
        {"economy_code": "USA", "economy": "United States", "region_code": "NAC", "year": 2020,
         "indicator_code": "SP.DYN.LE00.IN", "value": 77.0},
        {"economy_code": "USA", "economy": "United States", "region_code": "NAC", "year": 2020,
         "indicator_code": "NY.GDP.PCAP.PP.KD", "value": 60000.0},
    ]

    panel = build_panel(records)

    assert len(panel) == 1
    assert panel.loc[0, "life_expectancy_years"] == 77.0
    assert panel.loc[0, "gdp_per_capita_ppp_2021_usd"] == 60000.0
    assert pd.isna(panel.loc[0, "fertility_births_per_woman"])


def test_build_panel_rejects_duplicate_observations():
    observation = {
        "economy_code": "USA", "economy": "United States", "region_code": "NAC", "year": 2020,
        "indicator_code": "SP.DYN.LE00.IN", "value": 77.0,
    }

    with pytest.raises(ValueError, match="Duplicate"):
        build_panel([observation, observation.copy()])


def test_summary_reports_missingness_and_non_causal_caveat():
    panel = pd.DataFrame(
        {
            "economy_code": ["AAA", "BBB"],
            "economy": ["A", "B"],
            "region_code": ["AFR", "AFR"],
            "year": [2020, 2020],
            "gdp_per_capita_ppp_2021_usd": [1000.0, 2000.0],
            "life_expectancy_years": [60.0, 70.0],
            "fertility_births_per_woman": [4.0, 2.0],
            "population_people": [100.0, 200.0],
        }
    )

    summary = summarize_panel(panel, {"SP.DYN.LE00.IN": "2026-10-08"}, "2026-10-21T00:00:00+00:00")

    assert summary["latest_year"] == 2020
    assert summary["economies"] == 2
    assert summary["missing_fraction_by_indicator"]["life_expectancy_years"] == 0.0
    assert summary["latest_year_pairwise_observation_counts"]["life_expectancy_years"]["gdp_per_capita_ppp_2021_usd"] == 2
    assert "do not establish causation" in summary["interpretation"]