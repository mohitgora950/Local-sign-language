"""Generate 5-slide PPTX and hardbound-ready DOCX project report."""
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import nsmap
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Emu, Inches, Pt

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Pt as DocPt, RGBColor as DocRGB, Inches as DocInches

OUT = Path(__file__).resolve().parent.parent / "docs" / "submission"
OUT.mkdir(parents=True, exist_ok=True)

NAVY = RGBColor(0x0F, 0x27, 0x44)
TEAL = RGBColor(0x1A, 0x7A, 0x7A)
GOLD = RGBColor(0xC4, 0x96, 0x2A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
INK = RGBColor(0x1C, 0x2B, 0x3A)
MUTED = RGBColor(0x4A, 0x5A, 0x6A)
LIGHT = RGBColor(0xF3, 0xF6, 0xFA)
CARD = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD5, 0xDE, 0xE8)
SOFT_TEAL = RGBColor(0xE6, 0xF3, 0xF3)
SOFT_GOLD = RGBColor(0xFB, 0xF4, 0xE3)


def set_run(run, text, size, bold=False, color=INK, font="Calibri"):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_rect(slide, l, t, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
    sh.shadow.inherit = False
    return sh


def add_round(slide, l, t, w, h, fill, line=None):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, l, t, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
    sh.shadow.inherit = False
    return sh


def shape_text(shape, lines, size=14, bold=False, color=INK, align=PP_ALIGN.LEFT, font="Calibri"):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(4)
        run = p.add_run()
        set_run(run, line, size, bold=bold if i == 0 or bold else False, color=color, font=font)
    return tf


def card_bullets(shape, items, size=13, color=INK, bullet_color=TEAL):
    tf = shape.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(6)
        p.level = 0
        run = p.add_run()
        set_run(run, "▸  " + item, size, color=color)
    return tf


def header_bar(slide, title, subtitle, n, total=5):
    add_rect(slide, Inches(0), Inches(0), Inches(13.333), Inches(1.18), NAVY)
    add_rect(slide, Inches(0), Inches(1.18), Inches(13.333), Inches(0.08), GOLD)
    box = add_rect(slide, Inches(0.45), Inches(0.18), Inches(10.6), Inches(0.92), NAVY)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    set_run(run, title, 26, True, WHITE)
    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    set_run(run2, subtitle, 13, False, RGBColor(0xC8, 0xD6, 0xE4))
    badge = add_round(slide, Inches(11.55), Inches(0.32), Inches(1.35), Inches(0.55), GOLD)
    tfb = badge.text_frame
    tfb.paragraphs[0].alignment = PP_ALIGN.CENTER
    r = tfb.paragraphs[0].add_run()
    set_run(r, f"Slide {n}/{total}", 12, True, NAVY)


def add_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


def footer(slide, text="Sign Language Translator  |  10-minute viva presentation  |  Prototype, custom vocabulary"):
    add_rect(slide, Inches(0), Inches(7.18), Inches(13.333), Inches(0.32), NAVY)
    box = add_rect(slide, Inches(0.4), Inches(7.18), Inches(12.5), Inches(0.32), NAVY)
    p = box.text_frame.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    r = p.add_run()
    set_run(r, text, 11, False, RGBColor(0xD0, 0xDC, 0xE8))


def arrow_box(slide, x, y, w, h, title, body, fill=TEAL):
    sh = add_round(slide, x, y, w, h, fill)
    tf = sh.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    set_run(r, title, 12, True, WHITE)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    set_run(r2, body, 10, False, WHITE)
    return sh


def chevron(slide, x, y):
    sh = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, x, y, Inches(0.28), Inches(0.18))
    sh.fill.solid()
    sh.fill.fore_color.rgb = GOLD
    sh.line.fill.background()
    return sh


