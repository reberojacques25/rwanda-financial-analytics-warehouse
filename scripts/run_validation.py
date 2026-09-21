"""Run all validation checks and report results."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from rfaw.validation.checks import (
    validate_source_catalog, check_no_secrets
)
from rfaw.config import PROCESSED_DIR
import pandas as pd


def run_validation():
    print("=" * 60)
    print("RFAW Validation Suite")
    print("=" * 60)

    all_passed = True

    # 1. Source catalog validation
    print("\n[1/4] Source catalog validation...")
    errors = validate_source_catalog()
    if errors:
        print(f"  FAIL: {len(errors)} errors")
        for e in errors[:10]:
            print(f"    - {e}")
        all_passed = False
    else:
        print("  PASS")

    # 2. Check processed data files
    print("\n[2/4] Processed data file checks...")
    for fname in ["interest_rates_monthly.csv", "interest_rates_annual.csv", "macro_indicators.csv"]:
        fpath = PROCESSED_DIR / fname
        if fpath.exists():
            df = pd.read_csv(fpath)
            print(f"  {fname}: {len(df)} records, {len(df.columns)} columns")
        else:
            print(f"  {fname}: not found (run pipeline first)")

    # 3. Secret scan
    print("\n[3/4] Secret scan...")
    secret_errors = check_no_secrets(".")
    if secret_errors:
        print(f"  FAIL: {len(secret_errors)} issues")
        for e in secret_errors:
            print(f"    - {e}")
        all_passed = False
    else:
        print("  PASS")

    # 4. Git config check
    print("\n[4/4] Git config check...")
    import subprocess
    result = subprocess.run(["git", "config", "--local", "--list"],
                           capture_output=True, text=True, cwd=".")
    config = result.stdout
    if "github_pat_" in config or "ghp_" in config or "password=" in config.lower():
        print("  FAIL: Token or password found in git config")
        all_passed = False
    else:
        print("  PASS")

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL VALIDATION CHECKS PASSED")
    else:
        print("SOME VALIDATION CHECKS FAILED")
    print("=" * 60)


if __name__ == "__main__":
    run_validation()
