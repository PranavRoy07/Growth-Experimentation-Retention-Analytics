import streamlit as st
import plotly.express as px
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from app_utils import load_ab_data, experiment_results

st.set_page_config(page_title="Test Results", layout="wide")
st.title("A/B Test Results")

results = experiment_results(load_ab_data())
summary = results["summary"].reset_index()

col1, col2, col3 = st.columns(3)
col1.metric("P-value", f"{results['p_value']:.2e}")
col2.metric("Conversion lift", f"{results['lift']:.2%}")
col3.metric(
    "95% confidence interval",
    f"{results['ci_lower']:.2%} to {results['ci_upper']:.2%}"
)

chart = px.bar(
    summary,
    x="test_group",
    y="mean",
    text="mean",
    labels={"test_group": "Group", "mean": "Conversion rate"},
    color="test_group",
)
chart.update_traces(texttemplate="%{text:.2%}", textposition="outside")
chart.update_yaxes(tickformat=".0%")
st.plotly_chart(chart, use_container_width=True)

st.subheader("Interpretation")
st.write(
    "The p-value is below 0.05, so the conversion difference is statistically significant. "
    "The lift is below the 2-percentage-point MDE, so it is not practically significant "
    "under the project decision rule."
)