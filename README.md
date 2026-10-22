# Development Data Portfolio

A reproducible analytics and software-engineering project using the World Bank's
World Development Indicators (WDI). The first analysis studies how GDP per
capita, life expectancy, fertility, and population vary across reporting
economies over time.

The questions are descriptive: how have these measures changed, where are data
gaps concentrated, and how strongly do the measures move together in the latest
year with observations? Correlation is not evidence of causation. The dataset
contains economies and territories as classified by the World Bank, not only
sovereign states.

## Project Status

The first reproducible slice is in place: live API ingestion, validation,
country-year shaping, descriptive summaries, and unit tests. No downloaded data
is checked into Git. The next milestone is to review the first generated output,
document actual findings with caveats, and build a small presentation layer.

Baseline run accessed 2026-10-21: 5,425 economy-year rows across 217 reporting
economies for 2000-2024. In 2024, GDP per capita and life expectancy have a
Pearson correlation of 0.747 across 195 complete economy pairs. This is a
descriptive association, not a causal estimate; reruns can differ when the
World Bank revises its data.

## Run In VS Code

Requirements: Python 3.11 or newer and an internet connection. The World Bank
Indicators API does not require an API key for these requests.

In the VS Code terminal, from this folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m development_portfolio.cli --start-year 2000 --end-year 2024
python -m pytest
```

The pipeline writes `data/processed/wdi_panel.csv` and
`data/processed/analysis_summary.json`. Both are generated outputs and are
ignored by Git. Re-running the command refreshes the data from the live API;
the source can revise historical values, so the output is not a frozen snapshot.

Use `--start-year` and `--end-year` to select another period. Years must be
positive four-digit years and the start must not exceed the end.

## Source And Reuse

See [DATA_SOURCES.md](DATA_SOURCES.md) for source URLs, field definitions,
verified reuse terms, attribution text, and the limits of what was checked.
The WDI catalog identifies its dataset license as Creative Commons Attribution
4.0 International (CC BY 4.0). This project attributes the World Bank and
records its transformations. That dataset license does not automatically
license this project's source code; choose a separate code license before
publishing if you want others to reuse the code under explicit terms.

## Layout

```text
src/development_portfolio/  API client, analysis, and CLI
tests/                      Offline unit tests
data/processed/             Generated outputs (Git-ignored)
.github/workflows/          Automated test workflow
.vscode/tasks.json          Run pipeline and tests from VS Code
```

## GitHub Checklist

1. Run the setup, pipeline, and tests above; inspect the generated CSV and
   summary before describing findings.
2. Review `DATA_SOURCES.md` and retain attribution when sharing derived results.
3. Create an empty GitHub repository, then from this folder run the following
   after replacing the placeholder with your GitHub username:

   ```powershell
   git branch -M main
   git remote add origin https://github.com/<your-user>/development-data-portfolio.git
   git add .
   git commit -m "Build WDI analytics pipeline"
   git push -u origin main
   ```

   `.venv/` and generated data are ignored. Review `git status` before committing.
4. Add only findings you can reproduce from the output, including dates,
   sample sizes, missingness, and a warning that correlations are descriptive.

## Career Signal

- **Data analytics:** source validation, missing-data reporting, tidy data,
   descriptive statistics, interpretation limits, and reproducible outputs.
- **Software engineering:** modular Python, typed function contracts, API error
   handling, tests, packaging, command-line usage, and CI.
