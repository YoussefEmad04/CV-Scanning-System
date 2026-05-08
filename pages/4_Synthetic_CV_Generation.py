import os
import zipfile
from io import BytesIO

import pandas as pd
import plotly.express as px
import streamlit as st

from services.storage_service import load_synthetic_cvs, save_synthetic_cvs
from services.style_transformer_service import create_resume_pdf_bytes
from services.synthetic_cv_service import (
    generate_high_match_cv,
    generate_job_responsibilities,
    generate_synthetic_cvs,
)
from services.ui_helpers import apply_custom_css, render_sidebar_status


st.set_page_config(page_title="Synthetic CV Generation", layout="wide")
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
        <span class="page-badge">Synthetic Data Module</span>
        <h1>Synthetic CV Generation</h1>
        <p>Generate simulated candidate CV records and PDF resumes for demos, testing, and dashboard validation.</p>
        <div class="warning-note">Simulated GAN-generated CV data: these records are fake and must not be used as real candidate evidence.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

PDF_DIR = os.path.join("data", "synthetic", "pdf_cvs")
os.makedirs(PDF_DIR, exist_ok=True)


def save_pdf(name, pdf_bytes):
    safe_name = "".join(char for char in name if char.isalnum() or char in (" ", "_", "-")).strip()
    file_name = safe_name.replace(" ", "_") + ".pdf"
    path = os.path.join(PDF_DIR, file_name)
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    return path


def build_pdf_zip(df):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for index, row in df.iterrows():
            resume_text = row.get("resume_text", "")
            name = row.get("name", f"synthetic_cv_{index + 1}")
            pdf_bytes = create_resume_pdf_bytes(resume_text, title=name)
            pdf_path = save_pdf(name, pdf_bytes)
            zip_file.write(pdf_path, arcname=os.path.basename(pdf_path))
    buffer.seek(0)
    return buffer.getvalue()


tab1, tab2 = st.tabs(["Generate by category", "Generate from requirements"])

with tab1:
    st.markdown("<h2 class='section-title'>Generation Controls</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-card'><p class='muted'>Choose a role family and generate a batch of synthetic CVs.</p></div>",
        unsafe_allow_html=True,
    )
    control_col, note_col = st.columns([1, 2])
    with control_col:
        job_category = st.selectbox(
            "Choose job category",
            ["AI Engineer", "Data Engineer", "Software Engineer", "Cybersecurity Analyst", "Data Analyst"],
        )
        count = st.slider("Number of synthetic CVs", min_value=1, max_value=25, value=5, step=1)
    with note_col:
        st.markdown(
            "<div class='section-card'><h3>Output</h3><p class='muted'>OpenAI-enabled generation creates detailed fake resume text and downloadable PDFs.</p></div>",
            unsafe_allow_html=True,
        )

    if st.button("Generate Synthetic CVs", type="primary"):
        with st.spinner("Generating synthetic CVs and PDFs..."):
            generated = generate_synthetic_cvs(job_category, int(count))
            save_synthetic_cvs(generated)
            zip_bytes = build_pdf_zip(generated)

        st.success(f"Generated and saved {len(generated)} synthetic CVs.")
        m1, m2, m3 = st.columns(3)
        for col, (label, value) in zip(
            [m1, m2, m3],
            [
                ("Generated CVs", len(generated)),
                ("Selected Category", job_category),
                ("Average Experience", f"{generated['years_of_experience'].mean():.1f} years"),
            ],
        ):
            with col:
                st.markdown(
                    f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
                    unsafe_allow_html=True,
                )

        table_tab, preview_tab, download_tab = st.tabs(["Table", "Preview", "Download"])
        with table_tab:
            st.dataframe(generated.drop(columns=["resume_text"], errors="ignore"), use_container_width=True)
        with preview_tab:
            selected_name = st.selectbox("Preview generated CV", generated["name"].tolist())
            preview_text = generated.loc[generated["name"] == selected_name, "resume_text"].iloc[0]
            st.text_area("Generated resume text", preview_text, height=320)
        with download_tab:
            st.download_button(
                "Download generated CV PDFs",
                data=zip_bytes,
                file_name="synthetic_cv_pdfs.zip",
                mime="application/zip",
            )

