"""Compute derived financial metrics from observed data.

All derived metrics are labeled DERIVED with explicit formula documentation.
"""
import pandas as pd
from datetime import date


def compute_lending_deposit_spread(ir_monthly: pd.DataFrame) -> pd.DataFrame:
    """Compute lending-deposit spread from monthly observations.
    
    Formula: LENDING_RATE - DEPOSIT_RATE
    """
    lending = ir_monthly[ir_monthly["indicator_id"] == "LENDING_RATE"][["date", "value"]].rename(
        columns={"value": "lending_rate"}
    )
    deposit = ir_monthly[ir_monthly["indicator_id"] == "DEPOSIT_RATE"][["date", "value"]].rename(
        columns={"value": "deposit_rate"}
    )
    
    merged = pd.merge(lending, deposit, on="date", how="inner")
    merged["value"] = merged["lending_rate"] - merged["deposit_rate"]
    
    records = []
    for _, row in merged.iterrows():
        records.append({
            "source_id": "DERIVED-001",
            "indicator_id": "LENDING_DEPOSIT_SPREAD",
            "date": row["date"],
            "frequency": "monthly",
            "indicator_name": "Lending-Deposit Spread",
            "value": round(float(row["value"]), 4),
            "unit": "percentage_points",
            "evidence_classification": "DERIVED",
            "is_observed": False,
            "is_derived": True,
            "transformation_notes": "Formula: LENDING_RATE - DEPOSIT_RATE. Inputs: BNR-IRS-001.",
            "retrieval_date": date.today().isoformat(),
        })
    return pd.DataFrame(records)


def compute_rate_vs_cbr(ir_monthly: pd.DataFrame, rate_indicator: str, output_id: str, output_name: str) -> pd.DataFrame:
    """Compute difference between a market rate and the CBR.
    
    Formula: {rate_indicator} - CBR
    """
    rate = ir_monthly[ir_monthly["indicator_id"] == rate_indicator][["date", "value"]].rename(
        columns={"value": "market_rate"}
    )
    cbr = ir_monthly[ir_monthly["indicator_id"] == "CBR"][["date", "value"]].rename(
        columns={"value": "cbr"}
    )
    
    merged = pd.merge(rate, cbr, on="date", how="inner")
    merged["value"] = merged["market_rate"] - merged["cbr"]
    
    records = []
    for _, row in merged.iterrows():
        records.append({
            "source_id": "DERIVED-001",
            "indicator_id": output_id,
            "date": row["date"],
            "frequency": "monthly",
            "indicator_name": output_name,
            "value": round(float(row["value"]), 4),
            "unit": "percentage_points",
            "evidence_classification": "DERIVED",
            "is_observed": False,
            "is_derived": True,
            "transformation_notes": f"Formula: {rate_indicator} - CBR. Inputs: BNR-IRS-001.",
            "retrieval_date": date.today().isoformat(),
        })
    return pd.DataFrame(records)


def compute_real_rates(ir_annual: pd.DataFrame, macro: pd.DataFrame, rate_indicator: str, output_id: str, output_name: str) -> pd.DataFrame:
    """Compute real interest rate using Fisher equation approximation.
    
    Formula: nominal_rate - inflation_rate
    """
    rate = ir_annual[ir_annual["indicator_id"] == rate_indicator][["date", "value"]].rename(
        columns={"value": "nominal_rate"}
    )
    inflation = macro[macro["indicator_id"] == "INFLATION_YOY"][["date", "value"]].rename(
        columns={"value": "inflation"}
    )
    
    merged = pd.merge(rate, inflation, on="date", how="inner")
    merged["value"] = merged["nominal_rate"] - merged["inflation"]
    
    records = []
    for _, row in merged.iterrows():
        records.append({
            "source_id": "DERIVED-001",
            "indicator_id": output_id,
            "date": row["date"],
            "frequency": "annual",
            "indicator_name": output_name,
            "value": round(float(row["value"]), 4),
            "unit": "percent",
            "evidence_classification": "DERIVED",
            "is_observed": False,
            "is_derived": True,
            "transformation_notes": f"Formula: {rate_indicator} - INFLATION_YOY (Fisher approximation). Inputs: BNR-IRS-001, WB-MACRO-001.",
            "retrieval_date": date.today().isoformat(),
        })
    return pd.DataFrame(records)


