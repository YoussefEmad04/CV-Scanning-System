import streamlit as st

from services.openai_service import is_openai_configured
from services.rag_service import (
    answer_question_with_rag,
    build_cv_chunks,
    get_cv_index_status,
    retrieve_relevant_chunks,
)
from services.storage_service import load_cv_records
from services.ui_helpers import apply_custom_css, render_sidebar_status


st.set_page_config(page_title="RAG Assistant", layout="wide")
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
    .section-card, .metric-card, .answer-card, .empty-card {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #111827;
        color: #F9FAFB !important;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .section-card h3, .section-card p, .answer-card p, .empty-card h3, .empty-card p,
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
        <span class="page-badge">RAG Module</span>
        <h1>RAG Assistant</h1>
        <p>Ask questions over uploaded resumes using a retrieval-based assistant.</p>
        <div class="warning-note">Human review required: answers are grounded in retrieved snippets but should be verified against source resumes.</div>
    </div>
    """,
    unsafe_allow_html=True,
)
if not is_openai_configured():
    st.warning("OpenAI API key is missing. RAG retrieval will use simple keyword search fallback.")

cv_records = load_cv_records()
chunks = build_cv_chunks(cv_records) if not cv_records.empty else []
index_status = get_cv_index_status(chunks)

m1, m2, m3 = st.columns(3)
for col, (label, value) in zip(
    [m1, m2, m3],
    [
        ("Uploaded CVs", len(cv_records)),
        ("RAG Chunks", index_status["total_chunks"]),
        ("Cached Chunks", index_status["cached_chunks"]),
    ],
):
    with col:
        st.markdown(
            f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
            unsafe_allow_html=True,
        )

if cv_records.empty:
    st.markdown(
        "<div class='empty-card'><h3>RAG index not built yet</h3><p class='muted'>Upload CVs first so the assistant can retrieve relevant snippets.</p></div>",
        unsafe_allow_html=True,
    )
else:
    if index_status["missing_chunks"] > 0:
        st.warning("Building CV search index for the first time may take a moment.")
    if st.button("Build / refresh RAG index"):
        with st.spinner("Building CV search index..."):
            retrieve_relevant_chunks("candidate skills experience projects", chunks, top_k=3)
        st.success("RAG index checked. Repeated questions should be faster.")

sample_questions = [
    "Which candidates mention Python?",
    "Which candidates mention Airflow?",
    "Compare the top candidates.",
    "Which candidate is best for AI Engineer?",
]

st.markdown("<h2 class='section-title'>Ask a Question</h2>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-card'><p class='muted'>Ask about candidate skills, experience, tools, projects, or comparisons across uploaded resumes.</p></div>",
    unsafe_allow_html=True,
)
cols = st.columns(4)
for col, sample in zip(cols, sample_questions):
    if col.button(sample, use_container_width=True):
        st.session_state.rag_question = sample

question = st.text_input("Question", value=st.session_state.get("rag_question", ""))

if st.button("Ask", type="primary"):
    if not question.strip():
        st.error("Please enter a question.")
    elif cv_records.empty:
        st.error("No uploaded CVs found.")
    else:
        index_status = get_cv_index_status(chunks)
        if is_openai_configured() and index_status["missing_chunks"] > 0:
            st.info("Building CV search index for the first time. This may take a moment.")
            spinner_text = f"Creating embeddings for {index_status['missing_chunks']} CV chunks..."
        else:
            spinner_text = "Searching uploaded CVs..."

        with st.spinner(spinner_text):
            retrieved = retrieve_relevant_chunks(question, chunks, top_k=3)
            answer = answer_question_with_rag(question, retrieved)

        st.session_state.rag_answer = answer
        st.session_state.rag_sources = retrieved

answer = st.session_state.get("rag_answer")
sources = st.session_state.get("rag_sources", [])
if answer:
    st.markdown("<h2 class='section-title'>Assistant Answer</h2>", unsafe_allow_html=True)
    st.markdown(f"<div class='answer-card'><p>{answer}</p></div>", unsafe_allow_html=True)

    st.markdown("<h2 class='section-title'>Sources and Retrieved Snippets</h2>", unsafe_allow_html=True)
    for chunk in sources:
        with st.expander(f"{chunk['file_name']} - relevance {chunk['score']:.2f}"):
            st.write(chunk["text"])
