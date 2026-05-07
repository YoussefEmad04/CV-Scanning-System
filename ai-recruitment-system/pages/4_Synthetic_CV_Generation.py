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


st.set_page_config(page_title="Synthetic CV Generation", layout="wide")
st.title("Synthetic CV Generation")

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
    job_category = st.selectbox(
        "Choose job category",
        ["AI Engineer", "Data Engineer", "Software Engineer", "Cybersecurity Analyst", "Data Analyst"],
    )
    count = st.number_input("Number of synthetic CVs", min_value=1, max_value=100, value=10, step=1)

    if st.button("Generate Synthetic CVs", type="primary"):
        generated = generate_synthetic_cvs(job_category, int(count))
        save_synthetic_cvs(generated)
        zip_bytes = build_pdf_zip(generated)

        st.success(f"Generated and saved {len(generated)} synthetic CVs.")
        st.dataframe(generated.drop(columns=["resume_text"], errors="ignore"), use_container_width=True)
        st.download_button(
            "Download generated CV PDFs",
            data=zip_bytes,
            file_name="synthetic_cv_pdfs.zip",
            mime="application/zip",
        )

with tab2:
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

            st.subheader("Generated Job Responsibilities")
            st.text_area("Responsibilities", responsibilities, height=180)

            st.subheader("High-Match Synthetic CV")
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
    st.info("No synthetic CVs generated yet.")
else:
    st.subheader("Saved Synthetic CVs")
    st.dataframe(all_synthetic.drop(columns=["resume_text"], errors="ignore"), use_container_width=True)

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
