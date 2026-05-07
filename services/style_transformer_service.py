from io import BytesIO
from html import escape
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from services.openai_service import generate_text, is_openai_configured


def _fallback_transform(resume_text, style):
    lines = _split_resume_sentences(resume_text)
    if style == "Short summary style":
        return "Summary: " + " ".join(lines)[:700]
    if style == "ATS-friendly style":
        return "\n".join(f"- {line}" for line in lines)
    return "\n".join(lines)


def transform_resume_style(resume_text, style):
    if not is_openai_configured():
        return _fallback_transform(resume_text, style)

    prompt = f"""
Rewrite the resume text in the selected style. Keep the meaning accurate.
Do not invent experience, skills, certificates, companies, or education.
Improve wording only.
Return clean plain text suitable for a PDF resume.
Start with the candidate name if it is available, then contact details if available.
Use short section headings and bullet lines when useful.
Do not use markdown tables or code fences.

Style rules:
- Professional style: polished wording, clear sections, balanced detail.
- ATS-friendly style: simple headings, keyword-friendly bullet points, no columns or graphics.
- Short summary style: concise one-page summary, keep only the strongest relevant points.

Selected style: {style}

Resume text:
{resume_text}
"""
    return generate_text(prompt, system_message="You improve resume writing while preserving the original facts.")


def get_pdf_title_for_style(style):
    titles = {
        "Professional style": "Professional Resume",
        "ATS-friendly style": "ATS-Friendly Resume",
        "Short summary style": "Resume Summary",
    }
    return titles.get(style, "Transformed Resume")


def create_resume_pdf_bytes(resume_text, title="Transformed Resume"):
    lines = _normalize_resume_lines(resume_text)
    header_lines, body_lines = _split_header_and_body(lines)
    style_theme = _get_pdf_theme(title)

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=42,
        leftMargin=42,
        topMargin=38,
        bottomMargin=38,
    )
    styles = getSampleStyleSheet()
    name_style = ParagraphStyle(
        "ResumeName",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=style_theme["accent"],
        spaceAfter=3,
    )
    contact_style = ParagraphStyle(
        "ResumeContact",
        parent=styles["BodyText"],
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.HexColor("#333333"),
    )
    section_style = ParagraphStyle(
        "ResumeSection",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=style_theme["accent"],
        spaceBefore=9,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "ResumeBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=11.5,
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "ResumeBullet",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-8,
        bulletIndent=5,
    )

    story = []
    if header_lines:
        story.append(Paragraph(escape(_clean_header_line(header_lines[0])), name_style))
        for line in header_lines[1:3]:
            story.append(Paragraph(escape(_clean_header_line(line)), contact_style))
    else:
        story.append(Paragraph(escape(title), name_style))

    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.7, color=style_theme["line"]))
    story.append(Spacer(1, 8))

    for line in body_lines:
        if _is_bullet_line(line):
            story.append(Paragraph(escape(_clean_bullet_line(line)), bullet_style, bulletText="•"))
        elif _is_section_heading(line):
            story.append(Paragraph(escape(_clean_heading(line)), section_style))
            story.append(HRFlowable(width="100%", thickness=0.35, color=style_theme["line"]))
            story.append(Spacer(1, 3))
        else:
            for paragraph in _split_long_line(line):
                story.append(Paragraph(escape(paragraph), body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _get_pdf_theme(title):
    if "ATS" in title:
        return {"accent": colors.black, "line": colors.HexColor("#888888")}
    if "Summary" in title:
        return {"accent": colors.HexColor("#334155"), "line": colors.HexColor("#CBD5E1")}
    return {"accent": colors.HexColor("#1F4E79"), "line": colors.HexColor("#9BB7D4")}


def _split_resume_sentences(text):
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    if not cleaned:
        return []
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _normalize_resume_lines(text):
    lines = []
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("```"):
            continue
        line = re.sub(r"^\s{0,3}#{1,4}\s*", "", line)
        line = line.replace("**", "").replace("__", "")
        lines.append(line)

    if len(lines) <= 2:
        expanded = []
        for line in lines:
            expanded.extend(_split_long_line(line))
        return expanded
    return lines


def _split_header_and_body(lines):
    if not lines:
        return [], []

    first_line = lines[0]
    if _is_section_heading(first_line) or _is_bullet_line(first_line):
        return [], lines

    header_lines = [first_line]
    body_start = 1
    for idx in range(1, min(5, len(lines))):
        line = lines[idx]
        if _is_section_heading(line) or _is_bullet_line(line):
            break
        if _looks_like_contact_line(line) or (idx == 1 and len(line) <= 70):
            header_lines.append(line)
            body_start = idx + 1
        else:
            break
    return header_lines, lines[body_start:]


def _looks_like_contact_line(line):
    lower_line = line.lower()
    return any(
        token in lower_line
        for token in ["@", "phone", "email", "linkedin", "github", "location", "+20", "contact", "target role"]
    )


def _clean_header_line(line):
    return re.sub(r"^(candidate name|name|target role|role|contact)\s*:\s*", "", line.strip(), flags=re.I)


def _split_long_line(line, max_chars=520):
    if len(line) <= max_chars:
        return [line]

    parts = _split_resume_sentences(line)
    chunks = []
    current = ""
    for part in parts:
        if len(current) + len(part) + 1 <= max_chars:
            current = f"{current} {part}".strip()
        else:
            if current:
                chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks or [line]


def _is_bullet_line(line):
    return line.startswith(("- ", "* ", "• "))


def _clean_bullet_line(line):
    return re.sub(r"^[-*•]\s*", "", line).strip()


def _is_section_heading(line):
    cleaned = _clean_heading(line)
    known_headings = [
        "summary", "professional summary", "skills", "technical skills",
        "experience", "work experience", "projects", "education",
        "certifications", "languages", "career objective", "career overview",
        "training", "professional training", "skills summary", "key skills",
        "technical tools and platforms", "tools and technologies",
        "professional experience", "key projects", "core competencies",
        "education and certifications", "education & certifications",
    ]
    return (
        len(cleaned) <= 60
        and (
            cleaned.lower().rstrip(":") in known_headings
            or cleaned.endswith(":")
            or cleaned.isupper()
        )
    )


def _clean_heading(line):
    return line.strip().rstrip(":")
