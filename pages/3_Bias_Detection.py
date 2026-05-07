import plotly.express as px
import streamlit as st

from services.bias_detection_service import detect_bias_terms, rewrite_job_description_neutrally
from services.openai_service import is_openai_configured


st.set_page_config(page_title="Bias Detection", layout="wide")
st.title("Bias Detection in Job Descriptions")

job_description = st.text_area("Paste a job description", height=240)

if st.button("Detect Bias", type="primary"):
    findings = detect_bias_terms(job_description)
    if findings.empty:
        st.success("No listed bias terms were detected.")
    else:
        st.warning("Potentially biased or problematic wording was found.")
        st.dataframe(findings, use_container_width=True)
        counts = findings.groupby("category").size().reset_index(name="count")
        fig = px.bar(counts, x="category", y="count", title="Bias Count by Category")
        st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Optional Neutral Rewrite")
if not is_openai_configured():
    st.info("Configure OPENAI_API_KEY to use the neutral rewrite feature.")

if st.button("Rewrite job description neutrally using OpenAI"):
    if not job_description.strip():
        st.error("Please enter a job description first.")
    else:
        with st.spinner("Rewriting..."):
            rewritten = rewrite_job_description_neutrally(job_description)
        st.text_area("Neutral rewritten version", rewritten, height=260)
