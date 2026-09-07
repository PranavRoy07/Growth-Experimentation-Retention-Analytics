import streamlit as st
import plotly.express as px
from app.app_utils import load_clickstream_data, retention_data

st.set_page_config(page_title="Cohort Retention", layout="wide")
st.title("Cohort Retention")

customers, sessions, events = load_clickstream_data()

min_date = customers["signup_date"].min().date()
max_date = customers["signup_date"].max().date()
all_sources = sorted(sessions["source"].dropna().unique())

col1, col2 = st.columns(2)
date_range = col1.date_input(
    "Signup date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
sources = col2.multiselect(
    "Acquisition source",
    options=all_sources,
    default=all_sources
)

if len(date_range) == 2 and sources:
    retention = retention_data(
        customers, sessions, events, date_range[0], date_range[1], sources
    )

    week_4 = retention[retention["weeks_since_signup"] == 4]["retention_pct"]

    st.metric(
        "Average week-4 retention",
        f"{week_4.mean():.2%}" if not week_4.empty else "Not available"
    )

    matrix = retention.pivot(
        index="cohort_week",
        columns="weeks_since_signup",
        values="retention_pct"
    )

    heatmap = px.imshow(
        matrix,
        labels={
            "x": "Weeks since signup",
            "y": "Signup cohort week",
            "color": "Retention rate"
        },
        aspect="auto",
        color_continuous_scale="Blues",
    )
    heatmap.update_coloraxes(colorbar_tickformat=".0%")
    st.plotly_chart(heatmap, use_container_width=True)
else:
    st.info("Select a complete date range and at least one source.")