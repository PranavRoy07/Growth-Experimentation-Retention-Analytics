import streamlit as st
from app.app_utils import load_ab_data, experiment_results

st.set_page_config(
    page_title="Growth Experimentation Analytics",
    page_icon="📈",
    layout="wide"
)

st.title("Growth Experimentation and Retention Analytics")
st.caption("A/B conversion testing, funnel performance, and cohort retention")

results = experiment_results(load_ab_data())
summary = results["summary"]

col1, col2, col3, col4 = st.columns(4)
col1.metric("PSA conversion", f"{summary.loc['psa', 'mean']:.2%}")
col2.metric("Ad conversion", f"{summary.loc['ad', 'mean']:.2%}")
col3.metric("Conversion lift", f"{results['lift']:.2%}")
col4.metric("P-value", f"{results['p_value']:.2e}")

st.subheader("Decision summary")
st.write(
    "The ad group converted at a statistically higher rate than the PSA group. "
    "However, the observed lift is below the pre-defined 2-percentage-point MDE, "
    "so a full rollout is not recommended on this result alone."
)

st.info("Use the pages in the left sidebar to explore Test Results, Funnel, and Cohort Retention.")