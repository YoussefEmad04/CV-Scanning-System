import plotly.express as px
import streamlit as st

from services.openai_service import is_openai_configured
from services.ranking_service import rank_candidates
from services.storage_service import load_cv_records, save_ranking_results


st.set_page_config(page_title="Resume Ranking", layout="wide")
st.title("Resume Ranking")

st.info(
    "This system is a decision-support tool. Final recruitment decisions should be made by a human reviewer."
)
st.warning(
    "Do not rank candidates based on gender, age, nationality, religion, marital status, address, photo, or other protected attributes."
)

if not is_openai_configured():
    st.warning("OpenAI API key is missing. Ranking will use simple keyword matching fallback.")

job_description = st.text_area("Paste the job description", height=220)
cv_records = load_cv_records()

if cv_records.empty:
    st.info("Upload CVs first from the Upload CVs page.")

if st.button("Rank Candidates", type="primary"):
    if not job_description.strip():
        st.error("Please enter a job description.")
    elif cv_records.empty:
        st.error("No uploaded CVs found.")
    else:
        with st.spinner("Ranking candidates..."):
            results = rank_candidates(job_description, cv_records)
            save_ranking_results(results)

        st.success("Ranking completed and saved.")
        st.dataframe(results, use_container_width=True)

        fig = px.bar(
            results,
            x="candidate_name",
            y="match_score",
            color="match_score",
            title="Candidate Match Scores",
            labels={"candidate_name": "Candidate", "match_score": "Match Score (%)"},
        )
        st.plotly_chart(fig, use_container_width=True)
