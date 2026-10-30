"""Transform step: clean APRA class-of-business data into a tidy table."""

import pandas as pd

from extract import load_raw_data

# Map APRA's long data item names to short metric names.
# National and state-level versions of the same item share one metric name;
# they are told apart by the `state` column.
METRICS = {
    "Insurance revenue, by class of business": "insurance_revenue",
    "Insurance revenue, by class of business and state/territory": "insurance_revenue",
    # Note: APRA's source text has TWO spaces after the dash
    "Insurance service expense -  Incurred claims, by class of business": "incurred_claims",
    "Incurred claims, by class of business and state/territory": "incurred_claims",
    "Insurance service expense - Amortisation of insurance acquisition cash flows, by class of business": "acquisition_costs",
    "Insurance service expense - Other insurance service expenses, by class of business": "other_service_expenses",
    "Insurance service expense - Losses and reversal of losses on onerous contracts, by class of business": "onerous_contract_losses",
    "Insurance service expense - Changes that relate to past service: Changes to liabilities for incurred claims, by class of business": "prior_period_claims_changes",
    "Insurance service expense - Impairment losses/reversals on assets for insurance acquisition cash flows, by class of business": "acquisition_asset_impairment",
    "Insurance service expense, by class of business": "insurance_service_expense",
    "Insurance service result before reinsurance contracts held, by class of business": "service_result_gross",
    "Allocation of reinsurance premiums, by class of business": "reinsurance_premiums",
    "Amounts recoverable from reinsurers, by class of business": "reinsurance_recoveries",
    "Net expense from reinsurance contracts held, by class of business": "net_reinsurance_expense",
    "Insurance service result, by class of business": "service_result_net",
    "Gross written premium, by class of business": "gross_written_premium",
    "Number of risks written, by class of business": "risks_written",
}

# Rename APRA column headers to snake_case
COLUMNS = {
    "Reporting Period": "reporting_period",
    "Class of business": "class_of_business",
    "Class of business category": "class_category",
    "Class of business group": "class_group",
    "State and territory": "state",
    "Value": "value",
}

OUTPUT_COLUMNS = [
    "reporting_period", "class_of_business", "class_category", "class_group",
    "state", "metric", "value", "is_masked",
]


def transform(raw: pd.DataFrame) -> pd.DataFrame:
    """Return a tidy table of class-of-business performance metrics."""
    df = raw[raw["Subject"] == "Class of business performance"].copy()

    # 1. Translate long data item names into short metric names
    df["metric"] = df["Data item"].map(METRICS)

    # 2. Flag values that APRA masked with "*" BEFORE converting to numbers
    df["is_masked"] = df["Value"].astype(str).str.strip() == "*"

    # 3. Convert Value to numbers; masked values become NaN
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    # 4. Rows without a state are national totals
    df["State and territory"] = df["State and territory"].fillna("National")

    df = df.rename(columns=COLUMNS)
    return (
        df[OUTPUT_COLUMNS]
        .sort_values(["reporting_period", "class_of_business", "state", "metric"])
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    tidy = transform(load_raw_data())
    print(f"Shape: {tidy.shape}")
    print(f"Unmapped data items: {tidy['metric'].isna().sum()}")
    print(f"Masked values: {tidy['is_masked'].sum()}")
    print(tidy.head(10))