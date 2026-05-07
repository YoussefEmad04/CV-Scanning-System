import re

import pandas as pd

from services.openai_service import (
    cosine_similarity,
    generate_text,
    get_embedding,
    is_openai_configured,
)


COMMON_SKILLS = [
    "python", "sql", "excel", "machine learning", "deep learning", "pandas",
    "numpy", "tensorflow", "pytorch", "scikit-learn", "data analysis",
    "data visualization", "power bi", "tableau", "airflow", "spark", "hadoop",
    "aws", "azure", "docker", "linux", "git", "java", "javascript", "react",
    "node", "cybersecurity", "network security", "penetration testing",
]


def extract_skills_simple(text):
    lower_text = (text or "").lower()
    found = [skill for skill in COMMON_SKILLS if skill in lower_text]

    extras = re.findall(r"\b[A-Za-z][A-Za-z+#.]{2,}\b", text or "")
    for item in extras:
        token = item.lower()
        if token in COMMON_SKILLS and token not in found:
            found.append(token)
    return sorted(set(found))


def find_matched_skills(cv_text, job_description):
    cv_skills = set(extract_skills_simple(cv_text))
    job_skills = set(extract_skills_simple(job_description))
    return sorted(cv_skills.intersection(job_skills))


def find_missing_skills(cv_text, job_description):
    cv_skills = set(extract_skills_simple(cv_text))
    job_skills = set(extract_skills_simple(job_description))
    return sorted(job_skills.difference(cv_skills))


def _keyword_score(cv_text, job_description):
    job_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", (job_description or "").lower()))
    cv_words = set(re.findall(r"\b[a-zA-Z]{3,}\b", (cv_text or "").lower()))
    if not job_words:
        return 0.0
    return len(job_words.intersection(cv_words)) / len(job_words)


def generate_candidate_explanation(candidate_text, job_description, score, matched_skills, missing_skills):
    if not is_openai_configured():
        return (
            f"Demo explanation: this candidate matched {len(matched_skills)} listed skills. "
            f"Missing skills found: {', '.join(missing_skills[:5]) or 'none detected'}. "
            "A human reviewer should verify the resume details."
        )

    prompt = f"""
Explain in 3-4 lines why this candidate matches or does not match the job description.
Mention matched skills and missing skills. Do not make a hiring decision.
Recommend human review.

Match score: {score:.1f}%
Matched skills: {', '.join(matched_skills) or 'None detected'}
Missing skills: {', '.join(missing_skills) or 'None detected'}

Job description:
{job_description}

Candidate CV:
{candidate_text[:4000]}
"""
    return generate_text(
        prompt,
        system_message=(
            "You are an HR screening assistant. Do not infer sensitive attributes such as "
            "gender, age, nationality, religion, address, photo, or marital status."
        ),
    )


def rank_candidates(job_description, cv_records):
    if cv_records is None or len(cv_records) == 0:
        return pd.DataFrame()

    job_embedding = get_embedding(job_description) if is_openai_configured() else None
    rows = []

    for _, record in cv_records.iterrows():
        cv_text = record.get("extracted_text", "")
        if job_embedding is not None:
            cv_embedding = get_embedding(cv_text)
            similarity = cosine_similarity(job_embedding, cv_embedding)
        else:
            similarity = _keyword_score(cv_text, job_description)

        score = max(0.0, min(100.0, similarity * 100))
        matched_skills = find_matched_skills(cv_text, job_description)
        missing_skills = find_missing_skills(cv_text, job_description)
        explanation = generate_candidate_explanation(
            cv_text, job_description, score, matched_skills, missing_skills
        )

        rows.append(
            {
                "candidate_id": record.get("candidate_id", ""),
                "candidate_name": record.get("candidate_name", ""),
                "file_name": record.get("file_name", ""),
                "match_score": round(score, 2),
                "matched_skills": ", ".join(matched_skills),
                "missing_skills": ", ".join(missing_skills),
                "explanation": explanation,
            }
        )

    return pd.DataFrame(rows).sort_values("match_score", ascending=False)
