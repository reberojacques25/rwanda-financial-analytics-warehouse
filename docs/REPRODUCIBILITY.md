# Reproducibility Guide

## Prerequisites

- Python 3.9+
- PostgreSQL 13+ (optional for warehouse mode; pipeline works without DB)
- pip install -r requirements.txt

## Running the Pipeline

```bash
# 1. (Optional) Initialize PostgreSQL database
cp .env.example .env  # Edit with your DB credentials
python scripts/init_db.py

# 2. Run the data pipeline (ingests BNR + World Bank data)
python scripts/run_pipeline.py

# 3. Run validation
python scripts/run_validation.py

# 4. Run tests
pytest tests/ -v

# 5. Launch dashboard
streamlit run dashboard/app.py
```

## Expected Output

- BNR Interest Rates: ~200+ monthly observations (2002-2025)
- World Bank Macro: ~100+ annual observations (2000-2024)
- Source catalog: 10 sources with full provenance
- All validation checks pass

## Data Provenance

Every observation in the warehouse carries:
- source_id: links to metadata.sources
- retrieval_date: when the data was fetched
- evidence_classification: VERIFIED_PRIMARY or VERIFIED_SECONDARY
- is_observed / is_derived: distinguishes observed from computed values

## Without PostgreSQL

The pipeline saves processed data to `data/processed/` as CSV files. The Streamlit dashboard reads from these files if PostgreSQL is not available.
