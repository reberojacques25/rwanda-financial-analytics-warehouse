"""Run the full RFAW data pipeline: ingest → transform → load → validate."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rfaw.ingest.world_bank import ingest_world_bank
from rfaw.ingest.bnr_interest_rates import ingest_bnr_interest_rates
from rfaw.transform.interest_rates import transform_interest_rates, compute_annual_averages
from rfaw.transform.macro_indicators import transform_macro_indicators
from rfaw.validation.checks import (
    validate_source_catalog, validate_interest_rates,
    validate_macro_indicators, check_no_secrets
)
import pandas as pd


def run_pipeline():
    print("=" * 60)
    print("RFAW Data Pipeline")
    print("=" * 60)

    # Step 0: Validate source catalog
    print("\n[0/5] Validating source catalog...")
    catalog_errors = validate_source_catalog()
    if catalog_errors:
        print(f"  FAIL: {len(catalog_errors)} errors")
        for e in catalog_errors:
            print(f"    - {e}")
    else:
        print("  OK: Source catalog valid")

    # Step 1: Ingest World Bank data
    print("\n[1/5] Ingesting World Bank macro indicators...")
    try:
        wb_raw = ingest_world_bank()
        print(f"  OK: {len(wb_raw)} raw records ingested")
    except Exception as e:
        print(f"  WARNING: World Bank ingestion failed: {e}")
        wb_raw = pd.DataFrame()

    # Step 2: Ingest BNR interest rates
    print("\n[2/5] Ingesting BNR interest rates...")
    try:
        bnr_raw = ingest_bnr_interest_rates()
        print(f"  OK: {len(bnr_raw)} raw records ingested")
    except Exception as e:
        print(f"  WARNING: BNR ingestion failed: {e}")
        bnr_raw = pd.DataFrame()

    # Step 3: Transform
    print("\n[3/5] Transforming data...")
    interest_rates_monthly = transform_interest_rates(bnr_raw)
    interest_rates_annual = compute_annual_averages(interest_rates_monthly)
    macro_indicators = transform_macro_indicators(wb_raw)

    print(f"  Interest rates (monthly): {len(interest_rates_monthly)} observations")
    print(f"  Interest rates (annual avg, derived): {len(interest_rates_annual)} observations")
    print(f"  Macro indicators: {len(macro_indicators)} observations")

    # Save processed data locally (for dashboard use without DB)
    from rfaw.config import PROCESSED_DIR
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if not interest_rates_monthly.empty:
        interest_rates_monthly.to_csv(PROCESSED_DIR / "interest_rates_monthly.csv", index=False)
    if not interest_rates_annual.empty:
        interest_rates_annual.to_csv(PROCESSED_DIR / "interest_rates_annual.csv", index=False)
    if not macro_indicators.empty:
        macro_indicators.to_csv(PROCESSED_DIR / "macro_indicators.csv", index=False)

    # Step 4: Validate transformed data
    print("\n[4/5] Validating transformed data...")
    ir_errors = validate_interest_rates(interest_rates_monthly)
    macro_errors = validate_macro_indicators(macro_indicators)

    if ir_errors:
        print(f"  Interest rates: {len(ir_errors)} validation issues")
        for e in ir_errors[:5]:
            print(f"    - {e}")
    else:
        print(f"  Interest rates: OK ({len(interest_rates_monthly)} records)")

    if macro_errors:
        print(f"  Macro indicators: {len(macro_errors)} validation issues")
        for e in macro_errors[:5]:
            print(f"    - {e}")
    else:
        print(f"  Macro indicators: OK ({len(macro_indicators)} records)")

    # Step 5: Security check
    print("\n[5/5] Security check...")
    secret_errors = check_no_secrets(".")
    if secret_errors:
        print(f"  FAIL: {len(secret_errors)} security issues")
        for e in secret_errors:
            print(f"    - {e}")
    else:
        print("  OK: No secrets detected")

    # Summary
    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    print(f"  World Bank records: {len(wb_raw)}")
    print(f"  BNR interest rate records: {len(bnr_raw)}")
    print(f"  Transformed interest rates (monthly): {len(interest_rates_monthly)}")
    print(f"  Transformed interest rates (annual): {len(interest_rates_annual)}")
    print(f"  Transformed macro indicators: {len(macro_indicators)}")
    print(f"  Validation errors: {len(ir_errors) + len(macro_errors)}")
    print(f"  Security issues: {len(secret_errors)}")
    print()

    return {
        "wb_raw": wb_raw,
        "bnr_raw": bnr_raw,
        "interest_rates_monthly": interest_rates_monthly,
        "interest_rates_annual": interest_rates_annual,
        "macro_indicators": macro_indicators,
    }


if __name__ == "__main__":
    run_pipeline()
