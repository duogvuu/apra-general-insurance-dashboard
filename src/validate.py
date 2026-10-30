"""Data quality checks for the tidy class-of-business table."""

import pandas as pd

KEY_COLUMNS = ["reporting_period", "class_of_business", "state", "metric"]
EXPECTED_QUARTERS = 11
ROUNDING_TOLERANCE = 1_000_000  # APRA rounds values to the nearest $1m


def check_no_unmapped_metrics(df: pd.DataFrame) -> None:
    """Every APRA data item must have a short metric name."""
    missing = df["metric"].isna().sum()
    if missing > 0:
        raise ValueError(f"{missing} rows have an unmapped data item")


def check_no_duplicates(df: pd.DataFrame) -> None:
    """Each quarter + class + state + metric combination must appear only once."""
    dupes = df.duplicated(subset=KEY_COLUMNS).sum()
    if dupes > 0:
        raise ValueError(f"{dupes} duplicate rows found")


def check_quarter_count(df: pd.DataFrame) -> None:
    """The AASB 17 series should contain exactly 11 quarters of flow data."""
    n_quarters = df["reporting_period"].nunique()
    if n_quarters != EXPECTED_QUARTERS:
        raise ValueError(f"Expected {EXPECTED_QUARTERS} quarters, found {n_quarters}")


def check_service_result_reconciles(df: pd.DataFrame) -> int:
    """Revenue + service expense must equal APRA's published gross service result."""
    national = df[df["state"] == "National"].pivot_table(
        index=["reporting_period", "class_of_business"],
        columns="metric",
        values="value",
    )
    diff = (
        national["insurance_revenue"]
        + national["insurance_service_expense"]
        - national["service_result_gross"]
    ).abs()
    failures = diff[diff > ROUNDING_TOLERANCE]
    if not failures.empty:
        raise ValueError(f"{len(failures)} rows fail reconciliation:\n{failures}")
    return diff.notna().sum()


def run_all_checks(df: pd.DataFrame) -> None:
    """Run every check; stop the pipeline on the first failure."""
    check_no_unmapped_metrics(df)
    check_no_duplicates(df)
    check_quarter_count(df)
    n_checked = check_service_result_reconciles(df)
    print(f"  All checks passed ({n_checked} reconciliations within $1m rounding)")