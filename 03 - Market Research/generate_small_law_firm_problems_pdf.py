"""Generate the designed PDF of the research report
"Small law firm problems UK US" (reports/Small law firm problems UK US.md).

Reader: Mustafa (AI/RAG engineer). Content: problems, workflows, numbers,
vocabulary, gap cards and facts about existing products. No solutions or
recommendations are added; every number and dated quote in the source report
is carried over, inline URLs become numbered [n] references that resolve in
the Sources appendix, and the report's evidence tags ([snippet], [vendor],
[user, date], [secondary], [3p]) survive as small grey superscript tags.

Pipeline
  1. parse the markdown report into sections, paragraphs and tables
  2. build a URL registry in order of first appearance (the [n] numbers)
  3. render charts with matplotlib to PNG (200 dpi) in the scratchpad folder
  4. lay the document out with reportlab platypus (A4, DejaVu Sans)
  5. two-pass build so the contents page carries real page numbers

Run:  python generate_small_law_firm_problems_pdf.py
"""

import os
import re
import sys
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, inch
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
                                Spacer, Table, TableStyle, Image, PageBreak,
                                KeepTogether, HRFlowable, NextPageTemplate,
                                CondPageBreak, Flowable)
from reportlab.platypus.tableofcontents import TableOfContents

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
REPORT = Path(r"D:\Mustafa AI\reports\Small law firm problems UK US.md")
OUT_PDF = Path(r"D:\Mustafa AI\03 - Market Research\Small Law Firm Problems UK-US (11 Oct 2026).pdf")
CHART_DIR = Path(r"C:\Users\MICROS~1\AppData\Local\Temp\claude\d--Mustafa-AI\ed3e6955-5f88-400b-a9f5-fd8bdbc9bceb\scratchpad\pdfcharts")
FONT_DIR = Path(r"C:\Users\Microsoft\AppData\Local\Programs\Python\Python312\Lib\site-packages\matplotlib\mpl-data\fonts\ttf")
CHART_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------------------------------
# Fonts: DejaVu Sans everywhere so that £, €, curly quotes, dashes, arrows render
# --------------------------------------------------------------------------
pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", str(FONT_DIR / "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", str(FONT_DIR / "DejaVuSans-BoldOblique.ttf")))
addMapping("DejaVu", 0, 0, "DejaVu")
addMapping("DejaVu", 1, 0, "DejaVu-Bold")
addMapping("DejaVu", 0, 1, "DejaVu-Oblique")
addMapping("DejaVu", 1, 1, "DejaVu-BoldOblique")

for _f in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans-Oblique.ttf"):
    font_manager.fontManager.addfont(str(FONT_DIR / _f))
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 7.5,
    "xtick.labelsize": 7.2,
    "ytick.labelsize": 7.2,
    "legend.fontsize": 7.2,
    "axes.edgecolor": "#c3c2b7",
    "axes.linewidth": 0.6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "xtick.color": "#52514e",
    "ytick.color": "#52514e",
    "axes.labelcolor": "#52514e",
    "axes.titlecolor": "#0b0b0b",
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "grid.color": "#e1e0d9",
    "grid.linewidth": 0.6,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 200,
})

# --------------------------------------------------------------------------
# Colour system: one deep blue for structure, one warm colour for gaps and
# warnings, neutral greys for everything else.
# --------------------------------------------------------------------------
ACCENT = "#1c4f82"        # deep blue: headings, rules, header bars
BLUE = "#2a78d6"          # data marks (validated categorical slot 1)
BLUE_RAMP = ["#86b6ef", "#5598e7", "#2a78d6", "#184f95"]   # ordinal ramp, light end >= 2:1
WARM = "#eb6834"          # gap / warning emphasis (validated slot 2)
WARM_TEXT = "#b9471a"     # warm as text on white (readable)
WARM_TINT = "#fbe9df"
ACCENT_TINT = "#e3ebf3"
INK = "#0b0b0b"
INK2 = "#333230"
INK_SEC = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
LINE = "#c9c8c2"
ZEBRA = "#f4f4f1"
DEEMPH = "#c3c2b7"        # de-emphasis grey for context marks

C_ACCENT = HexColor(ACCENT)
C_WARM = HexColor(WARM)
C_WARM_TEXT = HexColor(WARM_TEXT)
C_WARM_TINT = HexColor(WARM_TINT)
C_TINT = HexColor(ACCENT_TINT)
C_INK = HexColor(INK)
C_INK2 = HexColor(INK2)
C_SEC = HexColor(INK_SEC)
C_MUTED = HexColor(MUTED)
C_LINE = HexColor(LINE)
C_ZEBRA = HexColor(ZEBRA)
C_GRID = HexColor(GRID)

# --------------------------------------------------------------------------
# Page geometry
# --------------------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN = 17 * mm
FRAME_W = PAGE_W - 2 * MARGIN           # about 176 mm
FRAME_H = PAGE_H - 2 * MARGIN
FOOTER_TEXT = "Small law firm problems UK and US, research 11 Oct 2026"

# --------------------------------------------------------------------------
# Paragraph styles
# --------------------------------------------------------------------------
def _ps(name, **kw):
    base = dict(fontName="DejaVu", fontSize=9, leading=12, textColor=C_INK2,
                bulletFontName="DejaVu", bulletFontSize=8, splitLongWords=1)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    "cover_title": _ps("cover_title", fontName="DejaVu-Bold", fontSize=26, leading=31, textColor=white),
    "cover_sub": _ps("cover_sub", fontSize=11.5, leading=15.5, textColor=white),
    "cover_meta": _ps("cover_meta", fontSize=9.5, leading=13, textColor=C_INK2),
    "cover_label": _ps("cover_label", fontName="DejaVu-Bold", fontSize=8, leading=11, textColor=C_ACCENT),
    "cover_small": _ps("cover_small", fontSize=8, leading=10.5, textColor=C_SEC),
    "cover_warn": _ps("cover_warn", fontName="DejaVu-Bold", fontSize=10, leading=13, textColor=C_WARM_TEXT),
    "chapter_no": _ps("chapter_no", fontName="DejaVu-Bold", fontSize=8, leading=10, textColor=C_MUTED, spaceAfter=2),
    "h1": _ps("h1", fontName="DejaVu-Bold", fontSize=17, leading=21, textColor=C_ACCENT, spaceAfter=4, keepWithNext=1),
    "h2": _ps("h2", fontName="DejaVu-Bold", fontSize=11.5, leading=14.5, textColor=C_ACCENT, spaceBefore=9, spaceAfter=3, keepWithNext=1),
    "h3": _ps("h3", fontName="DejaVu-Bold", fontSize=9.5, leading=12, textColor=C_INK, spaceBefore=6, spaceAfter=2, keepWithNext=0),
    "lead": _ps("lead", fontSize=9.8, leading=13.5, textColor=C_INK, spaceAfter=5),
    "body": _ps("body", spaceAfter=3.5),
    "bullet": _ps("bullet", fontSize=8.8, leading=11.6, leftIndent=11, bulletIndent=2, spaceAfter=2.2),
    "bullet2": _ps("bullet2", fontSize=8.4, leading=11, leftIndent=21, bulletIndent=12, spaceAfter=1.6),
    "quote": _ps("quote", fontSize=8.8, leading=11.6, textColor=C_INK2, leftIndent=4),
    "quote_src": _ps("quote_src", fontSize=7.2, leading=9.5, textColor=C_MUTED, leftIndent=4, spaceBefore=1),
    "cell": _ps("cell", fontSize=7.3, leading=9.2, textColor=C_INK2),
    "cell_small": _ps("cell_small", fontSize=6.9, leading=8.7, textColor=C_INK2),
    "cell_head": _ps("cell_head", fontName="DejaVu-Bold", fontSize=7.3, leading=9.2, textColor=C_ACCENT),
    "cell_label": _ps("cell_label", fontName="DejaVu-Bold", fontSize=7.5, leading=9.5, textColor=C_ACCENT),
    "card_cell": _ps("card_cell", fontSize=7.9, leading=10.2, textColor=C_INK2),
    "card_title": _ps("card_title", fontName="DejaVu-Bold", fontSize=11, leading=13.5, textColor=white),
    "card_rank": _ps("card_rank", fontName="DejaVu-Bold", fontSize=15, leading=17, textColor=white, alignment=TA_CENTER),
    "badge": _ps("badge", fontSize=7.3, leading=9.3, textColor=C_INK2, alignment=TA_CENTER),
    "caption": _ps("caption", fontSize=7.2, leading=9.3, textColor=C_MUTED, spaceBefore=1.5, spaceAfter=6),
    "source_line": _ps("source_line", fontSize=7, leading=9, textColor=C_MUTED, spaceBefore=1, spaceAfter=7),
    "note": _ps("note", fontSize=8, leading=10.5, textColor=C_SEC, spaceAfter=4),
    "tile_num": _ps("tile_num", fontName="DejaVu-Bold", fontSize=19, leading=22, textColor=C_ACCENT),
    "tile_label": _ps("tile_label", fontName="DejaVu-Bold", fontSize=7.6, leading=9.6, textColor=C_INK),
    "tile_src": _ps("tile_src", fontSize=6.6, leading=8.4, textColor=C_MUTED),
    "toc1": _ps("toc1", fontName="DejaVu-Bold", fontSize=9.6, leading=14, textColor=C_INK),
    "toc2": _ps("toc2", fontSize=8.6, leading=12, textColor=C_INK2, leftIndent=12),
    "src_entry": _ps("src_entry", fontSize=6.9, leading=8.8, textColor=C_INK2),
    "src_num": _ps("src_num", fontName="DejaVu-Bold", fontSize=6.9, leading=8.8, textColor=C_ACCENT),
    "legend_tag": _ps("legend_tag", fontSize=8.2, leading=11, textColor=C_INK2),
    "concl": _ps("concl", fontSize=9.4, leading=13, textColor=C_INK2, spaceAfter=5),
}

# --------------------------------------------------------------------------
# Markdown parsing
# --------------------------------------------------------------------------
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
ALIAS_RE = re.compile(r"\[([^\]]+)\]\(@([A-Za-z0-9_]+)\)")
TAG_RE = re.compile(r"\[((?:snippet|snippets|vendor|user|users|secondary|3p|tribunal|reported claim|self-reported)[^\[\]]*)\]")
BOLD_RE = re.compile(r"\*\*(.+?)\*\*")


def read_report():
    text = REPORT.read_text(encoding="utf-8")
    lines = text.split("\n")
    blocks = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            header = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
                j += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            i = j
            continue
        m = re.match(r"^(#{1,3})\s+(.*)$", ln)
        if m:
            blocks.append({"type": "h%d" % len(m.group(1)), "text": m.group(2).strip()})
        elif ln.strip():
            blocks.append({"type": "p", "text": ln.strip()})
        i += 1
    return text, blocks


REPORT_TEXT, BLOCKS = read_report()

# sections keyed by number 1..11 and "conclusion"
SEC = {}
_cur = None
for b in BLOCKS:
    if b["type"] == "h2":
        m = re.match(r"^(\d+)\.\s+(.*)$", b["text"])
        key = int(m.group(1)) if m else b["text"].lower()
        _cur = {"title": m.group(2) if m else b["text"], "blocks": [], "tables": [], "paras": [], "h3": []}
        SEC[key] = _cur
    elif _cur is not None:
        _cur["blocks"].append(b)
        if b["type"] == "table":
            _cur["tables"].append(b)
        elif b["type"] == "p":
            _cur["paras"].append(b["text"])
        elif b["type"] == "h3":
            _cur["h3"].append(b["text"])


def T(sec, idx):
    """Table idx (0-based) of section sec, as (header, rows)."""
    t = SEC[sec]["tables"][idx]
    return t["header"], t["rows"]


# --------------------------------------------------------------------------
# URL registry: numbered in order of first appearance in the report
# --------------------------------------------------------------------------
URLS = []
URL_INDEX = {}
URL_LABEL = {}
for m in LINK_RE.finditer(REPORT_TEXT):
    label, url = m.group(1), m.group(2)
    if url not in URL_INDEX:
        URLS.append(url)
        URL_INDEX[url] = len(URLS)
        URL_LABEL[url] = label


def ref(url, label=None):
    if url not in URL_INDEX:
        URLS.append(url)
        URL_INDEX[url] = len(URLS)
        URL_LABEL[url] = label or url
    return URL_INDEX[url]


# aliases for URLs used in the hand-written condensed text (all are report URLs)
U = {}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inl(text, refs=True):
    """Markdown-ish inline text -> reportlab paragraph XML.
    Links become 'label [n]' (small grey number); evidence tags become small grey
    superscripts; **bold** becomes <b>."""
    if text is None:
        return ""
    text = text.replace("&amp;", "&")      # hand-written text may already carry an entity
    holders = []

    def _link(m):
        label, url = m.group(1), m.group(2)
        n = ref(url, label)
        holders.append((label, n))
        return "\x00%d\x00" % (len(holders) - 1)

    def _alias(m):
        label, key = m.group(1), m.group(2)
        url = U[key]
        n = ref(url, label)
        holders.append((label, n))
        return "\x00%d\x00" % (len(holders) - 1)

    s = ALIAS_RE.sub(_alias, text)
    s = LINK_RE.sub(_link, s)
    s = esc(s)
    # hand-written text may carry <b>, <i>, <br/> markup: restore those tags after escaping
    for tag in ("b", "i"):
        s = s.replace("&lt;%s&gt;" % tag, "<%s>" % tag).replace("&lt;/%s&gt;" % tag, "</%s>" % tag)
    s = s.replace("&lt;br/&gt;", "<br/>")
    s = TAG_RE.sub(lambda m: '<font size="5.6" color="%s"><super>%s</super></font>' % (MUTED, esc(m.group(1))), s)
    s = BOLD_RE.sub(r"<b>\1</b>", s)

    def _restore(m):
        label, n = holders[int(m.group(1))]
        label = esc(label)
        if refs:
            return '%s <font size="6.3" color="%s">[%d]</font>' % (label, INK_SEC, n)
        return label
    s = re.sub("\x00(\\d+)\x00", _restore, s)
    return s


def P(text, style="body", **kw):
    return Paragraph(inl(text), S[style], **kw)


def B(text, style="bullet"):
    return Paragraph(inl(text), S[style], bulletText="\u2022")


def bullets(items, style="bullet"):
    return [B(t, style) for t in items]


def H2(text, toc=True):
    p = Paragraph(inl(text, refs=False), S["h2"])
    if toc:
        p._toc = (1, re.sub(r"<[^>]+>", "", inl(text, refs=False)))
    return p


class Caption(Paragraph):
    """A table caption that refuses to sit at the foot of a page: if less than
    `min_space` remains below it, it moves to the next page (the table that
    follows can then start under it and split normally)."""
    min_space = 34 * mm

    def wrap(self, aW, aH):
        w, h = Paragraph.wrap(self, aW, aH)
        if aH < self.min_space:
            return (w, aH + 1)
        return (w, h)

    def split(self, aW, aH):
        if aH < self.min_space:
            return []
        return Paragraph.split(self, aW, aH)


def H3(text):
    return Caption(inl(text, refs=False), S["h3"])


def rule(thickness=0.6, color=None, before=2, after=4):
    return HRFlowable(width="100%", thickness=thickness, color=color or C_LINE,
                      spaceBefore=before, spaceAfter=after)


def caption(text):
    return Paragraph(inl(text), S["caption"])


def source_line(text):
    return Paragraph(inl(text), S["source_line"])


