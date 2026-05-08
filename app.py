import streamlit as st

from services.openai_service import is_openai_configured
from services.storage_service import load_cv_records, load_ranking_results, load_synthetic_cvs
from services.ui_helpers import apply_custom_css, render_sidebar_status


st.set_page_config(
    page_title="AI Recruitment & Resume Screening System",
    page_icon="📄",
    layout="wide",
)
apply_custom_css()
render_sidebar_status()

st.sidebar.divider()
st.sidebar.subheader("Home Status")
st.sidebar.caption("Professional demo homepage for the recruitment screening workflow.")

cv_records = load_cv_records()
ranking_results = load_ranking_results()
synthetic_cvs = load_synthetic_cvs()
average_score = 0.0
if not ranking_results.empty and "match_score" in ranking_results:
    average_score = float(ranking_results["match_score"].mean())

st.markdown(
    """
    <style>
    .home-hero {
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 2rem;
        background: linear-gradient(135deg, #111827 0%, #1F2937 60%, #263449 100%);
        color: #F9FAFB;
        margin-bottom: 1rem;
    }
    .home-hero h1 {
        color: #FFFFFF !important;
        font-size: 2.35rem;
        margin-bottom: 0.5rem;
    }
    .home-hero p {
        color: #D1D5DB !important;
        font-size: 1rem;
        max-width: 920px;
    }
    .home-badge {
        display: inline-block;
        padding: 0.28rem 0.7rem;
        margin: 0.25rem 0.35rem 0.25rem 0;
        border-radius: 999px;
        background: #EAF2FF;
        color: #1F4E79 !important;
        border: 1px solid #9BB7D4;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .home-note {
        margin-top: 1rem;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        background: #FEF3C7;
        color: #78350F !important;
        border: 1px solid #F59E0B;
        font-weight: 600;
    }
    .metric-card, .module-card, .workflow-card, .demo-card {
        border: 1px solid #334155;
        border-radius: 12px;
        background: #111827;
        padding: 1rem;
        color: #F9FAFB !important;
        height: 100%;
    }
    .metric-card .label {
        color: #CBD5E1 !important;
        font-size: 0.85rem;
        margin-bottom: 0.35rem;
    }
    .metric-card .value {
        color: #FFFFFF !important;
        font-size: 1.8rem;
        font-weight: 750;
    }
    .module-card h3, .workflow-card h4, .demo-card h4 {
        color: #FFFFFF !important;
        margin-bottom: 0.45rem;
    }
    .module-card p, .workflow-card p, .demo-card p {
        color: #CBD5E1 !important;
        margin-bottom: 0.35rem;
    }
    .module-card .action {
        color: #93C5FD !important;
        font-size: 0.9rem;
        font-weight: 650;
    }
    .section-title {
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="home-hero">
        <span class="home-badge">Streamlit App</span>
        <span class="home-badge">OpenAI-powered</span>
        <span class="home-badge">Decision Support Tool</span>
        <h1>AI Recruitment & Resume Screening System</h1>
        <p>
            A university project that helps HR teams upload resumes, rank candidates against job descriptions,
            detect biased wording, generate synthetic CVs, transform resume style, and ask questions over CVs
            using a simple RAG assistant.
        </p>
        <div class="home-note">
            Human review required: this system supports recruitment screening, but final hiring decisions
            should always be made by a human reviewer.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not is_openai_configured():
    st.warning("OPENAI_API_KEY is missing. AI features will use simple demo fallbacks where possible.")

st.markdown("<h2 class='section-title'>System Overview</h2>", unsafe_allow_html=True)
metric_items = [
    ("Uploaded CVs", len(cv_records)),
    ("Ranked Candidates", len(ranking_results)),
    ("Average Match", f"{average_score:.1f}%"),
    ("Synthetic CVs", len(synthetic_cvs)),
]
metric_cols = st.columns(4)
for col, (label, value) in zip(metric_cols, metric_items):
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="label">{label}</div>
                <div class="value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<h2 class='section-title'>System Modules</h2>", unsafe_allow_html=True)
modules = [
    ("Upload CVs", "Upload PDF/DOCX resumes and extract text.", "Start here to build the candidate database."),
    ("Resume Ranking", "Rank candidates using semantic similarity.", "Review match scores, skills, and explanations."),
    ("Bias Detection", "Check job descriptions for problematic wording.", "Rewrite descriptions in a neutral tone."),
    ("Synthetic CV Generation", "Generate fake CV records and PDF resumes.", "Create demo candidates from categories or requirements."),
    ("Style Transformation", "Rewrite resumes into professional formats.", "Upload a resume and download the transformed PDF."),
    ("RAG Assistant", "Ask questions over uploaded CVs.", "Retrieve sources and snippets from candidate resumes."),
    ("Dashboard", "View overall project statistics.", "Use charts and metrics for presentation screenshots."),
]

for row_start in range(0, len(modules), 3):
    cols = st.columns(3)
    for col, (title, description, action) in zip(cols, modules[row_start : row_start + 3]):
        with col:
            st.markdown(
                f"""
                <div class="module-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <div class="action">{action}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

st.markdown("<h2 class='section-title'>Workflow</h2>", unsafe_allow_html=True)
workflow = [
    "Upload CVs",
    "Add Job Description",
    "Rank Candidates",
    "Check Bias",
    "Ask RAG Assistant",
    "Review Dashboard",
]
workflow_cols = st.columns(6)
for index, (col, step) in enumerate(zip(workflow_cols, workflow), start=1):
    with col:
        st.markdown(
            f"""
            <div class="workflow-card">
                <h4>{index}</h4>
                <p>{step}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<h2 class='section-title'>Recommended Demo Flow</h2>", unsafe_allow_html=True)
demo_steps = [
    "Upload CVs",
    "Run Resume Ranking",
    "Test Bias Detection",
    "Generate Synthetic CVs",
    "Transform Resume Style",
    "Ask RAG Assistant",
    "Open Dashboard",
]
left, right = st.columns([1, 1])
with left:
    st.markdown(
        """
        <div class="demo-card">
            <h4>Suggested presentation order</h4>
            <p>Follow this flow to show the full system end to end without jumping between unrelated screens.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
with right:
    for i, step in enumerate(demo_steps, start=1):
        st.write(f"**{i}. {step}**")

st.divider()
st.info("Use the sidebar page navigation to open each module. The data shown above updates from the local CSV files.")
