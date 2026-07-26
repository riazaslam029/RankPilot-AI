import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="RankPilot AI", layout="wide", page_icon="🚀")


def load_recommendations():
    path = Path("data/processed/recommendations.csv")
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def load_features():
    path = Path("data/processed/features.parquet")
    if path.exists():
        return pd.read_parquet(str(path))
    return pd.DataFrame()


st.title("🚀 RankPilot AI — Search Intelligence Command Center")
st.markdown("AI-powered page action recommendations for search performance optimization")

recs = load_recommendations()

if recs.empty:
    st.warning("No recommendations found. Run the analysis pipeline first.")
    st.stop()

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Pages Analyzed", len(recs))
col2.metric("Top Priority (Critical)", len(recs[recs.get("priority_tier") == "critical"]))
col3.metric("High Priority", len(recs[recs.get("priority_tier") == "high"]))
col4.metric("Est. Monthly Impact", f"${recs.get('estimated_monthly_impact_usd', pd.Series([0])).sum():,.0f}")

st.markdown("---")

st.subheader("Action Distribution")
action_counts = recs["primary_action"].value_counts()
fig = px.pie(
    values=action_counts.values,
    names=action_counts.index,
    color_discrete_sequence=px.colors.qualitative.Set2,
    hole=0.4,
)
fig.update_layout(showlegend=True, height=400)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

st.subheader("Top Opportunities")
filtered = recs[["priority_rank", "page", "primary_action", "priority_score", "priority_tier", "confidence", "reason_codes", "estimated_monthly_impact_usd"]].copy()
filtered.columns = ["Rank", "Page", "Action", "Priority Score", "Tier", "Confidence", "Reason Codes", "Est. Impact ($)"]
filtered["Tier"] = filtered["Tier"].map({
    "critical": "🔴 Critical", "high": "🟠 High", "medium": "🟡 Medium",
    "low": "🟢 Low", "monitor": "⚪ Monitor"
})
filtered = filtered.sort_values("Priority Score", ascending=False)

st.dataframe(filtered.head(50), use_container_width=True, height=500)

st.markdown("---")

st.subheader("Priority Score Distribution")
fig2 = px.histogram(recs, x="priority_score", color="priority_tier", nbins=50,
                     color_discrete_map={
                         "critical": "red", "high": "orange", "medium": "gold",
                         "low": "lightgreen", "monitor": "lightgray"
                     })
fig2.update_layout(height=400, xaxis_title="Priority Score", yaxis_title="Page Count")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

page = st.sidebar.selectbox("Filter by Action", ["All"] + sorted(recs["primary_action"].unique().tolist()))
tier = st.sidebar.selectbox("Filter by Tier", ["All"] + sorted(recs.get("priority_tier", pd.Series()).unique().tolist()))

df_filtered = recs
if page != "All":
    df_filtered = df_filtered[df_filtered["primary_action"] == page]
if tier != "All":
    df_filtered = df_filtered[df_filtered.get("priority_tier") == tier]

st.sidebar.markdown(f"**Showing {len(df_filtered)} pages**")

csv_path = "data/processed/recommendations_export.csv"
df_filtered.to_csv(csv_path, index=False)
st.sidebar.download_button("Export CSV", data=df_filtered.to_csv(index=False), file_name="rankpilot_recommendations.csv", mime="text/csv")
