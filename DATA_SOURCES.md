# Data Sources And Terms

Verified on 2026-10-21. Recheck the linked catalog and license before
redistributing data or publishing new derived artifacts; sources can change.

## World Development Indicators

- Publisher: World Bank.
- Dataset: [World Development Indicators catalog record](https://datacatalog.worldbank.org/search/dataset/0037712/world-development-indicators).
- API documentation: [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures).
- API base: `https://api.worldbank.org/v2/country/all/indicator/{indicator}`.
- Example checked successfully: [2020 GDP per capita API response](https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.KD?date=2020&format=json&per_page=5).
- The API documentation specifies `format=json`, date ranges, and pagination.
- The WDI catalog record identifies the dataset license as Creative Commons
  Attribution 4.0 International (CC BY 4.0). The World Bank's [license
  guidance](https://datacatalog.worldbank.org/public-licenses) describes
  attribution and disclosure of changes as requirements. Some World Bank
  catalog data is under different terms; this project uses the WDI record,
  not unrelated microdata or third-party datasets.
- The catalog page describes WDI as covering more than 1,500 indicators and
  200+ countries and territories. Individual indicators can have different
  sources, coverage, update schedules, and missingness.

### Indicators Used

| Code | Meaning | Unit |
| --- | --- | --- |
| `NY.GDP.PCAP.PP.KD` | GDP per capita, PPP (constant 2021 international $) | 2021 international dollars per person |
| `SP.DYN.LE00.IN` | Life expectancy at birth, total | Years |
| `SP.DYN.TFRT.IN` | Fertility rate, total | Births per woman |
| `SP.POP.TOTL` | Population, total | People |

Indicator responses provide economy codes and labels; the pipeline joins them
to the World Bank country endpoint for region metadata. It stores the economy
code and label, year, indicator value, and region code; removes rows whose
World Bank region code is `NA` (regional/income aggregates); retains null
observations; and reshapes observations to one row per economy-year. It does
not impute or interpolate values.

## Attribution

Suggested attribution for derived tables or charts:

> Source: World Bank, World Development Indicators, accessed 2026-10-21 via the
> World Bank Indicators API. Data filtered to reporting economies and selected
> indicators, then reshaped to economy-year records. Licensed under CC BY 4.0.

Update the access date and describe any additional transformations in anything
you publish. Do not imply that the World Bank endorses the analysis. The source
API's `lastupdated` metadata is recorded in the generated summary when
available.

## Limits

The test requests confirmed that the API returns live data, but this project
has not independently audited every national statistical source or reconciled
indicator methodologies. WDI values can be revised. Missingness varies by
indicator and year; comparisons should state the observation window and sample
size. Correlations are descriptive and do not establish causation.
