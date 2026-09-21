"""Load transformed data into warehouse mart tables."""
import pandas as pd
from sqlalchemy import text
from .db import get_engine


def _truncate_and_load(df: pd.DataFrame, table_name: str, schema: str = "mart"):
    """Truncate existing data and load new records (idempotent reload)."""
    engine = get_engine()
    # Get the actual column names from the database table
    with engine.connect() as conn:
        conn.execute(text(f"TRUNCATE TABLE {schema}.{table_name} RESTART IDENTITY CASCADE"))
        conn.commit()
        # Get valid columns for this table
        result = conn.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = :schema AND table_name = :table"
        ), {"schema": schema, "table": table_name})
        db_cols = {row[0] for row in result}
    # Only keep columns that exist in the database table (exclude 'id' which is auto-generated)
    db_cols.discard("id")
    available_cols = [c for c in df.columns if c in db_cols]
    df_to_load = df[available_cols]
    df_to_load.to_sql(table_name, engine, schema=schema, if_exists="append", index=False)
    print(f"  Loaded {len(df_to_load)} records into {schema}.{table_name}")


def load_interest_rates(df: pd.DataFrame):
    """Load interest rate observations into mart.fact_interest_rates."""
    _truncate_and_load(df, "fact_interest_rates")


def load_macro_indicators(df: pd.DataFrame):
    """Load macro indicator observations into mart.fact_macro_indicators."""
    _truncate_and_load(df, "fact_macro_indicators")


def load_banking_sector(df: pd.DataFrame):
    """Load banking sector aggregates into mart.fact_banking_sector."""
    _truncate_and_load(df, "fact_banking_sector")


def load_derived_metrics(df: pd.DataFrame):
    """Load derived financial metrics into mart.fact_derived_metrics."""
    _truncate_and_load(df, "fact_derived_metrics")


def load_exchange_rates(df: pd.DataFrame):
    """Load exchange rate observations into mart.fact_exchange_rates."""
    _truncate_and_load(df, "fact_exchange_rates")


def load_sources(catalog: dict):
    """Load source catalog into metadata.sources table."""
    engine = get_engine()
    sources = catalog.get("sources", [])
    if not sources:
        return
    with engine.connect() as conn:
        conn.execute(text("TRUNCATE TABLE metadata.sources CASCADE"))
        conn.commit()
    df = pd.DataFrame(sources)
    # Only keep columns that exist in the metadata.sources table
    valid_cols = [
        "source_id", "source_name", "source_organization", "source_type",
        "source_url", "source_format", "date_coverage", "geographic_coverage",
        "evidence_classification", "is_observed", "is_derived",
        "ingestion_status", "license", "retrieval_date", "is_active",
        "variables", "access_type", "api_access", "registration_required",
        "approximate_size", "last_update_date", "actively_maintained",
        "intended_use", "limitations", "redistribution_status",
        "historical_completeness", "transformations_applied",
        "methodology_notes", "source_reliability", "source_accessibility",
    ]
    available_cols = [c for c in valid_cols if c in df.columns]
    df = df[available_cols]
    df.to_sql("sources", engine, schema="metadata", if_exists="append", index=False)
    print(f"  Loaded {len(df)} sources into metadata.sources")


def load_all(interest_rates: pd.DataFrame = None, macro_indicators: pd.DataFrame = None,
             derived_metrics: pd.DataFrame = None, banking_sector: pd.DataFrame = None,
             source_catalog: dict = None):
    """Load all available data into the warehouse."""
    print("Loading data into PostgreSQL warehouse...")
    if source_catalog:
        load_sources(source_catalog)
    if interest_rates is not None and not interest_rates.empty:
        load_interest_rates(interest_rates)
    if macro_indicators is not None and not macro_indicators.empty:
        load_macro_indicators(macro_indicators)
    if derived_metrics is not None and not derived_metrics.empty:
        load_derived_metrics(derived_metrics)
    if banking_sector is not None and not banking_sector.empty:
        load_banking_sector(banking_sector)
    print("Warehouse loading complete.")


def get_warehouse_summary() -> dict:
    """Get row counts for all mart and metadata tables."""
    engine = get_engine()
    tables = [
        ("metadata", "sources"),
        ("mart", "fact_interest_rates"),
        ("mart", "fact_macro_indicators"),
        ("mart", "fact_derived_metrics"),
        ("mart", "fact_banking_sector"),
        ("mart", "fact_exchange_rates"),
    ]
    summary = {}
    with engine.connect() as conn:
        for schema, table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {schema}.{table}"))
                count = result.scalar()
                summary[f"{schema}.{table}"] = count
            except Exception:
                summary[f"{schema}.{table}"] = 0
    return summary
