"""Test warehouse loading and data integrity."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
import pandas as pd
from datetime import date


class TestWarehouseLoading:
    """Test that warehouse tables are populated correctly."""

    @pytest.fixture(scope="class")
    def engine(self):
        from rfaw.warehouse.db import get_engine
        return get_engine()

    def test_sources_loaded(self, engine):
        """metadata.sources should have 10 records."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM metadata.sources"))
            assert result.scalar() == 10

    def test_interest_rates_loaded(self, engine):
        """mart.fact_interest_rates should have > 1000 records."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM mart.fact_interest_rates"))
            assert result.scalar() > 1000

    def test_macro_indicators_loaded(self, engine):
        """mart.fact_macro_indicators should have > 100 records."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM mart.fact_macro_indicators"))
            assert result.scalar() > 100

    def test_derived_metrics_loaded(self, engine):
        """mart.fact_derived_metrics should have > 100 records."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM mart.fact_derived_metrics"))
            assert result.scalar() > 100

    def test_banking_sector_loaded(self, engine):
        """mart.fact_banking_sector should have NPL ratio data."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM mart.fact_banking_sector WHERE indicator_id = 'NPL_RATIO'"
            ))
            assert result.scalar() == 5  # 2019-2023

    def test_npl_data_is_verified_primary(self, engine):
        """NPL data should be VERIFIED_PRIMARY with provenance."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT evidence_classification, transformation_notes "
                "FROM mart.fact_banking_sector WHERE indicator_id = 'NPL_RATIO' LIMIT 1"
            ))
            row = result.fetchone()
            assert row[0] == "VERIFIED_PRIMARY"
            assert "Table 18" in row[1]
            assert "page 53" in row[1]

    def test_derived_metrics_are_derived(self, engine):
        """All derived metrics should have is_derived = True."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM mart.fact_derived_metrics WHERE is_derived = FALSE"
            ))
            assert result.scalar() == 0

    def test_derived_metrics_have_formula(self, engine):
        """All derived metrics should have transformation_notes with formula."""
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text(
                "SELECT COUNT(*) FROM mart.fact_derived_metrics "
                "WHERE transformation_notes IS NULL OR transformation_notes NOT LIKE '%Formula:%'"
            ))
            assert result.scalar() == 0

    def test_no_raw_data_tracked(self):
        """No raw data files should be tracked in git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "data/raw/"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        tracked = [f for f in result.stdout.strip().split("\n") if f and ".gitkeep" not in f]
        assert len(tracked) == 0, f"Raw data files tracked: {tracked}"

    def test_no_processed_data_tracked(self):
        """No processed data files should be tracked in git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "data/processed/"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        tracked = [f for f in result.stdout.strip().split("\n") if f and ".gitkeep" not in f]
        assert len(tracked) == 0, f"Processed data files tracked: {tracked}"

    def test_dashboard_data_not_tracked(self):
        """dashboard/data.json should not be tracked in git."""
        import subprocess
        result = subprocess.run(
            ["git", "ls-files", "dashboard/data.json"],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), "..")
        )
        assert result.stdout.strip() == "", "dashboard/data.json is tracked in git"
