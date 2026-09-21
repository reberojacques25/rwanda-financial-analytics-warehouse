# Warehouse Schema

## Overview

The RFAW warehouse uses PostgreSQL with four schemas:

1. **metadata** — Source catalog, provenance, data quality results
2. **staging** — Raw data as ingested (1:1 with source files)
3. **mart** — Transformed analytical tables (fact tables)
4. **reference** — Reference/dimension tables

## Schemas

### metadata.sources
| Column | Type | Description |
|--------|------|-------------|
| source_id | VARCHAR(50) PK | Unique source identifier |
| source_name | VARCHAR(200) | Human-readable name |
| source_organization | VARCHAR(200) | Publishing organization |
| source_type | VARCHAR(100) | Data type |
| source_url | TEXT | Direct URL |
| source_format | VARCHAR(20) | File format |
| date_coverage | TEXT | Temporal coverage |
| geographic_coverage | VARCHAR(100) | Geographic scope |
| evidence_classification | VARCHAR(50) | VERIFIED_PRIMARY, etc. |
| is_observed | BOOLEAN | Directly observed |
| is_derived | BOOLEAN | Computed |
| ingestion_status | VARCHAR(50) | INGESTED_AUTOMATED, CATALOGED_PENDING_EXTRACTION, MANUAL_EXTRACTION_REQUIRED |
| license | VARCHAR(200) | License terms |
| retrieval_date | DATE | When retrieved |
| is_active | BOOLEAN | Actively maintained |

### mart.fact_interest_rates
| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL PK | Primary key |
| source_id | VARCHAR(50) FK | Source reference |
| indicator_id | VARCHAR(100) | Standardized code (CBR, LENDING_RATE, etc.) |
| date | DATE | Observation date |
| frequency | VARCHAR(20) | monthly, annual |
| indicator_name | VARCHAR(200) | Original name |
| value | NUMERIC | Observed value |
| unit | VARCHAR(20) | Unit (percent) |
| evidence_classification | VARCHAR(50) | VERIFIED_PRIMARY, DERIVED |
| is_observed | BOOLEAN | Directly observed |
| is_derived | BOOLEAN | Computed |
| transformation_notes | TEXT | Coverage notes, formula |
| n_observations | INTEGER | Number of source observations (for derived) |
| retrieval_date | DATE | When data was retrieved |

### mart.fact_macro_indicators
Same structure as fact_interest_rates, with source_id = 'WB-MACRO-001' and evidence_classification = 'VERIFIED_SECONDARY'.

### mart.fact_banking_sector
| Column | Type | Description |
|--------|------|-------------|
| source_id | VARCHAR(50) FK | Source reference |
| indicator_id | VARCHAR(100) | Indicator code |
| date | DATE | Observation date |
| value | NUMERIC | Observed value |
| unit | VARCHAR(50) | Unit |
| currency | VARCHAR(20) | Currency (FRW) |

## Standardized Indicator Codes

| Code | Name | Source | Frequency |
|------|------|--------|-----------|
| CBR | Central Bank Rate / Key Repo Rate | BNR | Monthly |
| DEPOSIT_RATE | Deposit Rate | BNR | Monthly |
| LENDING_RATE | Lending Rate | BNR | Monthly |
| INTERBANK_RATE | Interbank Rate | BNR | Monthly |
| REPO_RATE | Repo Rate | BNR | Monthly |
| REVERSE_REPO_RATE | Reverse Repo Rate | BNR | Monthly |
| RESERVE_REQUIREMENT | Reserve Requirement | BNR | Monthly |
| STANDING_LENDING_FACILITY | Standing Lending Facility | BNR | Monthly |
| STANDING_DEPOSIT_FACILITY | Standing Deposit Facility | BNR | Monthly |
| OVERNIGHT_DEPOSIT_FACILITY | Overnight Deposit Facility | BNR | Monthly |
| REFINANCING_FACILITY | Refinancing Facility | BNR | Monthly |
| DISCOUNT_RATE | Discount Rate | BNR | Monthly |
| INFLATION_YOY | Inflation (annual %) | World Bank | Annual |
| GDP_GROWTH | GDP growth (annual %) | World Bank | Annual |
| GDP_USD | GDP (current US$) | World Bank | Annual |
| EXCHANGE_RATE_USD | Exchange rate (LCU per US$) | World Bank | Annual |
| REAL_INTEREST_RATE | Real interest rate (%) | World Bank | Annual |
| WB_LENDING_RATE | Lending interest rate (%) | World Bank | Annual |
| WB_DEPOSIT_RATE | Deposit interest rate (%) | World Bank | Annual |
| DOMESTIC_CREDIT_PRIVATE_GDP | Domestic credit to private sector (% GDP) | World Bank | Annual |

## Ingestion Status

| Status | Description | Sources |
|--------|-------------|---------|
| INGESTED_AUTOMATED | Pipeline fetches and parses automatically | BNR-IRS-001, WB-MACRO-001 |
| CATALOGED_PENDING_EXTRACTION | Source identified, extraction not yet implemented | BNR-FSS, BNR-MPFSS, BNR-FX, NISR-GDP, BNR-CPI, IMF-MACRO |
| MANUAL_EXTRACTION_REQUIRED | Requires manual PDF extraction | BANK-IMR-001, BANK-BK-001 |
