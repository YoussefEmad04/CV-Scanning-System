import os
import re

import docx
import pdfplumber
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    return clean_resume_text(text)


def extract_text_from_docx(file_path):
    document = docx.Document(file_path)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    return clean_resume_text(text)


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    if ext == ".docx":
        return extract_text_from_docx(file_path)
    raise ValueError("Unsupported file type. Please upload PDF or DOCX files.")


def clean_resume_text(text):
    text = re.sub(r"\s+", " ", text or "")
    return text.strip()


def extract_candidate_name_simple(text, file_name):
    fallback_name = _clean_name_from_file(file_name)
    if text:
        first_part = text[:300]
        lines = [line.strip() for line in re.split(r"[.\n|]", first_part) if line.strip()]
        for line in lines:
            if _looks_unlike_person_name(line):
                continue
            words = line.split()
            if 2 <= len(words) <= 4 and all(word[:1].isupper() for word in words if word):
                return line[:80]

    return fallback_name


def _clean_name_from_file(file_name):
    name = os.path.splitext(os.path.basename(file_name))[0]
    name = re.sub(r"[_-]+", " ", name)
    name = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", name)
    name = re.sub(r"\([^)]*\)", " ", name)
    name = re.sub(r"\b(cv|resume|data engineer|engineer|convertedv\d*|iti|de|v\d+)\b", " ", name, flags=re.I)
    name = re.sub(r"\d+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name.title() if name else os.path.splitext(os.path.basename(file_name))[0].title()


def _looks_unlike_person_name(line):
    lower_line = line.lower()
    blocked_terms = [
        "cv", "resume", "data engineer", "etl engineer", "big data", "software", "developer",
        "cairo", "egypt", "alexandria", "github", "linkedin", "email", "@",
    ]
    return any(term in lower_line for term in blocked_terms)
