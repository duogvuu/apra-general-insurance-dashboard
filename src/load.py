"""Load step: write the tidy table into a SQLite star schema."""

import sqlite3

import pandas as pd

from extract import PROJECT_ROOT

DB_FILE = PROJECT_ROOT / "data" / "processed" / "apra_gi.db"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"
VIEWS_FILE = PROJECT_ROOT / "sql" / "views.sql"

STATE_CODES = {
    "National": "AUS",
    "Australian Capital Territory": "ACT",
    "New South Wales": "NSW",
    "Northern Territory": "NT",
    "Queensland": "QLD",
    "South Australia": "SA",
    "Tasmania": "TAS",
    "Victoria": "VIC",
    "Western Australia": "WA",
}

COUNT_METRICS = {"risks_written"}  # every other metric is in AUD


def build_dim_quarter(tidy: pd.DataFrame) -> pd.DataFrame:
    """One row per reporting quarter, with calendar and Australian FY attributes."""
    dim = pd.DataFrame({"period_end": sorted(tidy["reporting_period"].unique())})
    dim["period_end"] = pd.to_datetime(dim["period_end"])
    dim["quarter_id"] = dim["period_end"].dt.strftime("%Y%m%d").astype(int)
    dim["calendar_year"] = dim["period_end"].dt.year
    dim["calendar_quarter"] = dim["period_end"].dt.quarter
    # Australian financial year ends 30 June: July-December belongs to the next FY
    fy = dim["period_end"].dt.year + (dim["period_end"].dt.month > 6).astype(int)
    dim["financial_year"] = "FY" + fy.astype(str)
    dim["quarter_label"] = dim["period_end"].dt.strftime("%b %Y")
    dim["period_end"] = dim["period_end"].dt.strftime("%Y-%m-%d")
    return dim[["quarter_id", "period_end", "calendar_year",
                "calendar_quarter", "financial_year", "quarter_label"]]


def build_dim_class(tidy: pd.DataFrame) -> pd.DataFrame:
    """One row per class of business."""
    dim = (
        tidy[["class_of_business", "class_category", "class_group"]]
        .drop_duplicates()
        .sort_values("class_of_business")
        .reset_index(drop=True)
    )
    dim.insert(0, "class_id", dim.index + 1)
    return dim


def build_dim_state() -> pd.DataFrame:
    """One row per state/territory, plus National."""
    dim = pd.DataFrame(list(STATE_CODES.items()), columns=["state_name", "state_code"])
    dim.insert(0, "state_id", dim.index + 1)
    return dim


def build_dim_metric(tidy: pd.DataFrame) -> pd.DataFrame:
    """One row per metric, with its unit."""
    dim = pd.DataFrame({"metric_name": sorted(tidy["metric"].unique())})
    dim["unit"] = dim["metric_name"].apply(
        lambda m: "count" if m in COUNT_METRICS else "AUD"
    )
    dim.insert(0, "metric_id", dim.index + 1)
    return dim


def build_fact(tidy, dim_class, dim_state, dim_metric) -> pd.DataFrame:
    """Replace descriptive text with dimension IDs."""
    fact = (
        tidy.assign(quarter_id=tidy["reporting_period"].dt.strftime("%Y%m%d").astype(int))
        .merge(dim_class[["class_id", "class_of_business"]], on="class_of_business")
        .merge(dim_state[["state_id", "state_name"]], left_on="state", right_on="state_name")
        .merge(dim_metric[["metric_id", "metric_name"]], left_on="metric", right_on="metric_name")
    )
    if len(fact) != len(tidy):
        raise ValueError(f"Join lost rows: {len(tidy)} in, {len(fact)} out")
    fact["is_masked"] = fact["is_masked"].astype(int)
    return fact[["quarter_id", "class_id", "state_id", "metric_id", "value", "is_masked"]]


def load_to_sqlite(tidy: pd.DataFrame, db_path=DB_FILE) -> None:
    """Rebuild the database from scratch and insert all tables."""
    dim_class = build_dim_class(tidy)
    dim_state = build_dim_state()
    dim_metric = build_dim_metric(tidy)
    tables = {  # dimensions first, fact last (foreign keys)
        "dim_quarter": build_dim_quarter(tidy),
        "dim_class": dim_class,
        "dim_state": dim_state,
        "dim_metric": dim_metric,
        "fact_cob_metric": build_fact(tidy, dim_class, dim_state, dim_metric),
    }

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_FILE.read_text())
        conn.execute("PRAGMA foreign_keys = ON")
        for name, table in tables.items():
            table.to_sql(name, conn, if_exists="append", index=False)
            print(f"  {name}: {len(table):,} rows")
        conn.executescript(VIEWS_FILE.read_text())
        conn.commit()
    finally:
        conn.close()