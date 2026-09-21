# Methodology

## Evidence-First Approach

1. **Source verification**: Every dataset is documented with source URL, retrieval date, and evidence classification
2. **No fabrication**: Missing data is marked as missing; no interpolation or estimation
3. **Observed vs. Derived**: Clear boolean flags distinguish observed values from computed metrics
4. **Provenance tracking**: Every observation carries source_id and retrieval_date

## Data Pipeline

1. **Ingestion**: Download/fetch data from authoritative sources (BNR XLS, World Bank API)
2. **Staging**: Store raw data in staging tables
3. **Transformation**: Clean, normalize, and map to standard indicators
4. **Loading**: Insert into analytical mart tables
5. **Validation**: Run automated quality checks on transformed data

## Frequency Strategy

- **Monthly layer**: BNR interest rates (2002-2025)
- **Annual layer**: World Bank macro indicators (2000-2024)
- Do NOT mix frequencies without documented aggregation rules
- Annual averages from monthly data are labeled as DERIVED

## Validation Rules

- Schema validation: required fields, data types
- Range checks: interest rates in [-50, 200] range
- Duplicate detection: no duplicate (source, indicator, date, frequency)
- Provenance: every observation has source_id and retrieval_date
- Evidence classification: must be from allowed list
- Security: no credentials in tracked files
