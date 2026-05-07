import os
from datetime import datetime
from uuid import uuid4

import streamlit as st

from services.resume_parser import extract_candidate_name_simple, extract_text
from services.storage_service import load_cv_records, save_cv_record


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploaded_cvs")
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(page_title="Upload CVs", layout="wide")
st.title("Upload CVs")

if "processed_uploads" not in st.session_state:
    st.session_state.processed_uploads = set()

uploaded_files = st.file_uploader(
    "Upload one or more resume files",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        upload_key = f"{uploaded_file.name}-{uploaded_file.size}"
        if upload_key in st.session_state.processed_uploads:
            continue

        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        try:
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
            st.success(f"Uploaded and parsed {uploaded_file.name}")
        except Exception as exc:
            st.warning(f"Could not parse {uploaded_file.name}: {exc}")

st.subheader("Uploaded CV Records")
cv_records = load_cv_records()

if cv_records.empty:
    st.info("No CVs uploaded yet.")
else:
    st.dataframe(
        cv_records[["candidate_id", "candidate_name", "file_name", "upload_time"]],
        use_container_width=True,
    )

    selected_file = st.selectbox("Preview extracted text", cv_records["file_name"].tolist())
    preview = cv_records.loc[cv_records["file_name"] == selected_file, "extracted_text"].iloc[-1]
    st.text_area("Extracted text preview", preview[:3000], height=250)
