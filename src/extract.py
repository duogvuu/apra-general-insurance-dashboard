"""Extract step: load the raw APRA quarterly general insurance database."""

from pathlib import Path

import pandas as pd

# Project root = two levels above this file (DA1/src/extract.py -> DA1)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = (
    PROJECT_ROOT / "data" / "raw"
    / "Quarterly general insurance performance statistics database September 2023 to June 2026.xlsx"
)


def load_raw_data(path: Path = RAW_FILE) -> pd.DataFrame:
    """Read the 'Database' sheet of the APRA workbook and return it as a DataFrame."""
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")
    return pd.read_excel(path, sheet_name="Database")


if __name__ == "__main__":
    df = load_raw_data()
    print(f"Loaded {len(df):,} rows and {df.shape[1]} columns from {RAW_FILE.name}")