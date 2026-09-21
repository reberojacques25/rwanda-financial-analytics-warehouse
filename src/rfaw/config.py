"""Configuration for RFAW pipeline. Reads from environment variables."""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
SQL_DIR = PROJECT_ROOT / "sql"

# Load .env file if it exists (for local development)
_env_file = PROJECT_ROOT / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

DATABASE_URL = os.getenv("DATABASE_URL", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "rfaw_warehouse")
DB_USER = os.getenv("DB_USER", "rfaw")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

BNR_INTEREST_RATE_URL = os.getenv(
    "BNR_INTEREST_RATE_URL",
    "https://www.bnr.rw/documents/Interest_rate_structure_up_to_March__2025.xls"
)
WORLD_BANK_API_BASE = os.getenv("WORLD_BANK_API_BASE", "https://api.worldbank.org/v2")

EVIDENCE_CLASSIFICATIONS = [
    "VERIFIED_PRIMARY",
    "VERIFIED_SECONDARY",
    "DERIVED",
    "ESTIMATED",
    "UNVERIFIED",
]

# World Bank indicator codes for Rwanda
WORLD_BANK_INDICATORS = {
    "FP.CPI.TOTL.ZG": "Inflation, consumer prices (annual %)",
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "NY.GDP.MKTP.KD.ZG": "GDP growth (annual %)",
    "FR.INR.RINR": "Real interest rate (%)",
    "FR.INR.LEND": "Lending interest rate (%)",
    "FR.INR.DPST": "Deposit interest rate (%)",
    "PA.NUS.FCRF": "Official exchange rate (LCU per US$)",
    "FM.LD.BOP.ZG": "Broad money growth (annual %)",
    "FS.AST.PRVT.GD.ZS": "Domestic credit to private sector (% GDP)",
    "GF.DD.AI.01": "Bank nonperforming loans to total gross loans (%)",
}
