"""Generate opportunity intelligence signals from financial data.

Signals are evidence-based observations, not causal claims.
Each signal includes metric references, dates, and limitations.
"""
import pandas as pd
from datetime import date


def generate_signals(ir_annual: pd.DataFrame, macro: pd.DataFrame, 
                      banking: pd.DataFrame, derived: pd.DataFrame) -> pd.DataFrame:
    """Generate opportunity intelligence signals from observed and derived data."""
    signals = []
    retrieval_date = date.today().isoformat()
    
    # 1. High real lending rate signal
    if not derived.empty:
        real_lending = derived[derived["indicator_id"] == "REAL_LENDING_RATE"]
        if not real_lending.empty:
            latest = real_lending.sort_values("date").iloc[-1]
            if latest["value"] > 5.0:
                signals.append({
                    "signal_id": "SIG_001",
                    "signal_type": "HIGH_REAL_LENDING_RATE",
                    "date": latest["date"],
                    "description": f"Real lending rate is {latest['value']:.1f}%, indicating tight monetary conditions",
                    "metric_value": float(latest["value"]),
                    "metric_unit": "percent",
                    "threshold": "> 5%",
                    "evidence_classification": "DERIVED",
                    "input_indicators": "REAL_LENDING_RATE",
                    "input_sources": "BNR-IRS-001, WB-MACRO-001",
                    "limitations": "Fisher approximation; does not account for inflation expectations or tax effects",
                    "opportunity_note": "High real rates may indicate limited credit access and potential for financial product innovation",
                    "retrieval_date": retrieval_date,
                })
    
    # 2. Widening lending-deposit spread
    if not derived.empty:
        spread = derived[derived["indicator_id"] == "LENDING_DEPOSIT_SPREAD"]
        if not spread.empty and len(spread) >= 2:
            spread_sorted = spread.sort_values("date")
            recent_avg = spread_sorted.tail(12)["value"].mean()
            older_avg = spread_sorted.head(12)["value"].mean()
            if recent_avg > older_avg:
                signals.append({
                    "signal_id": "SIG_002",
                    "signal_type": "WIDENING_SPREAD",
                    "date": spread_sorted.iloc[-1]["date"],
                    "description": f"Lending-deposit spread has widened from {older_avg:.1f}pp to {recent_avg:.1f}pp",
                    "metric_value": round(float(recent_avg - older_avg), 2),
                    "metric_unit": "percentage_points_change",
                    "threshold": "recent > historical",
                    "evidence_classification": "DERIVED",
                    "input_indicators": "LENDING_DEPOSIT_SPREAD",
                    "input_sources": "BNR-IRS-001",
                    "limitations": "Comparison based on first 12 vs last 12 observations; may not capture cyclical patterns",
                    "opportunity_note": "Widening spread may indicate inefficiency in financial intermediation or increased risk pricing",
                    "retrieval_date": retrieval_date,
                })
    
    # 3. NPL ratio trend
    if not banking.empty:
        npl = banking[banking["indicator_id"] == "NPL_RATIO"].sort_values("date")
        if not npl.empty:
            latest_npl = npl.iloc[-1]
            prev_npl = npl.iloc[-2] if len(npl) >= 2 else None
            if prev_npl is not None:
                change = latest_npl["value"] - prev_npl["value"]
                if change > 0:
                    signals.append({
                        "signal_id": "SIG_003",
                        "signal_type": "RISING_NPL",
                        "date": latest_npl["date"],
                        "description": f"NPL ratio increased from {prev_npl['value']:.1f}% to {latest_npl['value']:.1f}%",
                        "metric_value": round(float(change), 2),
                        "metric_unit": "percentage_points",
                        "threshold": "YoY increase",
                        "evidence_classification": "VERIFIED_PRIMARY",
                        "input_indicators": "NPL_RATIO",
                        "input_sources": "BNR-MPFSS-001",
                        "limitations": "Aggregate banking sector only; does not reflect individual bank conditions",
                        "opportunity_note": "Rising NPLs may signal need for credit risk management services and distressed asset resolution",
                        "retrieval_date": retrieval_date,
                    })
    
    # 4. FX depreciation pressure
    if not derived.empty:
        fx_dep = derived[derived["indicator_id"] == "FX_DEPRECIATION"]
        if not fx_dep.empty:
            latest_fx = fx_dep.sort_values("date").iloc[-1]
            if latest_fx["value"] > 5.0:
                signals.append({
                    "signal_id": "SIG_004",
                    "signal_type": "FX_DEPRECIATION_PRESSURE",
                    "date": latest_fx["date"],
                    "description": f"RWF depreciated {latest_fx['value']:.1f}% against USD",
                    "metric_value": float(latest_fx["value"]),
                    "metric_unit": "percent",
                    "threshold": "> 5%",
                    "evidence_classification": "DERIVED",
                    "input_indicators": "EXCHANGE_RATE_USD",
                    "input_sources": "WB-MACRO-001",
                    "limitations": "Based on official exchange rate; parallel market rates may differ",
                    "opportunity_note": "FX pressure may create demand for hedging products and local-currency lending solutions",
                    "retrieval_date": retrieval_date,
                })
    
    # 5. GDP growth momentum
    if not macro.empty:
        gdp = macro[macro["indicator_id"] == "GDP_GROWTH"].sort_values("date")
        if not gdp.empty and len(gdp) >= 2:
            latest_gdp = gdp.iloc[-1]
            prev_gdp = gdp.iloc[-2]
            if latest_gdp["value"] > prev_gdp["value"]:
                signals.append({
                    "signal_id": "SIG_005",
                    "signal_type": "GDP_ACCELERATION",
                    "date": latest_gdp["date"],
                    "description": f"GDP growth accelerated from {prev_gdp['value']:.1f}% to {latest_gdp['value']:.1f}%",
                    "metric_value": round(float(latest_gdp["value"] - prev_gdp["value"]), 2),
                    "metric_unit": "percentage_points",
                    "threshold": "YoY acceleration",
                    "evidence_classification": "VERIFIED_SECONDARY",
                    "input_indicators": "GDP_GROWTH",
                    "input_sources": "WB-MACRO-001",
                    "limitations": "World Bank data is secondary; NISR primary data may differ slightly",
                    "opportunity_note": "GDP acceleration may signal expanding credit demand and investment opportunities",
                    "retrieval_date": retrieval_date,
                })
    
    # 6. Credit to private sector trend
    if not macro.empty:
        credit = macro[macro["indicator_id"] == "DOMESTIC_CREDIT_PRIVATE_GDP"].sort_values("date")
        if not credit.empty and len(credit) >= 2:
            latest_credit = credit.iloc[-1]
            prev_credit = credit.iloc[-2]
            if latest_credit["value"] > prev_credit["value"]:
                signals.append({
                    "signal_id": "SIG_006",
                    "signal_type": "CREDIT_EXPANSION",
                    "date": latest_credit["date"],
                    "description": f"Domestic credit to private sector increased to {latest_credit['value']:.1f}% of GDP",
                    "metric_value": round(float(latest_credit["value"] - prev_credit["value"]), 2),
                    "metric_unit": "percentage_points",
                    "threshold": "YoY increase",
                    "evidence_classification": "VERIFIED_SECONDARY",
                    "input_indicators": "DOMESTIC_CREDIT_PRIVATE_GDP",
                    "input_sources": "WB-MACRO-001",
                    "limitations": "Aggregate metric; does not capture sectoral or bank-level credit distribution",
                    "opportunity_note": "Credit expansion may indicate growing financial intermediation and need for risk management tools",
                    "retrieval_date": retrieval_date,
                })
    
    return pd.DataFrame(signals)
