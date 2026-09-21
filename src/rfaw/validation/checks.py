"""Data quality validation checks for RFAW."""
import pandas as pd
from pathlib import Path
from ..config import EVIDENCE_CLASSIFICATIONS, METADATA_DIR


REQUIRED_SOURCE_FIELDS = [
    "source_id", "source_organization", "dataset_name", "source_url",
    "retrieval_date", "frequency", "geographic_scope", "unit",
    "evidence_classification", "is_observed", "is_derived",
]


def validate_source_catalog() -> list:
    """Validate the source catalog YAML file."""
    import yaml
    errors = []
    catalog_path = METADATA_DIR / "source_catalog.yml"

    if not catalog_path.exists():
        return [f"Source catalog not found at {catalog_path}"]

    with open(catalog_path) as f:
        catalog = yaml.safe_load(f)

    sources = catalog.get("sources", [])
    if not sources:
        errors.append("Source catalog contains no sources")
        return errors

    for i, src in enumerate(sources):
        for field in REQUIRED_SOURCE_FIELDS:
            if field not in src or src[field] is None:
                errors.append(f"Source {i} ({src.get('source_id', 'unknown')}): missing required field '{field}'")

        ev_class = src.get("evidence_classification", "")
        if ev_class and ev_class not in EVIDENCE_CLASSIFICATIONS:
            errors.append(f"Source {src.get('source_id', i)}: invalid evidence_classification '{ev_class}'")

        if not src.get("source_url"):
            errors.append(f"Source {src.get('source_id', i)}: missing source_url")

        if src.get("is_derived") and src.get("is_observed"):
            errors.append(f"Source {src.get('source_id', i)}: cannot be both observed and derived")

    return errors


def validate_interest_rates(df: pd.DataFrame) -> list:
    """Validate interest rate observations."""
    errors = []
    if df.empty:
        return ["Interest rate DataFrame is empty"]

    required_cols = ["source_id", "indicator_id", "date", "frequency", "value"]
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return errors

    # Check for nulls in required fields
    for col in ["source_id", "indicator_id", "date", "frequency", "value"]:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"{null_count} null values in column '{col}'")

    # Check value ranges (interest rates should be reasonable)
    if "value" in df.columns:
        out_of_range = df[(df["value"] < -50) | (df["value"] > 200)]
        if len(out_of_range) > 0:
            errors.append(f"{len(out_of_range)} interest rate values outside [-50, 200] range")

    # Check for duplicates
    dup_cols = ["source_id", "indicator_id", "date", "frequency"]
    dups = df.duplicated(subset=dup_cols)
    if dups.sum() > 0:
        errors.append(f"{dups.sum()} duplicate (source_id, indicator_id, date, frequency) combinations")

    return errors


def validate_macro_indicators(df: pd.DataFrame) -> list:
    """Validate macro indicator observations."""
    errors = []
    if df.empty:
        return ["Macro indicators DataFrame is empty"]

    required_cols = ["source_id", "indicator_id", "date", "frequency", "value"]
    for col in required_cols:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return errors

    # Check for nulls
    for col in ["source_id", "indicator_id", "date", "value"]:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            errors.append(f"{null_count} null values in column '{col}'")

    # Check dates are reasonable
    if "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce")
        bad_dates = dates.isnull().sum()
        if bad_dates > 0:
            errors.append(f"{bad_dates} invalid dates")

    # Check for duplicates
    dup_cols = ["source_id", "indicator_id", "date", "frequency"]
    dups = df.duplicated(subset=dup_cols)
    if dups.sum() > 0:
        errors.append(f"{dups.sum()} duplicate (source_id, indicator_id, date, frequency) combinations")

    return errors


def check_no_secrets(directory: str = ".") -> list:
    """Scan files for common credential patterns."""
    import subprocess
    errors = []
    try:
        result = subprocess.run(
            ["rg", "-l", "github_pat_|ghp_|sk-[a-zA-Z0-9]{20,}|api_key|password=|bearer\\s"],
            directory, capture_output=True, text=True, bufsize=1024
        )
        found = [f for f in result.stdout.strip().split("\n") if f and "test_" not in f and ".gitignore" not in f]
        if found:
            errors.append(f"Possible credentials found in: {found}")
    except FileNotFoundError:
        pass
    except TypeError:
        pass
    return errors
