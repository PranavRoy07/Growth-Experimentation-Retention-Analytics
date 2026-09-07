from pathlib import Path
from math import sqrt
import pandas as pd
from scipy.stats import chi2_contingency
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
AB_PATH = ROOT / "data" / "processed" / "marketing_ab_clean.csv"
RAW_DIR = ROOT / "data" / "raw" / "ecommerce_clickstream"

STAGES = ["page_view", "add_to_cart", "checkout", "purchase"]


@st.cache_data
def load_ab_data():
    return pd.read_csv(AB_PATH)


@st.cache_data
def load_clickstream_data():
    customers = pd.read_csv(RAW_DIR / "customers.csv")
    sessions = pd.read_csv(RAW_DIR / "sessions.csv")
    events = pd.read_csv(RAW_DIR / "events.csv")

    customers["signup_date"] = pd.to_datetime(customers["signup_date"])
    sessions["start_time"] = pd.to_datetime(sessions["start_time"])
    events["timestamp"] = pd.to_datetime(events["timestamp"])

    return customers, sessions, events


def experiment_results(df):
    summary = df.groupby("test_group")["converted"].agg(["sum", "count", "mean"])

    psa = summary.loc["psa"]
    ad = summary.loc["ad"]

    table = [
        [psa["count"] - psa["sum"], psa["sum"]],
        [ad["count"] - ad["sum"], ad["sum"]]
    ]

    chi2, p_value, _, _ = chi2_contingency(table)

    difference = ad["mean"] - psa["mean"]
    standard_error = sqrt(
        (ad["mean"] * (1 - ad["mean"]) / ad["count"])
        + (psa["mean"] * (1 - psa["mean"]) / psa["count"])
    )

    return {
        "summary": summary,
        "p_value": p_value,
        "lift": difference,
        "ci_lower": difference - 1.96 * standard_error,
        "ci_upper": difference + 1.96 * standard_error,
    }


def funnel_data(events, sessions, start_date, end_date, sources):
    session_filter = sessions[
        (sessions["start_time"].dt.date >= start_date)
        & (sessions["start_time"].dt.date <= end_date)
        & (sessions["source"].isin(sources))
    ]

    data = events.merge(
        session_filter[["session_id", "source"]],
        on="session_id",
        how="inner"
    )

    funnel = (
        data[data["event_type"].isin(STAGES)]
        .groupby("event_type")["session_id"]
        .nunique()
        .reindex(STAGES, fill_value=0)
        .reset_index()
        .rename(columns={"event_type": "stage", "session_id": "sessions"})
    )

    funnel["conversion_from_previous"] = (
        funnel["sessions"] / funnel["sessions"].shift(1)
    )
    funnel.loc[0, "conversion_from_previous"] = 1.0
    funnel["drop_off"] = 1 - funnel["conversion_from_previous"]

    return funnel


def retention_data(customers, sessions, events, start_date, end_date, sources):
    first_source = (
        sessions.sort_values("start_time")
        .groupby("customer_id", as_index=False)
        .first()[["customer_id", "source"]]
        .rename(columns={"source": "acquisition_source"})
    )

    filtered_customers = customers.merge(first_source, on="customer_id", how="left")
    filtered_customers = filtered_customers[
        (filtered_customers["signup_date"].dt.date >= start_date)
        & (filtered_customers["signup_date"].dt.date <= end_date)
        & (filtered_customers["acquisition_source"].isin(sources))
    ].copy()

    filtered_customers["cohort_week"] = (
        filtered_customers["signup_date"].dt.to_period("W-SUN").dt.start_time
    )

    event_data = (
        events.merge(
            sessions[["session_id", "customer_id"]],
            on="session_id",
            how="left"
        )
        .merge(
            filtered_customers[
                ["customer_id", "signup_date", "cohort_week"]
            ],
            on="customer_id",
            how="inner"
        )
    )

    event_data["event_week"] = (
        event_data["timestamp"].dt.to_period("W-SUN").dt.start_time
    )
    event_data["weeks_since_signup"] = (
        (event_data["event_week"] - event_data["cohort_week"]).dt.days // 7
    )
    event_data = event_data[event_data["weeks_since_signup"] >= 0]

    cohort_sizes = (
        filtered_customers.groupby("cohort_week")["customer_id"]
        .nunique()
        .rename("cohort_size")
        .reset_index()
    )

    active = (
        event_data.groupby(["cohort_week", "weeks_since_signup"])["customer_id"]
        .nunique()
        .rename("active_users")
        .reset_index()
    )

    retention = active.merge(cohort_sizes, on="cohort_week", how="left")
    retention["retention_pct"] = (
        retention["active_users"] / retention["cohort_size"]
    )

    week_zero = cohort_sizes.copy()
    week_zero["weeks_since_signup"] = 0
    week_zero["active_users"] = week_zero["cohort_size"]
    week_zero["retention_pct"] = 1.0

    return (
        pd.concat([retention, week_zero])
        .drop_duplicates(["cohort_week", "weeks_since_signup"], keep="last")
        .sort_values(["cohort_week", "weeks_since_signup"])
    )