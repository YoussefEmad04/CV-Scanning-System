#!/usr/bin/env python3
"""Generate static professional PNG diagrams for the final documentation."""

from __future__ import annotations

import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT / "docs" / "diagrams"

BG = "#ffffff"
PANEL = "#f8fafc"
BLUE_FILL = "#eef6ff"
BLUE_BORDER = "#2563eb"
GRAY_FILL = "#f1f5f9"
GRAY_BORDER = "#475569"
GREEN_FILL = "#ecfdf5"
GREEN_BORDER = "#047857"
INDIGO_FILL = "#eef2ff"
INDIGO_BORDER = "#4f46e5"
ORANGE_FILL = "#fff7ed"
ORANGE_BORDER = "#b45309"
TEXT = "#0f172a"
MUTED = "#475569"
LINE = "#334155"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


TITLE_FONT = font(34, bold=True)
GROUP_FONT = font(21, bold=True)
NODE_FONT = font(22, bold=True)
SMALL_FONT = font(18)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fnt, fill: str = TEXT, max_chars: int = 18) -> None:
    x1, y1, x2, y2 = box
    lines = []
    for part in text.split("\n"):
        wrapped = textwrap.wrap(part, width=max_chars) or [part]
        lines.extend(wrapped[:3])
    line_heights = [text_size(draw, line, fnt)[1] for line in lines]
    total_h = sum(line_heights) + max(0, len(lines) - 1) * 6
    y = y1 + ((y2 - y1) - total_h) / 2
    for line, h in zip(lines, line_heights):
        w, _ = text_size(draw, line, fnt)
        draw.text((x1 + ((x2 - x1) - w) / 2, y), line, font=fnt, fill=fill)
        y += h + 6


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    label: str,
    fill: str = BLUE_FILL,
    outline: str = BLUE_BORDER,
    radius: int = 22,
    width: int = 4,
    fnt=NODE_FONT,
    max_chars: int = 18,
) -> None:
    shadow = (box[0] + 5, box[1] + 7, box[2] + 5, box[3] + 7)
    draw.rounded_rectangle(shadow, radius=radius, fill="#dbe3ee")
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)
    center_text(draw, box, label, fnt, max_chars=max_chars)


