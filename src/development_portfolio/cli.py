"""Command-line entry point for downloading and analyzing WDI data."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from development_portfolio.analysis import INDICATORS, build_panel, summarize_panel
from development_portfolio.api import create_session, fetch_country_regions, fetch_indicator


def run(start_year: int, end_year: int, output_dir: Path) -> tuple[Path, Path]:
    if start_year < 1 or end_year < 1 or start_year > end_year:
        raise ValueError("Years must be positive and start_year must not exceed end_year.")

    records = []
    source_updated = {}
    with create_session() as session:
        region_by_economy = fetch_country_regions(session)
        for indicator_code in INDICATORS:
            indicator_records, updated = fetch_indicator(
                session, indicator_code, start_year, end_year, region_by_economy
            )
            records.extend(indicator_records)
            source_updated[indicator_code] = updated

    panel = build_panel(records)
    accessed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = summarize_panel(panel, source_updated, accessed_at)

    output_dir.mkdir(parents=True, exist_ok=True)
    panel_path = output_dir / "wdi_panel.csv"
    summary_path = output_dir / "analysis_summary.json"
    panel.to_csv(panel_path, index=False, float_format="%.6g")
    summary_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return panel_path, summary_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-year", type=int, default=2000)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    try:
        panel_path, summary_path = run(args.start_year, args.end_year, args.output_dir)
    except (ValueError, OSError) as error:
        parser.error(str(error))

    print(f"Panel written to {panel_path}")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()