with tab2:
    st.markdown("<h2 class='section-title'>Requirements-Based Generation</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-card'><p class='muted'>Paste a role brief to generate responsibilities and one high-match synthetic CV.</p></div>",
        unsafe_allow_html=True,
    )
    requirements = st.text_area(
        "Paste full job post or project requirements",
        height=260,
        placeholder="Paste the full job post here, including role, responsibilities, required skills, and desirable skills.",
    )
    high_match_category = st.selectbox(
        "Target role",
        ["Data Engineer", "AI Engineer", "Software Engineer", "Cybersecurity Analyst", "Data Analyst"],
    )

    if st.button("Generate responsibilities and high-match fake CV"):
        if not requirements.strip():
            st.error("Please enter a job post or project requirements first.")
        else:
            with st.spinner("Generating responsibilities and synthetic CV..."):
                responsibilities = generate_job_responsibilities(requirements)
                cv = generate_high_match_cv(requirements, high_match_category)
                generated = pd.DataFrame([cv])
                save_synthetic_cvs(generated)
                pdf_bytes = create_resume_pdf_bytes(cv["resume_text"], title=cv["name"])
                pdf_path = save_pdf(cv["name"], pdf_bytes)

            st.markdown("<h2 class='section-title'>Generated Job Responsibilities</h2>", unsafe_allow_html=True)
            st.text_area("Responsibilities", responsibilities, height=180)

            st.markdown("<h2 class='section-title'>High-Match Synthetic CV</h2>", unsafe_allow_html=True)
            st.dataframe(generated.drop(columns=["resume_text"], errors="ignore"), use_container_width=True)
            st.text_area("Generated CV Text", cv["resume_text"], height=280)
            st.download_button(
                "Download high-match CV as PDF",
                data=pdf_bytes,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf",
            )

all_synthetic = load_synthetic_cvs()
if all_synthetic.empty:
    st.markdown(
        "<div class='empty-card'><h3>No synthetic CVs generated yet</h3><p class='muted'>Generate a batch above to populate this section.</p></div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown("<h2 class='section-title'>Saved Synthetic CVs</h2>", unsafe_allow_html=True)
    avg_exp = float(all_synthetic["years_of_experience"].mean()) if "years_of_experience" in all_synthetic else 0.0
    a, b, c = st.columns(3)
    for col, (label, value) in zip(
        [a, b, c],
        [
            ("Saved Synthetic CVs", len(all_synthetic)),
            ("Average Experience", f"{avg_exp:.1f} years"),
            ("Categories", all_synthetic["job_category"].nunique() if "job_category" in all_synthetic else 0),
        ],
    ):
        with col:
            st.markdown(
                f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
                unsafe_allow_html=True,
            )

    saved_table, saved_charts, saved_preview = st.tabs(["Table", "Charts", "Preview"])
    with saved_table:
        st.dataframe(all_synthetic.drop(columns=["resume_text"], errors="ignore"), use_container_width=True)

    with saved_charts:
        col1, col2 = st.columns(2)
        with col1:
            category_counts = all_synthetic.groupby("job_category").size().reset_index(name="count")
            fig = px.bar(category_counts, x="job_category", y="count", title="Job Category Distribution")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.histogram(
                all_synthetic,
                x="years_of_experience",
                nbins=8,
                title="Years of Experience Distribution",
            )
            st.plotly_chart(fig, use_container_width=True)

    with saved_preview:
        if "resume_text" not in all_synthetic:
            st.info("Older saved synthetic rows do not include resume text.")
        else:
            selected = st.selectbox("Preview saved synthetic CV", all_synthetic["name"].tolist())
            text = all_synthetic.loc[all_synthetic["name"] == selected, "resume_text"].iloc[-1]
            st.text_area("Saved resume text", text, height=320)
