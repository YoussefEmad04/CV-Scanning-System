import streamlit as st

from services.openai_service import is_openai_configured


st.set_page_config(
    page_title="AI Recruitment & Resume Screening System",
    page_icon="📄",
    layout="wide",
)

st.title("AI Recruitment & Resume Screening System")
st.caption("A simple Streamlit university project for HR decision support.")

if not is_openai_configured():
    st.warning(
        "OPENAI_API_KEY is missing. The app will still open, but AI features will use simple demo fallbacks where possible."
    )

st.info(
    "This system is a decision-support tool. Final recruitment decisions should be made by a human reviewer."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("CV Upload")
    st.write("Upload PDF or DOCX resumes, extract text, and store candidate records locally.")

    st.subheader("Resume Ranking")
    st.write("Rank candidates using semantic similarity and explain results with simple LLM summaries.")

with col2:
    st.subheader("Bias Detection")
    st.write("Find potentially biased wording in job descriptions using readable rules.")

    st.subheader("Synthetic CVs")
    st.write("Generate simple demo CV records for testing charts and workflows.")

with col3:
    st.subheader("Style Transformation")
    st.write("Rewrite resume text in professional, ATS-friendly, or short-summary style.")

    st.subheader("RAG Assistant")
    st.write("Ask questions over uploaded CVs using simple chunk retrieval.")

st.divider()
st.write("Use the sidebar to open each module.")
