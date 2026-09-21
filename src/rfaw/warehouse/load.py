"""Load transformed data into warehouse mart tables."""
import pandas as pd
from sqlalchemy import text
from .db import get_engine


def load_interest_rates(df: pd.DataFrame):
    """Load interest rate observations into mart.fact_interest_rates."""
    engine = get_engine()
    df.to_sql("fact_interest_rates", engine, schema="mart", if_exists="append", index=False)
    print(f"Loaded {len(df)} interest rate observations into mart.fact_interest_rates")


def load_macro_indicators(df: pd.DataFrame):
    """Load macro indicator observations into mart.fact_macro_indicators."""
    engine = get_engine()
    df.to_sql("fact_macro_indicators", engine, schema="mart", if_exists="append", index=False)
    print(f"Loaded {len(df)} macro indicator observations into mart.fact_macro_indicators")


def load_banking_sector(df: pd.DataFrame):
    """Load banking sector aggregates into mart.fact_banking_sector."""
    engine = get_engine()
    df.to_sql("fact_banking_sector", engine, schema="mart", if_exists="append", index=False)
    print(f"Loaded {len(df)} banking sector observations into mart.fact_banking_sector")


def load_exchange_rates(df: pd.DataFrame):
    """Load exchange rate observations into mart.fact_exchange_rates."""
    engine = get_engine()
    df.to_sql("fact_exchange_rates", engine, schema="mart", if_exists="append", index=False)
    print(f"Loaded {len(df)} exchange rate observations into mart.fact_exchange_rates")
