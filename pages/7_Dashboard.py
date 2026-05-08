from collections import Counter

import plotly.express as px
import streamlit as st

from services.ranking_service import extract_skills_simple
from services.storage_service import load_cv_records, load_ranking_results, load_synthetic_cvs
from services.ui_helpers import apply_custom_css, get_rag_status, render_sidebar_status


st.set_page_config(page_title="Dashboard", layout="wide")
apply_custom_css()
render_sidebar_status()

st.markdown(
    """
    <style>
    .page-hero {
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 1.7rem;
        background: linear-gradient(135deg, #111827 0%, #1F2937 60%, #263449 100%);
        color: #F9FAFB;
        margin-bottom: 1rem;
    }
    .page-hero h1 { color: #FFFFFF !important; margin: 0.35rem 0 0.45rem; font-size: 2rem; }
    .page-hero p { color: #D1D5DB !important; max-width: 920px; margin-bottom: 0; }
    .page-badge {
        display: inline-block;
        padding: 0.28rem 0.7rem;
        border-radius: 999px;
        background: #EAF2FF;
        color: #1F4E79 !important;
        border: 1px solid #9BB7D4;
        font-size: 0.85rem;
        font-weight: 650;
    }
    .section-card, .metric-card, .empty-card {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #111827;
        color: #F9FAFB !important;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .section-card h3, .section-card p, .empty-card h3, .empty-card p,
    .metric-card .value { color: #F9FAFB !important; }
    .muted, .metric-card .label { color: #CBD5E1 !important; }
    .metric-card .value { font-size: 1.8rem; font-weight: 750; margin-top: 0.25rem; }
    .metric-card { min-height: 112px; }
    .section-title { margin-top: 1.1rem; margin-bottom: 0.55rem; color: #F9FAFB !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-hero">
        <span class="page-badge">Dashboard Module</span>
        <h1>Dashboard</h1>
        <p>Review project status, ranking outcomes, synthetic CV coverage, RAG index health, and extracted skill summaries.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

cv_records = load_cv_records()
ranking = load_ranking_results()
synthetic = load_synthetic_cvs()
rag_status = get_rag_status(cv_records)

average_score = float(ranking["match_score"].mean()) if not ranking.empty and "match_score" in ranking else 0.0

cols = st.columns(5)
for col, (label, value) in zip(
    cols,
    [
        ("Uploaded CVs", len(cv_records)),
        ("Ranked Candidates", len(ranking)),
        ("Average Match", f"{average_score:.1f}%"),
        ("Synthetic CVs", len(synthetic)),
        ("RAG Chunks", rag_status["total_chunks"]),
    ],
):
    with col:
        st.markdown(
            f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
            unsafe_allow_html=True,
        )

overview_tab, ranking_tab, synthetic_tab, skills_tab = st.tabs(["Overview", "Ranking", "Synthetic CVs", "Skills"])

with overview_tab:
    st.markdown("<h2 class='section-title'>System Overview</h2>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.markdown(
            f"""
            <div class="section-card">
                <h3>Candidate Pipeline</h3>
                <p class="muted">Uploaded CVs: {len(cv_records)}</p>
                <p class="muted">Ranked candidates: {len(ranking)}</p>
                <p class="muted">Average match: {average_score:.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            f"""
            <div class="section-card">
                <h3>Generated and RAG Data</h3>
                <p class="muted">Synthetic CVs: {len(synthetic)}</p>
                <p class="muted">Total RAG chunks: {rag_status['total_chunks']}</p>
                <p class="muted">Cached RAG chunks: {rag_status['cached_chunks']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with ranking_tab:
    if ranking.empty or "match_score" not in ranking:
        st.markdown(
            "<div class='empty-card'><h3>No ranking results yet</h3><p class='muted'>Run resume ranking first to populate this dashboard view.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<h2 class='section-title'>Ranking Outcomes</h2>", unsafe_allow_html=True)
        st.markdown(
            "<div class='section-card'><p class='muted'>Filter and review candidate match scores for presentation-ready analysis.</p></div>",
            unsafe_allow_html=True,
        )
        min_score = st.slider("Minimum score for chart", 0, 100, 0)
        chart_data = ranking[ranking["match_score"] >= min_score]
        fig = px.bar(
            chart_data,
            x="candidate_name",
            y="match_score",
            color="match_score",
            title="Ranking Score Chart",
            labels={"candidate_name": "Candidate", "match_score": "Match Score (%)"},
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(chart_data, use_container_width=True, hide_index=True)

with synthetic_tab:
    if synthetic.empty or "job_category" not in synthetic:
        st.markdown(
            "<div class='empty-card'><h3>No synthetic CVs generated yet</h3><p class='muted'>Generate synthetic CVs to populate these charts.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<h2 class='section-title'>Synthetic CVs</h2>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            counts = synthetic.groupby("job_category").size().reset_index(name="count")
            fig = px.bar(counts, x="job_category", y="count", title="Synthetic Job Category Distribution")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig = px.histogram(
                synthetic,
                x="years_of_experience",
                nbins=8,
                title="Synthetic Years of Experience",
            )
            st.plotly_chart(fig, use_container_width=True)

with skills_tab:
    skill_counter = Counter()
    for text in cv_records.get("extracted_text", []):
        skill_counter.update(extract_skills_simple(text))

    if not skill_counter:
        st.markdown(
            "<div class='empty-card'><h3>No skills found yet</h3><p class='muted'>Upload CVs to populate skill statistics.</p></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<h2 class='section-title'>Skills Summary</h2>", unsafe_allow_html=True)
        top_n = st.slider("Number of skills", 5, 20, 10)
        skills_df = [{"skill": skill, "count": count} for skill, count in skill_counter.most_common(top_n)]
        fig = px.bar(skills_df, x="skill", y="count", title="Skills Frequency Chart")
        st.plotly_chart(fig, use_container_width=True)
