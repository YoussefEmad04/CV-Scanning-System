from collections import Counter

import plotly.express as px
import streamlit as st

from services.ranking_service import extract_skills_simple
from services.storage_service import load_cv_records, load_ranking_results, load_synthetic_cvs


st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard")

cv_records = load_cv_records()
ranking = load_ranking_results()
synthetic = load_synthetic_cvs()

uploaded_count = len(cv_records)
ranked_count = len(ranking)
average_score = float(ranking["match_score"].mean()) if not ranking.empty and "match_score" in ranking else 0.0
synthetic_count = len(synthetic)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Uploaded CVs", uploaded_count)
col2.metric("Ranked Candidates", ranked_count)
col3.metric("Average Match Score", f"{average_score:.1f}%")
col4.metric("Synthetic CVs", synthetic_count)

st.divider()

if not ranking.empty and "match_score" in ranking:
    fig = px.bar(
        ranking,
        x="candidate_name",
        y="match_score",
        title="Ranking Scores",
        labels={"candidate_name": "Candidate", "match_score": "Match Score (%)"},
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No ranking results available yet.")

if not synthetic.empty and "job_category" in synthetic:
    counts = synthetic.groupby("job_category").size().reset_index(name="count")
    fig = px.bar(counts, x="job_category", y="count", title="Synthetic Job Category Distribution")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No synthetic CV data available yet.")

skill_counter = Counter()
for text in cv_records.get("extracted_text", []):
    skill_counter.update(extract_skills_simple(text))

if skill_counter:
    skills_df = (
        {"skill": skill, "count": count}
        for skill, count in skill_counter.most_common(10)
    )
    fig = px.bar(list(skills_df), x="skill", y="count", title="Most Common Skills in Uploaded CVs")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No skills found yet. Upload CVs to populate skill statistics.")
