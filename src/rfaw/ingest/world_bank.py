"""Ingest World Bank macro indicators for Rwanda via API."""
import requests
import pandas as pd
from datetime import date
from ..config import WORLD_BANK_API_BASE, WORLD_BANK_INDICATORS, RAW_DIR


def fetch_indicator(country_code: str, indicator_code: str) -> list:
    """Fetch a single indicator from World Bank API."""
    url = f"{WORLD_BANK_API_BASE}/country/{country_code}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 1000, "date": "2000:2025"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if len(data) < 2:
        return []
    return data[1] or []


def ingest_world_bank(country_code: str = "RWA") -> pd.DataFrame:
    """Ingest all configured World Bank indicators for Rwanda."""
    all_records = []
    retrieval_date = date.today().isoformat()

    for code, name in WORLD_BANK_INDICATORS.items():
        print(f"  Fetching {name} ({code})...")
        try:
            records = fetch_indicator(country_code, code)
            for r in records:
                if r.get("value") is not None:
                    all_records.append({
                        "source_id": "WB-MACRO-001",
                        "country_code": country_code,
                        "country_name": r.get("country", {}).get("value", "Rwanda"),
                        "indicator_code": code,
                        "indicator_name": name,
                        "year": int(r["date"]),
                        "value": float(r["value"]),
                        "unit": r.get("unit", ""),
                        "retrieval_date": retrieval_date,
                    })
        except Exception as e:
            print(f"    WARNING: Failed to fetch {code}: {e}")

    df = pd.DataFrame(all_records)
    if not df.empty:
        raw_path = RAW_DIR / "world_bank_macro_raw.csv"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(raw_path, index=False)
        print(f"  Saved {len(df)} records to {raw_path}")
    return df
