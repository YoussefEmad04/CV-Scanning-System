import pandas as pd
import plotly.express as px
import streamlit as st

from services.openai_service import is_openai_configured
from services.ranking_service import rank_candidates
from services.storage_service import load_cv_records, load_ranking_results, save_ranking_results
from services.ui_helpers import apply_custom_css, render_sidebar_status, render_tags


st.set_page_config(page_title="Resume Ranking", layout="wide")
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
    .section-card, .candidate-card, .empty-card {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #111827;
        color: #F9FAFB !important;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .candidate-card h3, .candidate-card p, .section-card p, .empty-card h3, .empty-card p {
        color: #F9FAFB !important;
    }
    .muted { color: #CBD5E1 !important; }
    .warning-note {
        margin: 0.75rem 0 1rem;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        background: #FEF3C7;
        color: #78350F !important;
        border: 1px solid #F59E0B;
        font-weight: 650;
    }
    .tag {
        display: inline-block;
        padding: 0.2rem 0.55rem;
        margin: 0.12rem;
        border-radius: 999px;
        background: #EAF2FF;
        color: #1F4E79 !important;
        border: 1px solid #9BB7D4;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .tag-missing {
        background: #FFF3E8;
        color: #9A3412 !important;
        border-color: #FED7AA;
    }
    .section-title { margin-top: 1.1rem; margin-bottom: 0.55rem; color: #F9FAFB !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-hero">
        <span class="page-badge">Ranking Module</span>
        <h1>Resume Ranking</h1>
        <p>Rank candidates by comparing CVs with the job description using AI-powered semantic matching.</p>
        <div class="warning-note">Human review required: use match scores as decision support, not as an automated hiring decision.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.warning("Do not rank candidates based on protected or sensitive attributes.")

if not is_openai_configured():
    st.warning("OpenAI API key is missing. Ranking will use simple keyword matching fallback.")

cv_records = load_cv_records()
ranking_results = load_ranking_results()

st.markdown("<h2 class='section-title'>Job Description</h2>", unsafe_allow_html=True)
st.markdown(
    f"<div class='section-card'><p class='muted'>Paste the role description and run ranking against {len(cv_records)} uploaded CVs.</p></div>",
    unsafe_allow_html=True,
)
job_description = st.text_area("Paste the job description", height=180)
run_col, data_col = st.columns([1, 3])
with run_col:
    run_ranking = st.button("Run / Rerun Ranking", type="primary", use_container_width=True)
with data_col:
    st.caption(f"Loaded CVs: {len(cv_records)}")

if cv_records.empty:
    st.markdown(
        "<div class='empty-card'><h3>No CVs uploaded yet</h3><p class='muted'>Upload resumes before running candidate ranking.</p></div>",
        unsafe_allow_html=True,
    )

if run_ranking:
    if not job_description.strip():
        st.error("Please enter a job description.")
    elif cv_records.empty:
        st.error("No uploaded CVs found.")
    else:
        with st.spinner("Ranking candidates and generating explanations..."):
            ranking_results = rank_candidates(job_description, cv_records)
            save_ranking_results(ranking_results)
        st.success("Ranking completed and saved.")

if ranking_results.empty:
    st.markdown(
        "<div class='empty-card'><h3>No ranking results yet</h3><p class='muted'>Run resume ranking to generate candidate match scores.</p></div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown("<h2 class='section-title'>Results Explorer</h2>", unsafe_allow_html=True)

    all_skills = sorted(
        {
            skill.strip()
            for skills in ranking_results.get("matched_skills", pd.Series(dtype=str)).astype(str)
            for skill in skills.split(",")
            if skill.strip()
        }
    )
    st.markdown(
        "<div class='section-card'><p class='muted'>Filter candidates by score, name, file, or matched skill.</p></div>",
        unsafe_allow_html=True,
    )
    f1, f2, f3, f4 = st.columns([1, 1, 1, 1])
    min_score = f1.slider("Minimum score", 0, 100, 0)
    search = f2.text_input("Search candidate/file")
    skill_filter = f3.selectbox("Matched skill", ["All"] + all_skills)
    sort_order = f4.selectbox("Sort", ["Highest score first", "Lowest score first"])

    filtered = ranking_results.copy()
    filtered = filtered[filtered["match_score"] >= min_score]
    if search:
        search_lower = search.lower()
        filtered = filtered[
            filtered["candidate_name"].astype(str).str.lower().str.contains(search_lower)
            | filtered["file_name"].astype(str).str.lower().str.contains(search_lower)
        ]
    if skill_filter != "All":
        filtered = filtered[filtered["matched_skills"].astype(str).str.contains(skill_filter, case=False, na=False)]
    filtered = filtered.sort_values("match_score", ascending=sort_order == "Lowest score first")

    summary_tab, details_tab, charts_tab = st.tabs(["Summary", "Details", "Charts"])

    with summary_tab:
        st.caption(f"Showing {len(filtered)} of {len(ranking_results)} candidates")
        for _, row in filtered.head(6).iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div class="candidate-card">
                        <h3>{row.get('candidate_name', 'Candidate')}</h3>
                        <p class="muted"><strong>File:</strong> {row.get('file_name', '')}</p>
                        <p><strong>Match score:</strong> {row['match_score']:.2f}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(float(row["match_score"]) / 100)
                c1, c2 = st.columns(2)
                with c1:
                    st.caption("Matched skills")
                    render_tags(str(row.get("matched_skills", "")).split(","))
                with c2:
                    st.caption("Missing skills")
                    render_tags(str(row.get("missing_skills", "")).split(","), class_name="tag tag-missing")
                with st.expander("LLM explanation"):
                    st.write(row.get("explanation", ""))
                st.divider()

    with details_tab:
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button(
            "Export filtered results as CSV",
            data=filtered.to_csv(index=False).encode("utf-8"),
            file_name="filtered_ranking_results.csv",
            mime="text/csv",
        )

    with charts_tab:
        if filtered.empty:
            st.markdown(
                "<div class='empty-card'><h3>No matching candidates</h3><p class='muted'>Adjust the filters to broaden the result set.</p></div>",
                unsafe_allow_html=True,
            )
        else:
            fig = px.bar(
                filtered,
                x="candidate_name",
                y="match_score",
                color="match_score",
                title="Candidate Match Scores",
                labels={"candidate_name": "Candidate", "match_score": "Match Score (%)"},
            )
            st.plotly_chart(fig, use_container_width=True)
