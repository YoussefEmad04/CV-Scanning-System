import os
from datetime import datetime
from uuid import uuid4

import streamlit as st

from services.resume_parser import extract_candidate_name_simple, extract_text
from services.storage_service import load_cv_records, save_cv_record
from services.ui_helpers import apply_custom_css, render_sidebar_status


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploaded_cvs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Upload CVs", layout="wide")
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
    .page-hero p { color: #D1D5DB !important; max-width: 900px; margin-bottom: 0; }
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
    .section-card h2, .section-card h3, .section-card p,
    .metric-card .value, .empty-card h3, .empty-card p { color: #F9FAFB !important; }
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
        <span class="page-badge">Upload Module</span>
        <h1>Upload CVs</h1>
        <p>Upload and parse candidate resumes for analysis. Supported files are saved locally for ranking, RAG, and dashboard workflows.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "processed_uploads" not in st.session_state:
    st.session_state.processed_uploads = set()

cv_records = load_cv_records()
c1, c2, c3 = st.columns(3)
for col, (label, value) in zip(
    [c1, c2, c3],
    [
        ("Total CVs", len(cv_records)),
        ("Parsed This Session", len(st.session_state.processed_uploads)),
        ("Supported Formats", "PDF / DOCX"),
    ],
):
    with col:
        st.markdown(
            f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
            unsafe_allow_html=True,
        )

st.markdown("<h2 class='section-title'>Upload Resume Files</h2>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-card'><p class='muted'>Add PDF or DOCX resumes. Text extraction runs immediately after upload.</p></div>",
    unsafe_allow_html=True,
)
uploaded_files = st.file_uploader(
    "Drag and drop resumes here",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

parsed_count = 0
failed_count = 0
if uploaded_files:
    for uploaded_file in uploaded_files:
        upload_key = f"{uploaded_file.name}-{uploaded_file.size}"
        if upload_key in st.session_state.processed_uploads:
            continue

        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        try:
            with st.spinner(f"Parsing {uploaded_file.name}..."):
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                extracted_text = extract_text(file_path)
                record = {
                    "candidate_id": str(uuid4())[:8],
                    "file_name": uploaded_file.name,
                    "candidate_name": extract_candidate_name_simple(extracted_text, uploaded_file.name),
                    "extracted_text": extracted_text,
                    "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                save_cv_record(record)
                st.session_state.processed_uploads.add(upload_key)
                parsed_count += 1
            st.success(f"Parsed {uploaded_file.name}")
        except Exception as exc:
            failed_count += 1
            st.warning(f"Could not parse {uploaded_file.name}: {exc}")

    if parsed_count or failed_count:
        a, b = st.columns(2)
        for col, (label, value) in zip([a, b], [("Parsed CVs", parsed_count), ("Failed CVs", failed_count)]):
            with col:
                st.markdown(
                    f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
                    unsafe_allow_html=True,
                )

st.markdown("<h2 class='section-title'>Uploaded CV Records</h2>", unsafe_allow_html=True)
cv_records = load_cv_records()

if cv_records.empty:
    st.markdown(
        "<div class='empty-card'><h3>No CVs uploaded yet</h3><p class='muted'>Upload resumes above to populate the candidate database.</p></div>",
        unsafe_allow_html=True,
    )
else:
    display_cols = ["candidate_id", "candidate_name", "file_name", "upload_time"]
    st.dataframe(cv_records[display_cols], use_container_width=True, hide_index=True)

    with st.expander("Preview extracted text", expanded=False):
        selected_file = st.selectbox("Choose a CV", cv_records["file_name"].tolist())
        preview = cv_records.loc[cv_records["file_name"] == selected_file, "extracted_text"].iloc[-1]
        st.text_area("Extracted text", preview[:4000], height=300)