def quote_block(quote, src=None):
    """A short 'their words' callout with a warm left bar."""
    rows = [[Paragraph(inl(quote), S["quote"])]]
    if src:
        rows.append([Paragraph(inl(src), S["quote_src"])])
    t = Table(rows, colWidths=[FRAME_W - 8])
    t.setStyle(TableStyle([
        ("LINEBEFORE", (0, 0), (0, -1), 2.2, C_WARM),
        ("BACKGROUND", (0, 0), (-1, -1), C_ZEBRA),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    t.spaceBefore = 3
    t.spaceAfter = 6
    return t


def note_box(text, warm=False):
    """A framed note; warm=True marks a gap/warning emphasis."""
    t = Table([[Paragraph(inl(text), S["note"])]], colWidths=[FRAME_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_WARM_TINT if warm else C_TINT),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    t.spaceBefore = 3
    t.spaceAfter = 6
    return t


# --------------------------------------------------------------------------
# Tables
# --------------------------------------------------------------------------
def _plain_len(cell):
    s = LINK_RE.sub(lambda m: m.group(1) + " [00]", cell)
    s = ALIAS_RE.sub(lambda m: m.group(1) + " [00]", s)
    return len(s)


def auto_widths(header, rows, total=FRAME_W, min_w=11 * mm, max_share=0.62, weights=None):
    ncol = len(header)
    if weights is None:
        weights = []
        for c in range(ncol):
            lens = [_plain_len(r[c]) for r in rows if c < len(r)] + [_plain_len(header[c])]
            avg = sum(lens) / len(lens)
            mx = max(lens)
            weights.append(min(max(0.55 * avg + 0.45 * mx, 8), 120))
    tot = float(sum(weights))
    widths = [max(min_w, total * w / tot) for w in weights]
    # renormalise after clamping
    s = sum(widths)
    widths = [w * total / s for w in widths]
    return widths


def tbl(header, rows, widths=None, weights=None, font="cell", head_font="cell_head",
        zebra=True, align_right_cols=(), first_col_bold=False, total=FRAME_W):
    """Markdown-style table -> platypus Table with wrapping Paragraph cells."""
    rows = [r + [""] * (len(header) - len(r)) for r in rows]
    if widths is None:
        widths = auto_widths(header, rows, total=total, weights=weights)
    else:
        widths = [w * mm for w in widths]
        s = sum(widths)
        if s > total + 0.5:
            widths = [w * total / s for w in widths]
    data = [[Paragraph(inl(h), S[head_font]) for h in header]]
    for r in rows:
        cells = []
        for ci, c in enumerate(r):
            st = S["cell_label"] if (first_col_bold and ci == 0) else S[font]
            cells.append(Paragraph(inl(c), st))
        data.append(cells)
    t = Table(data, colWidths=widths, repeatRows=1, splitByRow=1)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), C_TINT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, C_ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, C_GRID),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, C_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
    ]
    if zebra:
        for ri in range(1, len(data)):
            if ri % 2 == 0:
                style.append(("BACKGROUND", (0, ri), (-1, ri), C_ZEBRA))
    for c in align_right_cols:
        style.append(("ALIGN", (c, 1), (c, -1), "RIGHT"))
    t.setStyle(TableStyle(style))
    t.spaceBefore = 3
    t.spaceAfter = 5
    return t


def split_cols(header, rows, groups):
    """Split a wide table into several narrower ones that each repeat column 0.
    groups: list of lists of column indexes (excluding 0)."""
    out = []
    for g in groups:
        idx = [0] + list(g)
        h = [header[i] for i in idx]
        rs = [[r[i] if i < len(r) else "" for i in idx] for r in rows]
        out.append((h, rs))
    return out


def fig_image(path, w_in, h_in):
    img = Image(str(path), width=w_in * inch, height=h_in * inch)
    img.hAlign = "LEFT"
    img.spaceBefore = 4
    img.spaceAfter = 2
    return img


class SectionMarker(Flowable):
    """Zero-height flowable that tells the running header which section is live."""
    def __init__(self, title):
        Flowable.__init__(self)
        self._sec = title
        self.width = 0
        self.height = 0

    def wrap(self, aw, ah):
        return (0, 0)

    def draw(self):
        pass


def chapter(num, title, lead=None):
    """Chapter opener: starts a new page; registers the TOC entry and header."""
    out = [NextPageTemplate("main"), PageBreak(), SectionMarker(title)]
    label = ("SECTION %s" % num) if num else ""
    if label:
        out.append(Paragraph(label, S["chapter_no"]))
    h = Paragraph(inl(title, refs=False), S["h1"])
    h._toc = (0, re.sub(r"<[^>]+>", "", inl(title, refs=False)))
    out.append(h)
    out.append(rule(1.2, C_ACCENT, before=1, after=6))
    if lead:
        out.append(Paragraph(inl(lead), S["lead"]))
    return out


# ==========================================================================
# Charts (matplotlib -> PNG at 200 dpi, embedded at their drawn size so no
# text is scaled below 7 pt). Palette: blue for data, warm for gap/warning
# emphasis, grey for context. Validated with the dataviz palette script.
# ==========================================================================
import textwrap

plt.rcParams["text.parse_math"] = False   # "$49" is a price, not mathtext

FULL_W = 6.9      # inches, equals the frame width
TITLE_WRAP = 92   # characters per line at 8.6 pt bold across 6.9 in
SRC_WRAP = 124    # characters per line at 7 pt


def _wrap(s, n=34):
    return "\n".join(textwrap.wrap(s, n))


def _frame(w, h, title, source, ncols=1, width_ratios=None):
    fig, axes = plt.subplots(1, ncols, figsize=(w, h),
                             gridspec_kw={"width_ratios": width_ratios} if width_ratios else None)
    t = _wrap(title, TITLE_WRAP)
    s = _wrap(source, SRC_WRAP)
    fig.text(0.005, 0.995, t, ha="left", va="top", fontsize=8.6, fontweight="bold", color=INK, linespacing=1.25)
    fig.text(0.005, 0.008, s, ha="left", va="bottom", fontsize=7, color=MUTED, linespacing=1.2)
    fig._title_lines = t.count("\n") + 1
    fig._src_lines = s.count("\n") + 1
    return fig, axes


def _save(fig, name, w, h):
    top = 1 - (0.10 + 0.165 * fig._title_lines) / h
    bottom = (0.07 + 0.125 * fig._src_lines) / h
    fig.tight_layout(rect=[0, bottom, 1, top])
    # panel titles: re-anchor at the left edge of the tick-label column so a
    # title never runs past its own panel
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        t = getattr(ax, "_ptitle", None)
        if not t:
            continue
        ax.set_title("")
        bb = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
        pos = ax.get_position()
        fig.text(bb.x0, pos.y1 + 0.012, t, ha="left", va="bottom", fontsize=7.8, fontweight="bold",
                 color=INK_SEC, linespacing=1.15)
    path = CHART_DIR / (name + ".png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return (path, w, h)


def _hbar(ax, labels, values, colors=None, fmt="{:.0f}%", xlim=None, wrap=34, height=0.58,
          text_color=INK2, xlabel=None):
    n = len(labels)
    y = list(range(n))[::-1]
    cols = colors if colors else [BLUE] * n
    ax.barh(y, values, color=cols, height=height, edgecolor="white", linewidth=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels([_wrap(l, wrap) for l in labels], fontsize=7.2, color=INK2)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_color(DEEMPH)
    ax.spines["bottom"].set_visible(False)
    ax.set_xticks([])
    mx = max(values) if xlim is None else xlim
    ax.set_xlim(0, mx * 1.18)
    for yi, v in zip(y, values):
        ax.text(v + mx * 0.015, yi, fmt.format(v), va="center", ha="left", fontsize=7.2, color=text_color)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=7.2, color=INK_SEC)
    ax.set_ylim(-0.65, n - 0.35)


def _panel_title(ax, text):
    ax.set_title(text, fontsize=7.8, color=INK_SEC, loc="left", fontweight="bold")   # reserves the space
    ax._ptitle = text


def chart_funnel():
    h = 2.3
    fig, ax = _frame(FULL_W, h,
                     "Of 8 hours worked, 3.0 are billed, 2.6 invoiced and 2.4 collected (US firms on Clio, 2025)",
                     "Source: Clio Legal Trends benchmarks 2025 [%d] (seen in search snippets); utilisation 38%%, realisation 88%%, collection 93%%. "
                     "In 2017 the figure was 2.3 billed hours (29%%) [%d]." % (
                         ref("https://clio.com/resources/legal-trends/benchmarks/"),
                         ref("https://www.lawnext.com/2019/03/exclusive-survey-report-small-firms-see-many-challenges-but-do-little-to-address-them.html")))
    labels = ["Hours worked in a day", "Billed (utilisation 38%)", "Invoiced (realisation 88%)", "Collected (collection 93%)"]
    _hbar(ax, labels, [8.0, 3.0, 2.6, 2.4], colors=BLUE_RAMP, fmt="{:.1f} h", xlim=8.0, wrap=30, height=0.62,
          xlabel="Hours per 8-hour working day")
    return _save(fig, "funnel", FULL_W, h)


def chart_admin():
    h = 3.05
    fig, ax = _frame(FULL_W, h,
                     "Admin is the number-one complaint in both countries: 52% to 74% of small firms name it",
                     "Sources: Thomson Reuters 2020 [%d]; Above the Law / 8am index Sep 2026 [%d] (secondary); Law Week Colorado 2024 [%d]; "
                     "LexisNexis Bellwether 2026 [%d]. Different surveys and question wording; bars are indicative, not strictly comparable." % (
                         ref("https://www.thomsonreuters.com/en/press-releases/2020/september/small-law-firms-still-struggling-to-manage-administrative-tasks-says-thomson-reuters-survey"),
                         ref("https://abovethelaw.com/2026/09/lawyer-retention-in-three-words-automate-the-crap/"),
                         ref("https://www.lawweekcolorado.com/article/2024-state-of-the-solo-survey-findings/"),
                         ref("https://www.lexisnexis.com/community/pressroom/b/news/posts/small-law-firms-confident-on-client-service-but-held-back-by-operational-drag")))
    labels = [
        "US firms of 29 or fewer lawyers: admin a significant or moderate challenge (TR 2020)",
        "US legal staff: at least slightly miserable from admin (8am index, about 400, Sep 2026)",
        "US firms of 29 or fewer lawyers: same question (TR 2019)",
        "Colorado solos: 'spend too much time on administrative tasks' (146 solos, Mar 2024)",
        "UK small and mid firms: admin the biggest workflow issue (Bellwether 2026, 568)",
        "UK small and mid firms: case management the biggest workflow issue (2026)",
        "UK small and mid firms: document drafting and review the biggest issue (2026)",
    ]
    vals = [74, 73, 72, 59.86, 52, 41, 28]
    cols = [BLUE, BLUE, BLUE, BLUE, BLUE, DEEMPH, DEEMPH]
    _hbar(ax, labels, vals, colors=cols, fmt="{:.0f}%", xlim=80, wrap=84, height=0.6, xlabel="Share of respondents")
    return _save(fig, "admin", FULL_W, h)


def chart_leo():
    h = 2.7
    fig, (a1, a2) = _frame(FULL_W, h,
                           "Communication (24%) and delay (22%) are 46% of Legal Ombudsman complaint types; conveyancing is 36% of accepted complaints (2025/26)",
                           "Source: Legal Ombudsman annual complaints data 2025/26 [%d]: 14,259 complaints received (+37%%), 8,412 accepted (+16%%); "
                           "poor service found in 72%% of assessed cases (79%% in wills and probate)." % (
                               ref("https://www.legalombudsman.org.uk/information-centre/data-centre/complaints-data/legal-ombudsman-202526-annual-complaints-data-and-insight/")),
                           ncols=2, width_ratios=[1.1, 1])
    _hbar(a1, ["Poor communication", "Delay / failure to progress", "Failure to advise", "Costs", "Failure to follow instructions"],
          [24, 22, 19, 9, 8], colors=[WARM, WARM, DEEMPH, DEEMPH, DEEMPH], xlim=30, wrap=28,
          xlabel="Share of complaint types, 2025/26")
    _panel_title(a1, "Complaint type")
    _hbar(a2, ["Residential conveyancing (3,039, +41%)", "Wills and probate (1,147)", "Personal injury (1,140)"],
          [36, 14, 14], xlim=40, wrap=24, xlabel="Share of accepted complaints, 2025/26")
    _panel_title(a2, "Practice area")
    return _save(fig, "leo", FULL_W, h)


def chart_uk_delays():
    h = 3.6
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "UK waits the firm cannot control: a purchase takes 123 days, paper probate 12 to 15 weeks, a multi-track trial 56 weeks",
                               "Sources: Legal Futures Feb 2026 [%d]; ICAEW Jun 2025 [%d]; MoJ family and civil statistics 2025-26 [%d] [%d]; OTS Solicitors [%d]; "
                               "Legal Ombudsman horizon scan 2023 [%d]. Consumer ideal for a purchase is 6.78 weeks. Employment tribunal hearings are listed into 2028." % (
                                   ref("https://www.legalfutures.co.uk/associate-news/property-transactions-spike-at-123-days-driving-industry-to-seek-greater-certainty/print/"),
                                   ref("https://www.icaew.com/regulation/regulatory-news/regulatory-news-2025-06/hmcts-updates-for-probate-practitioners-june-2025"),
                                   ref("https://www.gov.uk/government/statistics/family-court-statistics-quarterly-october-to-december-2025/family-court-statistics-quarterly-october-to-december-2025"),
                                   ref("https://www.gov.uk/government/statistics/civil-justice-statistics-quarterly-april-to-june-2026/civil-justice-statistics-quarterly-april-to-june-2026"),
                                   ref("https://www.otssolicitors.co.uk/news/landlord-possession-court-delays-2026/"),
                                   ref("https://www.legalombudsman.org.uk/media/ne1jmwfa/129-11-23-horizon-scan.pdf")),
                               ncols=3, width_ratios=[1.1, 1.0, 1.5])
    x = ["2007", "2019", "2025", "ideal"]
    v = [75, 104, 123, 47.5]
    a1.bar(x, v, color=[BLUE_RAMP[0], BLUE_RAMP[1], BLUE_RAMP[3], DEEMPH], width=0.62, edgecolor="white")
    for i, vv in enumerate(v):
        a1.text(i, vv + 2.5, ("%d" % vv) if i < 3 else "6.78 wk", ha="center", fontsize=7.2, color=INK2)
    a1.set_ylim(0, 145)
    a1.set_yticks([])
    a1.spines["left"].set_visible(False)
    a1.tick_params(axis="x", length=0, labelsize=7)
    _panel_title(a1, "Purchase, instruction to\ncompletion (days)")
    v2 = [4.9, 15, 21]
    a2.bar(["Digital", "Paper", "Stopped"], v2, color=[BLUE_RAMP[1], BLUE_RAMP[2], BLUE_RAMP[3]], width=0.62, edgecolor="white")
    for i, lab in enumerate(["4.9", "12.3-15", "about 21"]):
        a2.text(i, v2[i] + 0.5, lab, ha="center", fontsize=7.2, color=INK2)
    a2.set_ylim(0, 25)
    a2.set_yticks([])
    a2.spines["left"].set_visible(False)
    a2.tick_params(axis="x", length=0, labelsize=7)
    _panel_title(a2, "Probate grant,\nApr 2025 (weeks)")
    labels3 = ["Possession, claim to repossession (2026)", "OIC whiplash portal, 251 days (2023)",
               "Private law children cases (2025)", "Small claims, issue to trial (2026)",
               "Multi-track, issue to trial (2026)", "Divorce to final order, mean (2025)"]
    _hbar(a3, labels3, [26.4, 35.9, 37, 41.0, 55.9, 69], fmt="{:.1f} wk", xlim=75, wrap=26, height=0.6)
    _panel_title(a3, "Court and tribunal waits (weeks)")
    return _save(fig, "uk_delays", FULL_W, h)


def chart_lead_response():
    h = 2.3
    fig, ax = _frame(FULL_W, h,
                     "Lead response got worse between Clio's 2019 and 2024 mystery shops of US firms",
                     "Sources: 2Civility on Clio Legal Trends 2019 [%d] (1,000 emailed, 500 called) and 2024 [%d] (500 firms). "
                     "2024: 48%% effectively unreachable by phone; 12%% of shoppers would recommend the firm; 7%% of firms use a website chatbot." % (
                         ref("https://www.2civility.org/clio-legal-trends-report-finds-law-firms-arent-responsive-to-potential-clients/"),
                         ref("https://www.2civility.org/2024-clio-legal-trends-report-fixing-the-first-impression-problem-for-law-firms/")))
    labels = ["Firms that replied to the email", "Calls answered by a person", "Missed calls returned"]
    v19 = [40, 56, 38]
    v24 = [33, 40, 25]
    y = [2, 1, 0]
    for yi, a, b in zip(y, v19, v24):
        ax.plot([b, a], [yi, yi], color=DEEMPH, linewidth=2.2, zorder=1, solid_capstyle="round")
    ax.scatter(v19, y, s=70, color=BLUE_RAMP[0], zorder=3, edgecolor="white", linewidth=1.2, label="2019")
    ax.scatter(v24, y, s=70, color=BLUE_RAMP[3], zorder=3, edgecolor="white", linewidth=1.2, label="2024")
    for yi, a, b in zip(y, v19, v24):
        ax.text(a + 1.4, yi, "%d%%" % a, va="center", fontsize=7.2, color=INK2)
        ax.text(b - 1.4, yi, "%d%%" % b, va="center", ha="right", fontsize=7.2, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.4, color=INK2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(15, 65)
    ax.set_xlabel("Share of firms (%)", fontsize=7.2, color=INK_SEC)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=7)
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper right", frameon=False, ncol=2, fontsize=7.2)
    return _save(fig, "lead_response", FULL_W, h)


def chart_shadow_ai():
    h = 4.2
    fig, (a1, a2) = _frame(FULL_W, h,
                           "59% of UK fee earners use unapproved AI tools while 68% of their leaders see 'zero risk'; accuracy is the top stated concern",
                           "Sources: Access Legal survey via Legal Futures [%d] (vendor-run, 200 respondents, Apr 2026); SRA 2025 [%d]; Solicitors Journal 2022 [%d]; "
                           "LawNext Apr 2025 [%d] (TR 2025, ABA 2024, AffiniPay 2025); LawNext Mar 2025 [%d] (Smokeball, vendor)." % (
                               ref("https://www.legalfutures.co.uk/blog/containing-the-spread-of-unapproved-ai"),
                               ref("https://publications.sra.org.uk/sole-practitioners-and-small-firms-use-of-technology/research-findings"),
                               ref("https://www.solicitorsjournal.com/sjarticle/bellwether-report-2022-revenue-is-up-but-recruitment-and-retention-remains-a-challenge"),
                               ref("https://www.lawnext.com/2025/04/an-ai-assisted-look-at-four-new-surveys-on-ai-adoption-in-law-how-do-they-compare-differ.html"),
                               ref("https://www.lawnext.com/2025/03/ai-adoption-nearly-doubles-among-small-law-firms-according-to-smokeballs-2025-state-of-law-report.html")),
                           ncols=2, width_ratios=[1.2, 1])
    labels = [
        "UK fee earners using unapproved AI tools (small/mid firms, Apr 2026)",
        "UK firm leaders 'confident of full visibility and zero risk' (Apr 2026)",
        "UK firms with AI inside their case-management system (Apr 2026)",
        "UK small firms using free Google for research (Bellwether 2022)",
        "...of which admit it is 'riskier and slower than legal tech' (2022)",
        "UK small firms using generative AI (SRA 2025, under £400k turnover)",
        "Professionals with no AI policy at their firm (TR 2025)",
        "Professionals with no generative-AI training (TR 2025)",
        "US small firms and solos integrating gen AI (Smokeball 2025)",
    ]
    vals = [59, 68, 25, 74, 63, 12, 52, 64, 53]
    cols = [WARM, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE, BLUE]
    _hbar(a1, labels, vals, colors=cols, xlim=80, wrap=38, height=0.6, xlabel="Share of respondents")
    _panel_title(a1, "Use and policy")
    labels2 = ["Accuracy (ABA 2024)", "Reliability (ABA 2024)", "Data privacy and security (ABA 2024)",
               "Trustworthiness (AffiniPay 2025)", "Ethical issues (AffiniPay 2025)", "Privilege (AffiniPay 2025)"]
    _hbar(a2, labels2, [75, 56, 47, 42, 42, 36], xlim=80, wrap=26, height=0.6, xlabel="Share naming the concern")
    _panel_title(a2, "Top AI concerns")
    return _save(fig, "shadow_ai", FULL_W, h)


def chart_cyber():
    h = 2.6
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "Small firms are least prepared: 19% of US solos have an incident plan, 9% of UK sole practitioners hold cyber insurance, ransom demands rose 60%",
                               "Sources: ABA 2023 Cybersecurity TechReport [%d]; Law Society PII research via Legal Futures 2023 [%d]; Insurance Business / QBE Jun 2026 [%d]. "
                               "SRA review 2019: 30 of 40 firms visited had been targeted, over £4m of client money stolen from 23 firms [%d]." % (
                                   ref("https://www.americanbar.org/groups/law_practice/resources/tech-report/2023/2023-cybersecurity-techreport/"),
                                   ref("https://legalfutures.co.uk/latest-news/pii-premiums-rises-to-be-lower-than-last-year-says-law-society-research"),
                                   ref("https://www.insurancebusinessmag.com/au/news/cyber/ransomware-groups-are-coming-for-law-firms-580610.aspx"),
                                   ref("https://www.legalfutures.co.uk/latest-news/review-spells-out-toll-of-cyber-crime-on-law-firms/print/")),
                               ncols=3, width_ratios=[1, 1, 0.8])
    _hbar(a1, ["Solos", "2-9 lawyers", "500+ lawyers"], [19, 19, 78], colors=[WARM, WARM, DEEMPH], xlim=85, wrap=20,
          xlabel="Share of US firms, 2023")
    _panel_title(a1, "Have an incident response plan")
    _hbar(a2, ["Firms up to 25 partners", "Sole practitioners"], [28, 9], colors=[BLUE, WARM], xlim=35, wrap=20,
          xlabel="Share of UK firms, 2023")
    _panel_title(a2, "Hold cyber insurance")
    a3.bar(["2024", "2025"], [383, 611], color=[BLUE_RAMP[1], BLUE_RAMP[3]], width=0.55, edgecolor="white")
    a3.text(0, 383 + 15, "US$383k", ha="center", fontsize=7.2, color=INK2)
    a3.text(1, 611 + 15, "US$611k (+60%)", ha="center", fontsize=7.2, color=INK2)
    a3.set_ylim(0, 720)
    a3.set_yticks([])
    a3.spines["left"].set_visible(False)
    a3.tick_params(axis="x", length=0, labelsize=7)
    _panel_title(a3, "Average ransom\ndemand, legal\nsector (US$)")
    return _save(fig, "cyber", FULL_W, h)


def chart_job_ads():
    h = 4.4
    fig, (a1, a2) = _frame(FULL_W, h,
                           "UK ads are written around the stage of the matter ('completion', 'Land Registry'); US ads around litigation mechanics and the front desk",
                           "Sources: scrape of 40 live UK Reed ads, 10 Oct 2026 [%d] (25 conveyancing paralegal, 15 legal secretary; 'chasing' in 0 ads, no case-management brand named); "
                           "manual count over 22 US ads (14 Indeed samples, 8 Craigslist Manhattan) [%d] [%d]. Both counts are indicative, not statistical." % (
                               ref("https://www.reed.co.uk/jobs/conveyancing-paralegal-jobs"),
                               ref("https://www.indeed.com/hire/job-description/paralegal"),
                               ref("https://www.craigslist.org/search/area/losangeles?cat=lgl")),
                           ncols=2, width_ratios=[1, 1.08])
    uk = [("completion / completions", 26), ("fee earner(s)", 21), ("Land Registry", 21), ("searches", 20),
          ("liaising with clients / client contact", 19), ("estate agents / lenders / brokers", 19),
          ("correspondence / letters", 18), ("post (incoming, outgoing)", 16), ("case management system", 16),
          ("diary management", 15), ("deadlines / key dates", 14), ("SDLT / stamp duty", 13), ("drafting", 12),
          ("compliance", 10), ("billing / invoices", 10), ("audio typing / digital dictation", 7),
          ("AML / ID checks", 5), ("chasing / chase", 0)]
    _hbar(a1, [u[0] for u in uk], [u[1] for u in uk], fmt="{:.0f}", xlim=30, wrap=40, height=0.6,
          colors=[BLUE] * 17 + [WARM], xlabel="Ads containing the phrase (of 40)")
    _panel_title(a1, "UK: 40 Reed ads, 10 Oct 2026")
    us = [("drafting / typing pleadings, motions, letters", 13), ("calendaring / deadline tracking", 10),
          ("court filing or e-filing", 8), ("answering phones / reception", 7), ("bilingual or translation (Spanish 4)", 7),
          ("billing or time entry", 5), ("scanning / PDF / records handling", 3), ("intake / interviewing potential clients", 3),
          ("medical records / record requests", 2), ("transcription or dictation", 2),
          ("'small' / 'boutique' / 'sole practitioner'", 8), ("named software (one ad each)", 1)]
    _hbar(a2, [u[0] for u in us], [u[1] for u in us], fmt="{:.0f}", xlim=15, wrap=44, height=0.6,
          xlabel="Ads containing the duty (of 22)")
    _panel_title(a2, "US: 22 Indeed and Craigslist ads")
    return _save(fig, "job_ads", FULL_W, h)


def chart_hallucination():
    h = 2.45
    fig, ax = _frame(FULL_W, h,
                     "AI-fabricated content in US court filings: 11 instances in 2023, 524 in 2025 and 668 in the first seven months of 2026",
                     "Source: Charlotin tracker as reported by MSBA, 27 Jul 2026 [%d] (secondary). 2025: 97 monetary sanctions, 59 disciplinary referrals; "
                     "37 cases at $1,000-$5,000, four over $50,000. 2026 to July: 58 sanctions, 21 referrals; offenders 405 pro se / 256 lawyers." % (
                         ref("https://www.msba.org/site/content/News-and-Publications/News/General-News/Confronting_the_Hard%20Numbers_Behind_Lawyers_AI_and_Phantom_Precedents.aspx")))
    x = ["2023", "2024", "2025", "2026 (to Jul)"]
    v = [11, 37, 524, 668]
    ax.bar(x, v, color=[BLUE_RAMP[0], BLUE_RAMP[1], BLUE_RAMP[2], WARM], width=0.55, edgecolor="white")
    for i, vv in enumerate(v):
        ax.text(i, vv + 14, "%d" % vv, ha="center", fontsize=7.4, color=INK2)
    ax.text(2, 524 + 85, "97 monetary sanctions\n59 referrals", ha="center", fontsize=7, color=INK_SEC)
    ax.text(3, 668 + 85, "58 sanctions\n21 referrals", ha="center", fontsize=7, color=INK_SEC)
    ax.set_ylim(0, 900)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", length=0, labelsize=7.4)
    ax.set_ylabel("Instances per year", fontsize=7.2, color=INK_SEC)
    return _save(fig, "hallucination", FULL_W, h)


