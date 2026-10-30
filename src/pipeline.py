"""Run the full pipeline: extract -> transform -> validate -> save -> load."""

from extract import PROJECT_ROOT, load_raw_data
from transform import transform
from validate import run_all_checks
from load import DB_FILE, load_to_sqlite

OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "cob_performance.csv"


def main() -> None:
    print("1/5 Extracting raw data...")
    raw = load_raw_data()

    print("2/5 Transforming...")
    tidy = transform(raw)

    print("3/5 Running data quality checks...")
    run_all_checks(tidy)

    print("4/5 Saving...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(OUTPUT_FILE, index=False)
    print(f"  Saved {len(tidy):,} rows to {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")

    print("5/5 Loading into SQLite...")
    load_to_sqlite(tidy)
    print(f"  Database ready: {DB_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()