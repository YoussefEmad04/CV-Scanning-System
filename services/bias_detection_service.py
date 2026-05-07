import pandas as pd

from services.openai_service import generate_text, is_openai_configured


BIAS_TERMS = {
    "age bias": {
        "young": "motivated",
        "fresh graduate only": "entry-level candidates are welcome",
        "energetic": "proactive",
    },
    "gender bias": {
        "male": "candidate",
        "female": "candidate",
        "guys": "team members",
    },
    "nationality/language bias": {
        "native speaker": "strong communication skills",
    },
    "aggressive wording": {
        "rockstar": "skilled professional",
        "ninja": "specialist",
        "dominant": "confident",
        "aggressive": "results-oriented",
    },
}


def detect_bias_terms(job_description):
    text = (job_description or "").lower()
    findings = []
    for category, terms in BIAS_TERMS.items():
        for term, alternative in terms.items():
            if term in text:
                findings.append(
                    {
                        "found_term": term,
                        "category": category,
                        "neutral_alternative": alternative,
                        "warning_message": "Review this wording because it may discourage qualified candidates.",
                    }
                )
    return pd.DataFrame(findings)


def rewrite_job_description_neutrally(job_description):
    if not is_openai_configured():
        return "OpenAI API key is missing. Please configure it to rewrite the job description."

    prompt = f"""
Rewrite this job description using neutral, inclusive wording.
Keep the job requirements accurate. Do not add new requirements.
Remove or replace biased wording such as young, male, female, guys, native speaker,
rockstar, ninja, dominant, aggressive, and fresh graduate only.
For language requirements, use wording like strong communication skills instead of native speaker.
Return only the rewritten job description.

Job description:
{job_description}
"""
    rewritten = generate_text(prompt, system_message="You rewrite recruitment text in a fair and inclusive way.")
    return rewritten.replace("Job description:", "", 1).strip()
