import streamlit as st
import plotly.express as px
from app.app_utils import load_clickstream_data, funnel_data

st.set_page_config(page_title="Funnel", layout="wide")
st.title("Funnel Analysis")

_, sessions, events = load_clickstream_data()

min_date = sessions["start_time"].min().date()
max_date = sessions["start_time"].max().date()

col1, col2 = st.columns(2)
date_range = col1.date_input(
    "Session date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
sources = col2.multiselect(
    "Acquisition source",
    options=sorted(sessions["source"].dropna().unique()),
    default=sorted(sessions["source"].dropna().unique())
)

if len(date_range) == 2 and sources:
    funnel = funnel_data(events, sessions, date_range[0], date_range[1], sources)

    largest_drop = funnel.iloc[1:].loc[funnel.iloc[1:]["drop_off"].idxmax()]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Page views", f"{funnel.iloc[0]['sessions']:,}")
    col2.metric("Purchases", f"{funnel.iloc[-1]['sessions']:,}")
    col3.metric("Purchase conversion", f"{funnel.iloc[-1]['sessions'] / funnel.iloc[0]['sessions']:.2%}")
    col4.metric("Biggest drop-off", largest_drop["stage"].replace("_", " ").title())

    chart = px.funnel(
        funnel,
        x="sessions",
        y="stage",
        text="sessions",
        color="stage"
    )
    st.plotly_chart(chart, use_container_width=True)

    st.warning(
        f"The biggest drop-off occurs before **{largest_drop['stage'].replace('_', ' ').title()}** "
        f"({largest_drop['drop_off']:.1%} drop from the previous stage)."
    )
else:
    st.info("Select a complete date range and at least one source.")