def _range_bars(ax, items, unit_fmt, xlim, wrap=34, point_color=BLUE_RAMP[3]):
    """items: (label, lo, hi[, prefix]) with lo == hi for a single point."""
    n = len(items)
    y = list(range(n))[::-1]
    for yi, it in zip(y, items):
        lab, lo, hi = it[0], it[1], it[2]
        pre = it[3] if len(it) > 3 else ""
        if lo == hi:
            ax.scatter([lo], [yi], s=46, color=point_color, zorder=3, edgecolor="white", linewidth=1)
            ax.text(lo + xlim * 0.018, yi, pre + unit_fmt(lo), va="center", fontsize=7.1, color=INK2)
        else:
            ax.barh(yi, hi - lo, left=lo, height=0.5, color=BLUE, edgecolor="white", linewidth=1)
            ax.text(hi + xlim * 0.015, yi, "%s%s-%s%s" % (pre, unit_fmt(lo), pre, unit_fmt(hi)), va="center",
                    fontsize=7.1, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([_wrap(i[0], wrap) for i in items], fontsize=7.1, color=INK2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, xlim)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color(DEEMPH)
    ax.set_ylim(-0.65, n - 0.35)


def chart_prices():
    h = 3.5
    fig, (a1, a2) = _frame(FULL_W, h,
                           "Clio publishes $49 to $119 per user per month and hides the top tier; Filevine is quote-only (estimates $80 to $200) and sells implementation through partners at $1,750 to $32,500",
                           "Sources: PricingSaaS Clio tracker Jun-Aug 2026 [%d] (3p); Lawyerist Clio Grow [%d]; Oktopeak Oct 2026 quoting Vineskills [%d]; Dupple [%d] (3p); "
                           "aimadefor [%d] (3p, unverified); Costbench [%d]; CASEpeer pricing [%d]; MyCase and PracticePanther via Lawyerist [%d] [%d]; SoftwareFinder user review Jun 2025 [%d]." % (
                               ref("https://pricingsaas.com/companies/clio"), ref("https://lawyerist.com/reviews/intake-crm/clio-grow/"),
                               ref("https://oktopeak.com/blog/filevine-pricing-real-cost-tco/"), ref("https://dupple.com/reviews/filevine"),
                               ref("https://www.aimadefor.com/blog/clio-pricing-2026/"),
                               ref("https://www.costbench.com/software/legal-practice-management/clio-grow/hidden-costs/"),
                               ref("https://www.casepeer.com/pricing/"),
                               ref("https://lawyerist.com/reviews/law-practice-management-software/mycase/"),
                               ref("https://lawyerist.com/reviews/law-practice-management-software/practicepanther/"),
                               ref("https://softwarefinder.com/legal/filevine-software/reviews")),
                           ncols=2, width_ratios=[1, 1])
    items = [("Clio Starter / EasyStart (published)", 49, 49), ("Clio Essentials (published)", 89, 89),
             ("Clio Advanced (published)", 119, 119), ("Clio Grow intake add-on", 59, 59),
             ("Filevine base licence (3p estimate)", 49, 87), ("Filevine small firm (3p estimate)", 80, 120),
             ("Filevine with modules (3p estimate)", 100, 200), ("MyCase Basic to Advanced", 50, 150),
             ("PracticePanther", 49, 89), ("CASEpeer (PI)", 90, 160)]
    _range_bars(a1, items, lambda v: "$%d" % v, 250, wrap=36)
    _panel_title(a1, "Per user per month, USD\n(Clio top tier quote-only; UK Clio £49 annual / £59 monthly)")
    items2 = [("Clio Grow set-up fee, one-time", 399, 399), ("Clio data migration, third party", 500, 5000),
              ("Filevine partner Sprint (1-20 users, 2 weeks)", 1750, 7500),
              ("Filevine module: reporting / Workato / LOIS", 2500, 2500),
              ("Filevine partner Launch (4-6 months)", 12500, 32500),
              ("Filevine user-reported spend 'never used'", 60000, 60000)]
    _range_bars(a2, items2, lambda v: "$%s" % format(v, ","), 80000, wrap=36)
    _panel_title(a2, "Implementation and set-up, USD\n ")
    return _save(fig, "prices", FULL_W, h)


GAP_POS = [  # rank, short name, problem-signal position, vendor-weakness position, coverage known?
    (1, "Confidential document work without a public AI tool", 4.0, 2.5, True),
    (2, "PI provider-list reconciliation at the intake handoff", 2.98, 3.14, True),
    (3, "CMS configuration validation and exception reports", 3.32, 2.95, True),
    (4, "UK court bundles to PD27A and tribunal rules", 3.3, 2.0, True),
    (5, "AML risk-assessment reasoning on file", 2.68, 3.0, True),
    (6, "Immigration evidence packets and RFE/RFI deadlines", 3.0, 2.5, True),
    (7, "Chasing clients and third parties", 4.0, 2.0, True),
    (8, "Land Registry requisitions and post-completion checks", 2.5, 2.0, True),
    (9, "Criminal defence discovery video review (coverage unknown)", 2.0, 2.6, False),
    (10, "Client-account and trust reconciliation errors", 3.02, 2.2, True),
    (11, "Legal aid billing (CCMS, LAA reconciliation)", 2.78, 1.86, True),
    (12, "Family financial disclosure assembly", 2.0, 2.0, True),
]
CROWDED_POS = [("Intake call answering\nand lead follow-up", 4.0, 0.5), ("Medical chronologies\nand demand letters", 3.0, 0.5),
               ("Dictation and\ntranscription", 1.5, 1.0)]


def chart_gap_matrix():
    w, h = FULL_W, 4.7
    fig, (ax, key) = _frame(w, h,
                            "Gap map: the twelve gaps placed by problem signal against vendor weakness, using the report's own ranking words",
                            "Positions follow the wording of the ranking table in section 9 (very high / high / medium-high / medium signal; weak / medium-weak / medium / strong coverage), "
                            "not measured scores. Warm = coverage weak or medium-weak; blue = medium; faded = coverage unknown; grey = the three crowded areas the report says are not gaps.",
                            ncols=2, width_ratios=[1.35, 1])
    ax.set_xlim(1.2, 4.5)
    ax.set_ylim(0.1, 3.5)
    ax.axhline(2.25, color=GRID, linewidth=0.8, zorder=0)
    ax.axvline(2.6, color=GRID, linewidth=0.8, zorder=0)
    ax.text(4.45, 3.44, "strong signal, weak vendor coverage", ha="right", va="top", fontsize=7, color=INK_SEC)
    ax.text(1.25, 0.16, "weaker signal, crowded", ha="left", va="bottom", fontsize=7, color=INK_SEC)
    for r, name, x, y, known in GAP_POS:
        ax.scatter([x], [y], s=210, color=WARM if y >= 2.4 else BLUE, zorder=3, edgecolor="white", linewidth=1.4,
                   alpha=1 if known else 0.55)
        ax.text(x, y, str(r), ha="center", va="center", fontsize=7.2, color="white", fontweight="bold", zorder=4)
    for name, x, y in CROWDED_POS:
        ax.scatter([x], [y], s=190, color=DEEMPH, zorder=3, edgecolor="white", linewidth=1.4)
        ax.text(x, y + 0.17, name, ha="center", va="bottom", fontsize=7, color=INK_SEC, zorder=4, linespacing=1.1)
    ax.set_xticks([1.5, 2.0, 2.5, 3.0, 4.0])
    ax.set_xticklabels(["low-\nmedium", "medium", "medium-\nhigh", "high", "very\nhigh"], fontsize=7)
    ax.set_yticks([0.5, 1.0, 2.0, 2.5, 3.0])
    ax.set_yticklabels(["very strong\n(crowded)", "strong", "medium", "medium-\nweak", "weak"], fontsize=7)
    ax.set_xlabel("Problem signal (regulator findings, insurer data, dated complaints, demand)", fontsize=7.2, color=INK_SEC)
    ax.set_ylabel("Vendor coverage of the exact sub-problem", fontsize=7.2, color=INK_SEC)
    ax.tick_params(length=0)
    key.axis("off")
    key.set_xlim(0, 1)
    key.set_ylim(0, 1)
    key.text(0, 1.0, "Key (rank. gap)", fontsize=7.6, fontweight="bold", color=INK, va="top")
    yy = 0.92
    for r, name, x, y, known in GAP_POS:
        key.scatter([0.035], [yy], s=100, color=WARM if y >= 2.4 else BLUE, edgecolor="white", linewidth=1,
                    alpha=1 if known else 0.55, clip_on=False)
        key.text(0.035, yy, str(r), ha="center", va="center", fontsize=6.9, color="white", fontweight="bold")
        key.text(0.1, yy, _wrap(name, 42), fontsize=7.1, color=INK2, va="center", linespacing=1.05)
        yy -= 0.073
    key.scatter([0.035], [yy], s=85, color=DEEMPH, edgecolor="white", linewidth=1, clip_on=False)
    key.text(0.1, yy, "crowded area (not a gap)", fontsize=7.1, color=INK_SEC, va="center")
    return _save(fig, "gap_matrix", w, h)


def chart_pay_employed():
    h = 3.9
    fig, ax = _frame(FULL_W, h,
                     "Employed pay: US legal-tech vendors post AI-engineer bases of $150,000 to $340,000; UK legal technologists earn a median of about £42,000",
                     "Sources: rlegaltech.com/jobs [%d]; Everlaw careers [%d]; Legal.io [%d]; Axial Search [%d] (43,500 postings); Court Cast Sep 2026 [%d]; ZipRecruiter [%d] [%d] (snippets); "
                     "Glassdoor [%d] (snippet, 14 submissions); ITJobsWatch [%d] (3 salaries). Remote in these ads means remote within the US or the UK." % (
                         ref("https://www.rlegaltech.com/jobs/"), ref("https://www.everlaw.com/careers/4648836006/"),
                         ref("https://www.legal.io/jobs/5787729/Full-time/Legal-Engineer/Remote"),
                         ref("https://axialsearch.com/insights/ai-engineering-jobs"),
                         ref("https://courtscast.com/law-firms-step-up-tech-hiring-as-ai-race-moves-deeper-into-legal-work/"),
                         ref("https://www.ziprecruiter.com/Salaries/Legal-Operations-Analyst-Salary"),
                         ref("https://www.ziprecruiter.com/Salaries/Legal-Technology-Consultant-Salary"),
                         ref("https://www.glassdoor.com/Salaries/london-legal-technologist-salary-SRCH_IL.0,6_IC2671300_KO7,25.htm"),
                         ref("https://www.itjobswatch.co.uk/jobs/london/legal%20technology%20specialist.do")))
    items = [("Harvey, Staff Software Engineer AI Platform (NY hybrid)", 231, 340, "$"),
             ("Everlaw, Staff AI Engineer base (Oakland hybrid)", 228, 288, "$"),
             ("Harvey, Legal Engineer OTE (JD + 3 years practising)", 220, 320, "$"),
             ("Midpage, Legal Engineer GTM (NYC on-site)", 200, 250, "$"),
             ("GC AI, Forward Deployed Engineer (remote US)", 165, 350, "$"),
             ("Blee / Centari / August, senior AI engineers (SF, NYC)", 150, 300, "$"),
             ("Generic US AI engineer, median of 43,500 postings", 176, 176, "$"),
             ("Law-firm senior AI data engineer (firms unnamed)", 220, 250, "$"),
             ("US Legal Technology Consultant, employed (10th-90th pct)", 39, 160, "$"),
             ("US Legal Operations Analyst (middle 50%)", 60, 87, "$"),
             ("UK Legal Technology Specialist, London advert median", 70, 70, "£"),
             ("UK Legal Technologist, London 25th-75th pct", 32.3, 56.0, "£")]
    _range_bars(ax, items, lambda v: ("%dk" % v) if v == int(v) else ("%.1fk" % v), 420, wrap=52)
    ax.set_xlabel("Annual pay, thousands (USD or GBP as marked)", fontsize=7.2, color=INK_SEC)
    return _save(fig, "pay_employed", FULL_W, h)


def chart_pay_freelance():
    h = 3.4
    fig, ax = _frame(FULL_W, h,
                     "Freelance and consulting rates: $15 to $61 an hour on marketplaces, $150 to $350 an hour at the law-firm consultancy tier",
                     "Sources: Upwork hire pages and job post [%d] [%d] [%d] (vendor marketing, snippets); PeoplePerHour [%d]; Clutch [%d]; Built In [%d]; ConsultingDemand [%d]; "
                     "aimadefor [%d] (3p); Pivot180 [%d] (self-reported); Lazige [%d]. Fiverr gigs start at $20-$80 and Clio set-up gigs at $10-$75 (project prices, not shown)." % (
                         ref("https://www.upwork.com/hire/ai-chatbot-specialists/"),
                         ref("https://www.upwork.com/freelance-jobs/apply/Automation-Developer-Legal-Operations-Ongoing-Engagement_~022052780018516086731/"),
                         ref("https://www.upwork.com/hire/legal-focus-freelancers/"),
                         ref("https://www.peopleperhour.com/freelance-jobs/artificial-intelligence/artificial-intelligence-chatbot-development"),
                         ref("https://clutch.co/it-services/legal-industry"),
                         ref("https://builtin.com/job/filevine-administrator/7571212"),
                         ref("https://consultingdemand.com/blog/consultant-hourly-rates/"),
                         ref("https://www.aimadefor.com/blog/clio-pricing-2026/"),
                         ref("https://pivot180.ai/resources/ai-consultant-for-law-firms-cost-process-how-to-choose-2026"),
                         ref("https://lazige.agency/guides/ai-consultant-pricing-guide-uk")))
    items2 = [("Upwork Clio automation and dashboard developer post (USD/h)", 15, 35),
              ("Upwork AI chatbot specialists, hire-page guidance (USD/h)", 30, 61),
              ("Freelance lawyers on Upwork (USD/h)", 30, 200),
              ("PeoplePerHour chatbot freelancers (EUR/h)", 8, 40),
              ("Clutch legal-industry IT providers (USD/h)", 25, 149),
              ("Filevine administrator, employment benchmark (USD/h)", 45, 45),
              ("GSA IT consulting, middle half (USD/h)", 123, 189),
              ("Clio third-party live training (USD/h)", 150, 300),
              ("Law-firm AI consultancy rate card, Pivot180 (USD/h)", 150, 350),
              ("UK AI consultants, agency guide (GBP/h)", 80, 200)]
    _range_bars(ax, items2, lambda v: "%d" % v, 420, wrap=60)
    ax.set_xlabel("Hourly rate (currency in the label)", fontsize=7.2, color=INK_SEC)
    return _save(fig, "pay_freelance", FULL_W, h)


def chart_tech_help():
    h = 2.9
    fig, (a1, a2) = _frame(FULL_W, h,
                           "Solos go to Google first (28%) and only 4% to internal IT; 55% of solo firms have no technology budget",
                           "Sources: ABA 2024 Technology and Training, Budgeting and Planning, and AI TechReports [%d] [%d] [%d] (search snippets; americanbar.org blocked); "
                           "LawNext 7 Mar 2025 [%d] (512 private-practice attorneys)." % (
                               ref("https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-technology-and-training/"),
                               ref("https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-budgeting-and-planning-techreport/"),
                               ref("https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-artificial-intelligence-techreport/"),
                               ref("https://www.lawnext.com/2025/03/aba-tech-survey-finds-growing-adoption-of-ai-in-legal-practice-with-efficiency-gains-as-primary-driver.html")),
                           ncols=2, width_ratios=[1.35, 1])
    labels = ["Solos: go first to internal technical support staff", "2-9 attorney firms: go first to internal support",
              "All respondents: go first to internal support", "Solos: go first to Google or a non-legal online resource",
              "Solos: no technology budget", "Solos: technology problems often or sometimes hurt productivity"]
    vals = [4, 25, 45, 28, 55.4, 50]
    _hbar(a1, labels, vals, colors=[WARM, BLUE, BLUE, WARM, WARM, BLUE], fmt="{:.0f}%", xlim=62, wrap=48,
          xlabel="Share of firms, ABA 2024")
    _panel_title(a1, "Where firms turn for technology help")
    _hbar(a2, ["Solos", "10-49 attorneys", "100+ attorneys", "All (11% in 2023)"], [18, 30, 46, 30],
          colors=[BLUE_RAMP[0], BLUE_RAMP[1], BLUE_RAMP[3], DEEMPH], fmt="{:.0f}%", xlim=52, wrap=20,
          xlabel="Share using AI tools, 2024")
    _panel_title(a2, "AI-tool use by firm size")
    return _save(fig, "tech_help", FULL_W, h)


def chart_vendor_jobs():
    h = 3.2
    fig, (a1, a2) = _frame(FULL_W, h,
                           "2,539 open legal-tech vendor postings across 133 vendors on 23 Sep 2026: Harvey alone 311, engineering 614",
                           "Source: rlegaltech.com/jobs [%d], 'Source checked 23 Sept 2026'; only 19%% of vendors publish pay. For scale, the general US AI-engineering market had 43,500 postings analysed Jan-Jul 2026 [%d]." % (
                               ref("https://www.rlegaltech.com/jobs/"), ref("https://axialsearch.com/insights/ai-engineering-jobs")),
                           ncols=2, width_ratios=[1, 1])
    vend = [("Harvey", 311), ("Clio", 123), ("Filevine", 105), ("ABC Legal Services", 95), ("Epiq", 78),
            ("Bloomberg Law", 67), ("Icertis", 47), ("Everlaw", 45), ("iManage", 41)]
    _hbar(a1, [v[0] for v in vend], [v[1] for v in vend], fmt="{:.0f}", xlim=340, wrap=22, xlabel="Open postings per vendor")
    _panel_title(a1, "By vendor (top nine of 133)")
    cat = [("Engineering", 614), ("Sales", 376), ("Legal", 371), ("Other", 371), ("Customer success", 264),
           ("Marketing and GTM", 182), ("Product", 128), ("Operations", 98), ("People", 79), ("Finance", 56)]
    _hbar(a2, [c[0] for c in cat], [c[1] for c in cat], fmt="{:.0f}", xlim=680, wrap=22,
          colors=[WARM] + [BLUE] * 9, xlabel="Open postings per category")
    _panel_title(a2, "By category")
    return _save(fig, "vendor_jobs", FULL_W, h)


def chart_malpractice():
    h = 2.1
    fig, ax = _frame(FULL_W, h,
                     "US malpractice claims by practice area, 2020-2023: estate and probate 13.6%, real estate 13.2%, plaintiff PI 12.7%; administrative errors near 25% of all claims and rising",
                     "Source: ABA claims profile 2020-2023 as relayed by ALPS, Jul 2026 [%d] (secondary). Missed deadlines are 'the single largest cause of malpractice claims against lawyers' in plaintiffs' PI work [%d]." % (
                         ref("https://www.alpsinsurance.com/blog/safeguarding-your-practice-what-current-malpractice-trends-are-telling-us-about-managing-risk"),
                         ref("https://lawyersmutualnc.com/blog/oops-i-did-it-again-missed-deadlines-continue-to-plague-plaintiffs-attorneys")))
    _hbar(ax, ["Estate and probate", "Real estate", "Plaintiff personal injury", "Family"], [13.58, 13.19, 12.73, 10.02],
          fmt="{:.2f}%", xlim=16, wrap=30, height=0.6, xlabel="Share of claims")
    return _save(fig, "malpractice", FULL_W, h)


def chart_pi_flow():
    w, h = FULL_W, 4.1
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    title = _wrap("The first 72 hours of a US PI case: the police report is step 5 in time, 'get it first' in importance, and the one step no vendor automates", TITLE_WRAP)
    src = _wrap("Sources: CASEpeer checklist, 2 Sep 2026 [%d] (vendor); Oregon PLF PI checklist [%d]; Tex. Transp. Code 550.065 [%d]; Fla. Stat. 316.066 [%d]; Cal. Veh. Code 20012 [%d]; "
                "Ohio Crash Retrieval [%d]; EvenUp Intake [%d] (vendor); Supio Mar 2026 [%d] (vendor). Time runs left to right on the top row, then down and right to left." % (
                    ref("https://www.casepeer.com/blog/personal-injury-case-management-guide-and-checklist/"),
                    ref("https://assets.osbplf.org/forms/practice_forms/issues-for-consideration-in-commencing-and-settling-a-personal-injury-case.docx"),
                    ref("https://texas.public.law/statutes/tex._transp._code_section_550.065"),
                    ref("https://florida.public.law/statutes/fla._stat._316.066"),
                    ref("https://california.public.law/codes/ca_veh_code_section_20012"),
                    ref("https://ohtrafficdata.dps.ohio.gov/CrashRetrieval"),
                    ref("https://www.evenuplaw.com/intake"),
                    ref("https://www.supio.com/blog/march-2026-release")), SRC_WRAP)
    fig.text(0.005, 0.99, title, ha="left", va="top", fontsize=8.6, fontweight="bold", color=INK, linespacing=1.25)
    fig.text(0.005, 0.01, src, ha="left", va="bottom", fontsize=7, color=MUTED, linespacing=1.2)
    steps = [
        ("1  Sign retainer; HIPAA and records authorisations", "Document step; e-signature vendors (Clio, Vinesign).", False),
        ("2  Calendar the statute of limitations 'immediately'", "CASEpeer 'Automated Statute Alerts' [vendor]; PLF: one person enters, a second verifies.", False),
        ("3  Letters of representation to all known insurers within 24-48 h", "Template step; logged per insurer.", False),
        ("4  Open the claims; get adjuster assignments", "EvenUp: 'AI Agents call carriers to open 5x more claims' [vendor].", False),
        ("5  Request the police or crash report", "HUMAN ACT. FL: sworn statement per report, felony for misuse. CA: attorney declaration under penalty of perjury. TX: written request, $6. OH: CAPTCHA portal, up to 6 weeks, statistical only. No vendor fetches it.", True),
        ("6  Spoliation letters; preserve evidence", "Template step.", False),
        ("7  Policy-limits request", "FL insurer must answer within 30 days with a sworn statement. EvenUp: 'confirm liability and coverage' [vendor].", False),
        ("8  Request records and bills from every provider; follow up", "Retrieval services (Finch, YoCierge); Supio and EvenUp read what is uploaded [vendor]. About 4 requests per matter.", False),
    ]
    bw, bh = 22.6, 35
    xs = [1.5, 26.3, 51.1, 75.9]
    rows_y = [49, 10]
    for i, (title_i, sub, warm) in enumerate(steps):
        r, c = divmod(i, 4)
        c = c if r == 0 else 3 - c
        x, y = xs[c], rows_y[r]
        face = WARM_TINT if warm else ACCENT_TINT
        edge = WARM if warm else ACCENT
        ax.add_patch(FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0,rounding_size=1.2",
                                    linewidth=1.4 if warm else 0.9, edgecolor=edge, facecolor=face, zorder=2))
        t = _wrap(title_i, 26)
        ax.text(x + 1.3, y + bh - 1.6, t, ha="left", va="top", fontsize=7.2, fontweight="bold",
                color=WARM_TEXT if warm else ACCENT, zorder=3, linespacing=1.12)
        nl = t.count("\n") + 1
        ax.text(x + 1.3, y + bh - 1.6 - 3.2 * nl - 1.2, _wrap(sub, 27), ha="left", va="top", fontsize=7,
                color=INK2, zorder=3, linespacing=1.1)
    for i in range(3):
        ax.add_patch(FancyArrowPatch((xs[i] + bw + 0.3, rows_y[0] + bh / 2), (xs[i + 1] - 0.3, rows_y[0] + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    ax.add_patch(FancyArrowPatch((xs[3] + bw / 2, rows_y[0] - 0.3), (xs[3] + bw / 2, rows_y[1] + bh + 0.3),
                                 arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    for i in range(3, 0, -1):
        ax.add_patch(FancyArrowPatch((xs[i] - 0.3, rows_y[1] + bh / 2), (xs[i - 1] + bw + 0.3, rows_y[1] + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    ax.text(1.5, 47, "Warm box = a legal, personal act (sworn statement, declaration, signed request) a script cannot perform.",
            fontsize=7, color=WARM_TEXT, va="center")
    path = CHART_DIR / "pi_flow.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return (path, w, h)


def build_charts():
    out = {}
    for fn in (chart_funnel, chart_admin, chart_leo, chart_uk_delays, chart_lead_response, chart_shadow_ai,
               chart_cyber, chart_job_ads, chart_hallucination, chart_prices, chart_gap_matrix, chart_pay_employed,
               chart_pay_freelance, chart_tech_help, chart_vendor_jobs, chart_malpractice, chart_pi_flow):
        path, w, h = fn()
        out[path.stem] = (path, w, h)
    return out


# ==========================================================================
# Content, part A: cover, contents, "Read this first", sections 1 to 4.
# Prose is condensed into short sentences and bullets; every number and
# dated quote from the report is kept; tables come straight from the report.
# ==========================================================================

# URL aliases used in the condensed text (all are URLs from the report)
U.update({
    "clio_bench": "https://clio.com/resources/legal-trends/benchmarks/",
    "lf_sme": "https://www.legalfutures.co.uk/latest-news/client-account-interest-drives-rising-profits-at-sme-law-firms",
    "lawnext2019": "https://www.lawnext.com/2019/03/exclusive-survey-report-small-firms-see-many-challenges-but-do-little-to-address-them.html",
    "clio_solo": "https://www.clio.com/wp-content/uploads/2022/10/2023-Legal-Trends-for-Solo-Law-Firms.pdf",
    "tr2020": "https://www.thomsonreuters.com/en/press-releases/2020/september/small-law-firms-still-struggling-to-manage-administrative-tasks-says-thomson-reuters-survey",
    "lii2022": "https://legaltechnology.com/small-us-law-firms-still-rate-time-spent-on-admin-as-number-one-challenge/",
    "lawnext2023": "https://www.lawnext.com/2023/11/small-law-firms-made-progress-this-year-on-their-biggest-challenge-thomson-reuters-survey-finds.html",
    "bellwether": "https://www.lexisnexis.com/community/pressroom/b/news/posts/small-law-firms-confident-on-client-service-but-held-back-by-operational-drag",
    "lf_chasing": "https://www.legalfutures.co.uk/latest-news/conveyancers-spend-nearly-half-their-time-chasing-people",
    "armstrong": "https://www.armstrongwatson.co.uk/news/2026/02/law-firm-benchmarking-review-20242025-provides-positive-findings",
    "lf_pii": "https://legalfutures.co.uk/latest-news/pii-premiums-rises-to-be-lower-than-last-year-says-law-society-research",
    "lf_2023trends": "https://www.legalfutures.co.uk/associate-news/highlights-from-the-2023-legal-trends-report",
    "civ2022": "https://www.2civility.org/clio-legal-trends-report-anticipates-stress-in-a-strong-legal-marketplace/",
    "tenpercent": "https://ten-percent.co.uk/?p=41317",
    "bls": "https://www.bls.gov/ooh/legal/paralegals-and-legal-assistants.htm",
    "lf_bighand": "https://www.legalfutures.co.uk/associate-news/bighands-latest-research-gives-insight-into-just-how-deep-the-staff-attrition-crisis-is-for-law-firms",
    "costbench": "https://www.costbench.com/software/legal-practice-management/",
    "civ2024": "https://www.2civility.org/2024-clio-legal-trends-report-fixing-the-first-impression-problem-for-law-firms/",
    "civ2019": "https://www.2civility.org/clio-legal-trends-report-finds-law-firms-arent-responsive-to-potential-clients/",
    "gazette_shopper": "https://www.lawgazette.co.uk/news/law-firms-are-their-own-competitors/64288.article",
    "lf_repeat": "https://www.legalfutures.co.uk/latest-news/more-than-third-of-clients-do-not-instruct-same-firm-for-new-work",
    "pie": "https://propertyindustryeye.com/the-factors-that-are-to-blame-for-conveyancing-delays/",
    "deka": "https://www.dekachambers.com/2023/10/06/court-bundles-if-we-dont-fear-them-we-should/",
    "jlea": "https://www.jonathanlea.net/moving-to-consultancy-from-being-a-sole-practitioner/",
    "ailawyer": "https://ailawyer.pro/research/small-firm-legal-operations-2026",
    "colorado": "https://www.lawweekcolorado.com/article/2024-state-of-the-solo-survey-findings/",
    "gavin": "https://toyagavin.substack.com/p/email",
    "adp": "https://adifferentpractice.substack.com/p/stop-doing-this-manually-5-tasks",
    "atl": "https://abovethelaw.com/2026/09/lawyer-retention-in-three-words-automate-the-crap/",
    "reed_conv": "https://www.reed.co.uk/jobs/conveyancing-paralegal-jobs",
    "reed_57348435": "https://www.reed.co.uk/jobs/conveyancing-paralegal/57348435",
    "indeed_para": "https://www.indeed.com/hire/job-description/paralegal",
    "cl_dweck": "https://www.craigslist.org/view/d/new-york-legal-secretary-and-biller/uE4UxdG4uWgNsND4YvCyYS",
    "cl_la": "https://www.craigslist.org/search/area/losangeles?cat=lgl",
    "suggest_conf": "https://suggestqueries.google.com/complete/search?client=firefox&gl=gb&q=is+chatgpt+confidential",
    "upwork_legal": "https://www.upwork.com/freelance-jobs/legal-assistance/",
    "upwork_immig": "https://www.upwork.com/freelance-jobs/apply/Intake-Specialist-for-Immigration-Law-Firm_~021907571624068917640/",
    "pph_legal": "https://www.peopleperhour.com/freelance-jobs/business/legal-services",
    "fiverr_clio": "https://www.fiverr.com/gigs/clio-automation",
    "fiverr_para": "https://www.fiverr.com/gigs/paralegal",
    "judiciary_min": "https://www.judiciary.uk/wp-content/uploads/2025/04/ACO-CUG-Meeting-10.02.2025-Minutes.pdf",
    "lf_bundletool": "https://www.legalfutures.co.uk/latest-news/solicitor-develops-free-software-to-organise-court-bundles",
    "leo2526": "https://www.legalombudsman.org.uk/information-centre/data-centre/complaints-data/legal-ombudsman-202526-annual-complaints-data-and-insight/",
    "sands": "https://www.sandsanderson.com/insights/thought/statistics-on-virginias-discipline-of-lawyers-fiscal-years-2020-2022",
    "md_agc": "https://mdcourts.gov/sites/default/files/import/attygrievance/docs/annualreport.pdf",
    "lm_missed": "https://lawyersmutualnc.com/blog/oops-i-did-it-again-missed-deadlines-continue-to-plague-plaintiffs-attorneys",
    "alps": "https://www.alpsinsurance.com/blog/safeguarding-your-practice-what-current-malpractice-trends-are-telling-us-about-managing-risk",
    "answering": "https://answeringlegal.com/blog/four-takeaways-from-2024-legal-trends-report",
    "civ_2024flat": "https://www.2civility.org/clio-2024-legal-trends-report-identifies-ai-alternative-billing-structures-and-client-engagement-as-focus-areas-for-todays-lawyers/",
    "minutedock": "https://minutedock.com/academy/flat-fee-vs-hourly-billing-guide-for-law-practices",
    "allington": "https://www.allingtonhughes.co.uk/",
    "taylorb": "https://www.taylorbracewell.co.uk/",
    "mckenzie": "https://mckenzie-bell.co.uk/",
    "kjones": "https://www.kennethjones.co.uk/",
    "greenway": "https://www.greenwaybankruptcy.com/",
    "salle": "https://www.sallelaw.com/",
    "hartley": "https://lawyers.uslegal.com/attorney/hartley-law-office-llc-77313550/",
    "lf_chatgpt": "https://www.legalfutures.co.uk/latest-news/solicitor-faces-probe-after-putting-client-documents-into-chatgpt",
    "lf_existential": "https://www.legalfutures.co.uk/latest-news/ai-poses-existential-threat-to-immigration-cases-tribunal-warns",
    "slaughter": "https://thelens.slaughterandmay.com/post/102n1a1/privilege-and-ai-hallucinations",
    "legalcheek_sra": "https://www.legalcheek.com/2026/08/sra-warns-over-ai-misuse-following-rise-in-blunders/",
    "letsdata": "https://letsdatascience.com/news/sra-warns-solicitors-over-ai-hallucinations-and-client-confi-2f083fd3",
    "barcouncil": "https://www.barcouncilethics.co.uk/wp-content/uploads/2024/01/Considerations-when-using-ChatGPT-and-generative-artificial-intelligence-Nov-2025.pdf",
    "legalcheek_bsb": "https://www.legalcheek.com/2026/05/hands-off-chatgpt-bsb-puts-barristers-on-notice-over-free-ai-tools/amp/",
    "michelmores": "https://www.lawcareers.net/Explore/CommercialQuestion/Michelmores-LLP-Generative-AI-use-and-client-confidentiality",
    "ayinde": "https://caselaw.nationalarchives.gov.uk/ewhc/admin/2025/1383",
    "zuva": "https://zuva.ai/blog/aba-formal-opinion-512/",
    "kba": "https://kybar.org/Portals/0/Admin/Ethics%20Opinions/KBA%20E-457.pdf",
    "epiq": "https://www.epiqglobal.com/en-US/Resource-Center/Articles/State-Bars-are-Issuing-Generative-AI-Guidance",
    "wlf": "https://www.wlf.org/2026/04/27/publishing/united-states-v-heppner-use-of-generative-ai-can-waive-privileges/",
    "aceds": "https://aceds.org/do-you-waive-privilege-by-using-ai-two-federal-courts-say-it-depends-aceds-blog/",
    "msba": "https://www.msba.org/site/content/News-and-Publications/News/General-News/Confronting_the_Hard%20Numbers_Behind_Lawyers_AI_and_Phantom_Precedents.aspx",
    "cronkite": "https://cronkitenews.azpbs.org/2025/10/28/lawyers-ai-hallucinations-chatgpt/",
    "lawnext_surveys": "https://www.lawnext.com/2025/04/an-ai-assisted-look-at-four-new-surveys-on-ai-adoption-in-law-how-do-they-compare-differ.html",
    "sra_tech": "https://publications.sra.org.uk/sole-practitioners-and-small-firms-use-of-technology/research-findings",
    "sra_ai2023": "https://www.sra.org.uk/sra/research-publications/artificial-intelligence-legal-market/",
    "lf_shadow": "https://www.legalfutures.co.uk/blog/containing-the-spread-of-unapproved-ai",
    "sj2022": "https://www.solicitorsjournal.com/sjarticle/bellwether-report-2022-revenue-is-up-but-recruitment-and-retention-remains-a-challenge",
    "bloomberg_policy": "https://news.bloomberglaw.com/business-and-practice/sure-youve-got-an-ai-policy-but-is-everyone-following-it",
    "intapp": "https://www.intapp.com/case-study/nelson-mullins-copilot-ai-permissions/",
    "aba_copilot": "https://www.americanbar.org/groups/law_practice/resources/law-technology-today/2026/what-should-law-firms-do-before-deploying-copilot/",
    "ncsc": "https://www.ncsc.gov.uk/files/Cyber-Threat-Report_UK-Legal-Sector.pdf",
    "lf_cyber2019": "https://www.legalfutures.co.uk/latest-news/review-spells-out-toll-of-cyber-crime-on-law-firms/print/",
    "ico_levales": "https://ico.org.uk/action-weve-taken/enforcement/2024/10/levales-solicitors-llp/",
    "teiss": "https://www.teiss.co.uk/privacy/ico-fines-law-firm-dpp-60000-over-a-major-client-data-breach-15669",
    "cts": "https://www.mortgagesolutions.co.uk/news/2023/12/05/thousands-of-sales-in-limbo-after-conveyancing-cyberattack-%e2%80%92-reports/",
    "qbe": "https://www.insurancebusinessmag.com/au/news/cyber/ransomware-groups-are-coming-for-law-firms-580610.aspx",
    "aba_cyber2023": "https://www.americanbar.org/groups/law_practice/resources/tech-report/2023/2023-cybersecurity-techreport/",
    "ls_friday": "https://www.lawsociety.org.uk/topics/regulation/solicitor-fined-for-failing-to-spot-friday-afternoon-cyber-fraud",
    "lf_whatsapp": "https://www.legalfutures.co.uk/latest-news/law-firms-need-whatsapp-policies-when-advising-asylum-clients",
    "lf_macinnes": "https://www.legalfutures.co.uk/latest-news/whatsapp-messages-form-part-of-firms-file-if-they-charge-for-them",
    "conventus": "https://conventuslaw.com/report/how-to-write-outside-counsel-guidelines-that-govern-ai-assisted-work/",
    "bloomberg_orders": "https://news.bloomberglaw.com/esg/ai-standing-orders-proliferate-as-federal-courts-forge-own-paths",
    "icaew_jun": "https://www.icaew.com/regulation/regulatory-news/regulatory-news-2025-06/hmcts-updates-for-probate-practitioners-june-2025",
})

BLOCKED_HOSTS = ("clio.com and its help centre; americanbar.org; lawsociety.org.uk; lawgazette.co.uk; sra.org.uk notice pages; "
                 "G2, Capterra and (for some products) TrustRadius; Upwork and Fiverr gig pages; Reddit on every mirror; "
                 "most US state crash-report portals and every UK police-force collision-report page.")


def cover_page():
    out = [NextPageTemplate("cover"), Spacer(1, 28 * mm)]
    band = Table([[Paragraph("Small law firms chase, wait and fear AI", S["cover_title"])],
                  [Paragraph("Problems, workflows, numbers, vocabulary and service gaps in small UK and US law firms "
                             "(1 to 30 lawyers, including sole practitioners)", S["cover_sub"])]],
                 colWidths=[FRAME_W])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 18),
        ("BOTTOMPADDING", (0, 0), (0, 0), 6),
        ("TOPPADDING", (0, 1), (0, 1), 2),
        ("BOTTOMPADDING", (0, 1), (0, 1), 18),
    ]))
    out.append(band)
    out.append(Spacer(1, 7 * mm))
    out.append(Paragraph("Research report, 11 October 2026", S["cover_meta"]))
    out.append(Spacer(1, 2 * mm))
    warn = Table([[Paragraph("Problems and gaps only. This document adds no solutions and no recommendations.", S["cover_warn"])]],
                 colWidths=[FRAME_W])
    warn.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C_WARM_TINT),
                              ("LINEBEFORE", (0, 0), (0, -1), 3, C_WARM),
                              ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    out.append(warn)
    out.append(Spacer(1, 8 * mm))
    scope_rows = [
        ["Scope", "UK (England and Wales) and US small law firms of 1 to 30 lawyers, including sole practitioners; "
                  "conveyancing, probate, family, immigration, personal injury, employment, criminal, bankruptcy, debt and possession work."],
        ["Inputs", "Ten note files compiled by the research team: time and money benchmarks, practitioners' vocabulary, practice-area workflows, "
                   "AI and confidentiality rulings, police and crash reports, Clio configuration, the PI case-opening handoff, Filevine versus Clio, "
                   "the twelve-gap ranking, and the employed-versus-freelance market."],
        ["Sources blocked", BLOCKED_HOSTS + " Facts from those hosts rest on search snippets, secondary reports or vendor claims and are tagged."],
        ["Currency and dates", "All currency as published: GBP for UK figures, USD for US figures. Dates are given so freshness can be judged."],
    ]
    st = Table([[Paragraph(a, S["cover_label"]), Paragraph(b, S["cover_small"])] for a, b in scope_rows],
               colWidths=[30 * mm, FRAME_W - 30 * mm])
    st.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.3, C_GRID),
                            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out.append(st)
    out.append(Spacer(1, 8 * mm))
    out.append(Paragraph("How to read the evidence tags", S["cover_label"]))
    tags = [
        ("[snippet]", "the fact was seen only in a search-engine summary because the page blocked the researcher"),
        ("[vendor]", "the vendor's own claim; no independent review confirmed it"),
        ("[user, date]", "a dated user review"),
        ("[secondary]", "the figure was relayed by a news site or blog rather than read from the primary report"),
        ("[3p]", "a third-party estimate or tracker, not the vendor's own figure"),
        ("[n]", "a numbered source; the URL is in the Sources appendix at the end"),
    ]
    tt = Table([[Paragraph("<b>%s</b>" % esc(a), S["legend_tag"]), Paragraph(esc(b), S["legend_tag"])] for a, b in tags],
               colWidths=[26 * mm, FRAME_W - 26 * mm])
    tt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out.append(tt)
    out.append(Spacer(1, 10 * mm))
    out.append(Paragraph("Prepared for Mustafa Shoukat. Built from the research report <i>Small law firm problems UK US</i> "
                         "(about 32,000 words, 12 sections, 41 tables, 12 gap cards). 381 numbered sources.", S["cover_small"]))
    return out


def contents_page():
    out = [NextPageTemplate("main"), PageBreak(), SectionMarker("Contents")]
    out.append(Paragraph("Contents", S["h1"]))
    out.append(rule(1.2, C_ACCENT, before=1, after=8))
    toc = TableOfContents()
    toc.levelStyles = [S["toc1"], S["toc2"]]
    toc.dotsMinLevel = 0
    out.append(toc)
    return out


def stat_tile(num, label, src):
    return [Paragraph(esc(num), S["tile_num"]), Paragraph(inl(label), S["tile_label"]), Paragraph(inl(src), S["tile_src"])]


def summary_page():
    out = [NextPageTemplate("main"), PageBreak(), SectionMarker("Read this first")]
    h = Paragraph("Read this first", S["h1"])
    h._toc = (0, "Read this first")
    out.append(h)
    out.append(rule(1.2, C_ACCENT, before=1, after=5))
    out.append(Paragraph("The eight numbers that carry the report, then the twelve service gaps in rank order. "
                         "Each gap has a full card in section 9.", S["lead"]))
    tiles = [
        stat_tile("3.0 of 8 h", "billable hours per 8-hour day; only 2.4 h collected",
                  "US firms on the Clio platform, 2025; utilisation 38% [Clio benchmarks](@clio_bench) [snippet]"),
        stat_tile("52% / 74%", "name admin the number-one workflow problem (UK 2026 / US 2020)",
                  "LexisNexis Bellwether 2026, 568 respondents [LexisNexis](@bellwether); Thomson Reuters 2020 [TR](@tr2020)"),
        stat_tile("97 days", "lock-up: 38 days unbilled plus 45 days unpaid (US median firm, 2023)",
                  "Clio Legal Trends 2023 via [Legal Futures](@lf_2023trends)"),
        stat_tile("46%", "of Legal Ombudsman complaint types are communication (24%) plus delay (22%)",
                  "14,259 complaints, 2025/26 (+37%) [Legal Ombudsman](@leo2526)"),
        stat_tile("123 days", "UK purchase conveyance, instruction to completion (75 in 2007; ideal 6.78 weeks)",
                  "2025 figure, +64% since 2007 [Legal Futures](https://www.legalfutures.co.uk/associate-news/property-transactions-spike-at-123-days-driving-industry-to-seek-greater-certainty/print/)"),
        stat_tile("59%", "of UK fee earners admit using unapproved AI tools; 68% of leaders see 'zero risk'",
                  "Censuswide for Access Legal, 200 respondents, Apr 2026 [Legal Futures](@lf_shadow) [vendor survey]"),
        stat_tile("524 → 668", "AI-fabricated filings in US courts, 2025 → 2026 to July; 97 monetary sanctions in 2025",
                  "Charlotin tracker via [MSBA](@msba) [secondary]"),
        stat_tile("$49–$119", "Clio per user per month (published); Filevine quote-only, est. $80–$120 small firm",
                  "[PricingSaaS](https://pricingsaas.com/companies/clio) [3p]; [Oktopeak](https://oktopeak.com/blog/filevine-pricing-real-cost-tco/)"),
    ]
    rows = [tiles[0:4], tiles[4:8]]
    tw = (FRAME_W - 3 * 3 * mm) / 4
    t = Table(rows, colWidths=[tw] * 4, hAlign="LEFT", spaceBefore=2, spaceAfter=6)
    sty = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("BACKGROUND", (0, 0), (-1, -1), C_ZEBRA),
           ("LINEABOVE", (0, 0), (-1, 0), 2.2, C_ACCENT), ("LINEABOVE", (0, 1), (-1, 1), 2.2, C_ACCENT),
           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
    # white gutters between tiles
    t2rows = []
    for r in rows:
        rr = []
        for i, cell in enumerate(r):
            rr.append(cell)
            if i < 3:
                rr.append("")
        t2rows.append(rr)
    widths = []
    for i in range(4):
        widths.append(tw)
        if i < 3:
            widths.append(3 * mm)
    t = Table(t2rows, colWidths=widths, hAlign="LEFT", spaceBefore=2, spaceAfter=6)
    sty = [("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
    for c in (0, 2, 4, 6):
        sty += [("BACKGROUND", (c, 0), (c, -1), C_ZEBRA), ("LINEABOVE", (c, 0), (c, 0), 2.2, C_ACCENT),
                ("LINEABOVE", (c, 1), (c, 1), 2.2, C_ACCENT)]
    t.setStyle(TableStyle(sty))
    out.append(t)
    out.append(Spacer(1, 2 * mm))
    out.append(Paragraph("The twelve gaps, ranked by problem signal and vendor weakness", S["h2"]))
    header, rows_ = T(9, 0)
    compact = []
    for r in rows_[:12]:
        rank, gap, signal, cov, fit, country, auto = r
        compact.append([rank, gap, signal.split(":")[0], cov.split(":")[0], auto.split(":")[0].split(";")[0], country])
    out.append(tbl(["#", "Gap", "Problem signal", "Vendor coverage", "Automatable", "Country"], compact,
                   widths=[7, 70, 24, 30, 28, 17], font="cell"))
    out.append(Paragraph("Crowded areas that are <b>not</b> gaps: intake call answering and lead follow-up; medical chronologies and demand letters; "
                         "dictation and transcription (section 9).", S["note"]))
    return out


# --------------------------------------------------------------------------
# Section 1
# --------------------------------------------------------------------------
def section_1(CH):
    out = chapter(1, SEC[1]["title"],
                  "The time problem is chronic, not new, and it is worse the smaller the firm: nearly two-thirds of a US lawyer's day "
                  "is not billed, a UK SME fee earner records 773 chargeable hours against a 1,100-hour target, and 'administrative tasks' "
                  "is the number-one complaint in both countries.")
    out.append(fig_image(*CH["funnel"]))
    out.append(H2("Hours: what is billed, invoiced and collected"))
    out += bullets([
        "US utilisation rose from <b>29% (2.3 hours a day) in 2017</b> to <b>38% (3.0 hours) in 2025</b>; realisation of 88% and collection of 93% "
        "shrink the 3.0 hours to <b>2.4 hours of cash per day</b> ([LawNext, 25 Mar 2019](@lawnext2019); [Clio benchmarks](@clio_bench) [snippet]).",
        "Solos are a full step behind: <b>25% utilisation (about 2 hours a day) against 36% for non-solos</b>, which is 211 fewer billed hours a year "
        "over 240 working days; 54% of solos work Saturdays ([Clio, Legal Trends for Solo Law Firms, 2023](@clio_solo)).",
        "Thomson Reuters, firms with 29 or fewer lawyers: time spent practising law <b>60% (2020), 56% (2022), 61% (2023)</b>; admin a significant "
        "or moderate challenge for <b>72% to 74%</b>; only about <b>20%</b> had any plan to act on it ([TR, Sep 2020](@tr2020); "
        "[Legal IT Insider, Nov 2022](@lii2022); [LawNext, Nov 2023](@lawnext2023)).",
        "UK, LexisNexis Bellwether 2026 (568 legal professionals): <b>52% named administrative tasks the biggest workflow issue, 41% case management, "
        "28% document drafting and review</b>; service 'still depends on stretched teams, manual processes and inefficient workflows behind the scenes' "
        "([LexisNexis pressroom, 18 May 2026](@bellwether)).",
        "Sharpest single UK number: <b>43% of a conveyancer's time is spent 'chasing stakeholders or being chased'</b>, up from 39% a year earlier "
        "([Legal Futures, 29 Oct 2024](@lf_chasing)).",
    ])
    out.append(fig_image(*CH["admin"]))
    out.append(H3("Table 1.1  Time measures, population and date"))
    h, r = T(1, 0)
    out.append(tbl(h, r, widths=[36, 52, 34, 54]))
    out.append(H2("Money: why the lost time hurts"))
    out += bullets([
        "Median UK SME firm: £146,000 of fee income per fee earner, <b>27% net profit (down from 31.4%)</b>, staff costs 39.4% of fees, PII 5.1% "
        "([Armstrong Watson, Feb 2026](@armstrong)); underlying profit grew just <b>1.2%</b> once client-account interest was stripped out "
        "([Legal Futures, Mar 2025](@lf_sme)).",
        "PII: a sole practice pays a median <b>£7,383 (6% of turnover)</b>, a conveyancing firm <b>£50,000 (8%)</b>; only <b>28% of firms with up to 25 partners, "
        "and 9% of sole practitioners, hold cyber insurance</b> ([Legal Futures, 21 Jul 2023](@lf_pii)).",
        "US: the median firm carried <b>97 days of lock-up</b> in 2023 (38 days unbilled plus 45 days unpaid); <b>41% of lawyers said clients pay late and "
        "24% said many never pay</b>; almost one in three admitted the firm takes too long to send bills ([Legal Futures, 20 Dec 2023](@lf_2023trends)); "
        "in 2022 the average firm collected only <b>$748 of every $1,000 of billable work</b> ([2Civility, 14 Oct 2022](@civ2022)).",
        "Staff are cheap to pay and expensive to lose: UK legal secretary £23,000 to £28,000, paralegal £22,000 to £27,000 ([Ten Percent Legal, Nov 2025](@tenpercent), "
        "a recruiter's list); US paralegal median <b>$62,890</b> with about <b>40,800 openings a year</b>, almost all from turnover ([BLS](@bls)); "
        "replacing one support-staff member costs <b>$10,000 to $40,000, sometimes $80,000</b> ([Legal Futures, 2 Aug 2023](@lf_bighand)).",
        "Practice-management software costs about <b>$81 per user per month</b> on average (Clio $49 to $159, MyCase $39 to $49) ([CostBench](@costbench) [snippet]): "
        "a three-user subscription is under $3,000 a year against a $30,000-plus paralegal replacement.",
    ])
    out.append(H2("The intake leak"))
    out += bullets([
        "Clio's 2024 mystery shop of 500 US firms: <b>only 33% replied to an email and 40% answered the phone</b>, <b>48% were effectively unreachable by phone</b>, "
        "just <b>12% of shoppers would recommend the firm</b>; all worse than 2019 (40%, 56%) ([2Civility, 1 Nov 2024](@civ2024); [2Civility, 23 Oct 2019](@civ2019)).",
        "UK secret-shopper exercise of 100 calls: <b>45%</b> of callers would not engage the firm because of poor service ([Law Gazette](@gazette_shopper) [snippet]).",
        "UK clients want same-day responses (<b>84%</b>) and weekly updates (<b>82%</b>); more than a third of repeat users did not return to the same firm "
        "([Legal Futures, 22 Jan 2025](@lf_repeat)).",
    ])
    out.append(fig_image(*CH["lead_response"]))
    out.append(H3("Table 1.2  Lead-response measures, Clio secret shopper"))
    h, r = T(1, 1)
    out.append(tbl(h, r, widths=[70, 53, 53]))
    out.append(source_line("Sources: [2Civility 2019](@civ2019); [2Civility 2024](@civ2024); [Answering Legal summary](@answering) [secondary]."))
    return out


# --------------------------------------------------------------------------
# Section 2
# --------------------------------------------------------------------------
def section_2(CH):
    out = chapter(2, SEC[2]["title"],
                  "The two markets describe the same pain with different nouns. Autocomplete and job boards match on the noun, not the complaint, "
                  "so a keyword list must follow the split: the UK 'chases' and talks about 'fee earners', 'bundles', 'SRA' and 'PII'; "
                  "the US does 'intake', 'non-billable', 'calendaring', 'IOLTA' and 'e-filing'.")
    out.append(H2("UK words"))
    out += bullets([
        "The dominant verb is <b>'chasing'</b>: clients for 'ID or payments on account', lenders for 'mortgage offers', local authorities for 'Local Searches', "
        "management packs, the other side's 'enquiries' ([Property Industry Eye, 29 Mar 2021](@pie)).",
        "People are <b>'fee earners'</b> and <b>'support staff'</b>; costs are <b>'PII'</b>, <b>'run-off cover'</b>, <b>'SRA fees'</b>, <b>'AML'</b>, <b>'Legal Aid'</b>.",
        "Litigation pain is the <b>'bundle'</b>, its <b>'pagination'</b>, whether it is <b>'CPR compliant'</b>, and the rule that it be lodged "
        "<b>'no less than three working days before the hearing'</b> ([Deka Chambers, 6 Oct 2023](@deka)).",
    ])
    out.append(quote_block("'All admin, file opening, compliance tasks and IT issues fall on you' ... 'AML, SRA compliance, conflict checks, audits, and complaints' ... "
                           "'client accounts, reconciliations, breaches, billing, credit control'",
                           "A UK sole practitioner's own list of burdens ([Jonathan Lea Network](@jlea), a platform-firm marketing page)"))
    out.append(H2("US words"))
    out += bullets([
        "The vocabulary is time and cash: <b>'non-billable administrative work'</b>, defined by one survey as 'intake, email follow-up, matter creation, deadlines, and billing preparation'; "
        "<b>'worked time never reaches the invoice'</b>; <b>'getting paid by clients'</b>; <b>'trust account' / 'IOLTA'</b>; <b>'e-filing'</b>; <b>'calendaring'</b> "
        "([AI Lawyer](@ailawyer) [vendor]; [Law Week Colorado](@colorado)).",
        "Staff titles: <b>'paralegal'</b>, <b>'legal assistant'</b>, <b>'case manager'</b>, <b>'intake specialist'</b>; none appear in UK ads.",
    ])
    out.append(quote_block("Email, texts and social messages 'began to drive me a little batty'; the public's number-one complaint is 'lack of attorney-client communication'; "
                           "'the real issue is overwhelm'", "US solo ([Toya Gavin, May 2018](@gavin))"))
    out.append(quote_block("'Communication' is 'the big culprit'; tasks that 'made me want to throw my laptop across the room'",
                           "[A Different Practice, Aug 2025](@adp)"))
    out.append(quote_block("The hated jobs: 'entering time, scheduling meetings, chasing unpaid invoices, and wrestling with administrative forms', "
                           "'revising incomprehensible billing entries' and 'writing dunning letters to non-paying clients'",
                           "Above the Law columnist, September 2026 ([Above the Law](@atl))"))
    out.append(H3("Table 2.1  High-signal markers by theme (keyword list)"))
    h, r = T(2, 0)
    out.append(tbl(h, r, widths=[24, 76, 76]))
    out.append(source_line("Sources: Reed conveyancing paralegal ads [%d]; Reed 57356370 [%d]; Huggins Lewis Foskett [%d]; Mallory Pryce [%d]; ILFM [%d]; Indeed US legal assistant [%d]; "
                           "Indeed US paralegal [%d]; Craigslist Los Angeles legal [%d]; Penningtons Manches Cooper [%d]; SRA Accounts Rules [%d]; Wikipedia: IOLTA [%d]." % tuple(
                               ref(u) for u in (
                                   "https://www.reed.co.uk/jobs/conveyancing-paralegal-jobs", "https://www.reed.co.uk/jobs/conveyancing-paralegal/57356370",
                                   "https://www.hugginslaw.co.uk/site/about/career-opportunities/conveyancing-secretary",
                                   "https://www.mallorypryce.co.uk/jobs/7821165-legal-assistant-private-client",
                                   "https://www.ilfm.org.uk/site/blog/ilfm-blog/legal-cashier-job-role-explained",
                                   "https://www.indeed.com/hire/job-description/legal-assistant", "https://www.indeed.com/hire/job-description/paralegal",
                                   "https://www.craigslist.org/search/area/losangeles?cat=lgl",
                                   "https://www.penningtonslaw.com/insights/transatlantic-litigation-disclosure-discovery-and-the-difference/",
                                   "https://www.sra.org.uk/solicitors/standards-regulations/accounts-rules/",
                                   "https://en.wikipedia.org/wiki/Interest_on_Lawyers%27_Trust_Accounts"))))
    out.append(H2("What job advertisements pay people to do"))
    out += bullets([
        "Job ads are the best proxy for what firms would pay a service to do. A scrape of <b>40 live UK Reed ads on 10 October 2026</b> (25 conveyancing paralegal, 15 legal secretary, "
        "salaries mostly £25,000 to £30,000) is dominated by process-stage words: <b>'completion' in 26 ads, 'fee earner' in 21, 'Land Registry' in 21, 'searches' in 20</b>, "
        "'liaising with clients, estate agents, lenders' in 19; 'audio typing / digital dictation' still in 7; <b>'chasing' in zero ads</b>; no case-management brand named "
        "([Reed conveyancing paralegal jobs](@reed_conv); [Reed 57348435](@reed_57348435)). UK firms write ads around the stage of the matter, not the task type.",
        "The <b>22 US ads</b> read in full (14 Indeed samples plus 8 Craigslist Manhattan postings) are built around litigation mechanics and the front desk: "
        "<b>drafting or typing pleadings in 13, calendaring deadlines in 10, e-filing in 8, answering phones in 7, bilingual (mostly Spanish) in 7</b>, billing or time entry in 5, "
        "intake in 3 ([Indeed US paralegal](@indeed_para); [Craigslist Dweck Law posting](@cl_dweck)).",
        "The Los Angeles Craigslist board alone had 94 legal postings with 'personal injury' in 9 titles, 'workers comp' in 9 and 'PI CASE MANAGER' twice ([Craigslist Los Angeles legal](@cl_la)).",
    ])
    out.append(fig_image(*CH["job_ads"]))
    out.append(H3("Table 2.2  Phrase counts in UK and US ads"))
    h, r = T(2, 1)
    out.append(tbl(h, r, widths=[62, 12, 90, 12], align_right_cols=(1, 3)))
    out.append(source_line("Sources: UK scrape of Reed [%d] and Reed legal secretary [%d] listings; US manual count over Indeed legal assistant [%d], Indeed paralegal [%d] and Craigslist postings "
                           "such as Senior Legal Assistant, PI [%d] and Court Calendar Clerk [%d]. Both counts are indicative, not statistical." % tuple(
                               ref(u) for u in ("https://www.reed.co.uk/jobs/conveyancing-paralegal-jobs", "https://www.reed.co.uk/jobs/legal-secretary-jobs",
                                                "https://www.indeed.com/hire/job-description/legal-assistant", "https://www.indeed.com/hire/job-description/paralegal",
                                                "https://www.craigslist.org/view/d/new-york-senior-legal-assistant/8oj9kyzSZDqrtqdSWQm4jt",
                                                "https://www.craigslist.org/view/d/new-york-court-calendar-clerk-landlord/n3xEo2Auk7SstQSJ4Vfk9H"))))
    out.append(H2("How lawyers phrase their searches (Google autocomplete, 10 October 2026)"))
    out += bullets([
        "Lawyers search in <b>noun phrases and job titles, not in complaint sentences</b>. UK and US settings returned near-identical lists.",
        "The seeds 'how to stop chasing clients' and 'law firm too much admin' returned <b>nothing</b>; 'chasing clients for' returned only 'chasing clients for payment'.",
        "The AI question is asked in the lawyer's own role word and in product-tier words: the worry is specifically whether a <b>paid tier changes confidentiality</b> "
        "([Google suggest, 'is chatgpt confidential'](@suggest_conf)).",
        "Search volumes are unknown; only the suggestion order was captured.",
    ])
    out.append(H3("Table 2.3  Autocomplete suggestions, verbatim (use as keywords)"))
    h, r = T(2, 2)
    out.append(tbl(h, r, widths=[40, 136], first_col_bold=True))
    out.append(source_line("Source: Google suggest endpoint calls such as ai for solicitors [%d], court bundle [%d], law firm automation [%d], outsource legal [%d]." % tuple(
        ref(u) for u in ("https://suggestqueries.google.com/complete/search?client=firefox&gl=gb&q=ai+for+solicitors",
                         "https://suggestqueries.google.com/complete/search?client=firefox&gl=gb&q=court+bundle",
                         "https://suggestqueries.google.com/complete/search?client=firefox&gl=us&q=law+firm+automation",
                         "https://suggestqueries.google.com/complete/search?client=firefox&gl=gb&q=outsource+legal"))))
    out.append(H2("What firms buy on freelance boards, and at what price"))
    out += bullets([
        "Upwork law-firm-side posts (nearly all US) are for intake calls, 'keep the file moving' administration, immigration form preparation and PI case management. Their words: "
        "'Following up with clients for missing documents, signatures, and information', 'Making repeated follow-up calls and sending messages when clients do not respond', "
        "'so I can focus on legal work and business development', 'so our paralegal can focus on substantive casework' ([Upwork legal-assistance jobs](@upwork_legal); [Upwork immigration-law jobs](@upwork_immig)).",
        "One PI case-manager post wants someone who will 'Order police reports', 'Open insurance claims', 'Communicate with insurance adjusters', 'Prepare demand packages' and "
        "'Coordinate lien reductions', with 'Clio Manage', 'Clio Grow' and 'AI tools (ChatGPT, Claude, Gemini)' as preferred experience ([Upwork](@upwork_legal)).",
        "UK firms are almost absent as buyers: PeoplePerHour's 'Legal Services' board on 10 October 2026 held 20 projects, every one a consumer or small business seeking a solicitor, "
        "none a firm seeking support ([PeoplePerHour legal services](@pph_legal)).",
        "Fiverr organises supply into landing pages titled '24 Best Paralegal Services To Buy Online', '24 Best Clio Automation Services', '24 Best Clio Grow Services' and "
        "'24 Best Legal Automation Services', which indicates measurable buyer search for brand-name set-up help; Fiverr blocked every fetch, so review counts and texts could not be read "
        "([Fiverr Clio automation](@fiverr_clio); [Fiverr paralegal](@fiverr_para)).",
    ])
    out.append(H3("Table 2.4  Work bought on freelance boards and prices seen"))
    h, r = T(2, 3)
    out.append(tbl(h, r, widths=[56, 48, 32, 40]))
    return out


# --------------------------------------------------------------------------
# Section 3
# --------------------------------------------------------------------------
def section_3(CH):
    out = chapter(3, SEC[3]["title"],
                  "In every practice area and both countries the firm's controllable work is front-loaded (intake, identity, authorisations, the first deadline) and back-loaded "
                  "(filing, registration, disbursement); the middle is weeks or months of waiting on a court, registry, agency, bank, insurer or medical provider, "
                  "while the file must be kept alive, the client updated and the deadline watched.")
    out.append(note_box("Step marks in the two workflow tables: <b>M</b> manual, <b>R</b> repetitive, <b>D</b> document-heavy, <b>T</b> deadline-driven. "
                        "The marks are the researcher's reading of the sources, not a survey result."))
    out.append(H2("UK practice areas: steps, numbers, sources"))
    out.append(H3("Table 3.1  UK workflows"))
    h, r = T(3, 0)
    out.append(tbl(h, r, widths=[24, 60, 60, 32], font="cell_small"))
    out.append(H2("The UK courts have shifted format risk onto firms"))
    out += bullets([
        "Administrative Court user-group minutes: CE-File sets the fee automatically, 'applications were being rejected because an incorrect fee had been used', and "
        "'once the application is rejected there is no way of resurrecting it' ([Judiciary.uk minutes, 10 Feb 2025](@judiciary_min)).",
        "A City solicitor who built a free bundling tool: 'It should be simple to prepare a bundle manually, but it's not'; it is 'a high-pressured task, shaped by conventions and certain rules' "
        "where 'human error creeps into the process'; his tool saves 'up to an hour per bundle' ([Legal Futures, 8 Apr 2026](@lf_bundletool)).",
        "The cost of getting it wrong: a bundle 'randomly thrown together' with replies '2,000 or 4,000 pages apart' drew a <b>£20,000 costs order</b>; a claimant who missed the bundle deadline "
        "blamed 'IT problems, lack of support staff, and miscommunications' and was refused relief; a judge called it 'dangerous to leave matters to the last minute' ([Deka Chambers, 6 Oct 2023](@deka)).",
    ])
    out.append(fig_image(*CH["uk_delays"]))
    out.append(H3("Table 3.2  UK queues and clocks"))
    h, r = T(3, 1)
    out.append(tbl(h, r, widths=[46, 62, 20, 48]))
    out.append(H2("What clients complain about tracks the same loops"))
    out += bullets([
        "Legal Ombudsman 2025/26: <b>14,259 complaints, up 37%</b>; <b>poor communication (24%) and delay or failure to progress (22%)</b> together 46%; "
        "<b>residential conveyancing 36% of accepted complaints (3,039, up 41%)</b>, wills and probate 14%, personal injury 14%; poor service found in <b>72%</b> of assessed cases "
        "(79% in wills and probate); the firm's own first-tier complaint handling unreasonable in 46% of investigated outcomes; a quarter of consumers never got a final response "
        "([Legal Ombudsman 2025/26](@leo2526)).",
        "US equivalent, the bar complaint: Virginia's leading violation sources 2020-2022 were 'Competency, Rule 1.1; Diligence, Rule 1.3; Managing Trust Accounts, Rule 1.15', with roughly "
        "<b>25% of complaints citing communication</b> ([Sands Anderson](@sands)); Maryland reports that 'failure to communicate and lack of diligence' produce the largest number of grievances "
        "([Maryland AGC](@md_agc) [snippet]).",
    ])
    out.append(fig_image(*CH["leo"]))
    out.append(H3("Table 3.3  Legal Ombudsman, 2024/25 against 2025/26"))
    h, r = T(3, 2)
    out.append(tbl(h, r, widths=[80, 48, 48]))
    out.append(source_line("Sources: Legal Ombudsman 2024/25 [%d]; Legal Ombudsman 2025/26 [%d]." % (
        ref("https://www.legalombudsman.org.uk/information-centre/data-centre/complaints-data/legal-ombudsman-202425-annual-complaints-data-and-insight/"),
        ref("https://www.legalombudsman.org.uk/information-centre/data-centre/complaints-data/legal-ombudsman-202526-annual-complaints-data-and-insight/"))))
    out.append(H2("US practice areas: agencies instead of registries, sharper deadline risk"))
    out += bullets([
        "<b>Missed deadlines are 'the single largest cause of malpractice claims against lawyers'</b> in plaintiffs' PI work; claims arise where 'a complaint was placed in the file and never filed' "
        "([Lawyers Mutual NC, Sep 2024](@lm_missed)).",
        "ABA claims profile 2020-2023 (relayed by ALPS): estate and probate <b>13.58%</b> of claims, real estate 13.19%, <b>plaintiff PI 12.73%</b>, family 10.02%; "
        "'administrative errors (including calendaring) are rising and now account for nearly 25% of all claims' ([ALPS, Jul 2026](@alps) [secondary]).",
    ])
    out.append(fig_image(*CH["malpractice"]))
    out.append(H3("Table 3.4  US workflows"))
    h, r = T(3, 3)
    out.append(tbl(h, r, widths=[24, 60, 60, 32], font="cell_small"))
    out.append(H2("The fee model decides which pain bites"))
    out += bullets([
        "A contingency PI firm is the client's lender for case costs and its own fee: every month of records or lien delay is a financing cost.",
        "An hourly family or business firm loses revenue to unrecorded time (38% utilisation) and slow billing: 37% of solos 'take too long to bill', 36% say clients do not pay on time "
        "([Answering Legal](@answering) [secondary]).",
        "A flat-fee criminal, bankruptcy or estate-planning firm bills and is paid fastest (flat-fee firms are 'five times more likely to send bills almost immediately' and 'close cases nearly three times faster' "
        "([2Civility](@civ_2024flat))) but absorbs every unplanned hour, such as body-cam review, as lost margin.",
        "Clients prefer flat fees for the whole case (<b>71%</b>); most solos offering them use them for the entire matter (<b>80%</b>) ([MinuteDock summary of Clio 2024](@minutedock) [snippet]).",
    ])
    out.append(H2("Website sweeps: how little is digital at the firm's edge"))
    out += bullets([
        "<b>24 reachable UK small-firm sites</b> (Hull, Stoke, Sunderland, Plymouth, Lincoln, Blackpool, Carlisle, Wolverhampton, Doncaster, Middlesbrough, Bradford, Wrexham, Swansea, Derry, Dundee): "
        "phone listed by all 24; <b>zero mention online onboarding, electronic ID verification, e-signature or document upload</b>; the only client portal belongs to a CLC-regulated conveyancer; "
        "five firms still publish fax numbers; one live home page contains 'Lorem ipsum'; one warns 'we cannot guarantee that your e-mail will be received by us'; another states "
        "'This Firm does not accept service of documents by Email or Fax'; a further 16 domains could not be read at all (expired, parked, wrong certificate, redirected to LinkedIn) "
        "([Allington Hughes](@allington); [Taylor Bracewell](@taylorb); [McKenzie Bell](@mckenzie); [Kenneth Jones redirect](@kjones)). Online quote tools exist only for conveyancing; everything else is 'call for a quote'.",
        "<b>18 US firm sites</b> (Tulsa, Birmingham, Greenville, Spokane, Toledo, Dayton, Knoxville, Chattanooga, Lubbock, Lexington, Albuquerque, Little Rock): every site leads with a phone number; "
        "11 have a four-or-five-field form; only one offers online scheduling (Calendly); only one a client portal (Qualia, a closing practice); four publish fax numbers; none describes e-signature, "
        "document upload or payment plans; one firm's domain now serves gambling spam ([Greenway Law Group](@greenway); [Sallé Law](@salle); [Hartley Law Office listing](@hartley)).",
        "Spanish-language service appears at every immigration firm read and almost nowhere else. The client's manual journey at every swept firm: find the phone number, wait for a call-back, "
        "be matched to a fee earner, then deliver documents by whatever means that person chooses.",
    ])
    return out


# --------------------------------------------------------------------------
# Section 4
# --------------------------------------------------------------------------
def section_4(CH):
    out = chapter(4, SEC[4]["title"],
                  "Every UK and US regulator that has spoken says the same thing: confidentiality, competence and supervision apply unchanged, putting client information into a public or free "
                  "AI tool is disclosure to a third party, and the lawyer stays personally responsible for the output. In 2025-26 the duty moved from guidance to enforcement, and the enforcement "
                  "landed on the 1-20 lawyer segment.")
    out.append(H2("UK: tribunal rulings, then warning notices"))
    out += bullets([
        "<b>November 2025, Upper Tribunal</b>: a Manchester immigration solicitor had 'put client emails he had drafted about Home Office decisions into ChatGPT to improve them' and "
        "'uploaded Home Office decision letters to summarise them for clients'; putting such information into open AI tools is <b>'to breach client confidentiality and waive legal privilege'</b>; "
        "lawyers who did this 'would have to self-report and should consult the ICO'; closed tools such as Microsoft Copilot are available 'without these risks'. A second Birmingham firm had grounds drafted by "
        "'a part-time trainee lawyer' who was in fact a very junior caseworker; the judge said the matter was 'principally about supervision' because 'anyone with Google has access to AI' "
        "([Legal Futures, 24 Feb 2026](@lf_chatgpt)).",
        "<b>October 2026, third ruling</b>: at an East London firm 'a junior member of staff, namely a paralegal' used ChatGPT to produce grounds of appeal that the solicitors 'did not check'; supervision "
        "'did not begin to mitigate the risk'; two self-reports to the SRA ([Legal Futures, 9 Oct 2026](@lf_existential)).",
        "A reported 2026 Upper Tribunal decision describes uploading confidential material to an open tool as placing it 'on the internet in the public domain' because such tools 'may retain and use inputs for model training' "
        "([Slaughter and May Lens, 8 Jun 2026](@slaughter), a large-firm commentary).",
        "<b>SRA warning notice, 17-18 August 2026</b>, after 'rising cases of hallucinated case law and confidentiality breaches': solicitors 'remain accountable for their work and outputs, regardless of how that work has been prepared'; "
        "entering confidential information into open tools such as ChatGPT would amount to a waiver of privilege; client information only with 'appropriate contractual, technical and organisational safeguards' "
        "([Legal Cheek, 18 Aug 2026](@legalcheek_sra) [secondary]; the notice text itself was blocked). The SRA had received <b>42 reports of potential AI misuse between July 2025 and July 2026</b> ([Lets Data Science](@letsdata) [secondary]).",
        "Bar Council guidance (reviewed 25 Nov 2025), para 21: 'anything that a user types into the system may be used to train the software and might find itself repeated verbatim in future results'; para 28: sharing privileged or "
        "confidential information with a generative LLM 'is likely to be a breach of Core Duty 6' ([Bar Council PDF](@barcouncil)).",
        "Bar Standards Board guidance in force from 18 May 2026: free tools are generally unsuitable for client work because their terms typically let providers 'claim rights over input data, store prompts indefinitely, and use them for model training' "
        "([Legal Cheek, May 2026](@legalcheek_bsb) [secondary]).",
        "Law Society, 'Generative AI: the essentials' (Aug 2024): for a free online tool with no operational relationship with the vendor 'you should not put any confidential data into the tool' ([LawCareers.Net, Michelmores](@michelmores) [secondary]).",
        "<b>Ayinde v Haringey and Al-Haroun v Qatar National Bank (Divisional Court, 6 June 2025)</b>: freely available tools 'are not capable of conducting reliable legal research' and 'may cite sources that do not exist'; "
        "in one case five cited authorities did not exist, in the other 18 of 45; both matters referred to the regulators; powers listed: admonishment, costs orders, strike-out, police referral, contempt ([Judgment, National Archives](@ayinde)).",
    ])
    out.append(H2("US: bar opinions, a privilege waiver, and routine sanctions"))
    out += bullets([
        "<b>ABA Formal Opinion 512 (29 July 2024)</b>: self-learning tools raise disclosure risk 'even if the tool is used exclusively by lawyers at the same firm'; 'a client's informed consent is required prior to inputting information relating "
        "to the representation into such a GAI tool'; 'merely adding general, boiler-plate provisions to engagement letters' is not enough ([Zuva summary](@zuva) [secondary]; the ABA PDF was blocked).",
        "<b>Kentucky E-457 (March 2024)</b>: do not 'input any client information that lacks reasonable and adequate security protections unless, of course, client consent is first obtained'; 'review the \"terms of use\" of any AI product' because some use "
        "'uploaded documents such as pleadings or contracts to train itself, or to share that information with third parties' ([KBA E-457](@kba)). <b>California (Nov 2023)</b>: attorneys 'must not input any confidential client information' into AI tools lacking adequate protections ([Epiq](@epiq) [secondary]).",
        "<b>United States v Heppner (S.D.N.Y., 10 Feb 2026)</b>: Judge Rakoff held that a client's use of a consumer AI tool waived attorney-client privilege because the platform was a third party whose terms warned that prompts 'may be shared further' "
        "([Washington Legal Foundation](@wlf)); two other federal courts treated AI as a tool rather than a person, so the US position is split ([ACEDS](@aceds)).",
        "Hallucination sanctions are routine: a tracker of AI-fabricated content in US filings counted <b>11 instances in 2023, 37 in 2024, 524 in 2025 and 668 in 2026 to July</b>, with <b>97 monetary sanctions and 59 disciplinary referrals in 2025</b> "
        "(37 cases at $1,000-$5,000, four over $50,000); 'judicial patience for unverified citations has evaporated' ([MSBA, 27 Jul 2026](@msba) [secondary]). The rate rose 'from about two cases per week before spring 2025 to two or three per day'; "
        "a Colorado attorney got a 90-day suspension after admitting he 'had not checked the work on a motion that ChatGPT helped draft' ([Cronkite News, 28 Oct 2025](@cronkite)).",
        "Even paid legal research tools hallucinate: Stanford (May 2024) found Lexis+ AI and Westlaw AI-Assisted Research 'each relatively hallucinate between 17% and 33% of queries' ([Bar Council PDF, para 11](@barcouncil)).",
    ])
    out.append(fig_image(*CH["hallucination"]))
    out.append(H3("Table 4.1  AI-fabricated content in US court filings (Charlotin tracker)"))
    h, r = T(4, 0)
    out.append(tbl(h, r, widths=[70, 22, 22, 36, 26]))
    out.append(source_line("Source: [MSBA, 27 Jul 2026](@msba) [secondary]."))
    out.append(H2("What firms are afraid of, in order: hallucination, then privilege and training, then vendor terms"))
    out += bullets([
        "Surveys rank accuracy first: <b>75%</b> of ABA-surveyed lawyers named accuracy the top concern and <b>47%</b> data privacy and security; AffiniPay's 2025 survey of more than 2,800 mostly small-firm respondents put "
        "trustworthiness and ethical issues at 42% each and privilege at 36%, with 60% unsure when their firm would adopt ([LawNext, Apr 2025](@lawnext_surveys)).",
        "SRA 2025 study of sole practitioners and small firms under £400,000 turnover: <b>only 12% use generative AI</b>, 25% are considering it; barriers are cost (25%), data breach or compliance risk (15%) and quality (11%) "
        "([SRA research findings](@sra_tech)). The SRA's 2023 AI report had already named the risk scenario of 'a staff member using an online AI tool such as ChatGPT on a client's case' and said automation "
        "'could be particularly beneficial for small firms where senior practitioners do not have support from an administrative team' ([SRA, Nov 2023](@sra_ai2023)).",
        "<b>The shadow-AI gap is the clearest single number</b>: Censuswide, 200 UK legal professionals, April 2026: <b>59% of fee earners in small and mid-sized firms admitted using unapproved tools such as free ChatGPT and Google AI search, "
        "while 68% of firm leaders were 'confident they have full visibility and zero risk'</b>; half would welcome AI built into their case-management system but only 25% of firms have it; 'restricting or banning AI may push staff toward shadow tools' "
        "([Legal Futures blog, Access Legal](@lf_shadow) [vendor-run survey]).",
        "The behavioural precursor, 2022: <b>74% of UK small firms used free Google for research and 63% admitted this was 'riskier and slower than legal tech'</b> ([Solicitors Journal, 16 May 2022](@sj2022)).",
        "Thomson Reuters 2025 cross-profession survey: <b>52% had no AI policy and 64% no generative-AI training</b> ([LawNext](@lawnext_surveys)); among in-house teams 83% use tools not provided by the company and 81% tools not approved ([Bloomberg Law](@bloomberg_policy)).",
        "The people pasting client material into free tools in the UK cases were paralegals, trainees and sole principals at immigration firms; the principal's defence that 'there was no mechanism by which staff at his firm could use AI' was rejected ([Legal Futures, 24 Feb 2026](@lf_chatgpt)).",
        "The closed-tool alternative has its own documented problem: Microsoft 365 Copilot 'can share confidential information with unauthorized firm personnel if data permissions aren't appropriately established', so document permissions and sensitivity labels must be fixed first "
        "([Intapp case study](@intapp); [ABA Law Technology Today, 2026](@aba_copilot)).",
    ])
    out.append(fig_image(*CH["shadow_ai"]))
    out.append(H3("Table 4.2  AI policy and shadow-use measures"))
    h, r = T(4, 1)
    out.append(tbl(h, r, widths=[62, 28, 42, 44]))
    out.append(H2("Cyber incidents: the other reason small firms are told to keep data inside"))
    out += bullets([
        "NCSC legal-sector report: 'many legal practices, especially smaller firms, chambers and individual practitioners, rely on an external IT services provider, making it challenging for them to assess for themselves whether the controls they have in place are appropriate'; "
        "'a small law firm with few resources could be devastated' by ransomware ([NCSC, Jun 2023](@ncsc)).",
        "SRA thematic review of 40 firms: <b>30 had been targeted, over £4 million of client money stolen from 23 firms, 18 firms paying about £400,000 of their own money, 43% of attacks on small firms, email modification fraud about half of all attacks</b>; "
        "one conveyancing firm's ransomware attack (an employee clicked a weekend email) closed it for 14 days and cost £60,000 to recover plus £150,000 in lost revenue ([Legal Futures, 31 Oct 2019](@lf_cyber2019)).",
        "ICO action against three small criminal-law firms: Tuckers (ransomware Aug 2020; no MFA, five-month patch gap, unencrypted data); Levales (reprimand Oct 2024; 8,234 people affected, no MFA on the compromised account); "
        "DPP Law (£60,000 fine Apr 2025; brute-forced admin account on a legacy case-management system, 791 people including privileged material, reported 43 days late after the NCA found the data on the dark web) ([ICO, Levales](@ico_levales); [teiss, 22 Apr 2025](@teiss)).",
        "A November 2023 attack on CTS, an IT provider to law firms, left an estimated 80 to 200 conveyancing firms unable to complete transactions ([Mortgage Solutions, 5 Dec 2023](@cts)). The average ransom demand on legal-sector organisations rose "
        "<b>60% to US$611,000 in 2025</b> with attack volume up 54% ([Insurance Business / QBE, Jun 2026](@qbe)).",
        "US: 27% to 29% of ABA-surveyed firms report a breach, but only <b>19% of solos and 19% of 2-9 lawyer firms have an incident response plan</b>, against 78% at firms of 500+ ([ABA 2023 Cybersecurity TechReport](@aba_cyber2023)).",
        "Everyday channel problems: email (a solicitor was fined by the SDT after transferring more than £290,000 to a hacker on emailed bank details ([Law Society](@ls_friday))) and WhatsApp, which the SRA's 2024 asylum review found had become the "
        "'preferred communications tool' at firms with no written policy and case-management systems that do not capture messages ([Legal Futures, 31 Jul 2024](@lf_whatsapp)); a costs judge has ruled WhatsApp messages form part of the solicitor's file if charged for ([Legal Futures on MacInnes v DWF](@lf_macinnes)).",
        "No UK or US regulator mandates on-premises or in-country hosting; the pressure comes from UK GDPR transfer rules, client outside-counsel guidelines that ask 'where data is stored' ([Conventus Law](@conventus)), and a few US judges' standing orders requiring a certificate that AI use "
        "'didn't disclose proprietary information to unauthorized parties' ([Bloomberg Law](@bloomberg_orders)). The practical exposure for a small firm: it cannot answer 'where is it processed' for a free consumer tool.",
    ])
    out.append(fig_image(*CH["cyber"]))
    out.append(H3("Table 4.3  Cyber incidents and costs"))
    h, r = T(4, 2)
    out.append(tbl(h, r, widths=[58, 70, 48]))
    return out


# ==========================================================================
# Content, part B: sections 5 to 8
# ==========================================================================
U.update({
    "casepeer_check": "https://www.casepeer.com/blog/personal-injury-case-management-guide-and-checklist/",
    "finch": "https://www.finchlegal.com/",
    "finch_guides": "https://www.finchlegal.com/guides",
    "mm_police": "https://www.forthepeople.com/blog/how-get-copy-police-report/",
    "icc": "https://www.injuryclaimcoach.com/police-report.html",
    "tx550": "https://texas.public.law/statutes/tex._transp._code_section_550.065",
    "fl316": "https://florida.public.law/statutes/fla._stat._316.066",
    "ca20012": "https://california.public.law/codes/ca_veh_code_section_20012",
    "ohio": "https://ohtrafficdata.dps.ohio.gov/CrashRetrieval",
    "fl627": "https://florida.public.law/statutes/fla._stat._627.4137",
    "cms": "https://www.cms.gov/medicare/coordination-benefits-recovery/beneficiary-services",
    "garretson": "https://web.garretsongroup.com/claimant-education-posts/claimant-education/long-normally-take-resolve-medicare-lien-individual-case",
    "plf_pi": "https://assets.osbplf.org/forms/practice_forms/issues-for-consideration-in-commencing-and-settling-a-personal-injury-case.docx",
    "plf_tickler": "https://assets.osbplf.org/forms/practice_forms/reminder-and-tickler-systems.pdf",
    "plf_docket": "https://assets.osbplf.org/forms/practice_forms/docketing-and-calendaring-checklist.pdf",
    "evenup_intake": "https://www.evenuplaw.com/intake",
    "evenup_lr": "https://www.evenuplaw.com/blog/lerner-rowe-faster-cases-efficiency-settlements/",
    "evenup": "https://www.evenuplaw.com/",
    "evenup_med": "https://www.evenuplaw.com/products/medical-management",
    "supio_mar": "https://www.supio.com/blog/march-2026-release",
    "supio_chron": "https://www.supio.com/medical-chronologies",
    "zapier_clio": "https://zapier.com/apps/clio/integrations",
    "zapier_fv": "https://zapier.com/apps/filevine/integrations",
    "cloudlex": "https://www.cloudlex.com/",
    "cloudlex_rec": "https://www.cloudlex.com/law-firm-management/essentials-of-medical-record-retrieval/",
    "oic": "https://www.officialinjuryclaim.org.uk/help-hub/start-a-new-claim/",
    "askmid": "https://www.askmid.com/",
    "mib": "https://www.mib.org.uk/",
    "stats19": "https://www.gov.uk/guidance/road-accident-and-safety-statistics-guidance",
    "lawyerist_clio": "https://lawyerist.com/reviews/law-practice-management-software/clio/",
    "clio_help_wf": "https://help.clio.com/hc/articles/35132279298843",
    "clio_wf_guide": "https://www.clio.com/wp-content/uploads/2025/05/Automated-Workflows-Best-Practice-Guide.pdf",
    "tr_clio": "https://web-v2.prod.trustradius.com/products/clio/reviews/all",
    "prn_oct25": "https://www.prnewswire.com/news-releases/clio-introduces-the-legal-industrys-first-intelligent-legal-work-platform-302586236.html",
    "prn_operate": "https://www.prnewswire.com/news-releases/clio-introduces-clio-operate-to-the-north-american-legal-market-302707832.html",
    "clio_help_zap": "https://help.clio.com/hc/en-us/articles/16186400854171",
    "zapier_comm": "https://community.zapier.com/troubleshooting-99/zap-isn-t-updating-custom-field-for-all-matters-in-clio-28292",
    "clio_rate": "https://docs.developers.clio.com/api-docs/clio-manage/rate-limits/",
    "clio_apps": "https://docs.developers.clio.com/api-docs/clio-manage/applications/",
    "prn_science": "https://www.prnewswire.com/news-releases/the-science-behind-smarter-law-clios-2025-legal-trends-report-reveals-how-technology-is-rewiring-the-way-lawyers-work-302585725.html",
    "trustpilot_clio": "https://www.trustpilot.com/review/clio.com",
    "clio_grow_conv": "https://help.clio.com/hc/articles/9286116462747",
    "bigmode": "https://www.clio.com/partnerships/certified-consultants/find-a-ccc/big-mode-consulting/",
    "act": "https://www.clio.com/partnerships/certified-consultants/find-a-ccc/apply-compliance-today/",
    "aimadefor": "https://www.aimadefor.com/blog/clio-pricing-2026/",
    "costbench_grow": "https://www.costbench.com/software/legal-practice-management/clio-grow/hidden-costs/",
    "jayva": "https://www.jayvaglobal.com/news/are-you-wasting-your-software-investment",
    "leap_dir": "https://www.leaplegalsoftware.com/uk/certified-partner-directory/",
    "leap_pn": "https://www.leaplegalsoftware.com/uk/partner-network/",
    "oktopeak": "https://oktopeak.com/blog/filevine-pricing-real-cost-tco/",
    "vineskills": "https://www.vineskills.com/pricing",
    "upwork_auto": "https://www.upwork.com/freelance-jobs/apply/Automation-Developer-Legal-Operations-Ongoing-Engagement_~022052780018516086731/",
    "upwork_fv": "https://www.upwork.com/freelance-jobs/apply/Filevine-Developer-Workflow-Optimization-Dashboard-Development_~022064174955884814478",
    "builtin_fv": "https://builtin.com/job/filevine-administrator/7571212",
    "zip_fv": "https://www.ziprecruiter.com/Jobs/Filevine",
    "baskerville": "https://baskervilledrummond.com/",
    "3kites": "https://www.3kites.com/",
    "lm_intake": "https://lawyersmutualnc.com/article/dont-leave-client-intake-to-chance/",
    "casepeer_med": "https://www.casepeer.com/blog/medical-records-management/",
    "chartrequest": "https://www.chartrequest.com/articles/medical-record-retrieval-delays-personal-injury",
    "smokeball_req": "https://www.smokeball.com/blog/document-request-reporting",
    "eve": "https://www.eve.legal/",
    "wisedocs": "https://www.wisedocs.ai/",
    "digitalowl": "https://www.digitalowl.com/",
    "sacra": "https://sacra.com/c/filevine",
    "lawyerist_fv": "https://lawyerist.com/reviews/law-practice-management-software/filevine/",
    "dupple": "https://dupple.com/reviews/filevine",
    "lawnext_pi": "https://www.lawnext.com/2023/10/clio-goes-all-out-with-major-product-announcements-including-a-personal-injury-add-on-e-filing-and-of-course-generative-ai.html",
    "fv_ct": "https://filevine.com/customers/case-studies/connecticut-trial-firm/",
    "capterra_fv2": "https://capterra.com/p/140815/Filevine/reviews/?page=2",
    "pricingsaas": "https://pricingsaas.com/companies/clio",
    "lawyerist_grow": "https://lawyerist.com/reviews/intake-crm/clio-grow/",
    "layer3": "https://www.layer3labs.io/comparisons/lawmatics-vs-clio-grow",
    "costbench_clio": "https://costbench.com/software/ai-legal-tools/clio/",
    "falkon": "https://clio.com/app-directory/falkon-sms",
    "textrequest": "https://www.clio.com/app-directory/text-request/",
    "clio_uk_leap": "https://www.clio.com/uk/compare/clio-vs-leap/",
    "softwarefinder": "https://softwarefinder.com/legal/filevine-software/reviews",
    "civiciq": "https://civiciq.com/public-contract/cbcdbbcd-a682-4543-8213-34422ff206e5",
    "rfp_clio": "https://www.rfp.wiki/legal-compliance/legal-practice-management/clio",
    "capterra_clio": "https://www.capterra.com/p/105428/Clio/reviews/%3Fpage%3D13",
    "capterra_fv": "https://capterra.com/p/140815/Filevine/reviews/",
    "tr_fv": "https://web-v2.prod.trustradius.com/products/filevine/reviews/all",
    "rfp_fv": "https://www.rfp.wiki/legal-compliance/filevine",
    "fv_partners": "https://filevine.com/partners/directory",
    "fv_news": "https://www.filevine.com/news/filevine-releases-payment-processing-to-deliver-end-to-end-timekeeping-billing-and-payments-platform",
    "clio_help_pi": "https://help.clio.com/hc/articles/18350703919899",
    "clio_intake": "https://www.clio.com/features/online-intake-forms/",
    "clio_help_text": "https://help.clio.com/hc/articles/14164457325595",
    "layer3_intake": "https://www.layer3labs.io/comparisons/best-legal-client-intake-software",
    "clio_conf22": "https://cliocloudconference.com/wp-content/uploads/2022/10/Clio-Cloud-Conference-2022-How-to-Set-Up-Dynamic-Information-and-Document-Automation.pdf",
    "g2_grow": "https://g2.com/products/clio-grow/reviews",
    "clio_grow_import": "https://help.clio.com/hc/en-us/articles/18952761837979",
    "ld_features": "https://www.leaddocket.com/features/",
    "ld_phase": "https://support.leaddocket.com/hc/en-us/articles/360048471211-Phase-Mapping",
    "ld_vinesign": "https://support.leaddocket.com/hc/en-us/articles/4410421026331",
    "sa_au": "https://www.softwareadvice.com.au/software/266483/leaddocket",
    "capterra_ca": "https://www.capterra.ca/compare/105428/176004/clio/vs/leaddocket",
    "tr_ld": "https://web-v2.prod.trustradius.com/products/lead-docket/reviews/all",
    "ls_leap": "https://www.lawsociety.org.uk/membership/offers/leap-legal-software",
    "capterra_uk": "https://www.capterra.co.uk/compare/105428/147413/clio/vs/leap",
    "trustpilot_leap": "https://uk.trustpilot.com/review/leap.co.uk",
    "sa_fr_leap": "https://softwareadvice.fr/software/20175/leap?page=2",
})


def section_5(CH):
    out = chapter(5, SEC[5]["title"],
                  "In every checklist read, the first 72 hours after a car-accident client signs run the same way, and the police report comes second in time "
                  "but 'first' in importance. Obtaining it is a manual, state-specific act, and no vendor page read claims to fetch it.")
    out.append(fig_image(*CH["pi_flow"]))
    out.append(H2("The sequence and why the report matters"))
    out += bullets([
        "CASEpeer's checklist: sign the retainer and the HIPAA and records authorisations, calendar the statute of limitations 'immediately', send letters of representation 'to all known insurers within 24 to 48 hours', "
        "open the claims and get adjuster assignments, and only then 'Request the police or incident report', send spoliation letters and pull policy limits ([CASEpeer checklist, 2 Sep 2026](@casepeer_check) [vendor]).",
        "Practitioners say 'get it first' in importance because it 'has the defendant, the carrier, and the officer's narrative' ([Finch](@finch) [vendor]); without it 'the details may \"boil down to he said, she said\"' ([Morgan &amp; Morgan, Mar 2025](@mm_police)).",
        "The firm reads from it: the adverse driver and carrier, the officer's narrative and opinion of fault, citations and coded contributing factors, the scene diagram, witness and passenger details, injury descriptions. "
        "Adjusters 'generally accept police accident reports as credible, unbiased evidence of fault'; roadway and weather conditions 'may appear as code numbers' that need a call to the department to decode; "
        "in fatal or pending-toxicology cases 'the report is amended as information becomes available', so a final copy is needed ([Injury Claim Coach](@icc)).",
        "Factual errors (a wrong address or spelling) can be corrected with supporting evidence, but 'changing the officer's opinion of fault is \"much more difficult\"' ([Injury Claim Coach](@icc); [Morgan &amp; Morgan](@mm_police)).",
    ])
    out.append(H2("Obtaining the report is a manual, state-specific act"))
    out += bullets([
        "<b>Texas</b> sells the collision report for <b>$6 plus $2 for certification</b>, releases the full version only 'on written request' to an enumerated list of persons 'directly concerned' (attorneys are not named and fall under 'authorized representative' by implication), "
        "and publishes a redacted copy anyone can buy ([Tex. Transp. Code 550.065](@tx550)).",
        "<b>Florida</b> makes reports <b>confidential for 60 days</b> except to 'the parties involved in the crash, their legal representatives', insurers and agencies; requires a written sworn statement that the report 'will not be used for any commercial solicitation of accident victims', "
        "which 'must be completed and sworn to by the requesting party for each individual crash report'; knowing misuse is 'a felony of the third degree'; the officer's long-form report is due within 10 days of completing the investigation ([Fla. Stat. 316.066](@fl316)).",
        "<b>California</b> releases confidential reports to anyone with 'a proper interest', including 'any attorney who declares under penalty of perjury that he or she represents' an involved person, and caps copy fees at actual cost ([Cal. Veh. Code 20012](@ca20012)).",
        "<b>Ohio's</b> statewide portal warns that 'Crash reports may take up to 6 weeks to be available', that they 'are to be used for statistical use only and are not sufficient to be used for any court proceeding', that 'the investigating agency is the official record keeper', "
        "and it sits behind a case-sensitive CAPTCHA ([Ohio Crash Retrieval](@ohio)).",
        "Firm-side explainers put the general cost at '$5 to $25' and availability at '5 to 10 business days after the accident, but it could take longer if the investigation is ongoing', with BuyCrash and LexisNexis as aggregators that 'may charge additional fees' ([Morgan &amp; Morgan](@mm_police)).",
        "Every aggregator (BuyCrash/LexisNexis, CrashDocs/Carfax, ReportBeam) and every other state portal attempted (Texas CRIS, Florida FLHSMV, CHP, Georgia, Kentucky, Tennessee, Oklahoma, Alabama, Nebraska, Idaho, NYPD) refused the researcher, so their fees, account terms and anti-bot clauses are unsourced.",
    ])
    out.append(H3("Table 5.1  Crash-report access by state or channel"))
    h, r = T(5, 0)
    out.append(tbl(h, r, widths=[20, 28, 42, 32, 32, 22], font="cell_small"))
    out.append(H2("The other intake verifications follow the same pattern"))
    out += bullets([
        "Policy limits are statutory in Florida: an insurer must answer a claimant's written request within 30 days with a sworn statement giving the insurer, each insured, the limits including umbrella and excess, any coverage defence and 'a copy of the policy' ([Fla. Stat. 627.4137](@fl627)).",
        "Medicare's recovery contractor expects 'the Medicare beneficiary or his/her attorney' to 'inform Medicare as soon as they become aware other insurance is available' and recovers conditional payments from any settlement ([CMS BCRC](@cms)); "
        "Medicare resolution 'takes about 5-6 months from start to finish' or about 45 days if opened early ([Garretson Resolution Group](@garretson)).",
        "Oregon's professional liability fund asks whether the lawyer has 'obtained the pertinent HIPAA-compliant medical authorizations', 'an employment and tax records authorization', determined Medicare or Medicaid eligibility and 'put the agencies on notice', "
        "and obtained records 'including treatment prior to the litigated incident' ([OSB PLF PI checklist](@plf_pi)).",
        "The one verification vendors have clearly automated is the carrier call: EvenUp says 'Once you've signed the client, AI Agents call carriers to open 5x more claims and get adjuster assignments', agents 'confirm liability and coverage, and deliver written confirmation to your team', "
        "saving '16+ Minutes Per Case On Coverage Checks' ([EvenUp Intake](@evenup_intake) [vendor]); its Lerner &amp; Rowe release claims '2x more claims opened in the same amount of time' and 'policy-limit tenders that I would not normally be getting' ([EvenUp, 3 Jun 2026](@evenup_lr) [vendor]).",
        "Supio's March 2026 release adds a Case Review Agent that 'automatically extracts incident facts from case files' and 'shows which information is present and which still needs to be collected from the client', plus Instant Liens that 'reads every document in the case file and identifies liens' "
        "as Government, ERISA/private or provider ([Supio, 16 Mar 2026](@supio_mar) [vendor]).",
    ])
    out.append(H2("The automation boundary is legal, not technical"))
    out += bullets([
        "None of the vendor pages read (EvenUp, Supio, Eve, Finch, Wisedocs, DigitalOwl, Parrot, Case Status, Filevine, Lead Docket, Litify, SmartAdvocate, CloudLex, CASEpeer, Lawmatics, Smokeball, and the Zapier listings for Clio and Filevine) claims to fetch a crash report from a state portal "
        "or names a crash-report parser. They automate upstream (intake calls, lead scoring, carrier calls) and downstream (fact extraction from whatever is uploaded, lien classification, demand drafting).",
        "Zapier can 'Upload Document to Matter' in Clio but cannot fetch one; Filevine's Zapier app exposes a single 'New Event' trigger and no document-upload action ([Zapier Clio](@zapier_clio); [Zapier Filevine](@zapier_fv)).",
        "The reasons are on the statute book: Florida's per-report sworn statement under felony penalty and California's attorney declaration under penalty of perjury are signed, personal acts, and any script that performed them would shift criminal exposure onto the firm; "
        "Texas requires a written request from an enumerated person; Ohio's portal is CAPTCHA-gated and non-evidentiary anyway.",
        "CloudLex describes its own records service as 'no portals, no uploads', which is a managed human service, not a software integration ([CloudLex](@cloudlex) [vendor]).",
        "The reliable boundary today: a human (paralegal, client or adjuster) obtains the PDF; software ingests it (Supio's forwarding inbox, SmartAdvocate's barcode scan, CloudLex's mail indexing) and extracts the facts; a human checks the version and the fault opinion.",
    ])
    out.append(note_box("<b>Fully manual, with no vendor claim at all:</b> decoding state-specific contributing-factor codes, chasing amended reports in fatal or toxicology cases, and asking the agency to correct a factual error.", warm=True))
    out.append(H2("England and Wales: the low-value route removes the police report as a precondition"))
    out += bullets([
        "The Official Injury Claim portal needs 'the full name and UK vehicle registration number of the driver you feel is responsible', witness details, the claimant's National Insurance number and police details only 'if the police attended the scene', with the Police Reference Number 'if available'; "
        "the compensator has up to 30 business days on liability and 20 to make a first offer ([OIC start a claim](@oic)).",
        "The other driver's insurer is found through askMID at <b>£10 for a one-off search or £774 a year</b> on subscription, migrating to 'Check Their Vehicle' from 7 December with new subscriptions paused until Q1 2027 ([askMID](@askmid)); "
        "uninsured or untraced drivers go to the Motor Insurers' Bureau, which says about 335,000 uninsured vehicles are on UK roads on any day ([MIB](@mib)).",
        "STATS19 is the police statistical return, not the disclosable collision report ([GOV.UK STATS19](@stats19)). Every police-force collision-report fee page attempted returned an error, so the typical fee, who may request and the turnaround are unverified.",
    ])
    return out


def section_6(CH):
    out = chapter(6, SEC[6]["title"],
                  "Clio Manage's native automation is template-based, not event-driven: it can apply a task list and show a stage, but nothing in the documentation enforces required fields, "
                  "named task owners or overdue exception reports. Across every US competitor page fetched, the words 'overdue alert', 'required field' and 'exception report' are absent.")
    out.append(H2("What Clio's native automation can and cannot do"))
    out += bullets([
        "Documented building blocks: matter templates (Essentials tier and above), task-template lists applied to a matter, and matter stages (Advanced and above) shown as Kanban boards ([Lawyerist Clio review](@lawyerist_clio)).",
        "'Automated Workflows': on matter creation or a stage move it can 'Assign a task list' or 'Generate a document', and on a Clio Grow to Manage conversion 'Apply a matter template'; that is the full list of actions; "
        "available only on the Advanced and Expand (or Complete) tiers ([Clio help 35132279298843](@clio_help_wf) [snippet]; [Clio Automated Workflows guide, May 2025](@clio_wf_guide)).",
        "A reviewer in August 2025: 'No conditional logic in task assignments' and a 'basic notification system with limited real-time updates' ([TrustRadius Clio](@tr_clio) [user, 7 Aug 2025]).",
        "Clio's October 2025 'intelligent legal work platform' release promises 'Manage AI' that 'turns court documents into calendar events' and 'Grow AI' that 'automatically follows up on outstanding intake items' but names no workflow tools and gives no availability or price "
        "([PR Newswire, 16 Oct 2025](@prn_oct25) [vendor]); Lawyerist notes that 'deeper automation for calendaring and task management is planned, not yet available' ([Lawyerist](@lawyerist_clio)).",
        "Clio Operate, the configurable-workflow product from the ShareDo acquisition, is 'built for firms with more than 200 users' ([PR Newswire, 9 Mar 2026](@prn_operate)), so it does not reach the 1-30 lawyer firm.",
    ])
    out.append(H2("Everything conditional, date-driven or cross-matter needs the API or middleware"))
    out += bullets([
        "Zapier's Clio app: 12 triggers (New Matter, Matter Status Updated, New Task, Task Status Updated, New Document, New Contact and so on), 17 actions (including 'Assign Task Template List' and 'Create Task'), 8 searches (including Find Matter by Custom Field); "
        "<b>no trigger on a custom-field value, no 'Updated Matter' trigger, no Clio Grow trigger</b> ([Zapier Clio](@zapier_clio)). Zaps are 'only compatible with Clio Manage' and 'run for every user on the account' ([Clio help 16186400854171](@clio_help_zap) [snippet]); "
        "a user found Clio's own 'Required Custom Field rules' blocked a Zap updating matters ([Zapier community](@zapier_comm)).",
        "Clio Manage API v4: 'a default rate limit of 50 requests per minute during peak usage hours' per access token; 'Clio does not currently offer custom rate limit increases' ([Clio developer docs](@clio_rate)); the docs sidebar lists no webhooks page and a guessed path returned 404 ([Clio developer docs](@clio_apps)). "
        "Fifty requests a minute is enough for a nightly sweep across a small firm's open matters, but any exception report is a polling job, not an event.",
        "Data-model limits: 'Clio does not allow a \"User\" custom field' and 'does not allow you to create custom fields that are \"lists\" or \"collections\"' ([TrustRadius Clio](@tr_clio) [user, 20 Jul 2022]); document templates can only be built from matter fields, not contact fields, "
        "'which made medical records requests hard to generate for multiple providers' ([Lawyerist](@lawyerist_clio) [user, 5 Jan 2020]).",
    ])
    out.append(H3("Table 6.1  Workflow capability by system (part 1: triggers, logic, rules, owners)"))
    h, r = T(6, 0)
    parts = split_cols(h, r, [[1, 2, 3, 4], [5, 6, 7, 8]])
    out.append(tbl(parts[0][0], parts[0][1], widths=[26, 40, 36, 38, 36], font="cell_small"))
    out.append(H3("Table 6.1  Workflow capability by system (part 2: alerts, exception reports, price, source)"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[26, 32, 44, 40, 34], font="cell_small"))
    out.append(H2("No vendor sells the exception report, and the evidence firms misconfigure is consistent"))
    out += bullets([
        "Clio publishes only a correlation: 'growing firms are 18 percent more likely to adopt key workflows' and are '2x more likely to use automation' ([PR Newswire, 16 Oct 2025](@prn_science) [vendor]), never a base rate for task-template or custom-field use.",
        "The insurer ALPS: 'routine errors, especially calendaring and the filing and service of documents, remain a primary cause of claims despite widespread adoption of legal technology'; 'technology is not a substitute for process'; "
        "'software can't fix inconsistent routines, ineffective internal processes, or poor documentation habits' ([ALPS, 21 Jul 2026](@alps)).",
        "Oregon's PLF sets the operational rule an audit would test: 'No file should ever be set aside without a reminder date on it or be tickled for more than 60 days', review all files at least every 30 days, 'Double-checking of all entries', and 'DO NOT assume anything. Verify it.' "
        "([OSB PLF tickler systems](@plf_tickler); [OSB PLF docketing checklist](@plf_docket)).",
        "Users from the inside: 'the reporting is not remotely close to be as great as they say' [user, 19 Sep 2026]; 'Clio creates duplicate invoices' and 'some trust activity is sent to QBO as a triple entry' [user, 21 Aug 2026]; "
        "'It's basically sink or swim, based on your own level of accounting knowledge' [user, 11 Jul 2026]; 'Grow and manage do not work together at all' and 'We got a 34% increase in per month per user increase two months ago' [user, 17 Aug 2026] ([Trustpilot](@trustpilot_clio)); "
        "'a firm will need to spend time getting set-up' and 'not all of your needed functionality will be included in Clio's price' ([Lawyerist](@lawyerist_clio)).",
        "The Grow-to-Manage conversion is a documented data-loss point: if sync was not previously enabled 'only the contact set as the default client in Clio Grow will be converted', related contacts are dropped, and 'matter status, assigned-to, estimated case value, emails, and tasks' do not convert "
        "([Clio Grow conversion help](@clio_grow_conv) [snippet]).",
    ])
    out.append(H2("The consultant market is real but opaque on price"))
    out += bullets([
        "Clio's Certified Consultant programme page and directory were blocked, so the count and any Clio-published rates are unverified; visible self-listed entries include Big Mode Consulting (DC, '50+ firms' moved to Clio), XPRTS (Austin, 'fractional operations leadership'), "
        "LawTech Partners (Florida, 'Clio Gold Partner') and Apply Compliance Today (Surrey, UK); Clio states it 'doesn't review or guarantee any advisor's listing' ([Big Mode](@bigmode); [Apply Compliance Today](@act)).",
        "Third-party estimates: Clio live training '$150 to $300 per hour', data migration '$500 to $5,000' ([aimadefor, Jul 2026](@aimadefor) [unverified against Clio]); a one-time $399 Grow set-up fee is 'optional for accounts with four or fewer users' ([Costbench](@costbench_grow)).",
        "The closest published 'health check' is Jayva Global, a LEAP consultancy (Boston, Manchester, Cumbria, Dublin, Auckland): 'Are you wasting your software investment? Don't let your LEAP system drift!'; covers 'Underused features and tools', 'Data quality, reporting and operational visibility', "
        "'Consistency across teams and departments' and 'Legal accounting processes and compliance controls'; 'quick wins and a clear roadmap'; no price or duration ([Jayva](@jayva)).",
        "LEAP's UK certified-partner directory lists only <b>12 partners (7 consultancies, 3 bookkeepers, 2 IT firms)</b>; certification 'can be finished within 2 weeks', after which 'LEAP refers new clients to you' ([LEAP partner directory](@leap_dir); [LEAP Partner Network](@leap_pn)).",
        "Filevine runs a formal Certified Implementation Partner tier with a published partner rate card: Sprint packages for 1-20 users at <b>$1,750 to $7,500</b>, Launch packages at <b>$12,500 to $32,500</b> over 4-6 months, and 'Reporting setup', Workato and LOIS automation modules at <b>$2,500 each</b> "
        "([Oktopeak, Oct 2026](@oktopeak) quoting [Vineskills](@vineskills)).",
        "Upwork shows the same demand at freelance prices: a Clio dashboard and automation developer post at $15-$35 an hour, 'Filevine Developer – Workflow Optimization &amp; Dashboard Development', a firm seeking 'a primary administrator for FileVine', a '27 Best Freelance Clio Specialists' hire page "
        "([Upwork automation job](@upwork_auto); [Upwork Filevine developer job](@upwork_fv)); employment benchmarks put a 'Filevine Administrator' at $45 an hour and Filevine-tagged jobs at an average $26.34 an hour ([Built In](@builtin_fv); [ZipRecruiter](@zip_fv)).",
        "Fiverr lists Clio set-up gigs at $10 to $75 with scopes such as 'custom legal intake forms and workflows, calendar, tasks, and document automation' and 'matter creation workflows, automatic task assignments'; some sellers 'describe themselves as law students or early-level sellers' ([Fiverr Clio automation](@fiverr_clio) [snippet]).",
    ])
    out.append(H3("Table 6.2  Consultant and freelance price points"))
    h, r = T(6, 1)
    out.append(tbl(h, r, widths=[60, 72, 44]))
    out.append(H2("UK: the audit function is split three ways"))
    out += bullets([
        "Vendors (Access, Osprey, LEAP) bundle implementation, training and file audits; certified consultants sell implementation, training and workflow build; strategic consultancies such as Baskerville Drummond (independent reviews and system selection, consultants who 'have held board-level positions in law firms') "
        "and 3Kites ('65+ system selection engagements', 'No vendor bias') sell board-level reviews on bespoke quotes ([Baskerville Drummond](@baskerville); [3Kites](@3kites)).",
        "A configuration-validation audit for a 1-30 lawyer firm sits between the certified-consultant and strategic tiers and was not clearly occupied by anyone fetched.",
    ])
    return out


def section_7(CH):
    out = chapter(7, SEC[7]["title"],
                  "The practitioner checklists converge on one opening sequence and one set of failure points, and the control point they name is the transfer from intake to the case manager. "
                  "Every checklist assumes the firm already knows every provider; none has a step that reconciles the provider list against what the records mention.")
    out.append(H2("The opening sequence the checklists converge on"))
    out += bullets([
        "CASEpeer (updated September 2026): gather client information and screen against acceptance criteria; sign the retainer; execute HIPAA and records-release authorisations; open the claim and enter client, incident and insurance details; letter of representation to all known insurers 'within 24 to 48 hours'; "
        "identify the statute of limitations and calendar it immediately; request the police report; preserve evidence; spoliation letters; identify witnesses; pull policy limits; track treatment and flag gaps; 'request records and bills from every provider and log them as they arrive'; "
        "check Medicare and Medicaid; check in with the client about every 14 days; identify every lienholder and request itemised lien statements early because 'they often take weeks to arrive'; run a 30/60/90-day audit of SOL calendared, records current and lien statements outstanding. "
        "The checklist 'does not include a separate medical provider list step' and 'does not assign owners to these steps' ([CASEpeer](@casepeer_check) [vendor]).",
        "Oregon's PLF adds the employment and tax authorisation, Medicare and Medicaid notice, uninsured-motorist notice in 'phantom vehicle' cases, records 'including treatment prior to the litigated incident', 'a reminder well in advance of the timeline', and "
        "'have someone assigned to screen incoming mail for calendaring needs BEFORE the mail is distributed' ([OSB PLF PI checklist](@plf_pi); [OSB PLF docketing](@plf_docket)).",
        "Lawyers Mutual: an intake checklist should capture 'important dates and deadlines', 'someone should be responsible for making sure it happens', and 'client intake is too important to leave to chance' ([Lawyers Mutual NC, 29 Sep 2026](@lm_intake)).",
    ])
    out.append(H2("The failure points, in practitioners' own words"))
    out.append(quote_block("A PI case 'most often fails because a lien wasn't tracked, a treatment gap went unexplained, or a statute of limitations deadline slipped through the cracks during a handoff'; unexplained treatment gaps are 'one of the fastest ways to lose value'",
                           "[CASEpeer](@casepeer_check) [vendor]"))
    out.append(quote_block("Providers 'may overlook requests if not reminded'; 'transcription mistakes, missing pages, or misfiled documents' compromise evidence",
                           "[CASEpeer medical records, Sep 2026](@casepeer_med) [vendor]"))
    out.append(quote_block("'Every provider has slightly different authorization requirements'; 'a missing field or expired date gets your record request rejected and might even reset the clock entirely'; 'fax-dependent workflows add days'; "
                           "common gaps on receipt are missing billing records, missing imaging pages and reports cut off mid-document", "[CloudLex](@cloudlex_rec) [vendor]"))
    out.append(quote_block("'A rejected authorization resets the clock'; late requests are 'the most common source of preventable delays'", "[ChartRequest](@chartrequest) [vendor, snippet]"))
    out.append(quote_block("'Chasing medical records' is 'the most failure-prone phase of pre-lit'; 'if a client is calling you for a status update, you've already failed'; 'send the demand too early and you cap the case at yesterday's bills'",
                           "[Finch guides](@finch_guides) [vendor]"))
    out.append(quote_block("Files fall 'through the cracks because nothing has happened to create any activity on the file'", "[OSB PLF tickler](@plf_tickler)"))
    out.append(quote_block("'Medical records, bills, and other documents are essential to the case but hard to track down'; the report exists because tracking requests 'matter by matter' fails",
                           "[Smokeball, Jan 2023](@smokeball_req) [vendor]"))
    out.append(H2("The open sub-problem: the provider list itself"))
    out += bullets([
        "Every checklist assumes the firm already knows every provider; none has a step that says 'reconcile the provider list against the providers, referrals and facilities named inside the records and bills that have arrived'.",
        "Vendors cluster around the adjacent problem, 'missing records' (a known provider's records have not come) or a chronological 'treatment gap'; <b>none of the eight vendor pages read claims to detect a provider referenced in received records that was never requested</b>.",
        "EvenUp: 'Recover $1,500 in missing documents on average before case value drops', a 'missing docs check', care timelines, treatment-gap flags, 'about 20% of missed appointments going unnoticed without the product', Communication Agents that automate 'record follow-ups'; missing providers 'not mentioned' "
        "([EvenUp](@evenup); [EvenUp Medical Management](@evenup_med) [vendor]).",
        "Supio: chronologies find 'missing documents' and 'missing bills', 'proactively spot case signals, like gaps or opportunities', 'human subject matter experts verify every chronology'; the Case Review Agent 'shows which information is present and which still needs to be collected from the client'; missing providers 'not addressed' "
        "([Supio chronologies](@supio_chron); [Supio March 2026](@supio_mar) [vendor]).",
        "Finch, a service rather than software: requests records 'in parallel with treatment', reports '14-day average time to records and 80% received within 30 days', '94% first-pass completeness' and a '94-day median time to demand'; 'says nothing about detecting new referrals or additional providers inside received records' ([Finch](@finch) [vendor]).",
        "Eve: '1200+ firms', nightly audits for 'buried injuries, treatment gaps', agents 'chasing records' ([Eve Legal](@eve) [vendor]). Wisedocs (insurer and defence customers): flags 'missing records', 'provider recurrence' and 'High-Risk Providers' ([Wisedocs](@wisedocs) [vendor]). "
        "DigitalOwl: '97% or higher' accuracy, 'up to 72% reduction in review time' for insurers ([DigitalOwl](@digitalowl) [vendor]).",
        "No vendor publishes a price; all are 'case-based' or 'per case'. No independent review of any of them could be read (G2, Capterra and TrustRadius blocked), so every figure is vendor-authored or a vendor-selected testimonial.",
    ])
    out.append(H3("Table 7.1  PI vendors: claims, crash report, provider detection, pricing, reviews"))
    h, r = T(7, 0)
    out.append(tbl(h, r, widths=[20, 62, 22, 28, 22, 22], font="cell_small"))
    out.append(source_line("Sources: EvenUp [%d]; EvenUp Medical Management [%d]; EvenUp Lerner &amp; Rowe [%d]; Supio [%d]; Supio chronologies [%d]; Finch [%d]; Eve [%d]; Wisedocs [%d]; DigitalOwl [%d]; CASEpeer pricing [%d]; Filevine [%d]; "
                           "TrustRadius Filevine [%d]; CloudLex [%d]; Case Status [%d]. All rows are vendor claims unless marked." % tuple(ref(u) for u in (
                               "https://www.evenuplaw.com/", "https://www.evenuplaw.com/products/medical-management", "https://www.evenuplaw.com/blog/lerner-rowe-faster-cases-efficiency-settlements/",
                               "https://www.supio.com/", "https://www.supio.com/medical-chronologies", "https://www.finchlegal.com/", "https://www.eve.legal/", "https://www.wisedocs.ai/",
                               "https://www.digitalowl.com/", "https://www.casepeer.com/pricing/", "https://www.filevine.com/", "https://web-v2.prod.trustradius.com/products/filevine/reviews/all",
                               "https://www.cloudlex.com/", "https://www.casestatus.com/"))))
    out.append(H2("What a daily 'missing-task' check on a PI practice would have to test"))
    out.append(Paragraph("Read together, the checklists give this list; none of the systems in section 6 produces it natively.", S["body"]))
    out += bullets([
        "retainer signed; HIPAA and employment authorisations on file;",
        "letter of representation sent to every known insurer within 48 hours;",
        "statute of limitations and any tort-claim-notice date entered with an advance reminder;",
        "police report requested and version checked; policy limits requested; spoliation letters sent;",
        "Medicare, Medicaid and uninsured-motorist notices sent;",
        "every provider on the list with a request date, a follow-up date inside the firm's interval and a received date;",
        "lien statements requested; last client contact within 14 days;",
        "no matter without a next reminder date within 60 days.",
    ], style="bullet2")
    out.append(Paragraph("The insurer data frames all of this as a growing 'administrative error' risk, not an IT project; the control point both CASEpeer ('during a handoff') and the PLF ('double-checking of all entries') name is the transfer from intake to the case manager.", S["body"]))
    return out


def section_8(CH):
    out = chapter(8, SEC[8]["title"],
                  "The two products sell to different buyers; the overlap zone is the 5-30 lawyer PI firm. Clio publishes a starting price and hides the rest; Filevine publishes nothing and sells implementation through partners. "
                  "User complaints about Clio have been stable for seven years and shifted in 2026 toward commercial behaviour; Filevine's are mostly delivery and people problems.")
    out.append(H2("Different buyers"))
    out += bullets([
        "Filevine has 'historically' sold to 'mid-sized plaintiff firms' with a focus on 'high-volume plaintiff practices', had about 3,400 customers in mid-2024 and 'nearly 6,000' by September 2025, ARR estimated at $250 million ([Sacra, May 2026](@sacra) [3p estimate]). "
        "Lawyerist: 'personal-injury firms and other process-oriented practices will likely find the best results with Filevine'; it 'needs more setup effort than many competitors' and is 'probably more than solo practices need' ([Lawyerist Filevine](@lawyerist_fv)); "
        "a 2026 review says it is not for 'solo and 2-3 attorney firms starting out' or 'firms with limited time for onboarding', and implementation 'is a multi-week project (4-12 weeks) requiring partners' ([Dupple, May 2026](@dupple) [3p]).",
        "Clio Manage 'is a good fit for most solo to medium-sized firms' ([Lawyerist Clio](@lawyerist_clio)), crossed <b>$500 million ARR in May 2026</b>, serves 'hundreds of thousands of legal professionals in 130+ countries' ([Sacra](@sacra)), and added a Personal Injury add-on in October 2023 "
        "'specifically designed for a PI lawyer's distinct workflows' ([LawNext, 9 Oct 2023](@lawnext_pi)).",
        "Switching stories concentrate in the overlap: a 10-staff Connecticut PI firm moved from 'Dropbox and Clio' because 'I remember having a lot of frustration with Clio and thinking \"This really isn't for injury firms\"' ([Filevine case study](@fv_ct) [vendor]); "
        "a Capterra reviewer who moved from Clio called the Filevine rollout 'absolute chaos', 'went live before the system was finished' and 'wished they'd stayed with Clio' ([Capterra Filevine p2](@capterra_fv2) [user, snippet, undated]).",
    ])
    out.append(H2("Real pricing is harder to pin down than either website suggests"))
    out += bullets([
        "A price tracker logged Clio EasyStart at $49, Essentials $89 and Advanced $119 per user per month (annual) in June 2026, with the top tier, Clio Grow, Manage AI and the PI add-on all 'Contact'; it recorded a Q2 2025 rise (EasyStart $39 to $49, up 25.6%), the removal of a 25% first-year discount in Q3 2025, "
        "prices hidden behind contact buttons from 23 March 2026, and a rename to Starter / Core / Signature / Elite on 5 August 2026 ([PricingSaaS Clio](@pricingsaas) [3p tracker]).",
        "Clio Grow is '$59/user/month', 'not available with Clio's EasyStart plan' and included only on the top tier ([Lawyerist Clio Grow](@lawyerist_grow)); 'Clio does not publish a way to buy Clio Grow without Clio Manage' ([Layer3Labs, 22 Sep 2026](@layer3)). "
        "Payments about 2.9% plus $0.30 per card transaction; e-signatures capped at 3 a month on EasyStart and 15 on Essentials ([Costbench Clio](@costbench_clio) [3p]); two-way texting for Grow leads needs a third-party app at $35 or $139 a month ([Clio app directory, Falkon](@falkon); [Text Request](@textrequest)).",
        "The commercial edge in users' words: 'charging me $2,842/yr for two seats' ([TrustRadius](@tr_clio) [user, 9 Aug 2024]); 'They renewed 4 licenses that I had inactive and would not refund after being a customer for over 10 years' ([Trustpilot](@trustpilot_clio) [user, 30 Jun 2026]); the 34% per-user rise (section 6). "
        "In the UK Clio sells at <b>£49 per user per month annual or £59 monthly with 'no contract'</b> ([Clio UK vs LEAP](@clio_uk_leap) [vendor]).",
        "Filevine 'does not post prices on the website' and sells AI analysis, demand drafting, document management, lead management and e-signatures as separate add-ons ([Lawyerist Filevine](@lawyerist_fv)); third-party estimates: '$49 to $87 per user per month' base, '$80-$120' small firms, '$100-$200' with modules, "
        "onboarding '$1,000-$10,000+', Lead Docket text lines '$20 per month per text line number', automations '$100 per 500 actions per user per month beyond 500', data kept only 30 days after termination ([Oktopeak, 2 Oct 2026](@oktopeak); [Dupple](@dupple) [3p]).",
        "Oktopeak's worked example for a 15-user firm over three years: <b>$32,710 to $64,480 before LOIS AI, Lead Docket and renewal increases</b> ([Oktopeak](@oktopeak)). Two reviewers in 2025 reported '$60,000' spent on Filevine services, one saying 'Nothing was deployed to production' ([SoftwareFinder](@softwarefinder) [user, Jun and Jul 2025]); "
        "a 2023 reviewer who 'tried to buy out my three year contract' was 'threatened with arbitration in Ohio by their legal department' ([Lawyerist Filevine](@lawyerist_fv) [user, 28 Sep 2023]). One hard public number: Marin County, California pays <b>$67,944 a year</b> for a three-year Filevine subscription with no auto-renewal ([CivicIQ](@civiciq)).",
    ])
    out.append(fig_image(*CH["prices"]))
    out.append(H3("Table 8.1  Cost items, Clio against Filevine"))
    h, r = T(8, 0)
    out.append(tbl(h, r, widths=[26, 56, 56, 38], font="cell_small"))
    out.append(H2("What each solves well, in users' words"))
    out += bullets([
        "Clio's praise clusters on money and speed to value: 'billing, time tracking, and centralized matter workflows are commonly highlighted wins' and 'ease of use and fast onboarding' ([rfp.wiki Clio](@rfp_clio) [3p aggregator]); 'Their support is second to none' ([Lawyerist](@lawyerist_clio) [user, Mar 2018]); "
        "'I love how I can streamline the intake process in Clio Grow and then hand off the client seamlessly' ([Capterra Clio](@capterra_clio) [user, 2024, snippet]); 'Pricing seems quite fair and reasonable to me' ([Trustpilot](@trustpilot_clio) [user, 23 Aug 2026]).",
        "Filevine's praise clusters on case control: 'Filevine feels more like a living/breathing system, that helps move cases forward', 'nothing is as customizable as Filevine', 'DOCUMENT GENERATION!' ([Lawyerist Filevine](@lawyerist_fv) [users, Mar 2020]); "
        "'the fact that I can do all aspects of case management from one platform' ([Capterra Filevine](@capterra_fv) [user, snippet]); in August 2026 the 'report builder and report generation, including real-time updates', letter generation, 'medical summaries and chronologies' and task tracking ([TrustRadius Filevine](@tr_fv) [users, Aug 2026]).",
    ])
    out.append(H2("What users say Clio does not solve (stable for seven years)"))
    out.append(H3("Table 8.2  Dated Clio complaints"))
    h, r = T(8, 1)
    out.append(tbl(h, r, widths=[22, 32, 86, 36]))
    out.append(P("Overall scores: Capterra 4.7 from about 1,740 reviews, G2 about 4.6-4.7, TrustRadius 8.1/10 from 117, Trustpilot 3.6 from 297 ([rfp.wiki](@rfp_clio); [Trustpilot](@trustpilot_clio)); the Trustpilot page skews negative by self-selection."))
    out.append(H2("What users say Filevine does not solve (delivery, people, reports, AI quality)"))
    out.append(H3("Table 8.3  Dated Filevine complaints"))
    h, r = T(8, 2)
    out.append(tbl(h, r, widths=[22, 32, 86, 36]))
    out += bullets([
        "Overall scores: Capterra 4.4 from about 286, G2 4.6-4.7 from about 300, TrustRadius 8.4/10 from 76, Lawyerist 4.3 editorial with cons 'Complex', 'Basic Task Management', 'No Client Portal' ([rfp.wiki Filevine](@rfp_fv); [Lawyerist Filevine](@lawyerist_fv)).",
        "Non-PI users say the templates assume plaintiff litigation ('useless for immigration cases'; built 'for lawyers, not investigators'), that billing and QuickBooks depth lag ([Capterra Filevine](@capterra_fv) [snippet]), and that there was no native client portal (the partner directory lists CaseStatus) ([Filevine partners](@fv_partners)); "
        "Filevine added timekeeping, invoicing and payments in 2023 for 'non-contingency practices such as criminal defense, family law, bankruptcy, estate, immigration and corporate law' ([Filevine news](@fv_news) [vendor]).",
        "PI users on Clio historically lacked provider tracking, lien tables and settlement maths, now in the paid PI add-on with provider cards in a 'Medical records subtab' and an 'Other liens table' on the 'Settlement subtab', 'not available for all Clio subscription plans' ([Clio help 18350703919899](@clio_help_pi) [vendor, snippet]), "
        "and still lack repeating fields and contact-based templates; Lawyerist's Grow verdict is 'Not for PI Intake' ([Lawyerist Grow](@lawyerist_grow)).",
    ])
    out.append(H2("Clio Grow versus Lead Docket: a general intake add-on against a PI-grade intake system"))
    out += bullets([
        "Grow: custom intake forms with 'conditional logic to adapt questions based on prior answers', a Kanban pipeline, HelloSign e-signature on engagement letters 'autofilled with intake data', conflict checks across Grow and Manage, a scheduler and source attribution ([Clio online intake forms](@clio_intake) [vendor]; [Layer3Labs](@layer3)).",
        "But its text message 'is a no-reply notification, and your client cannot respond to it' ([Clio help 14164457325595](@clio_help_text) [vendor, snippet]); 'follow-up sequences are linear (not branching)' and 'reporting on pipeline stage conversion is basic' ([Layer3Labs intake roundup, Jul 2026](@layer3_intake) [3p, snippet]); "
        "the form builder could not link Dropdown, Contact Select, Email, Integer, Money or Website custom fields to questions as of 2022 ([Clio Cloud Conference 2022 PDF](@clio_conf22)); users: 'the reports are not accurate', 'when booking consultations for repeat callers, Grow duplicates the contact. There isn't an easy way to merge' "
        "([G2 Clio Grow](@g2_grow) [user, snippet]); 'you cannot delete contacts in bulk in Clio Grow' ([Clio Grow data import](@clio_grow_import) [snippet]).",
        "Lead Docket captures leads 'through web forms, web chat, text, or call service', works with answering services and call-tracking numbers, tracks referral partners, reports 'Revenue by marketing source, conversion rates, lead volume over time, referral fees', runs two-way SMS on firm numbers (1,000 texts and 300 voice minutes a month each), "
        "assigns Vinesign signature tasks by lead status with a retainer payment attached, and maps lead status to Filevine phases, though phase mapping 'has to be enabled by Lead Docket support first' ([Lead Docket features](@ld_features); [Phase Mapping](@ld_phase); [Vinesign article](@ld_vinesign) [vendor, snippets]).",
        "Its public complaints are sparse: 'some clients can get past mandatory fields without issue, leaving the firm chasing vital information' ([Software Advice AU](@sa_au) [user, snippet]) and the add-on cost; it rates 4.9 on Capterra from 62 reviews but has '0 Reviews' of text on TrustRadius ([Capterra CA compare](@capterra_ca); [TrustRadius Lead Docket](@tr_ld)).",
    ])
    out.append(H3("Table 8.4  Clio Grow against Lead Docket, feature by feature"))
    h, r = T(8, 3)
    out.append(tbl(h, r, widths=[26, 75, 75], first_col_bold=True))
    out.append(H2("The UK mirror: Clio UK against LEAP, where the gap is contract and exit terms"))
    out += bullets([
        "LEAP serves 'over 26,000 legal professionals from more than 2,700 UK law firms' ([Law Society LEAP offer](@ls_leap)), rates 4.2 on Capterra UK against Clio's 4.7 ([Capterra UK compare](@capterra_uk)).",
        "2026 UK reviews: 'Leap makes it purposefully difficult for you to move data around' (29 Sep 2026), '1 person covering support for the whole of the UK' (20 Jul 2026), 'Annual prices increases, very expensive and very little help' (3 Jun 2026), 'once you signed up your trapped' (4 Mar 2026) ([Trustpilot LEAP UK](@trustpilot_leap) [users]); "
        "a sole practitioner 'tied in for 3 yrs' could not get client files back ([Software Advice FR LEAP](@sa_fr_leap) [user, snippet]).",
    ])
    out.append(H2("Six needs recur in the reviews of both products"))
    out.append(Paragraph("Both vendors sell that layer back as add-ons, partners or AI, which is why consultants, Zapier and spreadsheets persist on both sides.", S["body"]))
    h, r = T(8, 4)
    out.append(KeepTogether([H3("Table 8.5  Gaps common to Clio and Filevine"),
                             tbl(h, r, widths=[40, 68, 68], first_col_bold=True)]))
    out.append(source_line("Sources: TrustRadius Clio [%d]; Trustpilot Clio [%d]; G2 Clio Grow [%d]; TrustRadius Filevine [%d] and p2 [%d]; SoftwareFinder Filevine [%d]; Lawyerist Filevine [%d]; Oktopeak [%d]; Filevine support, phases [%d]; Filevine partners [%d]; Zapier community [%d]." % tuple(
        ref(u) for u in ("https://web-v2.prod.trustradius.com/products/clio/reviews/all", "https://www.trustpilot.com/review/clio.com", "https://g2.com/products/clio-grow/reviews",
                         "https://web-v2.prod.trustradius.com/products/filevine/reviews/all", "https://web-v2.prod.trustradius.com/products/filevine/reviews/all?page=2",
                         "https://softwarefinder.com/legal/filevine-software/reviews", "https://lawyerist.com/reviews/law-practice-management-software/filevine/",
                         "https://oktopeak.com/blog/filevine-pricing-real-cost-tco/", "https://support.filevine.com/hc/en-us/articles/360004186471", "https://filevine.com/partners/directory",
                         "https://community.zapier.com/how-do-i-3/avoid-creating-duplicate-contacts-in-clio-manage-13442"))))
    return out


# ==========================================================================
# Content, part C: section 9 (gap cards), 10, 11, conclusion, sources
# ==========================================================================
U.update({
    "rlegaltech": "https://www.rlegaltech.com/jobs/",
    "axial": "https://axialsearch.com/insights/ai-engineering-jobs",
    "itjobswatch": "https://www.itjobswatch.co.uk/jobs/london/legal%20technology%20specialist.do",
    "glassdoor_le": "https://www.glassdoor.co.uk/Job/legal-engineer-jobs-SRCH_KO0,14.htm",
    "reed_lt": "https://www.reed.co.uk/jobs/legal-tech-jobs",
    "totaljobs": "https://www.totaljobs.com/jobs/legal-tech",
    "legalio": "https://www.legal.io/jobs/5787729/Full-time/Legal-Engineer/Remote",
    "nonbillable": "https://www.nonbillable.co.uk/posts/legal-careers-big-law-ai-working-at-harvey-legora-luminance",
    "lawfuel": "https://www.lawfuel.com/ai-companies-poach-biglaw-talent-h1-2026-lateral-report/",
    "everlaw": "https://www.everlaw.com/careers/4648836006/",
    "aivortex": "https://www.aivortex.io/legal/guides/ai-legal-career-paths-2026/",
    "zip_visa": "https://www.ziprecruiter.com/Jobs/Artificial-Intelligence-Engineer-Visa-Sponsorship",
    "al_q1": "https://www.artificiallawyer.com/2026/04/13/legal-tech-raised-2-3b-in-q1-26-but-3-companies-dominate/",
    "cnbc": "https://www.cnbc.com/2026/03/25/legal-ai-startup-harvey-raises-200-million-at-11-billion-valuation.html",
    "lawnext_trends": "https://www.lawnext.com/2026/01/the-10-legal-tech-trends-that-defined-2025.html",
    "courtcast": "https://courtscast.com/law-firms-step-up-tech-hiring-as-ai-race-moves-deeper-into-legal-work/",
    "usnews": "https://money.usnews.com/investing/news/articles/2026-07-13/thomson-reuters-to-cut-small-number-of-engineering-jobs",
    "tnw": "https://thenextweb.com/news/thomson-reuters-engineering-layoffs-ai",
    "upwork_bot": "https://www.upwork.com/hire/ai-chatbot-specialists/",
    "upwork_clio": "https://www.upwork.com/hire/themis-solutions-clio-freelancers/",
    "fiverr_auto": "https://www.fiverr.com/gigs/legal-automation",
    "fiverr_cost": "https://www.fiverr.com/resources/guides/costs/ai-automation-experts",
    "pph_ai": "https://www.peopleperhour.com/freelance-jobs/artificial-intelligence/artificial-intelligence-chatbot-development",
    "lazige": "https://lazige.agency/guides/ai-consultant-pricing-guide-uk",
    "gigup": "https://giguphq.com/blog/rag-chatbot-development-jobs-on-upwork-how-to-find-better-ai-projects-faster",
    "pivot180": "https://pivot180.ai/resources/ai-consultant-for-law-firms-cost-process-how-to-choose-2026",
    "consultingdemand": "https://consultingdemand.com/blog/consultant-hourly-rates/",
    "clutch": "https://clutch.co/it-services/legal-industry",
    "marin": "https://marin.granicus.com/MetaViewer.php?view_id=&clip_id=13163&meta_id=1442479",
    "clio_li": "https://ca.linkedin.com/company/clio---cloud-based-legal-technology",
    "clio_ccc": "https://www.clio.com/partnerships/certified-consultants/",
    "hunnings": "https://hunningsconsultancy.co.uk/leap-assistance/",
    "aba_tt": "https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-technology-and-training/",
    "aba_budget": "https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-budgeting-and-planning-techreport/",
    "lawnext_aba": "https://www.lawnext.com/2025/03/aba-tech-survey-finds-growing-adoption-of-ai-in-legal-practice-with-efficiency-gains-as-primary-driver.html",
    "aba_ai": "https://www.americanbar.org/groups/law_practice/resources/tech-report/2024/2024-artificial-intelligence-techreport/",
    "clio_2025ss": "https://www.clio.com/resources/legal-trends/2025-solo-small-firm-report/",
    "ncbar": "https://www.ncbar.org/nc-lawyer/2026-05/by-the-numbers-what-surveys-show-about-law-firm-ai-adoption/",
    "tryclean": "https://www.tryclean.ai/solutions/legal/law-firm-technology",
    "lawyerai": "https://www.lawyerai.directory/blog/legal-ai-budget-allocation-2026",
    "leanlaw_clio": "https://www.leanlaw.co/blog/the-complete-guide-to-clio-100-essential-questions-answered-for-mid-sized-law-firms-2025/",
    "aba_clients": "https://www.americanbar.org/groups/law_practice/resources/law-technology-today/2025/how-to-get-clients-as-a-lawyer-11-steps-to-success/",
})

GAP_FIELDS = ["Problem", "Who has it", "Evidence", "Their words", "How they handle it today",
              "Vendors already covering it", "Automatable?", "What the reader would need to learn"]


def _badge_values(rank_row):
    signal, cov, auto = rank_row[2], rank_row[3], rank_row[6]
    s = signal.split(":")[0].strip().lower()
    sig = "strong" if s.startswith(("very high", "high")) else "medium"
    c = cov.split(":")[0].strip().lower()
    if c.startswith(("weak", "medium-weak", "unknown")):
        cv = "weak"
    elif c.startswith("very strong"):
        cv = "crowded"
    else:
        cv = "partial"
    a = auto.split(":")[0].split(";")[0].strip().lower()
    au = a.split()[0] if a else "partly"
    return sig, cv, au


def _chip(label, value, warm):
    txt = "<b>%s:</b> %s" % (esc(label), esc(value))
    t = Table([[Paragraph(txt, S["badge"])]], colWidths=[(FRAME_W - 2 * 4 * mm) / 3])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_WARM_TINT if warm else C_ZEBRA),
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, C_WARM if warm else C_LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def gap_card(rank, title, country, fields, badges):
    sig, cv, au = badges
    head = Table([[Paragraph(str(rank), S["card_rank"]),
                   Paragraph(inl(title, refs=False), S["card_title"]),
                   Paragraph("<b>%s</b>" % esc(country), ParagraphStyle("cc", parent=S["badge"], textColor=white, alignment=2))]],
                 colWidths=[13 * mm, FRAME_W - 13 * mm - 30 * mm, 30 * mm])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    chips = Table([[_chip("Problem signal", sig, sig == "strong"), "",
                    _chip("Vendor coverage", cv, cv == "weak"), "",
                    _chip("Automatable", au, False)]],
                  colWidths=[(FRAME_W - 8 * mm) / 3, 4 * mm, (FRAME_W - 8 * mm) / 3, 4 * mm, (FRAME_W - 8 * mm) / 3])
    chips.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    rows = []
    for label in GAP_FIELDS:
        content = fields.get(label, "")
        rows.append([Paragraph(esc(label), S["cell_label"]), Paragraph(inl(content), S["card_cell"])])
    body = Table(rows, colWidths=[34 * mm, FRAME_W - 34 * mm], splitByRow=1)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.3, C_GRID),
          ("LINEBELOW", (0, -1), (-1, -1), 0.8, C_ACCENT),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
          ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]
    for i in range(len(rows)):
        if i % 2 == 1:
            st.append(("BACKGROUND", (0, i), (-1, i), C_ZEBRA))
    body.setStyle(TableStyle(st))
    return [KeepTogether([head, chips, body]), Spacer(1, 7 * mm)]


def section_9(CH):
    out = chapter(9, SEC[9]["title"],
                  "Each gap is scored on two things: how strong and how recent the problem signal is (regulator findings, insurer claims data, dated user complaints, job-ad and freelance demand), "
                  "and how weak the vendor coverage is (whether a named product claims to solve the exact sub-problem and whether any independent review confirms it). A third column marks fit with a "
                  "self-hosted or private-data angle, strongest where the work touches client files that regulators say must not leave the firm.")
    out.append(H3("Table 9.1  The ranking, with the three crowded problems at the end"))
    h, r = T(9, 0)
    out.append(tbl(["#"] + h[1:], r, widths=[13, 34, 36, 39, 19, 14, 21], font="cell_small"))
    out.append(fig_image(*CH["gap_matrix"]))
    out.append(H2("The twelve gap cards"))
    out.append(Paragraph("Every card has the same eight fields in the same order. The three badges summarise the ranking table: problem signal (strong = very high or high), vendor coverage "
                         "(weak = weak, medium-weak or unknown; partial = medium), and the report's own word on automation (fully, largely, partly).", S["body"]))
    titles = SEC[9]["h3"]
    for i, (title, table) in enumerate(zip(titles, SEC[9]["tables"][1:13])):
        m = re.match(r"^Gap (\d+)\.\s+(.*)$", title)
        rank = int(m.group(1))
        name = m.group(2)
        fields = {row[0].strip(): row[1] for row in table["rows"]}
        rank_row = r[rank - 1]
        out += gap_card(rank, name, rank_row[5], fields, _badge_values(rank_row))
    out.append(H2("Crowded areas that are not gaps"))
    out += bullets([
        "<b>Intake call answering and lead follow-up</b> has the loudest problem signal of all (40% of calls answered, 33% of emails, 48% unreachable) but also the thickest vendor layer: answering services, Supio Intake (24/7 voice intake that scores leads and syncs to the CMS [vendor]), "
        "Eve Intake ('signs the client before the call ends' [vendor]), Lead Docket, CloudLex's Lexee, EvenUp's carrier-calling agents, Clio's 'after-hours AI phone and email answering' and the chatbot builders on Upwork at $1,200-$4,500 a project; only 7% of firms used a chatbot in 2024, so adoption is low, but the supply is not thin.",
        "<b>Medical chronologies and demand letters</b> are the most heavily funded corner of legal AI (EvenUp '$150M Series E at $2B+', Eve '$103M Series B', Supio, Parrot/MedChron, Wisedocs, DigitalOwl, Finch); user complaints are about quality ('entries from the early 1900s', '72 hrs'), "
        "which is a reason to study the space, not to enter it from scratch; the $150 Upwork consultation on 'how a chronology is built and priced' shows newcomers trying exactly that.",
        "<b>Dictation and transcription</b> has a real but small signal (7 of 40 UK ads, 'done in the Microsoft cloud', 'not always 100% accurate') and mature products, though the cloud-processing complaint is itself a small self-hosting signal.",
    ])
    return out


def section_10(CH):
    out = chapter(10, SEC[10]["title"],
                  "The employed path is small, concentrated and screened hard; the freelance path is open, cheap at the marketplace tier and expensive only inside consultancy and vendor-certification tiers. "
                  "No source measures time to first revenue or competition directly, so those criteria rest on proxies; the arithmetic comparisons are the researcher's calculations on cited figures.")
    out.append(H2("Employed demand: a dated snapshot"))
    out += bullets([
        "A legal-tech vendor job aggregator showed <b>2,539 open postings across 133 vendors on 23 September 2026, of which 614 are engineering</b>; only 19% of vendors publish pay; Harvey alone 311 postings (12% of the category), Clio 123, Filevine 105 ([rlegaltech.com/jobs](@rlegaltech)).",
        "The general US AI-engineering market had 43,500 postings analysed between January and July 2026; professional services the top hiring sector (28%); 47% of roles at employers with 10,000+ staff ([Axial Search](@axial)).",
        "Dedicated UK counts for the exact titles are tiny: 4 permanent 'Legal Technology Specialist' vacancies in London in the six months to 10 October 2026 (up from 1) ([ITJobsWatch](@itjobswatch)); 18 to 44 'legal engineer' jobs on Glassdoor UK ([Glassdoor UK](@glassdoor_le) [snippet]); "
        "broad 'legal tech' keyword counts (Reed 4,794; Totaljobs 464; Glassdoor UK 2,009) are inflated by unrelated roles ([Reed](@reed_lt); [Totaljobs](@totaljobs) [snippets]). No board gave a count for 'Clio consultant', 'Filevine consultant', 'practice management consultant' or 'legal operations analyst'.",
    ])
    out.append(fig_image(*CH["vendor_jobs"]))
    out.append(H3("Table 10.1  Legal-tech vendor postings, 23 Sep 2026"))
    h, r = T(10, 0)
    out.append(tbl(h, r, widths=[52, 26, 56, 26], align_right_cols=(1, 3)))
    out.append(source_line("Source: [rlegaltech.com/jobs](@rlegaltech), 'Source checked 23 Sept 2026'."))
    out.append(H2("Three title profiles that do not overlap"))
    out += bullets([
        "The <b>'legal engineer'</b> is a lawyer role: Harvey's New York posting requires a 'JD or equivalent legal qualification', 'At least 3 years of experience practicing law at a top-tier law firm (Vault 50 or equivalent) and/or in-house experience', 'Executive engagement skills and presence' and 'Outstanding presentation skills', "
        "and lists no technical skills ([Legal.io](@legalio)); 'coding is not required' for legal engineers, Luminance fills analyst roles with recent law graduates, some postings say 'qualified lawyers are strongly favoured' ([NonBillable, 19 Feb 2026](@nonbillable)). "
        "Of 46 Am Law 200 lawyers who joined AI companies in the first half of 2026 (Harvey 22, Anthropic 8, OpenAI 5, Legora 5), 15 took 'legal engineer' titles and 40 were associates ([Lawfuel, 3 Oct 2026](@lawfuel); the report's author sells talent data to the firms it covers).",
        "The <b>'AI engineer'</b> at the same vendors is a software role with no stated legal-domain requirement: Everlaw's Staff AI Engineer asks for Python, 'applied LLMs in production', NLP, 'at least 6 years' of ML and '8+ years overall' of software engineering, with retrieval-based models and RAG, vector and graph databases, multimodal work and "
        "'agent building incl. tool use and MCP' as pluses ([Everlaw careers](@everlaw)); across the 43,500 generic US AI postings Python appears in 62%, cloud platforms in 55%, foundation models in 51%, and RAG is 'commonly screened for' ([Axial Search](@axial)).",
        "The UK law-firm <b>'legal technology specialist'</b> is a third thing, a tool-rollout role: the four London adverts all list AI, Generative AI, Harvey AI, HighQ, Legatics, SharePoint and Smartsheet, not an engineering stack ([ITJobsWatch](@itjobswatch)). "
        "A career-content claim that a JD 'commands a 20-30% premium' over technical-only candidates is not employer data ([AI Vortex](@aivortex) [snippet]).",
    ])
    out.append(fig_image(*CH["pay_employed"]))
    out.append(H3("Table 10.2  Posted or estimated pay by title"))
    h, r = T(10, 1)
    out.append(tbl(h, r, widths=[44, 22, 54, 24, 32], font="cell_small"))
    out.append(H2("Remote and visa reality"))
    out += bullets([
        "Of the 43,500 US AI-engineering postings that state a work model, <b>48% are hybrid, 32% fully remote and 20% on-site</b> ([Axial Search](@axial)); the sampled legal-tech roles are mostly hybrid or on-site in New York, San Francisco or London, and 'remote' is written as 'Remote (UK)', 'Remote US' or 'Anywhere (USA)' ([rlegaltech.com/jobs](@rlegaltech)).",
        "No legal-engineer or legal-AI-engineer posting with visa-sponsorship language was found; Harvey's posting is silent on work authorisation; many generic AI roles state 'Employment visa sponsorship is unavailable for this position'; one New York forward-deployed engineer role is open to H-1B or TN; one contractor marketplace excludes contractors who need sponsorship ([ZipRecruiter](@zip_visa) [snippet]).",
        "The vendors do hire outside the US and UK, but in their own offshore engineering hubs: Filevine ML Ops in Bratislava, Legora legal engineers in Bengaluru and Stockholm, Onit in Pune, DeepJudge in Zurich, Legartis in Berlin and Leipzig ([rlegaltech.com/jobs](@rlegaltech); [NonBillable](@nonbillable)).",
    ])
    out.append(H2("The 2025-26 market moves explain the concentration"))
    out += bullets([
        "Legal-tech funding hit a record in 2025 (trackers disagree: Crunchbase '$4.08 billion', Legalcomplex '$5.99 billion across 292 companies' [snippets]); Q1 2026 alone raised <b>$2.34 billion across 103 deals, with Relativity, Legora and Harvey taking about 63% and a median round of just $1 million</b> ([Artificial Lawyer, 13 Apr 2026](@al_q1)); "
        "Harvey reached an <b>$11 billion valuation</b> in March 2026 ([CNBC](@cnbc) [snippet]); Clio closed a $500 million Series G at $5 billion and the $1 billion vLex acquisition, Filevine raised $400 million, Eve $150 million and Supio $60 million ([LawNext, Jan 2026](@lawnext_trends)).",
        "Large law firms started building in-house units: Cooley AI is recruiting for 14 positions including senior engineering; Covington, Cravath, Latham, Kirkland, McGuireWoods, Mayer Brown and White &amp; Case have advertised AI roles ([Court Cast, 26 Sep 2026](@courtcast)).",
        "Thomson Reuters cut engineering roles in July 2026 ('a small number' per the company; up to 500 worldwide per an anonymous employee) while planning 'more than 250 net-new engineering roles globally over the next two years, the large majority senior and AI-native' ([US News / Reuters](@usnews) [snippet]); "
        "Layoffs.fyi counted about 120,000 technology employees laid off across 228 companies in 2026 to that date ([The Next Web](@tnw) [snippet]). The employed path is a bet on a short list of employers that screen on six to eight years of production AI work or on a JD.",
    ])
    out.append(H2("The freelance and consulting path has three price tiers"))
    out += bullets([
        "<b>Marketplace tier.</b> Upwork's hire pages price AI chatbot specialists at '$30-$61 per hour', a 'Rule-based FAQ or support bot $300-$1,200/project', a 'Custom LLM or RAG assistant $1,500-$5,000/project', and 'focused Clio-related work' at '$500-$1,500 per project' ([Upwork AI chatbot specialists](@upwork_bot); [Upwork Clio freelancers](@upwork_clio) [vendor marketing, snippets]); "
        "Fiverr's '24 Best Legal Automation Services' page shows gigs 'From $30' and legal AI intake and chatbot gigs 'From $20' to 'From $80'; its cost guides put AI expert services at 'approximately $98 for basic consulting to $520 for complex chatbot development' ([Fiverr legal automation](@fiverr_auto); [Fiverr AI automation cost guide](@fiverr_cost) [vendor, snippets]); "
        "PeoplePerHour chatbot freelancers quote roughly €8-€40 an hour with no law-firm automation listings ([PeoplePerHour](@pph_ai) [snippet]); an agency guide puts UK AI consultants at £80-£200 an hour ([Lazige](@lazige) [vendor]). A guide to RAG jobs on Upwork warns that clients mix 'MVP budget with production expectations' ([GigUp](@gigup) [snippet]).",
        "<b>Consultancy tier.</b> One law-firm AI consultancy's own page lists <b>$150-$350 an hour, fixed-scope assessments at $1,500-$5,000, implementations at $5,000-$20,000 for a 5-25 attorney firm, and monthly retainers from about $1,500</b>, and tells buyers to vet consultants on prior law-firm work, confidentiality handling and referral fees ([Pivot180](@pivot180) [vendor, self-reported]); "
        "GSA-schedule medians are $151 an hour for IT consulting and $132 for legal and compliance consulting ([ConsultingDemand](@consultingdemand) [snippet]); Clutch's 'Top IT Services Companies for Legal Firms' is dominated by managed-service providers at $25-$149 an hour with one at $200-$300 ([Clutch](@clutch) [snippet]).",
        "<b>Vendor-certified tier.</b> Filevine's contract wording makes partners structurally necessary: 'Filevine will not perform or provide any implementation services and/or data migration services directly ... Such implementation services ... must be performed and provided by a Filevine-certified third-party implementation partner' ([Marin County contract](@marin) [snippet]), "
        "with partner packages at $1,750 to $32,500 (section 6); Clio's LinkedIn page says its ecosystem 'includes partnerships with over 280 app integration partners and 100 Clio Certified Consultants', a consultant being someone 'assessed by Clio as proficient in the use and resale of the Clio application' ([Clio LinkedIn](@clio_li); [Clio Certified Consultants](@clio_ccc) [snippets]), "
        "a small certified pool against hundreds of thousands of users; no Clio consultant publishes a rate and two consultant sites blocked the fetch. LEAP UK's certified partners include Jayva (since 2014), Thinkwild (since 2015), SPBK and Law Right; Hunnings Consultancy says it has assisted more than 800 of the UK's 2,500-plus LEAP firms ([Hunnings](@hunnings) [self-reported, snippet]).",
    ])
    out.append(fig_image(*CH["pay_freelance"]))
    out.append(H3("Table 10.3  Price tiers and who sets the price"))
    h, r = T(10, 2)
    out.append(tbl(h, r, widths=[30, 74, 30, 42], font="cell_small"))
    out.append(H2("How small firms actually buy technology help"))
    out += bullets([
        "ABA 2024 Technology and Training TechReport: 45% of all respondents turn first to internal technical support staff, but <b>only 4% of solos and 25% of 2-9 attorney firms</b> do, and solos were most likely (<b>28%</b>) to turn first to Google or another non-legal online resource ([ABA 2024 Technology and Training TechReport](@aba_tt) [snippet; page blocked]); "
        "<b>55.4% of solo firms reported no technology budget</b> ([ABA 2024 Budgeting and Planning TechReport](@aba_budget) [snippet]).",
        "Firms learn about AI mainly through CLE seminars and webinars (61% overall, 66% of solos, 68% of 2-9 firms), publications (37%), legal news (34%) and other law firms (32%); it is the 50-99 attorney firms that use 'legal technology consultants, product vendors, and trade shows' as sources ([LawNext, 7 Mar 2025](@lawnext_aba); [ABA 2024 AI TechReport](@aba_ai) [snippet]). "
        "AI-tool use in 2024 was 18% at solos, 30% at 10-49 attorney firms and 46% at 100+; ChatGPT was used or considered by 64% of 2-9 firms and 62% of solos ([LawNext](@lawnext_aba)).",
        "Clio's 2025 solo and small-firm report: 'finding time' is the biggest hurdle to adopting new technology for 27% of solos and 33% of small firms ([Clio 2025 report](@clio_2025ss) [snippet; vendor]); 55% of small firms have no AI policy ([NC Bar, May 2026](@ncbar) [snippet]). "
        "Circulating spend figures ('$3,000-$10,000 per lawyer per year', '$150-230/month in subscriptions for an AI-assisted solo practice') are vendor-cited and cover software, not consulting ([tryclean.ai](@tryclean); [LawyerAI Directory](@lawyerai) [vendor]).",
        "Put with the Clutch list: small firms' paid technology help is bought as managed IT support and cloud subscriptions, with consultants appearing as a channel mainly at 50-99 lawyer firms. No UK survey on who small firms turn to was found.",
    ])
    out.append(fig_image(*CH["tech_help"]))
    out.append(H3("Table 10.4  ABA 2024 measures by firm size"))
    h, r = T(10, 3)
    out.append(tbl(h, r, widths=[56, 20, 22, 18, 18, 18, 24], font="cell_small"))
    out.append(source_line("Sources: ABA 2024 Technology and Training [%d], Budgeting and Planning [%d] and AI [%d] TechReports (all via search snippets; americanbar.org blocked); LawNext, 7 Mar 2025 [%d] (512 private-practice attorneys)." % tuple(
        ref(u) for u in (U["aba_tt"], U["aba_budget"], U["aba_ai"], U["lawnext_aba"]))))
    out.append(H2("Side by side on five criteria"))
    out += bullets([
        "<b>Income range.</b> US vendor AI engineering is posted at $150,000-$340,000 base and legal engineering at $200,000-$325,000 OTE (management to $450,000); US law-firm roles at $126,000-$250,000 (directors to $438,000); US legal-ops and employed-consultant titles about $39,000-$160,000; UK employed roles £42,000-£70,000 (vendor legal engineers estimated at £46,000-£120,000). "
        "Freelance marketplace work is priced at $30-$61 an hour or $500-$5,000 a project; consultancy-tier work at $150-$350 an hour, $5,000-$20,000 an implementation and $1,500-plus a month on retainer. "
        "The researcher's arithmetic, not a reported figure: a solo consultant billing about $200 an hour for about ten hours a week would gross about $100,000 a year, level with the employed 'legal technology consultant' average and below the US vendor floor; a UK freelancer at £80-£200 an hour would at the same utilisation gross more than the £42,000 UK employed median.",
        "<b>Time to first revenue.</b> No source measures it; proxies: employed postings cycle within months (Harvey's New York legal-engineer post ran from 6 February 2026 to expiry, Danaher's remote role is filled, Husch Blackwell's April 2026 posting was removed); a Filevine partner 'Sprint' is scoped at two weeks and a Clio small-firm set-up at 'about two weeks' ([LeanLaw Clio guide](@leanlaw_clio) [snippet]); "
        "the buyer's own constraints are 'finding time' and no budget line.",
        "<b>Competition.</b> Employed: a few hundred engineering postings sector-wide concentrated in about five vendors, screened on 6-8+ years or a JD, against 43,500 generic AI postings. Freelance: priced down by marketplace sellers at $20-$61 an hour, with the protected niches being Clio's roughly 100 certified consultants, Filevine's handful of certified partners (one claiming '90+ specialists') and LEAP's 12 UK partners.",
        "<b>Need for a law background.</b> A hard requirement only for the 'legal engineer' title (JD plus three years at Harvey; 'qualified lawyers strongly favoured' at Luminance); absent from AI-engineer adverts; absent from freelance buyer-vetting advice, which asks for prior law-firm work and confidentiality handling instead; vendor certification is assessed on product proficiency, not law.",
        "<b>Skills in both job ads and buyer posts.</b> Python, production LLM work, retrieval and RAG, vector databases and agent or tool-use building (required or a plus at Everlaw and in 62%/51% of generic postings; the core of Upwork's 'custom LLM or RAG assistant' category and of the firm-side Upwork post that wanted 'Claude or OpenAI APIs', 'webhook-based automations' and Clio dashboards), "
        "and practice-management platform set-up for Clio, Filevine and LEAP (vendor client-success and implementation roles such as LEAP's Client Success Consultant in Bath and London and Filevine's 105 postings on one side; Upwork Clio projects, Filevine partner sprints and LEAP UK partners on the other). "
        "One side only: Harvey AI, HighQ, Legatics and SharePoint administration in UK law-firm technologist adverts with no freelance buyer category; intake automation, document automation and legal AI chatbots as Fiverr gig titles with no matching engineering job title.",
    ])
    out.append(H3("Table 10.5  Employed path against freelance path on the five criteria"))
    h, r = T(10, 4)
    out.append(tbl(h, r, widths=[24, 62, 62, 28], font="cell_small", first_col_bold=True))
    out.append(H2("What the notes do not contain"))
    out += bullets([
        "No interview, podcast or survey of independent legal-tech consultants' income or how they find clients; the only client-acquisition evidence is generic ABA advice about referrals and niche networking ([ABA Law Practice Today](@aba_clients) [snippet]).",
        "No seller-to-buyer-post ratios for 'law firm AI', 'Clio' or 'legal RAG' on Upwork or Fiverr; no LinkedIn Services counts; no actual law-firm buyer posts with budgets in this set (the dated ones are in section 2); no posted pay for any Clio, Filevine, LEAP or Actionstep consultant or implementation role; "
        "no evidence on whether freelancers outside the US and UK win law-firm work at consultancy-tier rates, since every consultancy rate card found is US-based.",
    ])
    return out


def section_11(CH):
    out = chapter(11, SEC[11]["title"],
                  "The researchers were blocked by many primary hosts (" + BLOCKED_HOSTS.rstrip(".") + "). The items below rest on search snippets, secondary reports or vendor claims, or were not found at all, "
                  "and should be checked before being repeated to a client.")
    out.append(H3("Table 11.1  Items that rest on snippets, secondary reports or vendor claims"))
    h, r = T(11, 0)
    out.append(tbl(h, r, widths=[72, 104], font="cell"))
    return out


def conclusion_page(CH):
    out = chapter(None, "Conclusion", None)
    out.append(Paragraph("What the research changes", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("<b>The problem a small firm will pay to remove is not drafting law.</b> It is the loop of chasing, waiting and checking that sits around every matter, and that loop is now policed from outside: by regulators "
            "(SRA AML inspections, the Legal Ombudsman's 36% conveyancing share), by courts (bundle rejections, CE-File fee rejections, hallucination sanctions) and by insurers (administrative errors at a quarter of claims). "
            "The strongest language is therefore risk language, not productivity language, and the strongest evidence is a regulator's own finding about the firm's own practice area."),
        inl("<b>The 2025-26 rulings and notices drew a hard line between 'open' and 'closed' tools</b>, and the firms most likely to cross it are the smallest and least supported. The market reaction so far is either a ban that staff ignore "
            "or a vendor AI add-on that users describe as forced on them and wrong in its details. The space between those two, where confidential files are processed inside the firm's control with a human check built into the step, "
            "is where every top-ranked gap sits: closed-tool document work, provider reconciliation on medical records, exception reports pulled from the firm's own Clio data, bundles built from the firm's own documents, AML reasoning written from the firm's own evidence."),
    ]]
    out.append(Paragraph("Where not to go, and what the law reserves to a person", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("Intake answering, chronologies and demand letters are where the venture money and the vendor claims are concentrated, and their users' complaints are about quality, support and price rather than absence."),
        inl("Anything the law reserves to a person is not a gap to automate but a boundary to design around: a sworn statement for a Florida crash report, an attorney's declaration in California, the COFA's signature on a reconciliation, the qualified lawyer's check of every citation."),
    ]]
    out.append(Paragraph("Two vocabularies, two markets for the same skills", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("The vocabulary split is not cosmetic: a UK buyer searches 'court bundle software', 'ai policy for solicitors' and hires a 'fee earner' support role around 'completion' and 'Land Registry'; a US buyer searches 'law firm intake automation', "
            "'is chatgpt confidential' and hires a 'case manager' around 'calendaring' and 'e-filing'. The same service will need two sets of words, and the notes give them verbatim."),
        inl("The job-market notes add a last contrast: the employed path pays most where a law degree or six to eight years of production AI work is the screen and where 'remote' stops at the national border, while the freelance path is priced down to $20 an hour "
            "by marketplace sellers and protected only inside vendor certification programmes, which is where the small firm's actual buying habit (no internal IT, no technology budget, Google first) meets a consultant at all."),
    ]]
    out.append(Spacer(1, 6 * mm))
    out.append(note_box("This document reports problems, workflows, numbers, vocabulary and gaps only. It contains no solutions and no recommendations. "
                        "The Sources appendix lists every URL the research cited; section 11 lists what could not be verified.", warm=False))
    return out


def sources_appendix():
    out = chapter(None, "Sources", "Every URL cited in the research report, numbered in order of first appearance. Body references [n] point here. "
                                   "Hosts that blocked the researcher are listed in section 11, which follows this appendix; facts from them carry the [snippet] or [secondary] tag.")
    rows = []
    for i, url in enumerate(URLS, 1):
        label = URL_LABEL.get(url, "")
        rows.append([Paragraph("[%d]" % i, S["src_num"]),
                     Paragraph("<b>%s</b> &nbsp; <font color='%s'>%s</font>" % (esc(label), INK_SEC, esc(url)), S["src_entry"])])
    t = Table(rows, colWidths=[11 * mm, FRAME_W - 11 * mm], repeatRows=0, splitByRow=1)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.25, C_GRID),
          ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
          ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6)]
    t.setStyle(TableStyle(st))
    out.append(t)
    return out