def compute_fx_depreciation(macro: pd.DataFrame) -> pd.DataFrame:
    """Compute annual FX depreciation rate.
    
    Formula: (FX_t / FX_t-1 - 1) * 100
    """
    fx = macro[macro["indicator_id"] == "EXCHANGE_RATE_USD"][["date", "value"]].sort_values("date").reset_index(drop=True)
    
    records = []
    for i in range(1, len(fx)):
        prev_fx = fx.iloc[i-1]["value"]
        curr_fx = fx.iloc[i]["value"]
        if prev_fx > 0:
            depreciation = ((curr_fx / prev_fx) - 1) * 100
            records.append({
                "source_id": "DERIVED-001",
                "indicator_id": "FX_DEPRECIATION",
                "date": fx.iloc[i]["date"],
                "frequency": "annual",
                "indicator_name": "RWF Depreciation vs USD (annual %)",
                "value": round(float(depreciation), 4),
                "unit": "percent",
                "evidence_classification": "DERIVED",
                "is_observed": False,
                "is_derived": True,
                "transformation_notes": "Formula: (FX_t / FX_t-1 - 1) * 100. Inputs: WB-MACRO-001 (PA.NUS.FCRF).",
                "retrieval_date": date.today().isoformat(),
            })
    return pd.DataFrame(records)


def compute_npl_change(banking: pd.DataFrame) -> pd.DataFrame:
    """Compute year-over-year NPL ratio change.
    
    Formula: NPL_t - NPL_t-1
    """
    npl = banking[banking["indicator_id"] == "NPL_RATIO"][["date", "value"]].sort_values("date").reset_index(drop=True)
    
    records = []
    for i in range(1, len(npl)):
        change = npl.iloc[i]["value"] - npl.iloc[i-1]["value"]
        records.append({
            "source_id": "DERIVED-001",
            "indicator_id": "NPL_CHANGE_YOY",
            "date": npl.iloc[i]["date"],
            "frequency": "annual",
            "indicator_name": "NPL Ratio Change (YoY, pp)",
            "value": round(float(change), 4),
            "unit": "percentage_points",
            "evidence_classification": "DERIVED",
            "is_observed": False,
            "is_derived": True,
            "transformation_notes": "Formula: NPL_t - NPL_t-1. Inputs: BNR-MPFSS-001.",
            "retrieval_date": date.today().isoformat(),
        })
    return pd.DataFrame(records)


def compute_all_derived_metrics(ir_monthly: pd.DataFrame, ir_annual: pd.DataFrame, 
                                 macro: pd.DataFrame, banking: pd.DataFrame) -> pd.DataFrame:
    """Compute all derived financial metrics."""
    all_metrics = []
    
    # Lending-deposit spread (monthly)
    spread = compute_lending_deposit_spread(ir_monthly)
    if not spread.empty:
        all_metrics.append(spread)
    
    # Lending rate minus CBR (monthly)
    lending_vs_cbr = compute_rate_vs_cbr(ir_monthly, "LENDING_RATE", "LENDING_VS_CBR", "Lending Rate minus CBR")
    if not lending_vs_cbr.empty:
        all_metrics.append(lending_vs_cbr)
    
    # Deposit rate minus CBR (monthly)
    deposit_vs_cbr = compute_rate_vs_cbr(ir_monthly, "DEPOSIT_RATE", "DEPOSIT_VS_CBR", "Deposit Rate minus CBR")
    if not deposit_vs_cbr.empty:
        all_metrics.append(deposit_vs_cbr)
    
    # Real lending rate (annual, Fisher approximation)
    real_lending = compute_real_rates(ir_annual, macro, "LENDING_RATE", "REAL_LENDING_RATE", "Real Lending Rate (Fisher approx.)")
    if not real_lending.empty:
        all_metrics.append(real_lending)
    
    # Real deposit rate (annual, Fisher approximation)
    real_deposit = compute_real_rates(ir_annual, macro, "DEPOSIT_RATE", "REAL_DEPOSIT_RATE", "Real Deposit Rate (Fisher approx.)")
    if not real_deposit.empty:
        all_metrics.append(real_deposit)
    
    # FX depreciation (annual)
    fx_dep = compute_fx_depreciation(macro)
    if not fx_dep.empty:
        all_metrics.append(fx_dep)
    
    # NPL change YoY (annual)
    if not banking.empty:
        npl_change = compute_npl_change(banking)
        if not npl_change.empty:
            all_metrics.append(npl_change)
    
    if not all_metrics:
        return pd.DataFrame()
    
    result = pd.concat(all_metrics, ignore_index=True)
    result = result.drop_duplicates(subset=["source_id", "indicator_id", "date", "frequency"])
    return result
