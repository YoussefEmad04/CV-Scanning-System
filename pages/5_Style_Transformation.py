import os
import tempfile

import streamlit as st

from services.openai_service import is_openai_configured
from services.resume_parser import extract_text
from services.style_transformer_service import (
    create_resume_pdf_bytes,
    get_pdf_title_for_style,
    transform_resume_style,
)


st.set_page_config(page_title="Style Transformation", layout="wide")
st.title("Resume Style Transformation")

if not is_openai_configured():
    st.warning("OpenAI API key is missing. A simple rule-based fallback will be used.")

uploaded_resume = st.file_uploader("Upload resume PDF or DOCX", type=["pdf", "docx"])
uploaded_text = ""

if uploaded_resume:
    try:
        suffix = os.path.splitext(uploaded_resume.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_resume.getbuffer())
            temp_path = temp_file.name
        uploaded_text = extract_text(temp_path)
        os.remove(temp_path)
        st.success(f"Extracted text from {uploaded_resume.name}")
    except Exception as exc:
        st.warning(f"Could not extract text from uploaded resume: {exc}")

resume_text = st.text_area("Resume text", value=uploaded_text, height=260)
style = st.selectbox(
    "Choose writing style",
    ["Professional style", "ATS-friendly style", "Short summary style"],
)

if st.button("Transform Resume", type="primary"):
    if not resume_text.strip():
        st.error("Please paste resume text first.")
    else:
        with st.spinner("Transforming resume text..."):
            transformed = transform_resume_style(resume_text, style)
            pdf_bytes = create_resume_pdf_bytes(transformed, title=get_pdf_title_for_style(style))
        st.text_area("Transformed resume text", transformed, height=320)
        st.download_button(
            "Download transformed resume as PDF",
            data=pdf_bytes,
            file_name=f"transformed_resume_{style.lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
