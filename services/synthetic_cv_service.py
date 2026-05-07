import random
import re

import pandas as pd

from services.openai_service import generate_text, is_openai_configured


NAMES = [
    "Ahmed Hassan", "Sara Ali", "Mona Ibrahim", "Omar Khaled", "Nour Adel",
    "Youssef Samir", "Laila Mostafa", "Karim Fathy", "Hana Tarek", "Mariam Nasser",
]

EDUCATION = [
    "BSc Computer Science", "BSc Information Systems", "BSc Software Engineering",
    "BSc Data Science", "BSc Cybersecurity",
]

CERTIFICATIONS = {
    "AI Engineer": ["TensorFlow Developer", "Machine Learning Specialization", "Azure AI Fundamentals"],
    "Data Engineer": ["AWS Data Analytics", "Databricks Fundamentals", "Google Data Engineer"],
    "Software Engineer": ["Oracle Java Foundations", "Meta Front-End Developer", "AWS Cloud Practitioner"],
    "Cybersecurity Analyst": ["Security+", "Cisco CyberOps", "CEH Foundation"],
    "Data Analyst": ["Google Data Analytics", "Microsoft Power BI", "Tableau Desktop Specialist"],
}

PROJECTS = {
    "AI Engineer": ["image classification model", "chatbot prototype", "resume screening model"],
    "Data Engineer": ["ETL pipeline", "data warehouse dashboard", "Airflow workflow"],
    "Software Engineer": ["web application", "REST API", "student management system"],
    "Cybersecurity Analyst": ["security audit", "phishing detection report", "network monitoring lab"],
    "Data Analyst": ["sales dashboard", "customer churn analysis", "Excel reporting system"],
}

COMMON_REQUIREMENT_SKILLS = [
    "Python", "SQL", "Airflow", "Spark", "AWS", "Azure", "GCP", "Docker",
    "ETL", "Data Warehousing", "PostgreSQL", "Power BI", "Tableau", "Kafka",
    "Machine Learning", "TensorFlow", "PyTorch", "React", "JavaScript", "Linux",
    "Network Security", "Excel", "Data Visualization", "Data Modeling",
    "Data Science", "Statistical Modeling", "R", "Pandas", "NumPy", "MLOps",
    "Deep Learning", "Banking", "Finance", "Presentation", "Communication",
]


def get_skill_pool(job_category):
    pools = {
        "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Numpy"],
        "Data Engineer": ["Python", "SQL", "Airflow", "Spark", "ETL", "AWS", "Data Warehousing"],
        "Software Engineer": ["Python", "Java", "JavaScript", "React", "Git", "REST APIs"],
        "Cybersecurity Analyst": ["Linux", "Network Security", "SIEM", "Python", "Penetration Testing"],
        "Data Analyst": ["Excel", "SQL", "Python", "Power BI", "Tableau", "Data Visualization"],
    }
    return pools.get(job_category, ["Python", "SQL", "Communication"])


def generate_synthetic_cv(job_category):
    # This module simulates GAN-generated CV data for demo purposes and can later be replaced with a real GAN model.
    skill_pool = get_skill_pool(job_category)
    skills = random.sample(skill_pool, k=min(5, len(skill_pool)))
    years = random.randint(0, 8)
    cv = {
        "name": random.choice(NAMES),
        "job_category": job_category,
        "skills": ", ".join(skills),
        "education": random.choice(EDUCATION),
        "years_of_experience": years,
        "projects": random.choice(PROJECTS[job_category]),
        "certifications": random.choice(CERTIFICATIONS[job_category]),
    }
    if is_openai_configured():
        resume_text = _generate_category_resume_text_with_llm(cv)
        cv["resume_text"] = _clean_llm_text(resume_text)
        extracted_name = _extract_name_from_resume_text(cv["resume_text"])
        if extracted_name:
            cv["name"] = extracted_name
    else:
        cv["resume_text"] = build_resume_text(cv)
    return cv


def generate_synthetic_cvs(job_category, n):
    rows = [generate_synthetic_cv(job_category) for _ in range(n)]
    return pd.DataFrame(rows)


def build_resume_text(cv):
    return f"""{cv['name']}
{cv['job_category']}

Professional Summary
Synthetic candidate profile for a {cv['job_category']} role with {cv['years_of_experience']} years of experience.

Technical Skills
- {cv['skills']}

Education
- {cv['education']}

Projects
- {cv['projects']}

Certifications
- {cv['certifications']}
"""


def generate_job_responsibilities(requirements):
    if is_openai_configured():
        prompt = f"""
Read this full job post or project requirement text and create 5-7 clear job responsibilities.
Keep the wording simple and suitable for a university recruitment demo.
Do not add unrelated requirements.
Focus on the selected role, practical tasks, tools, and domain.

Job post / requirements:
{requirements}
"""
        return _clean_llm_text(generate_text(prompt, system_message="You write concise job responsibilities for recruitment."))

    skills = extract_requirements_skills(requirements)
    focus = ", ".join(skills[:5]) if skills else "the listed project requirements"
    return "\n".join(
        [
            f"- Build and maintain solutions using {focus}.",
            "- Prepare clean, reliable data or software outputs for stakeholders.",
            "- Monitor quality, fix issues, and document the workflow.",
            "- Collaborate with team members and communicate progress clearly.",
            "- Support testing and final review before delivery.",
        ]
    )


