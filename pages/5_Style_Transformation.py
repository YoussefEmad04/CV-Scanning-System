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
from services.ui_helpers import apply_custom_css, render_sidebar_status


st.set_page_config(page_title="Style Transformation", layout="wide")
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
    .section-card, .empty-card {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #111827;
        color: #F9FAFB !important;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .section-card h3, .section-card p, .empty-card h3, .empty-card p { color: #F9FAFB !important; }
    .muted { color: #CBD5E1 !important; }
    .warning-note {
        margin-top: 0.9rem;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        background: #FEF3C7;
        color: #78350F !important;
        border: 1px solid #F59E0B;
        font-weight: 650;
    }
    .section-title { margin-top: 1.1rem; margin-bottom: 0.55rem; color: #F9FAFB !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="page-hero">
        <span class="page-badge">Style Module</span>
        <h1>Resume Style Transformation</h1>
        <p>Rewrite resume text into a clearer professional, ATS-friendly, or concise summary style.</p>
        <div class="warning-note">The system improves wording only and should not invent experience, skills, education, or certificates.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not is_openai_configured():
    st.warning("OpenAI API key is missing. A simple rule-based fallback will be used.")

uploaded_text = ""
st.markdown(
    "<div class='section-card'><h3>Upload Resume</h3><p class='muted'>Upload a PDF or DOCX resume, or paste text directly into the input card below.</p></div>",
    unsafe_allow_html=True,
)
uploaded_resume = st.file_uploader("Upload resume PDF or DOCX", type=["pdf", "docx"])
if uploaded_resume:
    try:
        suffix = os.path.splitext(uploaded_resume.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_resume.getbuffer())
            temp_path = temp_file.name
        with st.spinner("Extracting resume text..."):
            uploaded_text = extract_text(temp_path)
        os.remove(temp_path)
        st.success(f"Extracted text from {uploaded_resume.name}")
    except Exception as exc:
        st.warning(f"Could not extract text from uploaded resume: {exc}")

left, right = st.columns(2)
with left:
    st.markdown("<h2 class='section-title'>Input Resume Text</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-card'><p class='muted'>Choose a style and provide the source resume text.</p></div>",
        unsafe_allow_html=True,
    )
    style = st.radio(
        "Choose writing style",
        ["Professional style", "ATS-friendly style", "Short summary style"],
        horizontal=True,
    )
    resume_text = st.text_area("Resume text", value=uploaded_text, height=360)

with right:
    st.markdown("<h2 class='section-title'>Transformed Output</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-card'><p class='muted'>The rewritten resume and PDF download will appear here after transformation.</p></div>",
        unsafe_allow_html=True,
    )
    if st.button("Transform Resume", type="primary", use_container_width=True):
        if not resume_text.strip():
            st.error("Please upload or paste resume text first.")
        else:
            with st.spinner("Transforming resume text and preparing PDF..."):
                transformed = transform_resume_style(resume_text, style)
                pdf_bytes = create_resume_pdf_bytes(transformed, title=get_pdf_title_for_style(style))
            st.session_state.transformed_resume = transformed
            st.session_state.transformed_pdf = pdf_bytes
            st.session_state.transformed_style = style

    transformed = st.session_state.get("transformed_resume", "")
    if transformed:
        st.text_area("Transformed resume text", transformed, height=360)
        st.download_button(
            "Download transformed resume as PDF",
            data=st.session_state.transformed_pdf,
            file_name=f"transformed_resume_{st.session_state.transformed_style.lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.markdown(
            "<div class='empty-card'><h3>No transformed output yet</h3><p class='muted'>Upload or paste resume text, then run the transformation.</p></div>",
            unsafe_allow_html=True,
        )
