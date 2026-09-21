# License

## Source Data Licensing

### World Bank — World Development Indicators
- License: CC BY-4.0 (Creative Commons Attribution 4.0)
- Redistribution: Permitted with attribution
- URL: https://data.worldbank.org
- Note: Treated as VERIFIED_SECONDARY in the warehouse

### National Bank of Rwanda (BNR)
- License: Publicly accessible; redistribution status unclear
- Redistribution: Not committed to repository
- URL: https://www.bnr.rw
- Sources: Interest Rate Structure, Financial Sector Statistics, MPFSS, Exchange Rates, CPI

### National Institute of Statistics of Rwanda (NISR)
- License: Publicly accessible; redistribution status unclear
- Redistribution: Not committed to repository
- URL: https://statistics.gov.rw

### IMF DataMapper
- License: Publicly accessible; redistribution status unclear
- URL: https://www.imf.org/external/datamapper

### Bank Disclosures (I&M Bank Rwanda, Bank of Kigali)
- License: Individual bank terms
- Redistribution: Not committed to repository

## Code License

The pipeline code, SQL schemas, documentation, and configuration files in this repository are the original work of the project author. No third-party code is redistributed.

## Raw Data Policy

Raw data files (BNR XLS, World Bank JSON, bank PDFs) are NOT committed to this repository because:
1. BNR/NISR redistribution status is unclear
2. Bank disclosures are subject to individual bank terms
3. World Bank data, while CC BY-4.0, is regenerated on each pipeline run

The pipeline fetches raw data live from authoritative sources during execution.
