"""Run the full pipeline: extract -> transform -> validate -> save."""

from extract import PROJECT_ROOT, load_raw_data
from transform import transform
from validate import run_all_checks

OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "cob_performance.csv"


def main() -> None:
    print("1/4 Extracting raw data...")
    raw = load_raw_data()

    print("2/4 Transforming...")
    tidy = transform(raw)

    print("3/4 Running data quality checks...")
    run_all_checks(tidy)

    print("4/4 Saving...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(OUTPUT_FILE, index=False)
    print(f"  Saved {len(tidy):,} rows to {OUTPUT_FILE.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()