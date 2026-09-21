# Validation

## Automated Checks

### 1. Source Catalog Validation (`validate_source_catalog`)
- YAML schema: all required fields present
- Evidence classifications: must be from allowed list (VERIFIED_PRIMARY, VERIFIED_SECONDARY, DERIVED, ESTIMATED, UNVERIFIED)
- is_observed must not be True when is_derived is True
- At least one VERIFIED_PRIMARY source
- Every source has a URL

### 2. Interest Rate Validation (`validate_interest_rates`)
- Required fields: source_id, indicator_id, date, value, evidence_classification
- Range check: values in [-50, 200] range
- Duplicate detection: no duplicate (source_id, indicator_id, date, frequency) combinations
- Evidence classification: must be VERIFIED_PRIMARY for monthly, DERIVED for annual averages

### 3. Macro Indicator Validation (`validate_macro_indicators`)
- Required fields: source_id, indicator_id, date, value
- Non-empty DataFrame check
- Evidence classification must be VERIFIED_SECONDARY

### 4. Security Validation (`check_no_secrets`)
- Scans all tracked files for credential patterns
- Patterns: GitHub PATs, API keys, passwords, bearer tokens
- Excludes test files and security check source code
- Fails on any match

### 5. Git Hygiene
- Raw data files not tracked
- No secrets in git config
- .gitignore blocks .env, credentials, raw data

## Running Validation

```bash
# Full pipeline with validation
python scripts/run_pipeline.py

# Standalone validation
python scripts/run_validation.py

# Test suite
pytest tests/ -v
```

## Current Validation Results

- Source catalog: OK
- Interest rates (1,801 monthly): OK
- Macro indicators (205 annual): OK
- Annual averages (191 derived): OK with coverage flags
- Security: OK (no secrets detected)
- Tests: 15/15 passing
