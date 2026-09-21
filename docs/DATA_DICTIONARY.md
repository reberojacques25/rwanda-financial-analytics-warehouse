# Data Dictionary

## mart.fact_interest_rates

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| source_id | VARCHAR(50) | Foreign key to metadata.sources |
| indicator_id | VARCHAR(100) | Standardized indicator code (CBR, LENDING_RATE, etc.) |
| date | DATE | Observation date |
| frequency | VARCHAR(20) | Data frequency (monthly, annual) |
| indicator_name | VARCHAR(200) | Human-readable indicator name |
| value | NUMERIC | Observed value |
| unit | VARCHAR(20) | Unit of measurement (percent) |
| evidence_classification | VARCHAR(50) | VERIFIED_PRIMARY, DERIVED, etc. |
| is_observed | BOOLEAN | True if directly observed |
| is_derived | BOOLEAN | True if computed from other values |
| transformation_notes | TEXT | Notes on any transformations |
| retrieval_date | DATE | When data was retrieved |

## mart.fact_macro_indicators

Same structure as fact_interest_rates, with:
- source_id: WB-MACRO-001
- evidence_classification: VERIFIED_SECONDARY
- frequency: annual

## mart.fact_banking_sector

| Column | Type | Description |
|--------|------|-------------|
| source_id | VARCHAR(50) | Source identifier |
| indicator_id | VARCHAR(100) | Indicator code |
| date | DATE | Observation date |
| value | NUMERIC | Observed value |
| unit | VARCHAR(50) | Unit (FRW, percent, etc.) |
| currency | VARCHAR(20) | Currency (FRW) |

## Indicator Codes

| Code | Name | Source |
|------|------|--------|
| CBR | Central Bank Rate | BNR |
| LENDING_RATE | Lending Rate | BNR |
| DEPOSIT_RATE | Deposit Rate | BNR |
| INTERBANK_RATE | Interbank Rate | BNR |
| INFLATION_YOY | Inflation (annual %) | World Bank |
| GDP_GROWTH | GDP growth (annual %) | World Bank |
| GDP_USD | GDP (current US$) | World Bank |
| EXCHANGE_RATE_USD | Official exchange rate (LCU per US$) | World Bank |
| NPL_RATIO_WB | Bank NPL to total gross loans (%) | World Bank |
