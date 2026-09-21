"""Transform World Bank raw macro data into warehouse-ready fact table."""
import pandas as pd
from datetime import date


INDICATOR_MAP = {
    "FP.CPI.TOTL.ZG": ("INFLATION_YOY", "Inflation, consumer prices (annual %)"),
    "NY.GDP.MKTP.CD": ("GDP_USD", "GDP (current US$)"),
    "NY.GDP.MKTP.KD.ZG": ("GDP_GROWTH", "GDP growth (annual %)"),
    "FR.INR.RINR": ("REAL_INTEREST_RATE", "Real interest rate (%)"),
    "FR.INR.LEND": ("WB_LENDING_RATE", "Lending interest rate (%)"),
    "FR.INR.DPST": ("WB_DEPOSIT_RATE", "Deposit interest rate (%)"),
    "PA.NUS.FCRF": ("EXCHANGE_RATE_USD", "Official exchange rate (LCU per US$)"),
    "FM.LD.BOP.ZG": ("BROAD_MONEY_GROWTH", "Broad money growth (annual %)"),
    "FS.AST.PRVT.GD.ZS": ("DOMESTIC_CREDIT_PRIVATE_GDP", "Domestic credit to private sector (% GDP)"),
    "GF.DD.AI.01": ("NPL_RATIO_WB", "Bank nonperforming loans to total gross loans (%)"),
}


def transform_macro_indicators(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Transform World Bank raw data into mart.fact_macro_indicators format."""
    if raw_df.empty:
        return pd.DataFrame()

    records = []
    for _, row in raw_df.iterrows():
        code = str(row.get("indicator_code", ""))
        if code not in INDICATOR_MAP:
            continue

        indicator_id, indicator_name = INDICATOR_MAP[code]
        year = int(row.get("year", 0))

        records.append({
            "source_id": "WB-MACRO-001",
            "indicator_id": indicator_id,
            "date": pd.Timestamp(year=year, month=12, day=31),
            "frequency": "annual",
            "indicator_name": indicator_name,
            "value": float(row.get("value", 0)),
            "unit": row.get("unit", ""),
            "evidence_classification": "VERIFIED_SECONDARY",
            "is_observed": True,
            "is_derived": False,
            "transformation_notes": None,
            "retrieval_date": row.get("retrieval_date", date.today().isoformat()),
        })

    result = pd.DataFrame(records)
    result = result.drop_duplicates(subset=["source_id", "indicator_id", "date", "frequency"])
    return result
