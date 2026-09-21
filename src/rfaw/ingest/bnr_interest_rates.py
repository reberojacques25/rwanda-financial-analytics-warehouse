"""Ingest BNR Interest Rate Structure workbook."""
import re
import pandas as pd
from datetime import date
from ..config import BNR_INTEREST_RATE_URL, RAW_DIR


def download_interest_rate_workbook() -> str:
    """Download the BNR interest rate XLS file."""
    import requests
    raw_path = RAW_DIR / "bnr_interest_rates.xls"
    raw_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Downloading from {BNR_INTEREST_RATE_URL}...")
    resp = requests.get(BNR_INTEREST_RATE_URL, timeout=60)
    resp.raise_for_status()
    with open(raw_path, "wb") as f:
        f.write(resp.content)
    print(f"  Saved to {raw_path} ({len(resp.content)} bytes)")
    return str(raw_path)


# Indicators we want to extract (BNR names change over time)
TARGET_INDICATORS = {
    "central bank rate": "CBR",
    "key repo rate": "CBR",
    "key repo rate ( bank rate)": "CBR",
    "deposit rate": "DEPOSIT_RATE",
    "lending rate": "LENDING_RATE",
    "interbank rate": "INTERBANK_RATE",
    "reserve requirement": "RESERVE_REQUIREMENT",
    "repo": "REPO_RATE",
    "reverse repo": "REVERSE_REPO_RATE",
    "standing lending facility": "STANDING_LENDING_FACILITY",
    "standing deposit facility": "STANDING_DEPOSIT_FACILITY",
    "overnight deposit facility": "OVERNIGHT_DEPOSIT_FACILITY",
    "refinancing facility": "REFINANCING_FACILITY",
    "refinancing facility (discount rate)": "REFINANCING_FACILITY",
    "discount rate": "DISCOUNT_RATE",
}


def match_indicator(name: str):
    """Match an indicator name to a standardized code."""
    clean = name.lower().strip()
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean)
    for key, code in TARGET_INDICATORS.items():
        if clean == key or clean.startswith(key):
            return code
    return None


def parse_interest_rate_workbook(file_path: str) -> pd.DataFrame:
    """Parse the BNR interest rate XLS workbook into structured data.
    
    The workbook has a single sheet with years stacked vertically:
    - "Year YYYY" header rows
    - "Designation" rows with month dates as column headers
    - Indicator rows with values
    """
    df = pd.read_excel(file_path, header=None)
    all_records = []
    retrieval_date = date.today().isoformat()

    current_year = None
    month_dates = []  # list of (col_idx, month) tuples

    for idx in range(len(df)):
        row = df.iloc[idx]
        label = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""

        # Detect "Year YYYY" header
        year_match = re.match(r'^Year\s+(\d{4})', label)
        if year_match:
            current_year = int(year_match.group(1))
            month_dates = []
            continue

        # Detect "Designation" row with month dates
        if label.lower().startswith("designation"):
            month_dates = []
            for col_idx in range(1, min(len(row), 13)):
                val = row.iloc[col_idx]
                if pd.notna(val):
                    try:
                        if isinstance(val, pd.Timestamp):
                            month = val.month
                        else:
                            # Try parsing as date string
                            date_str = str(val)
                            if '-' in date_str:
                                parts = date_str.split('-')
                                month = int(parts[1])
                            else:
                                continue
                        month_dates.append((col_idx, month))
                    except (ValueError, IndexError):
                        pass
            continue

        # Skip if no year or month dates set
        if current_year is None or not month_dates:
            continue

        # Try to match indicator
        indicator_code = match_indicator(label)
        if indicator_code is None:
            continue

        # Extract values for each month
        for col_idx, month in month_dates:
            val = row.iloc[col_idx]
            if pd.notna(val):
                # Handle string values that might contain numbers
                try:
                    if isinstance(val, str):
                        # Clean non-breaking spaces and other artifacts
                        val_clean = val.replace('\xa0', '').strip()
                        if val_clean in ('-', '', 'nan', 'None'):
                            continue
                        numeric_val = float(val_clean)
                    else:
                        numeric_val = float(val)
                except (ValueError, TypeError):
                    continue

                all_records.append({
                    "source_id": "BNR-IRS-001",
                    "year": current_year,
                    "period_label": f"{current_year}-M{month:02d}",
                    "indicator_name": label,
                    "indicator_code": indicator_code,
                    "indicator_value": numeric_val,
                    "unit": "percent",
                    "retrieval_date": retrieval_date,
                })

    result = pd.DataFrame(all_records)
    if not result.empty:
        raw_path = RAW_DIR / "bnr_interest_rates_raw.csv"
        result.to_csv(raw_path, index=False)
        years = sorted(result["year"].unique())
        indicators = result["indicator_code"].unique()
        print(f"  Parsed {len(result)} observations: {len(years)} years ({years[0]}-{years[-1]}), {len(indicators)} indicators")
    return result


def ingest_bnr_interest_rates() -> pd.DataFrame:
    """Download and parse the BNR interest rate workbook."""
    file_path = download_interest_rate_workbook()
    return parse_interest_rate_workbook(file_path)