def generate_high_match_cv(requirements, job_category="Data Engineer"):
    skills = extract_requirements_skills(requirements)
    if not skills:
        skills = get_skill_pool(job_category)

    selected_skills = skills[:8]
    if is_openai_configured():
        resume_text = _generate_high_match_resume_text_with_llm(requirements, job_category, selected_skills)
        resume_text = _clean_llm_text(resume_text)
        name = _extract_name_from_resume_text(resume_text) or random.choice(NAMES)
        return {
            "name": name,
            "job_category": job_category,
            "skills": ", ".join(selected_skills),
            "education": "BSc Computer Science or related field",
            "years_of_experience": 2,
            "projects": _project_from_requirements(requirements, selected_skills),
            "certifications": "Machine Learning Specialization",
            "resume_text": resume_text,
        }

    cv = {
        "name": random.choice(NAMES),
        "job_category": job_category,
        "skills": ", ".join(selected_skills),
        "education": random.choice(EDUCATION),
        "years_of_experience": random.randint(3, 7),
        "projects": _project_from_requirements(requirements, selected_skills),
        "certifications": random.choice(CERTIFICATIONS.get(job_category, CERTIFICATIONS["Data Engineer"])),
    }
    cv["resume_text"] = f"""{cv['name']}
{cv['job_category']}

Professional Summary
Synthetic high-match candidate profile based on the provided requirements. Experience focuses on {', '.join(selected_skills[:5])}.

Technical Skills
{chr(10).join(f"- {skill}" for skill in selected_skills)}

Experience
- Built project workflows that match the provided requirements.
- Prepared reliable outputs, documented steps, and supported review.
- Used quality checks to reduce errors and improve delivery.

Projects
- {cv['projects']}

Education
- {cv['education']}

Certifications
- {cv['certifications']}
"""
    return cv


def _generate_high_match_resume_text_with_llm(requirements, job_category, selected_skills):
    prompt = f"""
Create a realistic but clearly fake synthetic CV for a high-match candidate.
Target role: {job_category}

Use this full job post / project requirement text:
{requirements}

The CV should look detailed like a real PDF resume, with these sections:
- Candidate name
- Target role
- Contact line with fake email, fake phone, Cairo/Egypt location, fake LinkedIn/GitHub if useful
- Professional Summary
- Education
- Professional Experience with 2 realistic entries
- Projects with 2-3 detailed projects
- Technical Skills grouped by category
- Certifications
- Soft Skills

Rules:
- Do not use a real person's name from the job post.
- Do not copy any real personal data.
- Keep it synthetic and demo-safe.
- Match the job requirements strongly.
- Use 0-2 years of experience if the job post asks for junior level.
- Include the most relevant skills: {', '.join(selected_skills)}.
- Return plain text only, no markdown table.
"""
    return generate_text(
        prompt,
        system_message="You generate realistic synthetic CV text for a recruitment demo without using real personal data.",
    )


def _generate_category_resume_text_with_llm(cv):
    prompt = f"""
Create a realistic but clearly fake synthetic CV for this role:
Role: {cv['job_category']}
Candidate name: {cv['name']}
Years of experience: {cv['years_of_experience']}
Core skills: {cv['skills']}
Education: {cv['education']}
Main project idea: {cv['projects']}
Certification: {cv['certifications']}

The CV should look detailed like a real PDF resume, with these sections:
- Candidate name
- Target role
- Contact line with fake email, fake phone, Cairo/Egypt location, fake LinkedIn/GitHub if useful
- Professional Summary
- Education
- Professional Experience with 2 realistic entries
- Projects with 2-3 detailed projects
- Technical Skills grouped by category
- Certifications
- Soft Skills

Rules:
- Keep it synthetic and demo-safe.
- Do not copy real personal data.
- Make it suitable for a university recruitment demo.
- Return plain text only, no markdown table.
"""
    return generate_text(
        prompt,
        system_message="You generate realistic synthetic CV text for a recruitment demo without using real personal data.",
    )


def _clean_llm_text(text):
    text = (text or "").replace("**", "").replace("__", "")
    text = re.sub(r"^\s{0,3}#{1,4}\s*", "", text, flags=re.MULTILINE)
    return text.strip()


def _extract_name_from_resume_text(resume_text):
    for line in (resume_text or "").splitlines()[:5]:
        clean_line = line.strip()
        if not clean_line:
            continue
        clean_line = re.sub(r"^(candidate name|name)\s*:\s*", "", clean_line, flags=re.I).strip()
        if 2 <= len(clean_line.split()) <= 4:
            return clean_line
    return ""


def extract_requirements_skills(requirements):
    text = requirements or ""
    found = [skill for skill in COMMON_REQUIREMENT_SKILLS if skill.lower() in text.lower()]
    extra_terms = re.findall(r"\b[A-Z][A-Za-z0-9+#.]{2,}\b", text)
    for term in extra_terms:
        if term not in found and len(term) <= 20:
            found.append(term)
    return found


def _project_from_requirements(requirements, skills):
    if skills:
        return f"Requirements-based project using {', '.join(skills[:5])}"
    return "Requirements-based project tailored to the role"
