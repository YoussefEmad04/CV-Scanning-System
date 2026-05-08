#!/usr/bin/env python3
"""Export final documentation Markdown to styled HTML and PDF."""

from __future__ import annotations

import html
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"
MD_PATH = DOCS_DIR / "final_documentation.md"
HTML_PATH = DOCS_DIR / "final_documentation.html"
PDF_PATH = DOCS_DIR / "final_documentation.pdf"
DIAGRAM_DIR = DOCS_DIR / "diagrams"
DIAGRAM_SCRIPT = ROOT / "scripts" / "generate_diagram_images.py"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "section"


def inline_markdown(text: str) -> str:
    placeholders: list[str] = []

    def stash(value: str) -> str:
        placeholders.append(value)
        return f"@@INLINE{len(placeholders) - 1}@@"

    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{m.group(1)}</code>"), escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', escaped)
    for index, value in enumerate(placeholders):
        escaped = escaped.replace(f"@@INLINE{index}@@", value)
    return escaped


def convert_markdown(md_text: str) -> str:
    lines = md_text.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    list_tag = "ul"
    table_rows: list[str] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            output.append(f"<p>{inline_markdown(' '.join(paragraph).strip())}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items, list_tag
        if list_items:
            output.append(f"<{list_tag}>")
            output.extend(list_items)
            output.append(f"</{list_tag}>")
            list_items = []
            list_tag = "ul"

    def flush_table() -> None:
        nonlocal table_rows
        if not table_rows:
            return
        parsed_rows = [
            [cell.strip() for cell in row.strip().strip("|").split("|")]
            for row in table_rows
            if row.strip()
        ]
        if len(parsed_rows) >= 2:
            header = parsed_rows[0]
            body_rows = parsed_rows[2:] if all(re.match(r"^:?-{3,}:?$", cell) for cell in parsed_rows[1]) else parsed_rows[1:]
            output.append("<table>")
            output.append("<thead><tr>")
            output.extend(f"<th>{inline_markdown(cell)}</th>" for cell in header)
            output.append("</tr></thead>")
            output.append("<tbody>")
            for row in body_rows:
                output.append("<tr>")
                output.extend(f"<td>{inline_markdown(cell)}</td>" for cell in row)
                output.append("</tr>")
            output.append("</tbody></table>")
        else:
            output.extend(f"<p>{inline_markdown(row)}</p>" for row in table_rows)
        table_rows = []

    for raw_line in lines:
        line = raw_line.rstrip()
        code_match = re.match(r"^```(\w+)?\s*$", line)
        if code_match:
            if in_code:
                code_text = html.escape("\n".join(code_lines))
                output.append(f'<pre><code class="language-{html.escape(code_lang)}">{code_text}</code></pre>')
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                flush_paragraph()
                flush_list()
                flush_table()
                in_code = True
                code_lang = (code_match.group(1) or "").strip()
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            continue

        if line.strip().startswith("|") and line.strip().endswith("|"):
            flush_paragraph()
            flush_list()
            table_rows.append(line)
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            flush_table()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            clean_text = re.sub(r"^\d+\.\s*", "", text).upper() if level == 2 else text
            section_class = " major-section" if level == 2 else ""
            figure_class = " diagram-heading" if level == 3 and text.startswith("Figure ") else ""
            output.append(
                f'<h{level} id="{slugify(text)}" class="{(section_class + figure_class).strip()}">{inline_markdown(clean_text)}</h{level}>'
            )
            continue

        image = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
        if image:
            flush_paragraph()
            flush_list()
            flush_table()
            alt = image.group(1).strip()
            src = image.group(2).strip()
            figure_class = "diagram" if src.startswith("diagrams/") else "screenshot"
            output.append(
                f'<figure class="{figure_class}"><img src="{html.escape(src)}" alt="{html.escape(alt)}"></figure>'
            )
            continue

        unordered = re.match(r"^-\s+(.+)$", line)
        if unordered:
            flush_paragraph()
            flush_table()
            if list_items and list_tag != "ul":
                flush_list()
            list_tag = "ul"
            list_items.append(f"<li>{inline_markdown(unordered.group(1).strip())}</li>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered:
            flush_paragraph()
            flush_table()
            if list_items and list_tag != "ol":
                flush_list()
            list_tag = "ol"
            list_items.append(f"<li>{inline_markdown(ordered.group(1).strip())}</li>")
            continue

        flush_table()
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    flush_table()
    return "\n".join(output)


def build_html(body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Recruitment & Resume Screening System - Final Documentation</title>
  <style>
    @page {{ size: A4; margin: 18mm 16mm 18mm 16mm; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #eef2f7;
      color: #172033;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 11.5pt;
      line-height: 1.62;
    }}
    .report {{ max-width: 980px; margin: 0 auto; background: #ffffff; padding: 0 44px 48px; }}
    .cover {{
      min-height: 92vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      border-bottom: 4px solid #1f4e79;
      page-break-after: always;
    }}
    .cover .eyebrow {{
      color: #1f4e79;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      font-size: 10pt;
      margin-bottom: 18px;
    }}
    .cover h1 {{ font-size: 34pt; line-height: 1.12; color: #0f172a; margin: 0 0 18px; }}
    .cover .subtitle {{ font-size: 15pt; color: #475569; max-width: 760px; margin-bottom: 34px; }}
    .cover .meta {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      max-width: 820px;
      color: #334155;
    }}
    .meta-box {{ border: 1px solid #cbd5e1; background: #f8fafc; border-radius: 8px; padding: 14px 16px; }}
    .meta-label {{
      display: block;
      color: #64748b;
      font-size: 9pt;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 4px;
      font-weight: 700;
    }}
    .students {{
      max-width: 820px;
      margin: 4px 0 18px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      overflow: hidden;
      background: #ffffff;
    }}
    .students-title {{
      background: #1f4e79;
      color: #ffffff;
      padding: 10px 14px;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      font-size: 9.5pt;
    }}
    .student-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    .student {{ padding: 10px 14px; border-top: 1px solid #e2e8f0; }}
    .student:nth-child(odd) {{ border-right: 1px solid #e2e8f0; }}
    .student-name {{ font-weight: 700; color: #0f172a; }}
    .student-id {{ color: #475569; font-size: 10pt; }}
    h1 {{ color: #0f172a; font-size: 24pt; line-height: 1.2; margin: 0 0 22px; }}
    h2 {{
      color: #1f4e79;
      font-size: 17pt;
      line-height: 1.25;
      margin: 34px 0 12px;
      padding-bottom: 7px;
      border-bottom: 2px solid #dbeafe;
      text-transform: uppercase;
    }}
    h2.major-section {{ page-break-before: always; }}
    h2.major-section:first-of-type {{ page-break-before: auto; }}
    h3 {{
      color: #0f172a;
      font-size: 13.5pt;
      margin: 22px 0 8px;
      page-break-after: avoid;
      break-after: avoid;
    }}
    h3.diagram-heading {{ page-break-before: always; break-before: page; margin-top: 0; }}
    p {{ margin: 0 0 12px; orphans: 3; widows: 3; }}
    h3.diagram-heading + p {{ page-break-after: avoid; break-after: avoid; }}
    ul, ol {{ margin: 8px 0 14px 22px; padding: 0; }}
    li {{ margin-bottom: 6px; }}
    code {{
      background: #eef2f7;
      color: #0f172a;
      border: 1px solid #d7dee9;
      border-radius: 4px;
      padding: 1px 4px;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace;
      font-size: 0.92em;
    }}
    pre {{
      background: #0f172a;
      color: #e2e8f0;
      border-radius: 8px;
      padding: 14px 16px;
      overflow: hidden;
      white-space: pre-wrap;
      border: 1px solid #1e293b;
    }}
    pre code {{ background: transparent; border: 0; color: inherit; padding: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin: 14px 0; font-size: 10.5pt; }}
    th, td {{ border: 1px solid #cbd5e1; padding: 8px 10px; vertical-align: top; }}
    th {{ background: #eaf2ff; color: #0f172a; font-weight: 700; }}
    figure {{ margin: 16px auto 8px; page-break-inside: avoid; break-inside: avoid; }}
    figure img {{ display: block; max-width: 100%; height: auto; margin: 0 auto; }}
    figure.diagram {{
      padding: 10px;
      border: 1px solid #d9e2ef;
      background: #f8fafc;
      border-radius: 10px;
      page-break-inside: avoid;
      break-inside: avoid;
    }}
    figure.diagram img {{ width: 100%; max-height: 650px; object-fit: contain; }}
    figure.screenshot {{
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      overflow: hidden;
      background: #f8fafc;
      box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    }}
    figure.screenshot img {{ width: 100%; }}
    p em {{
      display: block;
      text-align: center;
      color: #475569;
      font-size: 9.5pt;
      font-style: italic;
      margin-top: 6px;
    }}
    a {{ color: #1f4e79; text-decoration: none; }}
    @media print {{
      body {{ background: #ffffff; }}
      .report {{ max-width: none; padding: 0; }}
      h2.major-section {{ page-break-before: always; }}
      h3 {{ break-after: avoid; }}
      h3.diagram-heading {{ break-before: page; }}
      figure {{ break-inside: avoid; }}
    }}
  </style>
</head>
<body>
  <main class="report">
    <section class="cover">
      <div class="eyebrow">Final Project Documentation</div>
      <h1>AI Recruitment &amp; Resume Screening System</h1>
      <p class="subtitle">Professional report for an AI Application course project at Egyptian Russian University, generated from the implemented Streamlit project documentation.</p>
      <div class="students">
        <div class="students-title">Prepared By</div>
        <div class="student-grid">
          <div class="student"><div class="student-name">Youssef Emad</div><div class="student-id">ID: 225241</div></div>
          <div class="student"><div class="student-name">Omar Tokal</div><div class="student-id">ID: 225238</div></div>
          <div class="student"><div class="student-name">Amr Hamdy</div><div class="student-id">ID: 225182</div></div>
          <div class="student"><div class="student-name">Zeyad Mostafa</div><div class="student-id">ID: 225070</div></div>
        </div>
      </div>
      <div class="meta">
        <div class="meta-box"><span class="meta-label">Course</span>AI Application</div>
        <div class="meta-box"><span class="meta-label">Instructor</span>Mohamed Gonid</div>
        <div class="meta-box"><span class="meta-label">University</span>Egyptian Russian University</div>
        <div class="meta-box"><span class="meta-label">Project Type</span>Decision-Support Recruitment Screening</div>
      </div>
    </section>
    {body}
  </main>
</body>
</html>
"""


def export_pdf_with_playwright() -> None:
    html_url = HTML_PATH.resolve().as_uri()
    pdf_path = str(PDF_PATH.resolve())
    node_script = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch({{ headless: true }});
  const page = await browser.newPage({{ viewport: {{ width: 1280, height: 1600 }}, deviceScaleFactor: 1 }});
  await page.goto({html_url!r}, {{ waitUntil: 'load', timeout: 60000 }});
  await page.evaluate(async () => {{
    const images = Array.from(document.images);
    await Promise.all(images.map(img => {{
      if (img.complete) return Promise.resolve();
      return new Promise(resolve => {{
        img.onload = resolve;
        img.onerror = resolve;
      }});
    }}));
  }});
  await page.pdf({{
    path: {pdf_path!r},
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-family: Arial, sans-serif; font-size: 8px; color: #64748b; width: 100%; text-align: center; padding-top: 4px;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
    margin: {{ top: '18mm', right: '16mm', bottom: '18mm', left: '16mm' }}
  }});
  await browser.close();
}})().catch(error => {{
  console.error(error);
  process.exit(1);
}});
"""
    subprocess.run(["node", "-e", node_script], cwd=ROOT, check=True)


def validate_outputs() -> None:
    errors: list[str] = []
    html_text = HTML_PATH.read_text(encoding="utf-8") if HTML_PATH.exists() else ""
    md_text = MD_PATH.read_text(encoding="utf-8") if MD_PATH.exists() else ""
    screenshot_count = len(re.findall(r'<figure class="screenshot">', html_text))
    diagram_count = len(re.findall(r'<figure class="diagram">', html_text))
    forbidden = ["```" + "m" + "ermaid", "flow" + "chart TD", "flow" + "chart LR", "%" + "%{init", "language-" + "m" + "ermaid"]

    if not HTML_PATH.exists():
        errors.append("Missing HTML output")
    if not PDF_PATH.exists():
        errors.append("Missing PDF output")
    if PDF_PATH.exists() and PDF_PATH.stat().st_size < 10_000:
        errors.append("PDF output is unexpectedly small")
    if any(term in html_text or term in md_text for term in forbidden):
        errors.append("Raw diagram source text is still present in Markdown or HTML")
    if screenshot_count != 8:
        errors.append(f"Expected 8 screenshots in HTML, found {screenshot_count}")
    if diagram_count != 6:
        errors.append(f"Expected 6 diagram figures in HTML, found {diagram_count}")

    expected_diagrams = [
        "figure_01_system_architecture.png",
        "figure_02_ui_navigation.png",
        "figure_03_resume_ranking_flow.png",
        "figure_04_bias_detection_flow.png",
        "figure_05_rag_pipeline.png",
        "figure_06_synthetic_cv_generation_flow.png",
    ]
    for diagram in expected_diagrams:
        if not (DIAGRAM_DIR / diagram).exists():
            errors.append(f"Missing rendered diagram PNG: {diagram}")
        if diagram not in md_text:
            errors.append(f"Diagram not referenced in Markdown: {diagram}")

    if PDF_PATH.exists():
        with PDF_PATH.open("rb") as f:
            if f.read(5) != b"%PDF-":
                errors.append("PDF file does not have a valid PDF header")

    if errors:
        raise RuntimeError("; ".join(errors))

    print(f"HTML written: {HTML_PATH}")
    print(f"PDF written: {PDF_PATH}")
    print(f"Screenshots included: {screenshot_count}")
    print(f"Static PNG diagrams included: {diagram_count}")


def main() -> int:
    if not MD_PATH.exists():
        print(f"Missing Markdown source: {MD_PATH}", file=sys.stderr)
        return 1

    diagram_python = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable
    subprocess.run([diagram_python, str(DIAGRAM_SCRIPT)], cwd=ROOT, check=True)
    md_text = MD_PATH.read_text(encoding="utf-8")
    toc_start = md_text.find("## Table of Contents")
    body_source = md_text[toc_start:] if toc_start != -1 else md_text
    body = convert_markdown(body_source)
    HTML_PATH.write_text(build_html(body), encoding="utf-8")
    export_pdf_with_playwright()
    validate_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
