"""Test data validation logic."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pandas as pd
from rfaw.transform.interest_rates import transform_interest_rates, compute_annual_averages
from rfaw.transform.macro_indicators import transform_macro_indicators
from rfaw.validation.checks import validate_interest_rates, validate_macro_indicators


class TestInterestRateValidation:
    def test_valid_interest_rates_pass(self):
        """Valid interest rate data should pass validation."""
        df = pd.DataFrame({
            "source_id": ["BNR-IRS-001"] * 3,
            "indicator_id": ["CBR", "LENDING_RATE", "DEPOSIT_RATE"],
            "date": pd.to_datetime(["2024-01-15", "2024-01-15", "2024-01-15"]),
            "frequency": ["monthly"] * 3,
            "value": [7.5, 16.0, 9.5],
            "unit": ["percent"] * 3,
            "indicator_name": ["CBR", "Lending Rate", "Deposit Rate"],
        })
        errors = validate_interest_rates(df)
        assert len(errors) == 0, f"Validation errors: {errors}"

    def test_out_of_range_values_fail(self):
        """Interest rates outside reasonable range should fail."""
        df = pd.DataFrame({
            "source_id": ["BNR-IRS-001"],
            "indicator_id": ["CBR"],
            "date": pd.to_datetime(["2024-01-15"]),
            "frequency": ["monthly"],
            "value": [500.0],
            "unit": ["percent"],
            "indicator_name": ["CBR"],
        })
        errors = validate_interest_rates(df)
        assert len(errors) > 0

    def test_duplicates_fail(self):
        """Duplicate observations should fail validation."""
        df = pd.DataFrame({
            "source_id": ["BNR-IRS-001", "BNR-IRS-001"],
            "indicator_id": ["CBR", "CBR"],
            "date": pd.to_datetime(["2024-01-15", "2024-01-15"]),
            "frequency": ["monthly", "monthly"],
            "value": [7.5, 7.6],
            "unit": ["percent", "percent"],
            "indicator_name": ["CBR", "CBR"],
        })
        errors = validate_interest_rates(df)
        assert len(errors) > 0


class TestMacroValidation:
    def test_valid_macro_passes(self):
        """Valid macro data should pass validation."""
        df = pd.DataFrame({
            "source_id": ["WB-MACRO-001"],
            "indicator_id": ["INFLATION_YOY"],
            "date": pd.to_datetime(["2024-12-31"]),
            "frequency": ["annual"],
            "value": [5.2],
            "unit": ["%"],
            "indicator_name": ["Inflation"],
        })
        errors = validate_macro_indicators(df)
        assert len(errors) == 0

    def test_empty_df_fails(self):
        """Empty DataFrame should fail validation."""
        df = pd.DataFrame()
        errors = validate_macro_indicators(df)
        assert len(errors) > 0


class TestTransformFunctions:
    def test_annual_averages_are_derived(self):
        """Annual averages should be marked as DERIVED."""
        monthly = pd.DataFrame({
            "source_id": ["BNR-IRS-001"] * 12,
            "indicator_id": ["CBR"] * 12,
            "date": pd.date_range("2024-01-01", periods=12, freq="MS"),
            "frequency": ["monthly"] * 12,
            "value": [7.5] * 12,
            "unit": ["percent"] * 12,
            "indicator_name": ["CBR"] * 12,
        })
        annual = compute_annual_averages(monthly)
        assert len(annual) == 1
        assert annual.iloc[0]["is_derived"] == True
        assert annual.iloc[0]["is_observed"] == False
        assert annual.iloc[0]["evidence_classification"] == "DERIVED"