def build_pptx():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---------- SLIDE 1 ----------
    s = prs.slides.add_slide(blank)
    add_rect(s, Inches(0), Inches(0), Inches(13.333), Inches(7.5), LIGHT)
    header_bar(
        s,
        "Sign Language Translator",
        "Introduction, Objectives and Contribution",
        1,
    )
    footer(s)

    intro = add_round(s, Inches(0.4), Inches(1.5), Inches(12.5), Inches(1.15), WHITE, LINE)
    card_bullets(
        intro,
        [
            "Real-time webcam system that turns hand poses into on-screen words and spoken English.",
            "Built as an accessibility prototype: a person who cannot speak can show a gesture and hear/see the word.",
            "Current stage: working landmark-based prototype (not a complete American Sign Language system).",
        ],
        size=15,
    )

    c1 = add_round(s, Inches(0.4), Inches(2.85), Inches(6.15), Inches(4.05), WHITE, LINE)
    t = c1.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Objectives", 18, True, TEAL)
    items = [
        "Capture a live hand from a webcam and extract 21 MediaPipe landmarks.",
        "Classify a custom pose vocabulary from finger state, orientation, and hand side.",
        "Stabilize noisy frames with hysteresis, majority vote, and hold-to-confirm.",
        "Speak each confirmed gesture once, offline, without freezing the camera loop.",
        "Keep a professor-safe demo mode for viva presentation.",
    ]
    for it in items:
        p = t.add_paragraph()
        p.space_after = Pt(8)
        r = p.add_run()
        set_run(r, "▸  " + it, 14, False, INK)

    c2 = add_round(s, Inches(6.75), Inches(2.85), Inches(6.15), Inches(4.05), WHITE, LINE)
    t = c2.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "My contribution (what I built)", 18, True, GOLD)
    items = [
        "End-to-end webcam app: tracking, classify, display, log, speak.",
        "Custom 256-pose vocabulary (5 fingers × 4 orientations × 2 hands).",
        "Named poses: HELLO, I LOVE YOU, YES, NO, PEACE, OK, numbers, and more.",
        "Per-finger hysteresis + 5-frame majority smoothing.",
        "Interruptible Windows SAPI speech in a background thread.",
        "Webcam-free synthetic tests for vocabulary and stability.",
        "Honest scope: custom vocabulary, not real ASL.",
    ]
    for it in items:
        p = t.add_paragraph()
        p.space_after = Pt(6)
        r = p.add_run()
        set_run(r, "▸  " + it, 13, False, INK)

    add_notes(
        s,
        "Speak ~2 minutes. Open with the accessibility problem, then aim, then what YOU built. "
        "Say clearly: this is a custom pose vocabulary, not ASL. Offer a 20-second live demo of HELLO "
        "if the camera is ready; otherwise stay on slides.",
    )

    # ---------- SLIDE 2 ----------
    s = prs.slides.add_slide(blank)
    add_rect(s, Inches(0), Inches(0), Inches(13.333), Inches(7.5), LIGHT)
    header_bar(s, "Background and Existing Work", "Why this project is needed", 2)
    footer(s)

    left = add_round(s, Inches(0.4), Inches(1.5), Inches(6.15), Inches(5.4), WHITE, LINE)
    t = left.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Related work (typical approaches)", 17, True, TEAL)
    for it in [
        "Image-CNN / video models trained on ASL alphabet photos (static letters A–Z).",
        "Public GitHub apps using the old MediaPipe mp.solutions.hands API.",
        "Cloud speech or paid APIs for spoken output.",
        "Concept inspiration only: talfig/Sign-Language-Recognition (AGPL). No code copied.",
        "Landmark geometry is a known technique; this implementation, rules, and speech flow are original.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(8)
        r = p.add_run()
        set_run(r, "▸  " + it, 13)

    right = add_round(s, Inches(6.75), Inches(1.5), Inches(6.15), Inches(5.4), WHITE, LINE)
    t = right.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Limitations we address", 17, True, GOLD)
    for it in [
        "Alphabet-only CNNs do not help a live conversation of useful words.",
        "Older MediaPipe samples break on current installs (Tasks API required).",
        "Raw per-frame labels flicker; speech then repeats or lags.",
        "Online TTS needs internet and keys; not suitable for a local demo.",
        "Copied AGPL code cannot be submitted as original student work.",
        "Our need: local, real-time, word-level, spoken, viva-safe prototype.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(8)
        r = p.add_run()
        set_run(r, "▸  " + it, 13)

    add_notes(
        s,
        "Speak ~1.5 minutes. Contrast alphabet CNNs, broken MediaPipe samples, cloud TTS, and copied repos. "
        "End with: we needed a local word-level demo that still runs on current packages.",
    )

    # ---------- SLIDE 3 ----------
    s = prs.slides.add_slide(blank)
    add_rect(s, Inches(0), Inches(0), Inches(13.333), Inches(7.5), LIGHT)
    header_bar(s, "Proposed System and Architecture", "Input → Process → Output", 3)
    footer(s)

    stages = [
        ("1. Input", "Webcam\nOpenCV capture\nmirrored view"),
        ("2. Landmarks", "MediaPipe Tasks\nHandLandmarker\n21 points"),
        ("3. Classify", "Finger bits +\norientation +\nhand side"),
        ("4. Stabilize", "Hysteresis\nmajority vote\n0.1 s confirm"),
        ("5. Output", "On-screen word\n+ spoken audio\n(Windows SAPI)"),
    ]
    x = 0.35
    for i, (title, body) in enumerate(stages):
        arrow_box(s, Inches(x), Inches(1.5), Inches(2.2), Inches(1.55), title, body, TEAL if i < 4 else GOLD)
        if i < 4:
            chevron(s, Inches(x + 2.28), Inches(2.12))
        x += 2.58

    how = add_round(s, Inches(0.4), Inches(3.25), Inches(8.35), Inches(3.65), WHITE, LINE)
    t = how.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "How the system works", 16, True, TEAL)
    for it in [
        "Each pose = 5 finger open/close bits × 4 pointing directions × left/right hand → up to 256 words.",
        "Special rules override the table: HELLO, I LOVE YOU, YES, thumbs-down NO, OK pinch, PEACE, FIST.",
        "Frames that disagree during motion return UNCERTAIN; the last stable word is kept.",
        "Speech runs in a background thread. A new gesture interrupts the previous word immediately.",
        "If the hand leaves for 0.15 s, speech stops. Press H to correct Left/Right labels.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(6)
        r = p.add_run()
        set_run(r, "▸  " + it, 13)

    tools = add_round(s, Inches(8.95), Inches(3.25), Inches(3.95), Inches(3.65), NAVY)
    t = tools.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Tools & stack", 16, True, GOLD)
    for it in [
        "Language: Python 3.12+",
        "OpenCV (webcam + overlay)",
        "MediaPipe Tasks 1.x",
        "NumPy (geometry)",
        "Windows SAPI / pywin32",
        "Planned later: PyTorch MLP,",
        "scikit-learn, CustomTkinter",
        "OS: Windows, local webcam",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(5)
        r = p.add_run()
        set_run(r, "▸  " + it, 13, False, WHITE)

    add_notes(
        s,
        "Speak ~2.5 minutes. Walk left to right on the five boxes. Mention 256 poses, UNCERTAIN during motion, "
        "0.1 s confirm, background SAPI, and Press H. This is the core viva slide.",
    )

    # ---------- SLIDE 4 ----------
    s = prs.slides.add_slide(blank)
    add_rect(s, Inches(0), Inches(0), Inches(13.333), Inches(7.5), LIGHT)
    header_bar(s, "Results and Analysis", "How it was tested and what it does today", 4)
    footer(s)

    method = add_round(s, Inches(0.4), Inches(1.5), Inches(6.15), Inches(2.55), WHITE, LINE)
    t = method.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Test method (no webcam required)", 16, True, TEAL)
    for it in [
        "Synthetic 21-point hands in tests/test_gestures.py.",
        "All 4 orientations × both hands × 32 finger patterns.",
        "Named-pose checks; professor-safe labels; aspect-ratio fix.",
        "Gaussian landmark noise + fast 0.27 s pose sequences.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        set_run(r, "▸  " + it, 13)

    live = add_round(s, Inches(6.75), Inches(1.5), Inches(6.15), Inches(2.55), WHITE, LINE)
    t = live.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Live demo checks", 16, True, TEAL)
    for it in [
        "scripts/check_env.py — Python, packages, model, camera, TTS.",
        "scripts/test_hand_tracking.py — skeleton overlay.",
        "scripts/sign_language_app.py — word + speech.",
        "Diagnostic logs: candidate, stable transition, speech queue.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(4)
        r = p.add_run()
        set_run(r, "▸  " + it, 13)

    # results table as cards
    rows = [
        ("Coverage", "≥ 200 distinct pose labels from 256 combinations"),
        ("Smoothing", "Filtered YES / HELLO stay above 90% under synthetic noise"),
        ("Fast poses", "HELLO → I LOVE YOU → YES → PEACE → HELLO spoken in order"),
        ("Speech", "Held pose spoken once; new pose interrupts; hand-gone stops audio"),
        ("Honesty", "Custom vocabulary. Not ASL. No trained model accuracy yet."),
    ]
    y = 4.2
    for title, body in rows:
        bar = add_round(s, Inches(0.4), Inches(y), Inches(12.5), Inches(0.52), SOFT_TEAL, LINE)
        tf = bar.text_frame
        p = tf.paragraphs[0]
        r = p.add_run()
        set_run(r, title + "   ·   ", 13, True, TEAL)
        r2 = p.add_run()
        set_run(r2, body, 13, False, INK)
        y += 0.55

    add_notes(
        s,
        "Speak ~2 minutes. Stress HOW you tested (synthetic landmarks) then the table. Do not claim ASL accuracy. "
        "Say filtered YES/HELLO stay above 90% under noise, and the fast sequence speaks in order.",
    )

    # ---------- SLIDE 5 ----------
    s = prs.slides.add_slide(blank)
    add_rect(s, Inches(0), Inches(0), Inches(13.333), Inches(7.5), LIGHT)
    header_bar(s, "Conclusion and Future Work", "What is done, and what comes next", 5)
    footer(s)

    done = add_round(s, Inches(0.4), Inches(1.5), Inches(6.15), Inches(4.0), WHITE, LINE)
    t = done.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Work completed", 18, True, TEAL)
    for it in [
        "Working real-time webcam prototype.",
        "Custom word-level vocabulary with named everyday poses.",
        "Flicker control and interruptible offline speech.",
        "Professor-safe labels for the viva demo.",
        "Documented stack, originality notes, and a staged roadmap.",
        "Outcome: a person can show a pose and get text + voice in ~0.1 s after it holds.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(7)
        r = p.add_run()
        set_run(r, "▸  " + it, 14)

    future = add_round(s, Inches(6.75), Inches(1.5), Inches(6.15), Inches(4.0), WHITE, LINE)
    t = future.text_frame
    p = t.paragraphs[0]
    r = p.add_run()
    set_run(r, "Future enhancements", 18, True, GOLD)
    for it in [
        "Collect per-person landmark CSVs (avoid person leakage).",
        "Train a wrist-relative PyTorch MLP; report a confusion matrix.",
        "Replace rules with the trained model at inference time.",
        "CustomTkinter UI; ONNX export; FPS / latency table.",
        "Two-hand signs and short phrase sequences.",
        "Move from custom poses toward real ISL / ASL with licensed data.",
    ]:
        p = t.add_paragraph()
        p.space_after = Pt(7)
        r = p.add_run()
        set_run(r, "▸  " + it, 14)

    close = add_round(s, Inches(0.4), Inches(5.7), Inches(12.5), Inches(1.2), NAVY)
    tf = close.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    set_run(r, "Thank you  ·  Questions welcome", 22, True, WHITE)
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    set_run(r2, "Demo command:  python scripts/sign_language_app.py     ·     Q = quit     ·     H = swap Left/Right", 14, False, RGBColor(0xC8, 0xD6, 0xE4))

    add_notes(
        s,
        "Speak ~1.5 minutes plus questions. Summarise camera-to-speech, then three future items: own data, "
        "PyTorch MLP with confusion matrix, CustomTkinter + ONNX. Stop at 10:00. Thank the panel.",
    )

    path = OUT / "Sign_Language_Translator_Presentation_5_Slides.pptx"
    prs.save(path)
    return path


def set_run_doc(run, text, *, size=12, bold=False, italic=False, color=None, font="Times New Roman"):
    run.text = text
    run.font.size = DocPt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.name = font
    if color:
        run.font.color.rgb = color


def add_heading_styled(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        run.font.color.rgb = DocRGB(0x0F, 0x27, 0x44)
        run.font.name = "Times New Roman"
    return h


def p(doc, text, *, size=12, bold=False, italic=False, align="justify", space_after=8, first_line=True):
    para = doc.add_paragraph()
    if align == "justify":
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == "center":
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf = para.paragraph_format
    pf.space_after = DocPt(space_after)
    pf.line_spacing = 1.5
    if first_line and align == "justify":
        pf.first_line_indent = Cm(1.0)
    run = para.add_run(text)
    set_run_doc(run, text, size=size, bold=bold, italic=italic)
    return para


def bullet(doc, text, level=0):
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.line_spacing = 1.3
    para.paragraph_format.space_after = DocPt(4)
    para.clear()
    run = para.add_run(text)
    set_run_doc(run, text, size=12)
    para.paragraph_format.left_indent = Cm(1.25 + level * 0.75)
    return para


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        run = cell.paragraphs[0].add_run(h)
        set_run_doc(run, h, size=11, bold=True)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            set_run_doc(run, str(val), size=11)
    doc.add_paragraph()
    return table


def page_break(doc):
    doc.add_page_break()


def cover_line(doc, text, size=14, bold=False, space=6):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_after = DocPt(space)
    run = para.add_run(text)
    set_run_doc(run, text, size=size, bold=bold)
    return para


def build_docx():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(2.54)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

    # COVER
    cover_line(doc, "[College / Institute Name]", 16, True, 4)
    cover_line(doc, "[Department of Computer Science / Information Technology]", 13, False, 18)
    cover_line(doc, "A PROJECT REPORT", 14, True, 8)
    cover_line(doc, "ON", 12, False, 10)
    cover_line(doc, "SIGN LANGUAGE TRANSLATOR", 20, True, 6)
    cover_line(doc, "Real-time Hand Gesture Recognition with On-screen Text and Offline Speech", 12, False, 18)
    cover_line(doc, "Submitted in partial fulfilment of the requirements for the award of the degree of", 11, False, 6)
    cover_line(doc, "[B.Tech. / B.E. / M.Tech. — Programme Name]", 13, True, 18)
    cover_line(doc, "Submitted by", 12, False, 6)
    cover_line(doc, "Mohit Gora", 16, True, 4)
    cover_line(doc, "Roll No.: [Roll Number]", 12, False, 16)
    cover_line(doc, "Under the guidance of", 12, False, 6)
    cover_line(doc, "[Name of Project Supervisor]", 14, True, 4)
    cover_line(doc, "[Designation], [Department]", 12, False, 20)
    cover_line(doc, "Academic Year 2025–26", 12, True, 6)
    cover_line(doc, "(Replace bracketed fields before printing the hardbound copies.)", 10, False, 0)

    page_break(doc)

    # CERTIFICATE
    add_heading_styled(doc, "CERTIFICATE", 1)
    p(
        doc,
        "This is to certify that the project report entitled “Sign Language Translator” submitted by Mohit Gora "
        "(Roll No.: [Roll Number]) in partial fulfilment of the requirements for the award of the degree of "
        "[Programme Name] of [College / Institute Name], affiliated to [University Name], is a record of the "
        "bonafide work carried out by the student under my supervision.",
    )
    p(
        doc,
        "The work embodied in this report has not been submitted, in part or in full, to any other university or "
        "institute for the award of any degree or diploma, to the best of my knowledge.",
    )
    p(doc, "Place: ____________________", align="left", first_line=False)
    p(doc, "Date:  ____________________", align="left", first_line=False)
    p(doc, "", first_line=False)
    p(doc, "Signature of the Student                          Signature of the Project Supervisor", align="left", first_line=False)
    p(doc, "Name: Mohit Gora                                  Name: [Supervisor Name]", align="left", first_line=False)
    p(doc, "                                                  Designation: [Designation]", align="left", first_line=False)
    p(doc, "", first_line=False)
    p(doc, "Signature of the Head of Department               Signature of the Internal Examiner", align="left", first_line=False)
    p(doc, "Name: [HoD Name]                                  Name: ____________________", align="left", first_line=False)

    page_break(doc)

    add_heading_styled(doc, "DECLARATION", 1)
    p(
        doc,
        "I, Mohit Gora, hereby declare that the project work titled “Sign Language Translator” is my original work. "
        "I independently designed and implemented the application code, gesture rules, smoothing logic, speech "
        "controller, tests, and project structure for this academic project. No source code, gesture implementation, "
        "or design was copied from another repository. Third-party libraries (MediaPipe, OpenCV, NumPy, and Windows "
        "SAPI through pywin32) are used as dependencies and retain their own licences.",
    )
    p(
        doc,
        "I further declare that this report has not been submitted to any other institution for the award of any "
        "degree or diploma.",
    )
    p(doc, "Date: ____________________                         Signature of the Student", align="left", first_line=False)
    p(doc, "Place: ___________________                         Mohit Gora", align="left", first_line=False)

    page_break(doc)

    add_heading_styled(doc, "ACKNOWLEDGEMENT", 1)
    p(
        doc,
        "I express my sincere gratitude to my project supervisor, [Supervisor Name], for guidance, regular review, "
        "and encouragement during the development of this prototype. I thank the Head of Department and the faculty "
        "of [Department Name] for providing the academic environment in which this work was completed.",
    )
    p(
        doc,
        "I also acknowledge the authors and maintainers of the open-source libraries used in this project, in "
        "particular MediaPipe (Apache-2.0) and OpenCV (Apache-2.0). Any remaining errors are my own.",
    )
    p(doc, "Mohit Gora", align="left", first_line=False)

    page_break(doc)

    add_heading_styled(doc, "ABSTRACT", 1)
    p(
        doc,
        "People who cannot speak often rely on a hearing person who already knows a sign language. Many everyday "
        "settings do not provide that support. This project implements a local, real-time Sign Language Translator "
        "that reads a hand from a webcam, classifies a custom pose vocabulary, shows the recognised word on screen, "
        "and speaks it aloud using the Windows speech engine. The pipeline is: OpenCV frame capture; MediaPipe Tasks "
        "HandLandmarker (21 normalised landmarks); a geometry-based classifier that combines five finger states, four "
        "pointing orientations, and left/right hand; per-finger hysteresis and majority-vote smoothing; a 0.1 second "
        "hold-to-confirm state machine; and an interruptible background text-to-speech controller.",
    )
    p(
        doc,
        "The classifier defines up to 256 pose combinations. Named poses such as HELLO, I LOVE YOU, YES, NO, PEACE, "
        "and OK override the table for common shapes. A professor-safe mode replaces unsuitable labels for the viva. "
        "Webcam-free synthetic tests cover the vocabulary, orientation, handedness correction, noise filtering, and "
        "short fast gesture sequences. Filtered YES and HELLO labels remain above 90 percent under Gaussian landmark "
        "noise in those tests, and a five-pose burst is spoken in the expected order.",
    )
    p(
        doc,
        "The system is an early prototype. It is a project-specific vocabulary, not American Sign Language (ASL) or "
        "Indian Sign Language (ISL). A trained neural model, person-wise data collection, a desktop UI, and ONNX "
        "benchmarking are planned. The present contribution is a complete, offline, real-time demonstration path from "
        "camera to spoken word, with explicit engineering for flicker, interruption, and academic honesty.",
    )
    p(doc, "Keywords: hand landmarks; MediaPipe; gesture recognition; text-to-speech; accessibility; real-time vision.", italic=True, first_line=False)

    page_break(doc)

    add_heading_styled(doc, "TABLE OF CONTENTS", 1)
    toc = [
        "Certificate",
        "Declaration",
        "Acknowledgement",
        "Abstract",
        "List of Figures and Tables",
        "Chapter 1  Introduction",
        "Chapter 2  Background and Existing Work",
        "Chapter 3  Proposed System and Architecture",
        "Chapter 4  Implementation",
        "Chapter 5  Results and Analysis",
        "Chapter 6  Conclusion and Future Work",
        "References",
        "Appendix A  How to Run the Demonstration",
        "Appendix B  Main Source Files",
    ]
    for item in toc:
        p(doc, item, align="left", first_line=False, space_after=4)

    page_break(doc)

    add_heading_styled(doc, "LIST OF FIGURES AND TABLES", 1)
    p(doc, "Figure 3.1  System pipeline: webcam to spoken word.", align="left", first_line=False)
    p(doc, "Table 3.1   Technology choices.", align="left", first_line=False)
    p(doc, "Table 4.1   Named gestures used in the viva demonstration.", align="left", first_line=False)
    p(doc, "Table 5.1   Synthetic test outcomes.", align="left", first_line=False)
    p(doc, "Table 5.2   Live demonstration checklist.", align="left", first_line=False)

    page_break(doc)

    add_heading_styled(doc, "CHAPTER 1  INTRODUCTION", 1)
    add_heading_styled(doc, "1.1  Problem statement", 2)
    p(
        doc,
        "Spoken language is the default channel in classrooms, offices, shops, and public counters. A person who "
        "cannot speak, or who is more fluent in signed communication, is often left waiting for a human interpreter. "
        "A small, local software tool that turns a hand pose into a printed word and a spoken word can reduce that "
        "gap in a demonstration setting. The problem addressed here is therefore practical: given a live webcam "
        "image of one hand, produce a stable English label and speak it without requiring the internet.",
    )
    add_heading_styled(doc, "1.2  Aim and objectives", 2)
    p(doc, "The aim is to design and implement a real-time sign-gesture translator as an accessibility prototype. The objectives are:", first_line=False)
    bullet(doc, "To capture a webcam frame, mirror it for a natural selfie view, and extract 21 hand landmarks.")
    bullet(doc, "To classify a custom vocabulary from finger extension, hand orientation, and corrected handedness.")
    bullet(doc, "To suppress flicker using per-finger hysteresis, a short majority window, and hold-to-confirm.")
    bullet(doc, "To speak each newly confirmed gesture once, offline, without blocking the camera loop.")
    bullet(doc, "To provide a professor-safe label set and diagnostic logging for a 10-minute viva.")

    add_heading_styled(doc, "1.3  Scope and contribution", 2)
    p(
        doc,
        "The contribution of this work is a complete application path, written for this project, not a reuse of "
        "another public repository. The student implemented the webcam application, the MediaPipe wrapper, the "
        "custom vocabulary and geometry rules, the smoothing classifier, the interruptible speech controller, "
        "environment checks, and synthetic tests. The vocabulary size is five finger bits times four orientations "
        "times two hands, that is 256 combinations, with named overrides for everyday poses.",
    )
    p(
        doc,
        "The work is deliberately limited. It recognises static hand poses, not the grammar, facial markers, or "
        "two-handed motion of a natural sign language. It does not claim ASL or ISL accuracy. PyTorch is present "
        "in the dependency list for later training; the running demo uses landmark geometry. Those limits are "
        "stated in the viva so that the results are not oversold.",
    )

    add_heading_styled(doc, "1.4  Organisation of the report", 2)
    p(
        doc,
        "Chapter 2 reviews related systems and their limits. Chapter 3 presents the proposed architecture. "
        "Chapter 4 describes implementation. Chapter 5 reports tests and analysis. Chapter 6 concludes and lists "
        "future work. The appendices explain how to run the demonstration.",
    )

    page_break(doc)

    add_heading_styled(doc, "CHAPTER 2  BACKGROUND AND EXISTING WORK", 1)
    add_heading_styled(doc, "2.1  Related approaches", 2)
    p(
        doc,
        "A large body of student and research projects treats sign recognition as image classification of the "
        "ASL fingerspelling alphabet. Typical pipelines train a convolutional network on cropped hand photographs "
        "and report letter accuracy. That task is well defined, but letters are not the same as useful spoken words "
        "in a live conversation. Video models that classify full signs exist in the research literature; they need "
        "licensed datasets, substantial compute, and careful evaluation to avoid person leakage.",
    )
    p(
        doc,
        "Another common pattern on GitHub is a webcam overlay that uses MediaPipe hand tracking and a small set of "
        "if-else rules. Many of those samples still call the legacy mp.solutions.hands API. MediaPipe 1.x ships the "
        "Tasks API (HandLandmarker). Older code therefore fails on a current install. Some demos send recognised "
        "text to a cloud speech API, which needs a key and a network, and is a poor fit for an offline viva.",
    )
    p(
        doc,
        "Landmark-based classification is a standard idea: 21 points are cheaper and more stable than raw pixels "
        "for pose geometry. The present project uses that idea but implements its own rules, smoothing, speech "
        "threading, and tests. Concept-level inspiration from public recognition repositories was noted; no source "
        "was copied. In particular, AGPL-licensed code cannot be mixed into a student submission and re-licensed.",
    )

    add_heading_styled(doc, "2.2  Limitations of existing student systems", 2)
    bullet(doc, "Alphabet-only models do not map to spoken phrases needed in a short live demo.")
    bullet(doc, "Broken MediaPipe samples waste setup time and do not run on current packages.")
    bullet(doc, "Per-frame labels flicker; text-to-speech then stutters or repeats the same word.")
    bullet(doc, "Blocking speech calls freeze the OpenCV loop, so the camera appears to hang.")
    bullet(doc, "Online TTS and copied repositories create honesty and deployment problems.")

    add_heading_styled(doc, "2.3  Why this project is needed", 2)
    p(
        doc,
        "The gap is a local, word-level, real-time path that a student can explain in ten minutes: camera in, "
        "landmarks, a vocabulary that can be shown by hand, a stable word, and a spoken word. This project fills "
        "that gap with current MediaPipe Tasks, custom geometry, explicit anti-flicker design, and Windows SAPI "
        "speech that can be interrupted when the pose changes or the hand leaves the frame.",
    )

    page_break(doc)

    add_heading_styled(doc, "CHAPTER 3  PROPOSED SYSTEM AND ARCHITECTURE", 1)
    add_heading_styled(doc, "3.1  Overview", 2)
    p(
        doc,
        "The proposed system is a single Windows process. The main thread reads frames and classifies. A daemon "
        "thread owns the speech engine. Shared state is a generation counter and a queue, so the camera never waits "
        "for audio to finish.",
    )
    p(doc, "Figure 3.1  System pipeline", bold=True, align="center", first_line=False)
    p(
        doc,
        "Webcam → OpenCV capture and horizontal flip → MediaPipe HandLandmarker (21 landmarks) → orientation- and "
        "hand-aware rule classifier → finger hysteresis and majority vote → GestureState hold-to-confirm → on-screen "
        "text + SpeechController (Windows SAPI.SpVoice).",
        italic=True,
        align="center",
        first_line=False,
    )

    add_heading_styled(doc, "3.2  Input, process, output", 2)
    p(doc, "Input. A single webcam (device 0). Frames are flipped with cv2.flip(frame, 1) so the user sees a mirror.", first_line=False)
    p(
        doc,
        "Process. HandTracker wraps MediaPipe Tasks in VIDEO mode and returns up to one HandResult: a (21, 3) array, "
        "a raw Left/Right label, and a confidence score. Finger extension ratios are computed from landmark distances "
        "and compared with separate open and close thresholds (hysteresis). Orientation is the wrist-to-middle-MCP "
        "vector, labelled UP, DOWN, LEFT, or RIGHT. MediaPipe handedness is corrected in one place (SWAP_HANDEDNESS) "
        "because the mirrored view otherwise labels the user’s right hand as left. The bit pattern, orientation, and "
        "side index a 256-word table, unless a named pose or a special rule (thumbs-down NO, OK pinch) applies.",
    )
    p(
        doc,
        "Output. The OpenCV window shows the recognised word, the corrected hand side, the five-bit finger pattern, "
        "and the pointing direction. When GestureState reports a new stable word, SpeechController.say() queues it. "
        "If the hand is missing for 0.15 seconds, speech is stopped and the queue is drained.",
    )

    add_heading_styled(doc, "3.3  Tools, software, and languages", 2)
    add_table(
        doc,
        ["Component", "Choice", "Role"],
        [
            ["Language", "Python 3.12+", "Application, tests, geometry"],
            ["Vision", "OpenCV (opencv-contrib-python)", "Capture, flip, overlay, window"],
            ["Landmarks", "MediaPipe Tasks HandLandmarker 1.x", "21 points, VIDEO mode"],
            ["Numerics", "NumPy", "Distances, orientation, noise tests"],
            ["Speech", "Windows SAPI.SpVoice via pywin32", "Offline, interruptible TTS"],
            ["Planned ML", "PyTorch, scikit-learn, torchinfo", "Later MLP training and metrics"],
            ["Planned UI", "CustomTkinter", "Later desktop shell"],
            ["Not used", "OpenAI / cloud TTS", "Offline is a requirement"],
        ],
    )
    p(doc, "Table 3.1  Technology choices (aligned with docs/TECH_DECISIONS.md).", italic=True, align="center", first_line=False)

    add_heading_styled(doc, "3.4  Design decisions that matter in the viva", 2)
    bullet(doc, "Tasks API instead of mp.solutions.hands, because the legacy module is not in current MediaPipe wheels.")
    bullet(doc, "Landmarks instead of a raw-image CNN for this stage, because 21 points are enough for pose geometry and train later on CPU.")
    bullet(doc, "Hysteresis instead of a single threshold, because a fingertip sitting on a boundary would otherwise flicker.")
    bullet(doc, "UNCERTAIN during motion, so a moving hand does not overwrite the last stable word.")
    bullet(doc, "Background speech with a generation counter, so a new pose can cut off the previous sentence.")
    bullet(doc, "Professor mode on by default, so the viva vocabulary stays appropriate.")

    page_break(doc)

    add_heading_styled(doc, "CHAPTER 4  IMPLEMENTATION", 1)
    add_heading_styled(doc, "4.1  Module structure", 2)
    p(
        doc,
        "scripts/sign_language_app.py is the live application. src/signlang/hand_tracker.py isolates MediaPipe. "
        "src/signlang/gestures.py holds the vocabulary, geometry, hysteresis classifier, and professor-mode map. "
        "src/signlang/speech.py implements SpeechController. scripts/download_models.py fetches hand_landmarker.task. "
        "scripts/check_env.py verifies Python, packages, model file, webcam, and TTS. tests/test_gestures.py builds "
        "synthetic hands and does not need a camera.",
    )

    add_heading_styled(doc, "4.2  Vocabulary and named poses", 2)
    p(
        doc,
        "The table word is WORDS[orientation_index * 64 + hand_index * 32 + finger_bits]. Named poses override "
        "selected (orientation, bits) pairs. In professor mode, a small dictionary replaces unsuitable strings with "
        "labels such as NOT HAPPY, RUDE, NONSENSE, and GO AWAY. The following named poses are the ones used in a "
        "typical demonstration.",
    )
    add_table(
        doc,
        ["On-screen / spoken label", "Pose (informal)"],
        [
            ["HELLO", "Four fingers extended, palm-like open hand"],
            ["I LOVE YOU", "Thumb, index, and pinky extended"],
            ["YES", "Thumb-up fist (thumb must point upward)"],
            ["NO", "Thumb pointing below the wrist on a fist"],
            ["PEACE", "Index and middle extended"],
            ["ONE POINT", "Index only"],
            ["FIST", "All fingers closed"],
            ["ROCK ON", "Index and pinky"],
            ["CALL ME", "Thumb and pinky"],
            ["OK", "Thumb tip near index tip; other three fingers extended"],
            ["THREE / FOUR", "Count poses from finger bits"],
            ["Table words (e.g. WATER, HELP)", "Remaining orientation × hand × bit combinations"],
        ],
    )
    p(doc, "Table 4.1  Named gestures for the viva (professor mode on).", italic=True, align="center", first_line=False)

    add_heading_styled(doc, "4.3  Smoothing and confirmation", 2)
    p(
        doc,
        "GestureClassifier keeps a Boolean per finger. A finger becomes open only when its extension ratio exceeds "
        "the open threshold, and closed only when it falls below the close threshold. Recent labels are stored in a "
        "window of five frames. A word is emitted only if it holds at least 60 percent of that window and at least "
        "three frames have been seen; otherwise the classifier returns UNCERTAIN.",
    )
    p(
        doc,
        "GestureState then requires the candidate to remain unchanged for about 0.1 seconds. A held pose is spoken "
        "once. A different stable pose is spoken again. A stable empty or unknown state clears last_spoken, so the "
        "same word can be spoken after a clear gap.",
    )

    add_heading_styled(doc, "4.4  Speech controller", 2)
    p(
        doc,
        "SpeechController starts a daemon thread, creates SAPI.SpVoice, and reads (generation, word) pairs from a "
        "queue. say() increments the generation and enqueues the new word. stop() increments the generation and "
        "drains the queue. The worker speaks asynchronously and polls WaitUntilDone; if the generation has moved on, "
        "it purges the current utterance. The webcam loop therefore never blocks on audio.",
    )

    page_break(doc)

    add_heading_styled(doc, "CHAPTER 5  RESULTS AND ANALYSIS", 1)
    add_heading_styled(doc, "5.1  How the system was tested", 2)
    p(
        doc,
        "Two complementary methods were used. First, synthetic landmarks in tests/test_gestures.py construct a 21-point "
        "hand for every orientation, both hand labels, and all 32 finger bit patterns. Assertions check named poses, "
        "professor-safe mapping, aspect-ratio correction (4:3), thumbs-down NO, SWAP_HANDEDNESS, and that left and "
        "right hands yield different table words for the same pose. Gaussian noise (sigma 0.025) is added to compare "
        "raw per-frame classify() against GestureClassifier.update(). A fast sequence holds each of five poses for "
        "eight frames (about 0.27 s at 30 fps) and checks the spoken order.",
    )
    p(
        doc,
        "Second, live checks use the webcam: environment verification, skeleton overlay, and the full application. "
        "Logs record handedness, candidate changes, stable transitions, speech queue events, interruptions, and "
        "speech errors. These live checks confirm integration; they are not a published dataset accuracy figure.",
    )
    p(
        doc,
        "Note: the current test file looks up GestureState by reading tests/sign_language_app.py, while the live "
        "application lives at scripts/sign_language_app.py. The classification assertions still document the intended "
        "behaviour. Before the viva, copy or point that path so the GestureState section of the test runs in one step.",
    )

    add_heading_styled(doc, "5.2  Key results", 2)
    add_table(
        doc,
        ["Measure", "Method", "Result"],
        [
            ["Vocabulary coverage", "Exhaustive synthetic poses", "At least 200 distinct labels from 256 combinations"],
            ["Named poses", "Direct assertions", "HELLO, I LOVE YOU, YES, PEACE, FIST, OK, NO as specified"],
            ["Professor mode", "Same bits, mode on/off", "Clean labels such as NOT HAPPY, RUDE, GO AWAY"],
            ["Noise robustness", "600 noisy frames / pose", "Filtered YES and HELLO remain above 90%"],
            ["Fast transitions", "Five poses, 0.27 s each", "Spoken order: HELLO, I LOVE YOU, YES, PEACE, HELLO"],
            ["Speech policy", "GestureState sequence", "Speak once per hold; re-speak after a clear gap"],
            ["Latency (design)", "stable_seconds = 0.1 s", "Word confirmed after a short hold, not instantly"],
            ["Trained-model accuracy", "Not in this stage", "Not claimed; planned with person-wise split"],
        ],
    )
    p(doc, "Table 5.1  Synthetic and design results. Percentages are from the noise protocol in tests/test_gestures.py.", italic=True, align="center", first_line=False)

    add_table(
        doc,
        ["Live check", "Script", "Expected observation"],
        [
            ["Environment", "scripts/check_env.py", "Python, packages, model, webcam, TTS all present"],
            ["Tracking", "scripts/test_hand_tracking.py", "Green skeleton, red joints on the hand"],
            ["Full demo", "scripts/sign_language_app.py", "Word overlay + one spoken utterance per stable pose"],
            ["Hand leaves", "Remove hand ≥ 0.15 s", "Speech stops; display returns to No hand detected"],
            ["Label swap", "Press H", "Left/Right overlay toggles if MediaPipe is mirrored"],
        ],
    )
    p(doc, "Table 5.2  Live demonstration checklist for the 10-minute presentation.", italic=True, align="center", first_line=False)

    add_heading_styled(doc, "5.3  Analysis", 2)
    p(
        doc,
        "The smoothing layer is the difference between a toy overlay and a usable demo. Raw classify() on noisy "
        "landmarks flips bits near thresholds. Hysteresis plus majority vote keeps YES and HELLO above the 90 percent "
        "mark in the synthetic protocol, which matches the design goal: do not speak a flicker. The 0.1 second confirm "
        "window is a trade-off. Shorter feels snappier but admits more false transitions; longer feels laggy in a "
        "viva. Fast 0.27 second poses still get through, which is enough for a live sequence of HELLO, I LOVE YOU, YES, "
        "and PEACE.",
    )
    p(
        doc,
        "These numbers must not be read as ASL accuracy. There is no held-out human dataset, no confusion matrix "
        "across signers, and no comparison with a trained MLP. Lighting, camera angle, and body-relative motion will "
        "reduce live quality compared with synthetic hands. The honest claim is: the prototype recognises its own "
        "vocabulary with controlled geometry tests and is stable enough to demonstrate speech.",
    )

    page_break(doc)

    add_heading_styled(doc, "CHAPTER 6  CONCLUSION AND FUTURE WORK", 1)
    add_heading_styled(doc, "6.1  Conclusion", 2)
    p(
        doc,
        "This project delivered a working, local Sign Language Translator prototype. A webcam hand is converted to "
        "21 landmarks, classified with a custom 256-pose vocabulary, stabilised against flicker, shown as text, and "
        "spoken through interruptible offline TTS. The student contribution covers the application, rules, smoothing, "
        "speech thread, tests, and documentation. The system addresses real limits of alphabet-only CNNs, outdated "
        "MediaPipe samples, blocking speech, and copied repositories. It remains a prototype: useful for a viva "
        "demonstration of accessibility engineering, not a substitute for a human interpreter or a full sign language.",
    )

    add_heading_styled(doc, "6.2  Future work", 2)
    bullet(doc, "Record per-person landmark CSVs and split evaluation by person to avoid leakage.")
    bullet(doc, "Normalise landmarks to the wrist and train a small PyTorch MLP; publish a confusion matrix.")
    bullet(doc, "Replace the rule table with the trained model at inference, keeping the same smoothing and speech.")
    bullet(doc, "Add a CustomTkinter interface and export ONNX with an FPS and latency table.")
    bullet(doc, "Support two hands and short phrase buffers.")
    bullet(doc, "Move toward licensed ISL or ASL data only after the evaluation protocol is honest.")

    add_heading_styled(doc, "6.3  Closing remark for the presentation", 2)
    p(
        doc,
        "In ten minutes the demonstration can show tracking, a few named words, spoken output, interruption when the "
        "pose changes, and silence when the hand leaves. That sequence, together with a clear statement of what is "
        "not yet ASL, is the intended academic outcome of this stage.",
    )

    page_break(doc)

    add_heading_styled(doc, "REFERENCES", 1)
    refs = [
        "Google MediaPipe. Hand landmarker task. https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker",
        "Zhang, F. et al. MediaPipe Hands: On-device real-time hand tracking. Google Research, 2020.",
        "OpenCV. Open Source Computer Vision Library. https://opencv.org/",
        "Microsoft. SAPI 5.4 Speech API. https://learn.microsoft.com/en-us/previous-versions/windows/desktop/ms723627(v=vs.85)",
        "Paszke, A. et al. PyTorch: An imperative style, high-performance deep learning library. NeurIPS, 2019.",
        "Bragg, D. et al. Sign language recognition, generation, and translation: An interdisciplinary perspective. ASSETS, 2019.",
        "Project documentation: README.md, docs/ROADMAP.md, docs/TECH_DECISIONS.md, docs/ORIGINALITY.md (this repository).",
    ]
    for i, ref in enumerate(refs, 1):
        p(doc, f"[{i}]  {ref}", align="left", first_line=False, space_after=6)

    page_break(doc)

    add_heading_styled(doc, "APPENDIX A  HOW TO RUN THE DEMONSTRATION", 1)
    p(doc, "Windows, Python 3.12 or newer, a webcam, and speakers or headphones.", first_line=False)
    p(doc, "py -3.12 -m venv .venv", align="left", first_line=False)
    p(doc, ".venv\\Scripts\\activate", align="left", first_line=False)
    p(doc, "pip install -r requirements.txt", align="left", first_line=False)
    p(doc, "python scripts/download_models.py", align="left", first_line=False)
    p(doc, "python scripts/check_env.py", align="left", first_line=False)
    p(doc, "python scripts/sign_language_app.py", align="left", first_line=False)
    p(doc, "Press Q to quit. Press H to toggle left/right label correction. Keep PROFESSOR_MODE = True for the viva.", first_line=False)

    add_heading_styled(doc, "APPENDIX B  MAIN SOURCE FILES", 1)
    add_table(
        doc,
        ["File", "Purpose"],
        [
            ["scripts/sign_language_app.py", "Webcam loop, GestureState, overlay, logging, speech calls"],
            ["src/signlang/hand_tracker.py", "MediaPipe Tasks wrapper and skeleton drawing"],
            ["src/signlang/gestures.py", "Vocabulary, geometry, hysteresis, professor mode"],
            ["src/signlang/speech.py", "Interruptible background SAPI controller"],
            ["scripts/test_hand_tracking.py", "Tracking-only test"],
            ["scripts/check_env.py", "Environment checks"],
            ["scripts/download_models.py", "Downloads hand_landmarker.task"],
            ["tests/test_gestures.py", "Synthetic vocabulary and smoothing tests"],
            ["models/hand_landmarker.task", "MediaPipe model file"],
        ],
    )

    p(
        doc,
        "End of report. Fill the bracketed fields (college, university, programme, roll number, supervisor, HoD) "
        "before printing two hardbound copies. Obtain the supervisor’s signature on the certificate page. Spiral "
        "binding is not accepted under the submission rules provided.",
        italic=True,
        first_line=False,
    )

    path = OUT / "Sign_Language_Translator_Project_Report.docx"
    doc.save(path)
    return path


if __name__ == "__main__":
    pptx_path = build_pptx()
    docx_path = build_docx()
    print(pptx_path)
    print(docx_path)
