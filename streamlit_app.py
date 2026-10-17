import pandas as pd
import plotly.express as px
import streamlit as st

from app.dashboard_data import latest_video_frame, read_exports

st.set_page_config(page_title="YouTube Analytics | MrBeast", page_icon="▶", layout="wide")
st.markdown(
    """
    <style>
    .stApp { background:#151515; color:#f5f5f5; }
    .block-container { padding-top:1rem; max-width:1600px; }
    [data-testid="stMetric"] { background:#202020; border:1px solid #303030; padding:13px 16px; border-radius:8px; }
    [data-testid="stMetricLabel"] { color:#c4c4c4; font-size:.78rem; }
    [data-testid="stMetricValue"] { color:#f8f8f8; font-weight:700; }
    </style>
    """,
    unsafe_allow_html=True,
)

videos, metrics, _ = read_exports()
frame = latest_video_frame(videos, metrics)
st.title("YouTube Analytics Dashboard")
channel = videos["channel_title"].dropna().iloc[0] if not videos.empty and videos["channel_title"].notna().any() else "MrBeast"
st.caption(f"Channel: {channel} · Public YouTube statistics · Latest stored snapshot per video")

if frame.empty:
    st.warning("No exported video data found. Collect channel data, then run `python -m scripts.export_data`.")
    st.stop()

views = frame["views"].dropna()
rates = frame["engagement_rate"].dropna()
likes_sum = frame["likes"].sum(min_count=1)
comments_sum = frame["comments"].sum(min_count=1)
kpis = st.columns(7)
cards = [
    ("Videos Analyzed", f"{frame.video_id.nunique():,}"),
    ("Sum of Views", f"{views.sum()/1e9:.1f}bn" if len(views) else "Unavailable"),
    ("Avg Engagement Rate", f"{rates.mean():.2f}%" if len(rates) else "Unavailable"),
    ("Sum of Comments", f"{comments_sum/1e6:.1f}M" if pd.notna(comments_sum) else "Unavailable"),
    ("Sum of Likes", f"{likes_sum/1e9:.2f}bn" if pd.notna(likes_sum) else "Unavailable"),
    ("Avg Like Rate", f"{frame.like_rate.mean():.2f}%" if frame.like_rate.notna().any() else "Unavailable"),
    ("Avg Comment Rate", f"{frame.comment_rate.mean():.2f}%" if frame.comment_rate.notna().any() else "Unavailable"),
]
for col, (label, value) in zip(kpis, cards):
    col.metric(label, value)

# One latest observation per video; month groups are upload cohorts, not daily growth.
plot = frame.dropna(subset=["published_at", "views"]).copy()
plot["Publishing Month"] = plot["published_at"].dt.to_period("M").astype(str)
monthly = plot.groupby("Publishing Month", as_index=False).agg(views=("views", "sum"), videos=("video_id", "nunique"))
ranked = frame.dropna(subset=["views"]).nlargest(10, "views").sort_values("views")
left, right = st.columns([0.85, 1.4], gap="small")
with left:
    st.subheader("Views by Publishing Month")
    fig = px.line(monthly, x="Publishing Month", y="views", markers=True)
    fig.update_traces(line_color="#38a9ff", fill="tozeroy", fillcolor="rgba(56,169,255,.22)")
    fig.update_layout(template="plotly_dark", height=290, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="#1c1c1c", plot_bgcolor="#1c1c1c", xaxis_title=None, yaxis_tickformat=".2s")
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader("Top 10 Videos by Views")
    fig = px.bar(ranked, x="views", y="title", orientation="h", text="views")
    fig.update_traces(marker_color="#38a9ff", texttemplate="%{x:.3s}", textposition="outside", cliponaxis=False)
    fig.update_layout(template="plotly_dark", height=290, margin=dict(l=8, r=38, t=8, b=8), paper_bgcolor="#1c1c1c", plot_bgcolor="#1c1c1c", xaxis_title="Views", yaxis_title=None, xaxis_tickformat=".2s")
    st.plotly_chart(fig, use_container_width=True)

left, middle, right = st.columns([1.2, 1, 1], gap="small")
with left:
    st.subheader("Videos by Engagement Rate")
    table = frame.sort_values("engagement_rate", ascending=False, na_position="last")[["title", "engagement_rate", "views", "likes", "comments"]].head(15).copy()
    table["engagement_rate"] = table["engagement_rate"].map(lambda x: f"{x:.2f}%" if pd.notna(x) else "Unavailable")
    st.dataframe(table, use_container_width=True, hide_index=True, height=330)
with middle:
    st.subheader("Year-wise Engagement Comparison")
    years = frame.dropna(subset=["published_at", "engagement_rate"]).copy()
    years["Year"] = years["published_at"].dt.year.astype(str)
    yearly = years.groupby("Year", as_index=False).agg(engagement_rate=("engagement_rate", "median"), videos=("video_id", "nunique"))
    if yearly.empty:
        st.info("No videos have complete engagement metrics.")
    else:
        fig = px.pie(yearly, names="Year", values="videos", color_discrete_sequence=["#42c4e8", "#328aff", "#8585ff", "#43ddba"])
        fig.update_layout(template="plotly_dark", height=330, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor="#1c1c1c", legend_title=None)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Median engagement by year: " + " · ".join(f"{r.Year}: {r.engagement_rate:.2f}%" for r in yearly.itertuples()))
with right:
    st.subheader("Videos Interaction Coverage")
    coverage = pd.DataFrame({"Metric": ["Views available", "Likes available", "Comments available"], "Videos": [int(frame.views.notna().sum()), int(frame.likes.notna().sum()), int(frame.comments.notna().sum())]})
    fig = px.pie(coverage, names="Metric", values="Videos", hole=0.62, color_discrete_sequence=["#42c4e8", "#328aff", "#8585ff"])
    fig.update_layout(template="plotly_dark", height=330, margin=dict(l=5, r=5, t=5, b=5), paper_bgcolor="#1c1c1c", legend_title=None)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("Data and metric notes"):
    st.write("Counts use each video's latest stored observation, so repeated snapshots are not added together. Engagement rate = (available likes + comments) / views × 100; it is calculated only when views are positive and both statistics are available.")
    st.write(f"Rows with complete engagement data: {len(rates):,} of {len(frame):,}. Historical snapshots: {len(metrics):,}. Missing public statistics are unavailable, not zero.")