# ==========================================================================
# Document template: running header (section name), footer (page number and
# report line), bookmarks, TOC entries; two-pass build for page numbers.
# ==========================================================================
class ReportDoc(BaseDocTemplate):
    def __init__(self, path):
        BaseDocTemplate.__init__(self, path, pagesize=A4,
                                 leftMargin=MARGIN, rightMargin=MARGIN,
                                 topMargin=21 * mm, bottomMargin=19 * mm,
                                 title="Small law firm problems UK and US (11 Oct 2026)",
                                 author="Research for Mustafa Shoukat",
                                 subject="Problems, workflows, numbers, vocabulary and service gaps in small UK and US law firms")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="f",
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates([PageTemplate(id="cover", frames=[frame], onPageEnd=self._cover_decor),
                               PageTemplate(id="main", frames=[frame], onPageEnd=self._main_decor)])
        self._section = ""
        self._toc_n = 0

    def beforeDocument(self):
        self._section = ""
        self._toc_n = 0

    def afterFlowable(self, fl):
        sec = getattr(fl, "_sec", None)
        if sec:
            self._section = sec
        toc = getattr(fl, "_toc", None)
        if toc:
            level, text = toc
            self._toc_n += 1
            key = "toc%d" % self._toc_n
            self.canv.bookmarkPage(key)
            self.notify("TOCEntry", (level, text, self.page, key))
            try:
                self.canv.addOutlineEntry(text, key, level=level, closed=(level > 0))
            except Exception:
                pass

    def _cover_decor(self, canv, doc):
        canv.saveState()
        canv.setFont("DejaVu", 7.2)
        canv.setFillColor(C_MUTED)
        canv.drawString(MARGIN, 10 * mm, FOOTER_TEXT)
        canv.restoreState()

    def _main_decor(self, canv, doc):
        canv.saveState()
        canv.setFont("DejaVu", 7.2)
        canv.setFillColor(C_MUTED)
        canv.drawString(MARGIN, PAGE_H - 12.5 * mm, self._section[:120])
        canv.setStrokeColor(C_LINE)
        canv.setLineWidth(0.4)
        canv.line(MARGIN, PAGE_H - 15 * mm, PAGE_W - MARGIN, PAGE_H - 15 * mm)
        canv.line(MARGIN, 14 * mm, PAGE_W - MARGIN, 14 * mm)
        canv.drawString(MARGIN, 10 * mm, FOOTER_TEXT)
        canv.setFont("DejaVu-Bold", 7.6)
        canv.setFillColor(C_ACCENT)
        canv.drawRightString(PAGE_W - MARGIN, 10 * mm, "Page %d" % doc.page)
        canv.restoreState()


def build_story(CH):
    story = []
    story += cover_page()
    story += contents_page()
    story += summary_page()
    story += section_1(CH)
    story += section_2(CH)
    story += section_3(CH)
    story += section_4(CH)
    story += section_5(CH)
    story += section_6(CH)
    story += section_7(CH)
    story += section_8(CH)
    story += section_9(CH)
    story += section_10(CH)
    # closing order asked for: Sources appendix, then what could not be verified, then the conclusion as the closing page
    story += sources_appendix()
    story += section_11(CH)
    story += conclusion_page(CH)
    return story


def main():
    print("rendering charts ...")
    CH = build_charts()
    print("building story ...")
    story = build_story(CH)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = ReportDoc(str(OUT_PDF))
    print("laying out (two passes for the contents page) ...")
    doc.multiBuild(story)
    size = OUT_PDF.stat().st_size
    print("wrote %s (%d pages, %.1f MB, %d sources)" % (OUT_PDF, doc.page, size / 1e6, len(URLS)))


if __name__ == "__main__":
    main()
