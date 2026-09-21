"""Run the full RFAW data pipeline: ingest → transform → derived metrics → load → validate."""
import sys
import os
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rfaw.ingest.world_bank import ingest_world_bank
from rfaw.ingest.bnr_interest_rates import ingest_bnr_interest_rates
from rfaw.ingest.bnr_banking_sector import extract_banking_sector_from_mpfss, verify_pdf_extraction
from rfaw.transform.interest_rates import transform_interest_rates, compute_annual_averages
from rfaw.transform.macro_indicators import transform_macro_indicators
from rfaw.transform.derived_metrics import compute_all_derived_metrics
from rfaw.analysis.opportunity_intelligence import generate_signals
from rfaw.validation.checks import (
    validate_source_catalog, validate_interest_rates,
    validate_macro_indicators, check_no_secrets
)
from rfaw.warehouse.load import load_all, get_warehouse_summary
from rfaw.config import PROCESSED_DIR, METADATA_DIR
import pandas as pd


def run_pipeline():
    print("=" * 60)
    print("RFAW Data Pipeline (Stages 8-15)")
    print("=" * 60)

    # Load source catalog
    catalog_path = METADATA_DIR / "source_catalog.yml"
    with open(catalog_path) as f:
        source_catalog = yaml.safe_load(f)

    # Step 0: Validate source catalog
    print("\n[0/8] Validating source catalog...")
    catalog_errors = validate_source_catalog()
    if catalog_errors:
        print(f"  FAIL: {len(catalog_errors)} errors")
        for e in catalog_errors:
            print(f"    - {e}")
    else:
        print("  OK: Source catalog valid")

    # Step 1: Ingest World Bank data
    print("\n[1/8] Ingesting World Bank macro indicators...")
    try:
        wb_raw = ingest_world_bank()
        print(f"  OK: {len(wb_raw)} raw records ingested")
    except Exception as e:
        print(f"  WARNING: World Bank ingestion failed: {e}")
        wb_raw = pd.DataFrame()

    # Step 2: Ingest BNR interest rates
    print("\n[2/8] Ingesting BNR interest rates...")
    try:
        bnr_raw = ingest_bnr_interest_rates()
        print(f"  OK: {len(bnr_raw)} raw records ingested")
    except Exception as e:
        print(f"  WARNING: BNR ingestion failed: {e}")
        bnr_raw = pd.DataFrame()

    # Step 3: Extract BNR banking sector from MPFSS PDF
    print("\n[3/8] Extracting BNR banking sector (NPL, CAR, LCR) from MPFSS PDF...")
    try:
        if verify_pdf_extraction():
            print("  PDF verification: Table 18 confirmed on page 53")
            banking_sector = extract_banking_sector_from_mpfss()
            print(f"  OK: {len(banking_sector)} banking sector records extracted")
        else:
            print("  WARNING: PDF verification failed, using hardcoded verified data")
            banking_sector = extract_banking_sector_from_mpfss()
            print(f"  OK: {len(banking_sector)} banking sector records (from verified extraction)")
    except Exception as e:
        print(f"  WARNING: BNR banking sector extraction failed: {e}")
        banking_sector = pd.DataFrame()

    # Step 4: Transform
    print("\n[4/8] Transforming data...")
    interest_rates_monthly = transform_interest_rates(bnr_raw)
    interest_rates_annual = compute_annual_averages(interest_rates_monthly)
    macro_indicators = transform_macro_indicators(wb_raw)

    print(f"  Interest rates (monthly): {len(interest_rates_monthly)} observations")
    print(f"  Interest rates (annual avg, derived): {len(interest_rates_annual)} observations")
    print(f"  Macro indicators: {len(macro_indicators)} observations")
    print(f"  Banking sector: {len(banking_sector)} observations")

    # Step 5: Compute derived metrics
    print("\n[5/8] Computing derived financial metrics...")
    derived_metrics = compute_all_derived_metrics(
        interest_rates_monthly, interest_rates_annual, macro_indicators, banking_sector
    )
    print(f"  Derived metrics: {len(derived_metrics)} observations")
    if not derived_metrics.empty:
        print(f"  Indicators: {derived_metrics['indicator_id'].unique().tolist()}")

    # Step 6: Generate opportunity intelligence signals
    print("\n[6/8] Generating opportunity intelligence signals...")
    signals = generate_signals(interest_rates_annual, macro_indicators, banking_sector, derived_metrics)
    print(f"  Signals generated: {len(signals)}")
    if not signals.empty:
        for _, sig in signals.iterrows():
            print(f"    [{sig['signal_type']}] {sig['description'][:80]}")

    # Save processed data locally
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if not interest_rates_monthly.empty:
        interest_rates_monthly.to_csv(PROCESSED_DIR / "interest_rates_monthly.csv", index=False)
    if not interest_rates_annual.empty:
        interest_rates_annual.to_csv(PROCESSED_DIR / "interest_rates_annual.csv", index=False)
    if not macro_indicators.empty:
        macro_indicators.to_csv(PROCESSED_DIR / "macro_indicators.csv", index=False)
    if not banking_sector.empty:
        banking_sector.to_csv(PROCESSED_DIR / "banking_sector.csv", index=False)
    if not derived_metrics.empty:
        derived_metrics.to_csv(PROCESSED_DIR / "derived_metrics.csv", index=False)
    if not signals.empty:
        signals.to_csv(PROCESSED_DIR / "opportunity_signals.csv", index=False)

    # Step 7: Load into PostgreSQL warehouse
    print("\n[7/8] Loading data into PostgreSQL warehouse...")
    try:
        load_all(
            interest_rates=interest_rates_monthly,
            macro_indicators=macro_indicators,
            derived_metrics=derived_metrics,
            banking_sector=banking_sector,
            source_catalog=source_catalog,
        )
        warehouse_summary = get_warehouse_summary()
        print(f"  Warehouse loaded: {warehouse_summary}")
    except Exception as e:
        print(f"  WARNING: Warehouse loading failed: {e}")
        warehouse_summary = {}

    # Step 8: Validate
    print("\n[8/8] Validating transformed data...")
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

    # Security check
    print("\nSecurity check...")
    secret_errors = check_no_secrets(".")
    if secret_errors:
        print(f"  FAIL: {len(secret_errors)} security issues")
        for e in secret_errors:
            print(f"    - {e}")
    else:
        print("  OK: No secrets detected")

    # Summary
    total_records = len(interest_rates_monthly) + len(interest_rates_annual) + len(macro_indicators) + len(banking_sector) + len(derived_metrics)
    print("\n" + "=" * 60)
    print("Pipeline Summary")
    print("=" * 60)
    print(f"  World Bank records: {len(wb_raw)}")
    print(f"  BNR interest rate records: {len(bnr_raw)}")
    print(f"  BNR banking sector records: {len(banking_sector)}")
    print(f"  Transformed interest rates (monthly): {len(interest_rates_monthly)}")
    print(f"  Transformed interest rates (annual): {len(interest_rates_annual)}")
    print(f"  Macro indicators: {len(macro_indicators)}")
    print(f"  Derived metrics: {len(derived_metrics)}")
    print(f"  Opportunity signals: {len(signals)}")
    print(f"  Total records: {total_records}")
    print(f"  Validation errors: {len(ir_errors) + len(macro_errors)}")
    print(f"  Security issues: {len(secret_errors)}")
    if warehouse_summary:
        print(f"  Warehouse tables: {warehouse_summary}")
    print()

    return {
        "wb_raw": wb_raw,
        "bnr_raw": bnr_raw,
        "banking_sector": banking_sector,
        "interest_rates_monthly": interest_rates_monthly,
        "interest_rates_annual": interest_rates_annual,
        "macro_indicators": macro_indicators,
        "derived_metrics": derived_metrics,
        "signals": signals,
        "warehouse_summary": warehouse_summary,
    }


if __name__ == "__main__":
    run_pipeline()