def diamond(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str) -> None:
    x1, y1, x2, y2 = box
    points = [
        ((x1 + x2) // 2, y1),
        (x2, (y1 + y2) // 2),
        ((x1 + x2) // 2, y2),
        (x1, (y1 + y2) // 2),
    ]
    draw.polygon(points, fill=ORANGE_FILL, outline=ORANGE_BORDER)
    draw.line(points + [points[0]], fill=ORANGE_BORDER, width=4, joint="curve")
    center_text(draw, box, label, NODE_FONT, max_chars=16)


def cylinder(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], label: str) -> None:
    rounded_box(draw, box, label, GREEN_FILL, GREEN_BORDER, radius=20, width=4, max_chars=16)
    x1, y1, x2, _ = box
    draw.arc((x1, y1, x2, y1 + 34), 180, 360, fill=GREEN_BORDER, width=3)


def arrow_head(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = LINE, size: int = 16) -> None:
    sx, sy = start
    ex, ey = end
    angle = math.atan2(ey - sy, ex - sx)
    left = (ex - size * math.cos(angle - math.pi / 6), ey - size * math.sin(angle - math.pi / 6))
    right = (ex - size * math.cos(angle + math.pi / 6), ey - size * math.sin(angle + math.pi / 6))
    draw.polygon([(ex, ey), left, right], fill=color)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], color: str = LINE, width: int = 4) -> None:
    draw.line([start, end], fill=color, width=width)
    arrow_head(draw, start, end, color=color)


def poly_arrow(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: str = LINE, width: int = 4) -> None:
    draw.line(points, fill=color, width=width, joint="curve")
    arrow_head(draw, points[-2], points[-1], color=color)


def title(draw: ImageDraw.ImageDraw, width: int, text: str) -> None:
    w, h = text_size(draw, text, TITLE_FONT)
    draw.text(((width - w) / 2, 28), text, font=TITLE_FONT, fill=TEXT)


def group_label(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, w: int) -> None:
    tw, _ = text_size(draw, text, GROUP_FONT)
    draw.text((x + (w - tw) / 2, y), text, font=GROUP_FONT, fill=MUTED)


def save(img: Image.Image, name: str) -> None:
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    img.save(DIAGRAM_DIR / name, "PNG", optimize=True)


def system_architecture() -> None:
    w, h = 2200, 1300
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    title(d, w, "Figure 1. System Architecture Diagram")

    actor = (80, 590, 350, 690)
    ui = (470, 590, 740, 690)
    pages_x, services_x, external_x = 850, 1240, 1690
    y0, step, bw, bh = 210, 135, 300, 86
    pages = [
        ("Upload CVs", "Resume Parser", "Local CSV Files"),
        ("Resume Ranking", "Ranking Service", "OpenAI API"),
        ("Bias Detection", "Bias Detection Service", "OpenAI API"),
        ("Synthetic CV Generation", "Synthetic CV Service", "OpenAI API"),
        ("Style Transformation", "Style Transformer", "OpenAI API"),
        ("RAG Assistant", "RAG Service", "Vector Cache"),
        ("Dashboard", "Storage Service", "Local CSV Files"),
    ]

    group_label(d, "User", actor[0], 130, actor[2] - actor[0])
    group_label(d, "Interface", ui[0], 130, ui[2] - ui[0])
    group_label(d, "Pages", pages_x, 130, bw)
    group_label(d, "Services", services_x, 130, bw)
    group_label(d, "External / Storage", external_x, 130, 330)

    rounded_box(d, actor, "Recruiter /\nReviewer", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, ui, "Streamlit UI", GRAY_FILL, GRAY_BORDER)
    arrow(d, (actor[2] + 10, 640), (ui[0] - 16, 640))

    page_bus_x = pages_x - 55
    service_bus_x = services_x - 45
    external_targets = {
        "OpenAI API": (external_x, 405, external_x + 320, 505),
        "Local CSV Files": (external_x, 620, external_x + 320, 720),
        "Vector Cache": (external_x, 835, external_x + 320, 935),
    }
    for label, box in external_targets.items():
        fill, border = (INDIGO_FILL, INDIGO_BORDER) if label == "OpenAI API" else (GREEN_FILL, GREEN_BORDER)
        cylinder(d, box, label) if label != "OpenAI API" else rounded_box(d, box, label, fill, border)

    arrow(d, (ui[2] + 10, 640), (page_bus_x - 8, 640))
    d.line([(page_bus_x, y0 + bh // 2), (page_bus_x, y0 + (len(pages) - 1) * step + bh // 2)], fill=LINE, width=4)
    d.line([(service_bus_x, y0 + bh // 2), (service_bus_x, y0 + (len(pages) - 1) * step + bh // 2)], fill=LINE, width=4)

    for i, (page, service, target) in enumerate(pages):
        y = y0 + i * step
        pbox = (pages_x, y, pages_x + bw, y + bh)
        sbox = (services_x, y, services_x + bw, y + bh)
        rounded_box(d, pbox, page, BLUE_FILL if i != 6 else GRAY_FILL, BLUE_BORDER if i != 6 else GRAY_BORDER, max_chars=18)
        rounded_box(d, sbox, service, BLUE_FILL if i != 6 else GREEN_FILL, BLUE_BORDER if i != 6 else GREEN_BORDER, max_chars=18)
        cy = y + bh // 2
        poly_arrow(d, [(page_bus_x, cy), (pbox[0] - 18, cy)])
        arrow(d, (pbox[2] + 10, cy), (sbox[0] - 18, cy))
        tbox = external_targets[target]
        ty = (tbox[1] + tbox[3]) // 2
        poly_arrow(d, [(sbox[2] + 10, cy), (sbox[2] + 85, cy), (sbox[2] + 85, ty), (tbox[0] - 18, ty)])

    save(img, "figure_01_system_architecture.png")


def ui_navigation() -> None:
    w, h = 1800, 900
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    title(d, w, "Figure 2. Streamlit UI Navigation Diagram")
    nodes = [
        ("Home Page", 70, 390),
        ("Upload CVs", 330, 390),
        ("Resume Ranking", 590, 390),
        ("Bias Detection", 850, 390),
        ("Synthetic CV\nGeneration", 1110, 390),
        ("Style\nTransformation", 1370, 260),
        ("RAG Assistant", 1370, 520),
        ("Dashboard", 1600, 390),
    ]
    boxes = {}
    for label, x, y in nodes:
        box = (x, y, x + 190, y + 92)
        boxes[label] = box
        rounded_box(d, box, label, max_chars=16)
    chain = nodes[:5]
    for (a, ax, ay), (b, bx, by) in zip(chain, chain[1:]):
        arrow(d, (ax + 200, ay + 46), (bx - 16, by + 46))
    arrow(d, (1110 + 200, 390 + 46), (1370 - 16, 260 + 46))
    arrow(d, (1110 + 200, 390 + 46), (1370 - 16, 520 + 46))
    arrow(d, (1370 + 200, 260 + 46), (1600 - 16, 390 + 46))
    arrow(d, (1370 + 200, 520 + 46), (1600 - 16, 390 + 46))
    save(img, "figure_02_ui_navigation.png")


def resume_ranking_flow() -> None:
    w, h = 1800, 1050
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    title(d, w, "Figure 3. Resume Ranking Flow")
    jd = (90, 250, 340, 345)
    cvs = (90, 465, 340, 560)
    extract = (450, 360, 720, 455)
    choice = (835, 345, 1035, 475)
    emb = (1145, 230, 1415, 325)
    key = (1145, 500, 1415, 595)
    score = (1510, 360, 1740, 455)
    skills = (1510, 535, 1740, 630)
    explain = (1145, 720, 1415, 815)
    save_box = (765, 720, 1035, 815)
    display = (390, 720, 660, 815)
    rounded_box(d, jd, "Job Description", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, cvs, "Uploaded CV\nRecords", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, extract, "Extract CV Text", BLUE_FILL, BLUE_BORDER)
    diamond(d, choice, "OpenAI API\nExists?")
    rounded_box(d, emb, "Generate\nEmbeddings", INDIGO_FILL, INDIGO_BORDER)
    rounded_box(d, key, "Fallback Keyword\nMatching", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, score, "Calculate\nMatch Score", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, skills, "Matched / Missing\nSkills", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, explain, "Generate\nExplanation", INDIGO_FILL, INDIGO_BORDER)
    rounded_box(d, save_box, "Save Ranking\nResults", GREEN_FILL, GREEN_BORDER)
    rounded_box(d, display, "Display Table\nand Chart", BLUE_FILL, BLUE_BORDER)
    poly_arrow(d, [(340, 298), (395, 298), (395, 408), (432, 408)])
    arrow(d, (340, 512), (432, 408))
    arrow(d, (720, 408), (815, 408))
    poly_arrow(d, [(1035, 385), (1090, 385), (1090, 278), (1127, 278)])
    poly_arrow(d, [(1035, 435), (1090, 435), (1090, 548), (1127, 548)])
    poly_arrow(d, [(1415, 278), (1460, 278), (1460, 408), (1492, 408)])
    poly_arrow(d, [(1415, 548), (1460, 548), (1460, 408), (1492, 408)])
    arrow(d, (1625, 455), (1625, 517))
    poly_arrow(d, [(1510, 582), (1460, 582), (1460, 768), (1433, 768)])
    arrow(d, (1145, 768), (1053, 768))
    arrow(d, (765, 768), (678, 768))
    save(img, "figure_03_resume_ranking_flow.png")


def bias_detection_flow() -> None:
    w, h = 1700, 980
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    title(d, w, "Figure 4. Bias Detection Flow")
    boxes = {
        "input": (80, 420, 310, 515),
        "norm": (410, 420, 640, 515),
        "dict": (740, 420, 970, 515),
        "found": (1080, 395, 1280, 540),
        "show": (1380, 250, 1640, 345),
        "chart": (1380, 420, 1640, 515),
        "rewrite": (740, 665, 970, 760),
        "review": (1080, 665, 1280, 760),
    }
    rounded_box(d, boxes["input"], "Job Description\nInput", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, boxes["norm"], "Normalize Text", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, boxes["dict"], "Check Bias\nDictionary", BLUE_FILL, BLUE_BORDER)
    diamond(d, boxes["found"], "Found\nTerms?")
    rounded_box(d, boxes["show"], "Show Terms,\nCategory,\nAlternative", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, boxes["chart"], "Bias Chart", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, boxes["rewrite"], "Optional Neutral\nRewrite", INDIGO_FILL, INDIGO_BORDER)
    rounded_box(d, boxes["review"], "Human Review", GRAY_FILL, GRAY_BORDER)
    arrow(d, (310, 468), (392, 468))
    arrow(d, (640, 468), (722, 468))
    arrow(d, (970, 468), (1062, 468))
    poly_arrow(d, [(1280, 430), (1330, 430), (1330, 298), (1362, 298)])
    arrow(d, (1280, 468), (1362, 468))
    poly_arrow(d, [(970, 468), (1015, 468), (1015, 712), (1058, 712)])
    arrow(d, (970, 712), (1062, 712))
    poly_arrow(d, [(80, 515), (80, 712), (722, 712)])
    save(img, "figure_04_bias_detection_flow.png")


def rag_pipeline() -> None:
    w, h = 1800, 1050
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    title(d, w, "Figure 5. RAG Pipeline")
    cv = (80, 240, 330, 335)
    chunk = (430, 240, 680, 335)
    index = (780, 240, 1030, 335)
    q = (80, 565, 330, 660)
    retrieve = (780, 565, 1030, 660)
    search1 = (1130, 430, 1400, 525)
    search2 = (1130, 700, 1400, 795)
    answer = (1490, 565, 1740, 660)
    sources = (1490, 795, 1740, 890)
    review = (1130, 890, 1400, 985)
    rounded_box(d, cv, "Uploaded CV\nRecords", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, chunk, "Chunk CV Text", BLUE_FILL, BLUE_BORDER)
    cylinder(d, index, "Build / Load\nIndex")
    rounded_box(d, q, "User Question", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, retrieve, "Retrieve Relevant\nChunks", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, search1, "OpenAI Embeddings", INDIGO_FILL, INDIGO_BORDER)
    rounded_box(d, search2, "Keyword Fallback", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, answer, "Generate Answer\nfrom Context", INDIGO_FILL, INDIGO_BORDER)
    rounded_box(d, sources, "Show Sources\nand Snippets", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, review, "Human Review", GRAY_FILL, GRAY_BORDER)
    arrow(d, (330, 288), (412, 288))
    arrow(d, (680, 288), (762, 288))
    poly_arrow(d, [(1030, 288), (1080, 288), (1080, 612), (1048, 612)])
    arrow(d, (330, 612), (762, 612))
    poly_arrow(d, [(1030, 612), (1080, 612), (1080, 478), (1112, 478)])
    poly_arrow(d, [(1030, 612), (1080, 612), (1080, 748), (1112, 748)])
    poly_arrow(d, [(1400, 478), (1445, 478), (1445, 612), (1472, 612)])
    poly_arrow(d, [(1400, 748), (1445, 748), (1445, 612), (1472, 612)])
    arrow(d, (1615, 660), (1615, 777))
    poly_arrow(d, [(1490, 842), (1445, 842), (1445, 938), (1418, 938)])
    save(img, "figure_05_rag_pipeline.png")


def synthetic_generation_flow() -> None:
    w, h = 1800, 980
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    title(d, w, "Figure 6. Synthetic CV Generation Flow")
    start = (80, 420, 360, 515)
    structured = (470, 420, 750, 515)
    fields = (860, 280, 1160, 395)
    text = (860, 560, 1160, 655)
    csv = (1270, 420, 1510, 515)
    pdf = (1600, 275, 1740, 370)
    charts = (1600, 560, 1740, 655)
    rounded_box(d, start, "Select Category\nor Requirements", GRAY_FILL, GRAY_BORDER)
    rounded_box(d, structured, "Generate Structured\nSynthetic CV Record", BLUE_FILL, BLUE_BORDER)
    rounded_box(d, fields, "Skills / Education /\nExperience / Projects /\nCertifications", BLUE_FILL, BLUE_BORDER, max_chars=20)
    rounded_box(d, text, "Generate\nResume Text", INDIGO_FILL, INDIGO_BORDER)
    cylinder(d, csv, "Save\nsynthetic_cvs.csv")
    rounded_box(d, pdf, "Optional PDF\nResume", GREEN_FILL, GREEN_BORDER)
    rounded_box(d, charts, "Display Table\nand Charts", BLUE_FILL, BLUE_BORDER)
    arrow(d, (360, 468), (452, 468))
    poly_arrow(d, [(750, 468), (805, 468), (805, 338), (842, 338)])
    poly_arrow(d, [(750, 468), (805, 468), (805, 608), (842, 608)])
    poly_arrow(d, [(1160, 338), (1210, 338), (1210, 468), (1252, 468)])
    poly_arrow(d, [(1160, 608), (1210, 608), (1210, 468), (1252, 468)])
    poly_arrow(d, [(1510, 468), (1555, 468), (1555, 322), (1582, 322)])
    poly_arrow(d, [(1510, 468), (1555, 468), (1555, 608), (1582, 608)])
    save(img, "figure_06_synthetic_cv_generation_flow.png")


def main() -> int:
    DIAGRAM_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in DIAGRAM_DIR.glob("figure_*.png"):
        old_file.unlink()
    for old_file in DIAGRAM_DIR.glob("figure_*.svg"):
        old_file.unlink()
    for old_file in DIAGRAM_DIR.glob("diagram_*.svg"):
        old_file.unlink()
    system_architecture()
    ui_navigation()
    resume_ranking_flow()
    bias_detection_flow()
    rag_pipeline()
    synthetic_generation_flow()
    for file_path in sorted(DIAGRAM_DIR.glob("figure_*.png")):
        print(file_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
