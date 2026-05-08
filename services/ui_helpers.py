import streamlit as st

from services.rag_service import build_cv_chunks, get_cv_index_status
from services.storage_service import load_cv_records, load_ranking_results, load_synthetic_cvs


def apply_custom_css():
    st.markdown(
        """
        <style>
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
        .app-card {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            background: #FFFFFF;
            color: #111827;
            min-height: 132px;
        }
        .app-card h1, .app-card h2, .app-card h3, .app-card p, .app-card strong {
            color: #111827 !important;
        }
        .soft-card {
            border: 1px solid #E5E7EB;
            border-radius: 8px;
            padding: 1rem;
            background: #F9FAFB;
            color: #111827;
        }
        .soft-card h1, .soft-card h2, .soft-card h3, .soft-card p, .soft-card strong {
            color: #111827 !important;
        }
        .hero {
            border: 1px solid #D8E3F3;
            border-radius: 8px;
            padding: 1.4rem;
            background: #F8FBFF;
            color: #111827;
        }
        .hero h1, .hero h2, .hero h3, .hero p, .hero strong {
            color: #111827 !important;
        }
        .tag {
            display: inline-block;
            padding: 0.18rem 0.5rem;
            margin: 0.12rem;
            border-radius: 999px;
            font-size: 0.82rem;
            background: #EAF2FF;
            color: #1F4E79;
            border: 1px solid #C9DCF5;
        }
        .tag-missing {
            background: #FFF3E8;
            color: #9A3412;
            border-color: #FED7AA;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_status():
    cv_records = load_cv_records()
    ranking_results = load_ranking_results()
    synthetic_cvs = load_synthetic_cvs()

    st.sidebar.title("AI Recruitment System")
    st.sidebar.caption("AI-assisted recruitment decision-support system.")
    st.sidebar.divider()
    st.sidebar.metric("Uploaded CVs", len(cv_records))
    st.sidebar.metric("Ranked Candidates", len(ranking_results))
    st.sidebar.metric("Synthetic CVs", len(synthetic_cvs))
    st.sidebar.divider()
    st.sidebar.info("Use the page list above to move between modules.")


def metric_row(cv_records=None, ranking_results=None, synthetic_cvs=None):
    cv_records = load_cv_records() if cv_records is None else cv_records
    ranking_results = load_ranking_results() if ranking_results is None else ranking_results
    synthetic_cvs = load_synthetic_cvs() if synthetic_cvs is None else synthetic_cvs

    avg_score = 0.0
    if not ranking_results.empty and "match_score" in ranking_results:
        avg_score = float(ranking_results["match_score"].mean())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Uploaded CVs", len(cv_records))
    c2.metric("Ranked Candidates", len(ranking_results))
    c3.metric("Average Match", f"{avg_score:.1f}%")
    c4.metric("Synthetic CVs", len(synthetic_cvs))


def render_tags(items, class_name="tag"):
    if not items:
        st.caption("None detected")
        return
    tags = "".join(f"<span class='{class_name}'>{item.strip()}</span>" for item in items if item.strip())
    st.markdown(tags, unsafe_allow_html=True)


def get_rag_status(cv_records=None):
    cv_records = load_cv_records() if cv_records is None else cv_records
    if cv_records.empty:
        return {"total_chunks": 0, "cached_chunks": 0, "missing_chunks": 0}
    return get_cv_index_status(build_cv_chunks(cv_records))
