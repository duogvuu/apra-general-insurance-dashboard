from pathlib import Path
import pandas as pd

# Path to the raw APRA data file
RAW_FILE = Path("data/raw") / "Quarterly general insurance performance statistics database September 2023 to June 2026.xlsx"

# 1. Read ONLY the "Database" sheet
df = pd.read_excel(RAW_FILE, sheet_name="Database")

# 2. Print the number of rows and columns
num_rows, num_columns = df.shape
print(f"Number of rows: {num_rows}, Number of columns: {num_columns}")

# 3. Print the first 5 rows
first_5_rows = df.head(5)
print("\nFirst 5 rows:")
print(first_5_rows)

# 4. Print the column names
col_names = df.columns
print("\nColumn names:")
print(col_names)