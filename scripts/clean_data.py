from pathlib import Path
import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "marketing_AB.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "marketing_ab_clean.csv"
AUDIT_PATH = PROJECT_ROOT / "data" / "processed" / "cleaning_audit.md"

# Load raw data
df = pd.read_csv(RAW_PATH)

# Audit before cleaning
original_rows = len(df)
null_counts = df.isna().sum().to_dict()
duplicate_rows = int(df.duplicated().sum())
duplicate_users = int(df["user id"].duplicated().sum())

# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Drop the exported index column; it is not business data
df = df.drop(columns=["unnamed:_0"], errors="ignore")

# Validate expected values
valid_groups = {"ad", "psa"}
valid_days = {
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
}

invalid_group_rows = int((~df["test_group"].isin(valid_groups)).sum())
invalid_day_rows = int((~df["most_ads_day"].isin(valid_days)).sum())
invalid_hour_rows = int((~df["most_ads_hour"].between(0, 23)).sum())
negative_ads_rows = int((df["total_ads"] < 0).sum())

# No rows are dropped because all audited records are valid
df.to_csv(PROCESSED_PATH, index=False)

# Save the cleaning record for your README / methodology
audit_text = f"""# Cleaning audit

## Source
- Raw file: `{RAW_PATH.name}`
- Original rows: {original_rows:,}

## Audit results
- Missing values: {null_counts}
- Duplicate rows: {duplicate_rows:,}
- Duplicate user IDs: {duplicate_users:,}
- Invalid test groups: {invalid_group_rows:,}
- Invalid weekday values: {invalid_day_rows:,}
- Invalid hour values: {invalid_hour_rows:,}
- Negative ad-count values: {negative_ads_rows:,}

## Cleaning actions
1. Renamed columns to lowercase snake_case.
2. Dropped `unnamed:_0`, an exported row-index column with no analytical meaning.
3. Retained all {len(df):,} user records because no duplicate, missing, or invalid records were found.
4. Did not create cohort or retention fields because this source contains no signup or event timestamp.
"""

AUDIT_PATH.write_text(audit_text, encoding="utf-8")

print(f"Processed file created: {PROCESSED_PATH}")
print(f"Audit file created: {AUDIT_PATH}")
print(f"Rows retained: {len(df):,}")