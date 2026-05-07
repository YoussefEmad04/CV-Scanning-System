import streamlit as st

from services.openai_service import is_openai_configured
from services.rag_service import (
    answer_question_with_rag,
    build_cv_chunks,
    get_cv_index_status,
    retrieve_relevant_chunks,
)
from services.storage_service import load_cv_records


st.set_page_config(page_title="RAG Assistant", layout="wide")
st.title("RAG Assistant over Uploaded CVs")

st.info(
    "This system is a decision-support tool. Final recruitment decisions should be made by a human reviewer."
)
if not is_openai_configured():
    st.warning("OpenAI API key is missing. RAG retrieval will use simple keyword search fallback.")

question = st.text_input("Ask a question about uploaded CVs")
st.caption(
    "Examples: Which candidates know Python? Which CV has Airflow experience? Compare the top candidates."
)

cv_records = load_cv_records()
if cv_records.empty:
    st.info("Upload CVs first from the Upload CVs page.")

if st.button("Ask", type="primary"):
    if not question.strip():
        st.error("Please enter a question.")
    elif cv_records.empty:
        st.error("No uploaded CVs found.")
    else:
        chunks = build_cv_chunks(cv_records)
        index_status = get_cv_index_status(chunks)
        if is_openai_configured() and index_status["missing_chunks"] > 0:
            st.info("Building CV search index for the first time. This may take a moment.")
            spinner_text = (
                f"Creating embeddings for {index_status['missing_chunks']} CV chunks..."
            )
        else:
            spinner_text = "Searching uploaded CVs..."

        with st.spinner(spinner_text):
            retrieved = retrieve_relevant_chunks(question, chunks, top_k=3)
            answer = answer_question_with_rag(question, retrieved)

        st.subheader("Answer")
        st.write(answer)

        st.subheader("Sources")
        for chunk in retrieved:
            with st.expander(f"{chunk['file_name']} - score {chunk['score']:.2f}"):
                st.write(chunk["text"])
