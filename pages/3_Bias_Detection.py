import plotly.express as px
import streamlit as st

from services.bias_detection_service import detect_bias_terms, rewrite_job_description_neutrally
from services.openai_service import is_openai_configured
from services.ui_helpers import apply_custom_css, render_sidebar_status


st.set_page_config(page_title="Bias Detection", layout="wide")
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
    .section-card, .finding-card, .empty-card {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #111827;
        color: #F9FAFB !important;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .section-card h3, .section-card p, .finding-card h3, .finding-card p,
    .empty-card h3, .empty-card p { color: #F9FAFB !important; }
    .muted { color: #CBD5E1 !important; }
    .warning-note {
        margin-bottom: 0.75rem;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        background: #FEF3C7;
        color: #78350F !important;
        border: 1px solid #F59E0B;
        font-weight: 650;
    }
    .success-note {
        margin-bottom: 0.75rem;
        padding: 0.85rem 1rem;
        border-radius: 8px;
        background: #DCFCE7;
        color: #14532D !important;
        border: 1px solid #22C55E;
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
        <span class="page-badge">Bias Module</span>
        <h1>Bias Detection</h1>
        <p>Detect potentially biased language in job descriptions and suggest neutral alternatives.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

sample = "We need a young energetic male data engineer who is a rockstar and native speaker."
if st.button("Load sample biased job description"):
    st.session_state.bias_text = sample

st.markdown("<h2 class='section-title'>Job Description Input</h2>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-card'><p class='muted'>Check job posts for wording that may discourage qualified candidates.</p></div>",
    unsafe_allow_html=True,
)
job_description = st.text_area(
    "Paste a job description",
    value=st.session_state.get("bias_text", ""),
    height=220,
)

if st.button("Detect Bias", type="primary"):
    st.session_state.bias_findings = detect_bias_terms(job_description)

findings = st.session_state.get("bias_findings")
if findings is not None:
    if findings.empty:
        st.markdown(
            "<div class='success-note'>No listed bias terms were detected.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div class='warning-note'>Potentially biased or problematic wording was found.</div>",
            unsafe_allow_html=True,
        )
        summary_tab, table_tab, chart_tab = st.tabs(["Detected Terms", "Table", "Chart"])

        with summary_tab:
            for _, row in findings.iterrows():
                st.markdown(
                    f"""
                    <div class="finding-card">
                        <h3>{row['found_term']}</h3>
                        <p class="muted">Category: {row['category']}</p>
                        <p><strong>Neutral alternative:</strong> {row['neutral_alternative']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with table_tab:
            st.dataframe(findings, use_container_width=True, hide_index=True)

        with chart_tab:
            counts = findings.groupby("category").size().reset_index(name="count")
            fig = px.bar(counts, x="category", y="count", title="Bias Count by Category")
            st.plotly_chart(fig, use_container_width=True)

st.markdown("<h2 class='section-title'>Neutral Rewrite</h2>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-card'><p class='muted'>Generate a more neutral version after reviewing detected terms.</p></div>",
    unsafe_allow_html=True,
)
if not is_openai_configured():
    st.info("Configure OPENAI_API_KEY to use the neutral rewrite feature.")

if st.button("Rewrite job description neutrally using OpenAI"):
    if not job_description.strip():
        st.error("Please enter a job description first.")
    else:
        with st.spinner("Rewriting job description..."):
            rewritten = rewrite_job_description_neutrally(job_description)
        st.text_area("Neutral rewritten version", rewritten, height=240)
