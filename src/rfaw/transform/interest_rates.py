"""Transform raw BNR interest rate data into warehouse-ready fact table."""
import pandas as pd
from datetime import date


INDICATOR_MAPPING = {
    "central bank rate": "CBR",
    "key repo rate": "CBR",
    "central bank rate (cbr)": "CBR",
    "deposit rate": "DEPOSIT_RATE",
    "lending rate": "LENDING_RATE",
    "interbank rate": "INTERBANK_RATE",
    "repo rate": "REPO_RATE",
    "reverse repo rate": "REVERSE_REPO_RATE",
    "reserve requirement": "RESERVE_REQUIREMENT",
    "treasury bill": "TBILL_RATE",
    "treasury bond": "TBOND_RATE",
}


def map_indicator(name: str) -> str:
    """Map BNR indicator names to standardized codes."""
    lower = name.lower().strip()
    for key, code in INDICATOR_MAPPING.items():
        if key in lower:
            return code
    return f"OTHER_{name.upper()[:30]}"


def transform_interest_rates(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Transform raw interest rate data into mart.fact_interest_rates format."""
    if raw_df.empty:
        return pd.DataFrame()

    records = []
    for _, row in raw_df.iterrows():
        indicator_id = map_indicator(str(row.get("indicator_name", "")))
        period = str(row.get("period_label", ""))

        try:
            year = int(row.get("year", 0))
            month = int(period.split("M")[1]) if "M" in period else 1
            obs_date = pd.Timestamp(year=year, month=month, day=15)
        except (ValueError, IndexError):
            continue

        value = row.get("indicator_value")
        if pd.isna(value):
            continue

        records.append({
            "source_id": "BNR-IRS-001",
            "indicator_id": indicator_id,
            "date": obs_date,
            "frequency": "monthly",
            "indicator_name": str(row.get("indicator_name", "")),
            "value": float(value),
            "unit": "percent",
            "evidence_classification": "VERIFIED_PRIMARY",
            "is_observed": True,
            "is_derived": False,
            "transformation_notes": None,
            "retrieval_date": row.get("retrieval_date", date.today().isoformat()),
        })

    result = pd.DataFrame(records)
    result = result.drop_duplicates(subset=["source_id", "indicator_id", "date", "frequency"])
    return result


def compute_annual_averages(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """Compute annual average rates from monthly observations. Clearly labeled as DERIVED."""
    if monthly_df.empty:
        return pd.DataFrame()

    monthly_df = monthly_df.copy()
    monthly_df["year"] = pd.to_datetime(monthly_df["date"]).dt.year

    annual = monthly_df.groupby(["indicator_id", "year"]).agg(
        value=("value", "mean"),
        indicator_name=("indicator_name", "first"),
        source_id=("source_id", "first"),
    ).reset_index()

    records = []
    for _, row in annual.iterrows():
        records.append({
            "source_id": row["source_id"],
            "indicator_id": row["indicator_id"],
            "date": pd.Timestamp(year=int(row["year"]), month=12, day=31),
            "frequency": "annual",
            "indicator_name": row["indicator_name"],
            "value": round(float(row["value"]), 4),
            "unit": "percent",
            "evidence_classification": "DERIVED",
            "is_observed": False,
            "is_derived": True,
            "transformation_notes": "Annual average computed from monthly observations",
            "retrieval_date": date.today().isoformat(),
        })

    return pd.DataFrame(records)
