from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "ecommerce_clickstream"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

PROCESSED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Load the three files needed for this phase
customers = pd.read_csv(RAW_DIR / "customers.csv")
sessions = pd.read_csv(RAW_DIR / "sessions.csv")
events = pd.read_csv(RAW_DIR / "events.csv")

# Convert date fields into real dates
customers["signup_date"] = pd.to_datetime(customers["signup_date"])
sessions["start_time"] = pd.to_datetime(sessions["start_time"])
events["timestamp"] = pd.to_datetime(events["timestamp"])

# ---------------------------------------------------------
# 1. COHORT RETENTION
# ---------------------------------------------------------

# A customer's acquisition source is the source of their first session.
first_session = (
    sessions.sort_values("start_time")
    .groupby("customer_id", as_index=False)
    .first()[["customer_id", "source"]]
    .rename(columns={"source": "acquisition_source"})
)

# Add customer and acquisition information to each event.
event_data = (
    events.merge(
        sessions[["session_id", "customer_id", "source"]],
        on="session_id",
        how="left"
    )
    .merge(
        customers[["customer_id", "signup_date"]],
        on="customer_id",
        how="left"
    )
    .merge(
        first_session,
        on="customer_id",
        how="left"
    )
)

# Weeks begin on Monday.
customers["cohort_week"] = (
    customers["signup_date"].dt.to_period("W-SUN").dt.start_time
)

event_data["cohort_week"] = (
    event_data["signup_date"].dt.to_period("W-SUN").dt.start_time
)
event_data["event_week"] = (
    event_data["timestamp"].dt.to_period("W-SUN").dt.start_time
)

event_data["weeks_since_signup"] = (
    (event_data["event_week"] - event_data["cohort_week"]).dt.days // 7
)

# Ignore events dated before a customer's signup date.
event_data = event_data[event_data["weeks_since_signup"] >= 0]

# Each cohort's denominator is every customer who signed up that week.
cohort_sizes = (
    customers.groupby("cohort_week")["customer_id"]
    .nunique()
    .rename("cohort_size")
    .reset_index()
)

# Count distinct active customers for every cohort/week combination.
retained_users = (
    event_data.groupby(["cohort_week", "weeks_since_signup"])["customer_id"]
    .nunique()
    .rename("active_users")
    .reset_index()
)

retention = retained_users.merge(cohort_sizes, on="cohort_week", how="left")
retention["retention_pct"] = retention["active_users"] / retention["cohort_size"]

# Week 0 is always 100% because it represents the original signup cohort.
week_zero = cohort_sizes.copy()
week_zero["weeks_since_signup"] = 0
week_zero["active_users"] = week_zero["cohort_size"]
week_zero["retention_pct"] = 1.0

retention = (
    pd.concat([retention, week_zero], ignore_index=True)
    .drop_duplicates(["cohort_week", "weeks_since_signup"], keep="last")
    .sort_values(["cohort_week", "weeks_since_signup"])
)

retention.to_csv(PROCESSED_DIR / "cohort_retention.csv", index=False)

retention_matrix = retention.pivot(
    index="cohort_week",
    columns="weeks_since_signup",
    values="retention_pct"
)
retention_matrix.to_csv(PROCESSED_DIR / "cohort_retention_matrix.csv")

# ---------------------------------------------------------
# 2. FUNNEL DROP-OFF
# ---------------------------------------------------------

stage_order = ["page_view", "add_to_cart", "checkout", "purchase"]

available_stages = set(events["event_type"].unique())
missing_stages = set(stage_order) - available_stages

if missing_stages:
    raise ValueError(
        f"These expected event stages are missing: {missing_stages}. "
        f"Available values are: {sorted(available_stages)}"
    )

funnel = (
    events[events["event_type"].isin(stage_order)]
    .groupby("event_type")["session_id"]
    .nunique()
    .reindex(stage_order)
    .reset_index(name="sessions")
    .rename(columns={"event_type": "stage"})
)

funnel["conversion_from_previous"] = funnel["sessions"] / funnel["sessions"].shift(1)
funnel.loc[0, "conversion_from_previous"] = 1.0
funnel["drop_off_from_previous"] = 1 - funnel["conversion_from_previous"]

funnel.to_csv(PROCESSED_DIR / "funnel_summary.csv", index=False)

largest_drop = funnel.iloc[1:].loc[funnel.iloc[1:]["drop_off_from_previous"].idxmax()]

# Funnel chart
plt.figure(figsize=(9, 5))
plt.bar(funnel["stage"], funnel["sessions"], color="#4F46E5")
plt.title("E-commerce Funnel: Sessions Reaching Each Stage")
plt.xlabel("Funnel stage")
plt.ylabel("Unique sessions")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "funnel_dropoff.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 3. SEGMENTATION BY ACQUISITION SOURCE
# ---------------------------------------------------------

# Funnel by source uses each session's recorded source.
funnel_source = (
    events.merge(
        sessions[["session_id", "source"]],
        on="session_id",
        how="left"
    )
    .query("event_type in @stage_order")
    .groupby(["source", "event_type"])["session_id"]
    .nunique()
    .rename("sessions")
    .reset_index()
    .rename(columns={"event_type": "stage"})
)

funnel_source.to_csv(PROCESSED_DIR / "funnel_by_source.csv", index=False)

# Retention by acquisition source uses each customer's first-session source.
retention_source = (
    event_data.groupby(
        ["acquisition_source", "weeks_since_signup"]
    )["customer_id"]
    .nunique()
    .rename("active_users")
    .reset_index()
)

source_cohort_sizes = (
    customers.merge(first_session, on="customer_id", how="left")
    .groupby("acquisition_source")["customer_id"]
    .nunique()
    .rename("customers")
    .reset_index()
)

retention_source = retention_source.merge(
    source_cohort_sizes,
    on="acquisition_source",
    how="left"
)
retention_source["retention_pct"] = (
    retention_source["active_users"] / retention_source["customers"]
)

retention_source.to_csv(
    PROCESSED_DIR / "retention_by_source.csv",
    index=False
)

# Retention chart by acquisition source
plt.figure(figsize=(10, 6))

for source, source_data in retention_source.groupby("acquisition_source"):
    plt.plot(
        source_data["weeks_since_signup"],
        source_data["retention_pct"],
        marker="o",
        label=source
    )

plt.title("Retention Curve by Acquisition Source")
plt.xlabel("Weeks Since Signup")
plt.ylabel("Retention Rate")
plt.legend(title="Acquisition source")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "retention_by_source.png", dpi=150)
plt.close()

# ---------------------------------------------------------
# 4. SAVE A SHORT INSIGHT REPORT
# ---------------------------------------------------------

insights = f"""# Phase 4: Retention and Funnel Analysis

## Biggest funnel drop-off
The largest drop-off is from the previous stage to **{largest_drop["stage"]}**.
- Sessions at this stage: {largest_drop["sessions"]:,}
- Drop-off rate: {largest_drop["drop_off_from_previous"]:.2%}

## Files created
- cohort_retention.csv
- cohort_retention_matrix.csv
- funnel_summary.csv
- funnel_by_source.csv
- retention_by_source.csv
- funnel_dropoff.png
- retention_by_source.png

## Method note
Cohorts are based on customer signup week. Retention means a customer generated at least one event during a given week after signup. Funnel metrics count unique sessions that reached each event stage. Acquisition source is assigned from each customer's first recorded session.
"""

(PROCESSED_DIR / "phase4_insights.md").write_text(insights, encoding="utf-8")

print(insights)
print("Phase 4 files created successfully.")