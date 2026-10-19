"""Generate the designed PDF of the research report
"Small dental practice problems UK US" (reports/Small dental practice problems UK US.md).

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

Run:  python generate_small_dental_practice_problems_pdf.py
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
REPORT = Path(r"D:\Mustafa AI\reports\Small dental practice problems UK US.md")
OUT_PDF = Path(r"D:\Mustafa AI\03 - Market Research\Small Dental Practice Problems UK-US (16 Oct 2026).pdf")
CHART_DIR = Path(r"C:\Users\MICROS~1\AppData\Local\Temp\claude\d--Mustafa-AI\ed3e6955-5f88-400b-a9f5-fd8bdbc9bceb\scratchpad\pdfcharts_dental")
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
FOOTER_TEXT = "Small dental practice problems UK and US, research 16 Oct 2026"

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
TAG_RE = re.compile(r"\[((?:snippet|snippets|vendor|user|users|secondary|3p|tribunal|reported claim|self-reported|sponsored|competitor|unverified|member-only|listing, not fetched|official|press|vendor/user)[^\[\]]*)\]")
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

plt.rcParams["text.parse_math"] = False   # "$215,320" is money, not mathtext

FULL_W = 6.9
TITLE_WRAP = 92
SRC_WRAP = 124


def _wrap(s, n=34):
    return "\n".join(textwrap.wrap(s, n))


def _frame(w, h, title, source, ncols=1, width_ratios=None, nrows=1):
    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h),
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
    fig.tight_layout(rect=[0, bottom, 0.99, top], h_pad=3.2)
    renderer = fig.canvas.get_renderer()
    last_right = -1.0
    last_y = None
    for ax in sorted(fig.axes, key=lambda a: (-round(a.get_position().y1, 2), a.get_position().x0)):
        t = getattr(ax, "_ptitle", None)
        if not t:
            continue
        ax.set_title("")
        bb = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
        pos = ax.get_position()
        if last_y is None or abs(pos.y1 - last_y) > 0.02:
            last_right = -1.0
        last_y = pos.y1
        x0 = max(bb.x0, 0.0, last_right + 0.015)
        txt = fig.text(x0, pos.y1 + 0.012, t, ha="left", va="bottom", fontsize=7.8, fontweight="bold",
                       color=INK_SEC, linespacing=1.15)
        tb = txt.get_window_extent(renderer).transformed(fig.transFigure.inverted())
        last_right = max(pos.x1, tb.x1)
    path = CHART_DIR / (name + ".png")
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return (path, w, h)


def _hbar(ax, labels, values, colors=None, fmt="{:.0f}%", xlim=None, wrap=34, height=0.58,
          text_color=INK2, xlabel=None, labels_override=None):
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
    for i, (yi, v) in enumerate(zip(y, values)):
        txt = labels_override[i] if labels_override else fmt.format(v)
        ax.text(v + mx * 0.015, yi, txt, va="center", ha="left", fontsize=7.2, color=text_color)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=7.2, color=INK_SEC)
    ax.set_ylim(-0.65, n - 0.35)


def _cols(ax, labels, values, colors, fmt="{:.0f}", ylim=None, ann=None):
    x = list(range(len(labels)))
    ax.bar(x, values, color=colors, width=0.58, edgecolor="white")
    mx = max(values) if ylim is None else ylim
    for i, v in enumerate(values):
        ax.text(i, v + mx * 0.02, (ann[i] if ann else fmt.format(v)), ha="center", fontsize=7.2, color=INK2)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7)
    ax.set_ylim(0, mx * 1.2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", length=0)


def _k(v):
    if v >= 1000:
        t = ("%.1f" % (v / 1000.0)).rstrip("0").rstrip(".")
        return t + "k"
    return "%g" % v


def _panel_title(ax, text):
    ax.set_title(text, fontsize=7.8, color=INK_SEC, loc="left", fontweight="bold")
    ax._ptitle = text


def _range_bars(ax, items, unit_fmt, xlim, wrap=34, point_color=BLUE_RAMP[3]):
    n = len(items)
    y = list(range(n))[::-1]
    for yi, it in zip(y, items):
        lab, lo, hi = it[0], it[1], it[2]
        pre = it[3] if len(it) > 3 else ""
        col = it[4] if len(it) > 4 else BLUE
        if lo == hi:
            ax.scatter([lo], [yi], s=46, color=point_color if col == BLUE else col, zorder=3, edgecolor="white", linewidth=1)
            ax.text(lo + xlim * 0.03, yi, pre + unit_fmt(lo), va="center", fontsize=7.1, color=INK2)
        else:
            ax.barh(yi, hi - lo, left=lo, height=0.5, color=col, edgecolor="white", linewidth=1)
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


def _dumbbell(ax, rows, xlim, wrap=30, lo_label="average", hi_label="top 10%", fmt="{:g}%"):
    """rows: (label, lo, hi, lo_text, hi_text)"""
    n = len(rows)
    y = list(range(n))[::-1]
    for yi, (lab, lo, hi, lt, ht) in zip(y, rows):
        ax.plot([lo, hi], [yi, yi], color=DEEMPH, linewidth=2.2, zorder=1, solid_capstyle="round")
        ax.scatter([lo], [yi], s=60, color=BLUE_RAMP[0], zorder=3, edgecolor="white", linewidth=1.2)
        ax.scatter([hi], [yi], s=60, color=BLUE_RAMP[3], zorder=3, edgecolor="white", linewidth=1.2)
        ax.text(lo - xlim * 0.03, yi, lt, va="center", ha="right", fontsize=7, color=INK2)
        ax.text(hi + xlim * 0.03, yi, ht, va="center", ha="left", fontsize=7, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([_wrap(r[0], wrap) for r in rows], fontsize=7.2, color=INK2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, xlim)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_ylim(-0.7, n + 0.75)
    ax.scatter([], [], s=60, color=BLUE_RAMP[0], label=lo_label)
    ax.scatter([], [], s=60, color=BLUE_RAMP[3], label=hi_label)
    ax.legend(loc="upper right", frameon=False, fontsize=7, ncol=2, handletextpad=0.3, columnspacing=1.2, borderaxespad=0.2)


# ---------------------------------------------------------------- charts
def chart_funnel():
    h = 2.6
    fig, ax = _frame(FULL_W, h,
                     "Of 100 callers to a US dental practice, 31 hang up before reaching anyone, 21 book, 13 walk away unbooked, 4.8 get a follow-up call and 0.7 come back and book",
                     "Source: Patient Prism, 2 Jul 2026 [%d] (vendor data: 11.55 million calls across 8,280 US locations in 2025). Reasons for not booking: timing 45.2%%, money and insurance 34.4%%, service fit 10.3%%, "
                     "connection failed 9.3%%; 1,445,814 patients walked away without an appointment and 890,621 never got a callback." % (
                         ref("https://www.patientprism.com/report/dental-patient-access-report/")))
    labels = ["Hang up before reaching anyone", "Book an appointment", "Walk away without booking", "Non-bookers who get a follow-up call", "Non-bookers who come back and book"]
    vals = [31, 21, 13, 4.8, 0.7]
    _hbar(ax, labels, vals, colors=[WARM, BLUE, WARM, BLUE_RAMP[1], BLUE_RAMP[3]], fmt="{:g}", xlim=36, wrap=40, height=0.6,
          labels_override=["31", "21", "13", "4.8", "0.7"], xlabel="Callers per 100 inbound calls (vendor-measured)")
    return _save(fig, "funnel", FULL_W, h)


def chart_ranges():
    h = 3.4
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "Vendor benchmarks: 31-38% of calls go unanswered, no-shows run 4-14% depending on definition, and average practices sit far below the top 10% on acceptance, recall and collection",
                               "Sources: Patient Prism [%d], DenteMax [%d], Pain-Free Dental Marketing via Dentaltown [%d], Peerlogic [%d] (all vendor); Henry Schein One Catalyst Index 2026 [%d] (vendor), Planet DDS via Ainora [%d] (vendor), "
                               "peer-reviewed studies as relayed by Patient Prism [%d]; recall benchmarks Ainora [%d] (vendor). No regulator or academic body publishes these rates in either country." % (
                                   ref("https://www.patientprism.com/report/dental-patient-access-report/"),
                                   ref("https://www.dentemax.com/dentists/blog-articles/2025/Why_missed_phone_calls_are_dental_offices_largest_revenue_loss"),
                                   ref("https://www.dentaltown.com/channel/post/26399/your-marketing-isnt-broken-your-front-desk-is"),
                                   ref("https://www.peerlogic.com/post/peerlogic-dso-case-study"),
                                   ref("https://henryscheinone.com/insights/ebook/2026-catalyst-index"),
                                   ref("https://ainora.lt/blog/dental-no-show-statistics-ai-reduction"),
                                   ref("https://www.patientprism.com/blog/missed-calls-medical-practice-revenue/"),
                                   ref("https://ainora.lt/blog/dental-recall-reactivation-statistics-benchmarks")),
                               ncols=3, width_ratios=[1, 1, 1.4])
    _hbar(a1, ["Patient Prism (11.55m calls, 2025)", "DenteMax", "Pain-Free (55,000+ calls)", "Peerlogic (4,280 calls, Feb 2026)"], [31, 35, 37, 38],
          colors=[WARM] * 4, xlim=45, wrap=20, xlabel="Share of calls")
    _panel_title(a1, "Missed or abandoned calls")
    _hbar(a2, ["Henry Schein One (top 10%: under 1%)", "Planet DDS 2025 (plus 12.9% cancellations)", "Saudi study 2023", "Buffalo pediatric 2025"], [4, 6.9, 9.14, 14.3],
          colors=[BLUE] * 4, xlim=17, wrap=20, fmt="{:g}%", xlabel="No-show rate")
    _panel_title(a2, "No-shows by source")
    rows = [("Case acceptance", 42, 75, "42-46%", "75-83%"), ("Hygiene reappointment", 63, 94, "42-81%", "94%"),
            ("Recall rate", 65, 90, "60-70%", "85-95%"), ("Collection rate", 80, 97, "80%", "97%"), ("Patient retention", 70, 94, "70%", "94%")]
    _dumbbell(a3, rows, 128, wrap=22)
    _panel_title(a3, "Average practice against the top 10%")
    return _save(fig, "ranges", FULL_W, h)


def chart_us_economics():
    h = 3.7
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "US practice economics: the average general dentist netted $215,320 in 2025, about $60,000 below 2010 in real terms, on overhead of 60-65%, while DSO affiliation more than doubled and ownership fell",
                               "Sources: ADA HPI dental practice trends [%d] (snippet) and Becker's [%d] [%d] (secondary); DrBicuspid on ADA HPI [%d]; Dental Economics/Levin survey [%d] (snippet); Clerri [%d] (vendor, 100+ practices); ADA HPI Q1 2026 [%d]; Dental Economics 2025 survey [%d]." % (
                                   ref("https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/dental-practice-trends"),
                                   ref("https://www.beckersdental.com/?p=21392"), ref("https://www.beckersdental.com/dentists/good-news-bad-news-for-dentists/"),
                                   ref("https://www.drbicuspid.com/dental-practice/office-management/practice-trends/article/15683050/how-dentistrys-practice-models-continue-to-evolve"),
                                   ref("https://www.dentaleconomics.com/practice/overhead-and-profitability/article/55280684/higher-production-helps-offset-chronic-overhead-increases"),
                                   ref("https://clerri.com/blog/dental-practice-overhead-statistics/"),
                                   ref("https://www.ada.org/-/media/project/ada-organization/ada/ada-org/files/resources/research/hpi/state_us_dental_economy_q12026.pdf"),
                                   ref("https://www.dentaleconomics.com/practice/article/55368689/findings-from-the-2025-dental-economics-levin-group-annual-practice-survey")),
                               ncols=3, width_ratios=[1.1, 0.85, 1.25])
    _hbar(a1, ["Own a practice, 2005", "Own a practice, 2023", "DSO-affiliated, 2015", "DSO-affiliated, 2024"], [84.7, 72.5, 7.2, 16.1],
          colors=[BLUE_RAMP[1], BLUE_RAMP[3], BLUE_RAMP[1], BLUE_RAMP[3]], xlim=100, wrap=22, fmt="{:g}%", xlabel="Share of US dentists; about 34%\nwork alone in one location (2024)")
    _panel_title(a1, "Ownership and DSO share")
    _hbar(a2, ["2024", "2025"], [207.98, 215.32], colors=[BLUE_RAMP[1], BLUE_RAMP[3]], xlim=300, wrap=10,
          labels_override=["$208k", "$215k"], xlabel="$207,980 then $215,320;\nreal average about\n$60,000 below 2010")
    _panel_title(a2, "General dentist\nnet income")
    _hbar(a3, ["Overhead, general practice (2024)", "Report higher overhead (+5.1%)", "Overhead the top challenge (2025)",
               "'Not busy enough' (Q1 2026)", "Plan to drop some networks", "Participate in Medicaid (2024)"],
          [61.8, 65, 55, 33, 35, 41], colors=[WARM, BLUE, BLUE, WARM, BLUE, BLUE], xlim=75, wrap=34, fmt="{:g}%", xlabel="Share of dentists")
    _panel_title(a3, "Overhead and demand")
    return _save(fig, "us_economics", FULL_W, h)


def chart_staffing():
    h = 3.9
    fig, (a1, a2) = _frame(FULL_W, h,
                           "Staffing: 91% of US dentists recruiting a hygienist call it very or extremely hard and only 60% have enough; 77% of UK owners who tried to hire a dental nurse had difficulty and 63% of vacancies stayed open more than six months",
                           "Sources: ADA HPI hygienist shortage, Apr 2026 [%d]; ADA HPI Q1 2026 [%d]; ADA HPI Jul 2026 [%d]; BDA DDRB 2026-27 evidence [%d]; Dentistry.co.uk 15 Nov 2024 [%d] and 31 Mar 2026 [%d]; PMC12334352 [%d] (n=1,507, 2023)." % (
                               ref("https://www.ada.org/resources/research/health-policy-institute/dentist-workforce/dental-hygienist-shortage"),
                               ref("https://www.ada.org/-/media/project/ada-organization/ada/ada-org/files/resources/research/hpi/state_us_dental_economy_q12026.pdf"),
                               ref("https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/dentists-ai-usage-and-attitudes"),
                               ref("https://www.bda.org/media/lm1nw32p/ddrb-26-27-round-bda-submission.pdf"),
                               ref("https://dentistry.co.uk/2024/11/15/one-fifth-of-nhs-general-dentist-positions-unfilled-data-shows/"),
                               ref("https://dentistry.co.uk/2026/03/31/dentistry-is-the-uks-most-loyal-profession/"),
                               ref("https://pmc.ncbi.nlm.nih.gov/articles/PMC12334352/")),
                           ncols=2, width_ratios=[1, 1])
    _hbar(a1, ["Recruiting a hygienist very or extremely hard", "Have enough hygienists", "Recruiting assistants very or extremely hard (about)",
               "Recruited a hygienist in the last 3 months", "Report being overworked", "Lack enough administrative staff"],
          [91, 60, 70, 37.6, 32.4, 20], colors=[WARM, BLUE, WARM, BLUE, BLUE, BLUE], xlim=105, wrap=34, fmt="{:g}%", xlabel="Share of US dentists")
    _panel_title(a1, "United States")
    _hbar(a2, ["Owners with difficulty recruiting nurses", "Difficulty recruiting therapists", "Difficulty recruiting hygienists",
               "Vacancies open over six months (76% high-NHS)", "Candidates reluctant to work in the NHS", "NHS general-dentist vacancy rate (10% Dec 2025)",
               "Job-changing nurses who leave dentistry", "High emotional exhaustion (dentists, 2023)"],
          [77, 70, 63, 63, 40, 19, 75, 69.8], colors=[WARM, BLUE, BLUE, WARM, BLUE, BLUE, WARM, BLUE], xlim=90, wrap=34, fmt="{:g}%", xlabel="Share, UK")
    _panel_title(a2, "United Kingdom")
    return _save(fig, "staffing", FULL_W, h)


def chart_nhs():
    h = 4.6
    fig, axes = _frame(FULL_W, h,
                       "NHS England: contracts fell from about 6,260 to 5,650, only 40% of adults saw an NHS dentist in 24 months, and about £900m was clawed back over two years at £36.22 per UDA",
                       "Sources: Nuffield Trust and BDA via GDPUK, 24 Aug 2026 [%d] (secondary); NHSBSA dental statistics 2024/25 [%d]; Dentistry.co.uk, 5 Mar 2026 [%d] (secondary); GDPUK UDA rates [%d]; NHSBSA KA-02003 [%d] (charges from Apr 2026); "
                       "below 96%% of the annual UDA target is recovered in full [%d]." % (
                           ref("https://www.gdpuk.com/news/one-in-ten-practices-have-ceased-general-nhs-dentistry-since-2017/"),
                           ref("https://www.nhsbsa.nhs.uk/statistical-collections/dental-england/dental-statistics-england-202425"),
                           ref("https://dentistry.co.uk/2026/03/05/nhs-contract-clawback-at-900-million-in-past-two-years/"),
                           ref("https://www.gdpuk.com/news/news-in-focus/does-size-matter-corporate-versus-independent-uda-rates/"),
                           ref("https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-02003"),
                           ref("https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01672/en-us")),
                       nrows=2, ncols=2, width_ratios=[1, 1.15])
    (a1, a2), (a3, a4) = axes
    _hbar(a1, ["March 2017", "March 2026"], [6260, 5650], colors=[BLUE_RAMP[1], WARM], xlim=7200, wrap=20,
          labels_override=["about 6,260 (64.6% of practices)", "about 5,650 (55.6%)"], xlabel="General NHS contracts, England")
    _panel_title(a1, "One practice in ten has left NHS dentistry")
    _hbar(a2, ["Adults seen, 24 months to Mar 2025", "Adults seen, 24 months to Mar 2026", "Children seen, 12 months"], [40, 40, 57],
          colors=[WARM, WARM, BLUE], xlim=72, wrap=24, labels_override=["40% (18.0m)", "40% (18.8m)", "57%"], xlabel="Share of the population")
    _panel_title(a2, "NHS access")
    _hbar(a3, ["2024", "2025"], [479, 457], colors=[WARM, WARM], xlim=580, wrap=20,
          labels_override=["£479m", "£457m"], xlabel="Clawback, £ million")
    _panel_title(a3, "Clawback for under-delivered UDAs")
    _hbar(a4, ["Band 1 (and urgent)", "Average UDA value", "Minimum UDA value", "Band 2", "Band 3"], [27.90, 36.22, 28, 76.60, 332.10],
          colors=[BLUE, WARM, WARM, BLUE, BLUE], xlim=400, wrap=20, labels_override=["£27.90", "£36.22", "£28", "£76.60", "£332.10"], xlabel="GBP (charges from Apr 2026)")
    _panel_title(a4, "Patient charge bands and UDA value")
    return _save(fig, "nhs", FULL_W, h)


def chart_verification():
    h = 3.3
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "US verification and denials: $2.1bn a year on benefit checks at about 12 minutes by phone against 4 electronic; first-pass denials of 8-15% against a 4% benchmark; 32-60 days in AR",
                               "Sources: ADA News, 24 Mar 2025 [%d] (CAQH Index: 1.2bn checks, $580m savings opportunity); StealthAgents on CAQH [%d] (secondary); DentistryIQ [%d] (snippet); The Dental Billing Podcast [%d] (secondary; Delta transparency files); "
                               "Becker's on Zentist [%d] (snippet); Dental Billing Assist [%d] (vendor); Arini [%d] (vendor); dentalbilling.com [%d] (snippet). 72.88%% of denials are administrative; about 80%% of practices report more denials; "
                               "AR over 90 days runs 18%% against a 5-10%% target; 54%% of denied claims are paid after about three cycles; about 5%% are appealed and about half of appeals succeed." % (
                                   ref("https://adanews.ada.org/ada-news/2025/march/benefit-verification-drives-increased-administrative-spending-in-dental-offices/"),
                                   ref("https://stealthagents.com/research/dental-insurance-verification-workload-statistics-2026"),
                                   ref("https://www.dentistryiq.com/revenue-cycle-management/article/55409403/the-7-revenue-cycle-gaps-most-dental-practices-dont-know-they-have"),
                                   ref("https://thedentalbillingpodcast.buzzsprout.com/1783772/episodes/19634075-27-837-denials-zero-appeals-make-this-make-sense"),
                                   ref("https://beckersdental.com/revenue-cycle-management/78-of-dental-offices-see-uptick-in-claim-denials-report"),
                                   ref("https://dentalbillingassist.com/blog/posts/dental-billing-kpis-benchmarks"),
                                   ref("https://www.arini.ai/blog/days-sales-outstanding-benchmarks-dental-practices"),
                                   ref("https://dentalbilling.com/?p=31917")),
                               ncols=3, width_ratios=[0.9, 1.2, 1.05])
    _hbar(a1, ["Phone, fax or mail", "Portal", "Fully electronic"], [12, 7, 4], colors=[WARM, BLUE_RAMP[2], BLUE_RAMP[3]], xlim=14, wrap=14,
          labels_override=["about 12 min", "about 7 min", "about 4 min"], xlabel="Minutes per check")
    _panel_title(a1, "Eligibility check time (CAQH)")
    items = [("Benchmark (clean practices)", 4, 4, "", BLUE_RAMP[3]), ("Typical first-pass denials", 8, 15, "", WARM), ("Vendor and podcast claims", 10, 19.3, "", BLUE),
             ("Delta in-network claims, 2024 (podcast analysis)", 22.5, 22.5, "", WARM)]
    _range_bars(a2, items, lambda v: "%g%%" % v, 30, wrap=26)
    a2.set_xlabel("Share of claims", fontsize=7.2, color=INK_SEC)
    _panel_title(a2, "Denial rates")
    items3 = [("Days in AR, average practice", 32, 45, "", BLUE), ("Days in AR, solo practice", 40, 60, "", WARM), ("Appeal windows, days from denial", 90, 180, "", DEEMPH)]
    _range_bars(a3, items3, lambda v: "%d" % v, 330, wrap=24)
    a3.set_xlabel("Days", fontsize=7.2, color=INK_SEC)
    _panel_title(a3, "Receivables and appeals")
    return _save(fig, "verification", FULL_W, h)


def chart_marketing():
    h = 3.6
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "Marketing: cost per tracked lead runs from $7.64 (branded search) to $212.63 (Invisalign) on one agency's 187 campaigns; 61% of surveyed US practices spend $501+ a month and retainers cluster at $1,000-$2,500 (UK £1,500-£8,000+)",
                               "Sources: Delmain, Jun 2026 [%d] (vendor; calls or forms, not booked patients; dentures, cosmetic and Invisalign rows 'thin and directional'); ProSites survey via DrBicuspid, 21 Mar 2022 [%d] (110 practices); RankAI [%d], HIP Agency [%d], ClicksGeek [%d], "
                               "Dominate Dental [%d] (all vendor; the Dominate page showed a 'Hacked by' header when read); Whito [%d] (vendor)." % (
                                   ref("https://delmain.co/blog/dental-patient-acquisition/"),
                                   ref("https://www.drbicuspid.com/dental-practice/patient-communication/marketing/article/15379233/marketing-spending-reaches-new-high-in-2022-survey"),
                                   ref("https://rankai.ai/articles/dental-seo-pricing-guide-costs-factors-roi"), ref("https://hip.agency/dental-marketing-budget-guide-investing-the-right-amount-in-growth/"),
                                   ref("https://clicksgeek.com/white-label-seo-reseller-pricing/"), ref("https://cms.dominatedental.com/?p=467"), ref("https://whito.co.uk/research/uk-dentist-marketing-data/")),
                               ncols=3, width_ratios=[1.15, 0.8, 1.15])
    labels = ["Branded search", "General 'dentist'", "Emergency", "Dentures", "Implants", "Cosmetic", "Invisalign"]
    vals = [7.64, 50.60, 77.62, 87.01, 107.63, 119.62, 212.63]
    _hbar(a1, labels, vals, colors=[BLUE, BLUE, BLUE, DEEMPH, DEEMPH, DEEMPH, DEEMPH], xlim=250, wrap=18,
          labels_override=["$%.2f" % v for v in vals], xlabel="USD per tracked lead (grey = thin rows)")
    _panel_title(a1, "Cost per lead by service (Delmain)")
    _hbar(a2, ["Spend $501+ a month", "Spend $1,000+ a month", "Spend $5,000+ a month"], [61, 35, 4], colors=[BLUE, BLUE, DEEMPH], xlim=75, wrap=18,
          labels_override=["61%", "35%", "under 4%"], xlabel="Share of 110 US practices, Oct 2021")
    _panel_title(a2, "Monthly spend, surveyed")
    items = [("US basic retainer", 750, 1500, "$"), ("US typical retainer", 1000, 2500, "$"), ("US mid retainer", 1500, 3000, "$"), ("US premium retainer", 3000, 5000, "$"),
             ("White-label wholesale, one location", 500, 1500, "$"), ("UK SEO retainer (agency)", 1500, 8000, "£"), ("UK budget, sole dentist", 500, 1500, "£"),
             ("UK budget, 4-6 dentists", 3000, 8000, "£")]
    _range_bars(a3, items, _k, 14000, wrap=26)
    a3.set_xlabel("Monthly, USD or GBP as marked", fontsize=7.2, color=INK_SEC)
    _panel_title(a3, "Retainers and budgets")
    return _save(fig, "marketing", FULL_W, h)


def chart_ocr():
    h = 4.3
    fig, (a1, a2) = _frame(FULL_W, h,
                           "OCR's dental penalties run from $5,000 to $140,000 (2019-2026), mostly for unanswered record requests and review replies, while breaches reach the practice through vendors: Change Healthcare 190 million, Delta Dental 7 million",
                           "Sources: HIPAA Journal penalty list [%d]; HealthITSecurity [%d] (snippet); National Law Review [%d] (snippet); Paubox, 12 Oct 2026 [%d] (vendor); HIPAA Journal on Westend [%d] (Indiana AG, not OCR); LexBlog [%d] (class action); "
                           "breach scale from KrebsOnSecurity [%d], Cybersecurity Dive [%d], Orthodontic Products [%d], Healthcare Finance News [%d], HIPAA Journal [%d] [%d], TEISS [%d]. Not shown: Westend $350,000 (Indiana AG, 2024) and First Choice $1.225m (class action, 2025); the 2019 DDS Safe ransomware hit about 400 practices." % (
                               ref("https://www.hipaajournal.com/hipaa-violation-fines/"), ref("https://healthitsecurity.com/news/ocr-settles-three-hipaa-right-of-access-cases-with-dental-practices"),
                               ref("https://natlawreview.com/node/166110/printable/pdf"), ref("https://www.paubox.com/blog/dental-practice-agrees-to-140k-settlement-after-records-complaint"),
                               ref("https://www.hipaajournal.com/indiana-ag-westend-dental-hipaa-violations/"), ref("https://www.lexblog.com/2025/11/18/dental-practice-settles-data-breach-lawsuit-for-1-2-million/"),
                               ref("https://krebsonsecurity.com/2019/08/ransomware-bites-dental-data-backup-firm/"), ref("https://www.cybersecuritydive.com/news/henry-schein-cyberattack-29k-affected/702036/"),
                               ref("https://orthodonticproductsonline.com/practice-management/it/delta-dental-hack-exposes-sensitive-data/"), ref("https://www.healthcarefinancenews.com/news/190-million-people-affected-change-healthcare-cyberattack"),
                               ref("https://www.hipaajournal.com/absolute-dental-data-breach/"), ref("https://www.hipaajournal.com/data-breaches-oral-healthcare-practices/"),
                               ref("https://www.teiss.co.uk/news/new-jersey-dental-care-practice-says-data-breach-impacted-close-to-75000-patients-14395")),
                           ncols=2, width_ratios=[1.15, 1])
    pens = [("2019  Elite Dental (review reply)", 10), ("2022  Bell DDS (right of access)", 5), ("2022  New Vision (Yelp replies)", 23),
            ("2022  Hardy / Paradise (access)", 25), ("2022  Family Dental Care (access)", 30), ("2022  Brockley (access)", 30),
            ("2022  Igbinadolor (review reply)", 50), ("2022  Northcutt (patient list)", 62.5), ("2022  Great Expressions (access fee)", 80),
            ("2024  Gums Dental (timely access)", 70), ("2026  Shen Smiles (no policies)", 140)]
    _hbar(a1, [p[0] for p in pens], [p[1] for p in pens], colors=[BLUE] * 10 + [WARM], xlim=165, wrap=40,
          labels_override=["$%gk" % p[1] for p in pens], xlabel="USD thousands (OCR settlements and civil money penalties)")
    _panel_title(a1, "OCR penalties on dental practices")
    br = [("Totem Lake (2025-26)", 3400), ("West Texas OFS (2025)", 11151), ("360 Dental (2025-26)", 11273), ("Westend Dental (2020)", 17000),
          ("32 Pearls (2025)", 23517), ("Henry Schein (2023)", 29112), ("New Jersey OMS (2025-26)", 74413), ("First Choice Dental (2023)", 150000),
          ("Absolute Dental, MSP (2025)", 1223635), ("Delta Dental CA, MOVEit (2023)", 7000000), ("Change Healthcare (2024)", 190000000)]
    n = len(br)
    y = list(range(n))[::-1]
    a2.barh(y, [b[1] for b in br], color=[BLUE] * 8 + [WARM, WARM, WARM], height=0.58, edgecolor="white")
    a2.set_xscale("log")
    a2.set_xlim(1000, 3e9)
    for yi, (lab, v) in zip(y, br):
        a2.text(v * 1.3, yi, format(v, ","), va="center", fontsize=7, color=INK2)
    a2.set_yticks(y)
    a2.set_yticklabels([_wrap(b[0], 32) for b in br], fontsize=7.1, color=INK2)
    a2.tick_params(axis="y", length=0)
    a2.set_xticks([1e4, 1e6, 1e8])
    a2.set_xticklabels(["10k", "1m", "100m"], fontsize=7)
    a2.set_xlabel("People affected (log scale)", fontsize=7, color=INK_SEC)
    a2.spines["left"].set_color(DEEMPH)
    a2.set_ylim(-0.65, n - 0.35)
    _panel_title(a2, "Breach sizes, dental and dental vendors")
    return _save(fig, "ocr", FULL_W, h)


def chart_security():
    h = 3.0
    fig, ax = _frame(FULL_W, h,
                     "Everyday security at UK dental practices: 48% run out-of-date operating systems, 25% share logins, 20% expose remote access and 17% have failing or absent backups",
                     "Source: Dental IT, 30 Jul 2026 [%d] (vendor; 192 on-site audits at 184 dental and orthodontic practices, median three surgeries; antivirus assessed at a subset). Cases: RDP 'left open to the entire internet'; "
                     "'Every member of staff logged in with the same password: Password1!'; nightly backup logs reading 'backed up files: 0'." % (
                         ref("https://www.dentalit.ltd.uk/assets/files/state-of-dental-practice-it.pdf")))
    labels = ["Out-of-date Windows or server OS (Windows 7 in 40 practices)", "Slow or unreliable internet", "Antivirus inadequate or none (where assessable)",
              "No proper server (a desktop 'pressed into service')", "Generic shared logins or weak passwords", "Exposed or unmanaged remote access",
              "Consumer router with no real firewall", "Backups failing, partial or absent", "Wi-Fi shared with patients"]
    vals = [48, 45, 43, 29, 25, 20, 20, 17, 9]
    _hbar(ax, labels, vals, colors=[WARM, BLUE, BLUE, BLUE, WARM, WARM, BLUE, WARM, BLUE], xlim=58, wrap=64, height=0.6, xlabel="Share of audited practices")
    return _save(fig, "security", FULL_W, h)


def chart_job_ads():
    h = 3.4
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "Job ads: US front-office pay runs $15-$42 an hour, UK receptionists and nurses earn £13.92-£17 an hour, and 49 of 188 DentalPost front-office titles name treatment, patient-care, insurance or billing roles",
                               "Sources: DentalPost front-office listings [%d] [%d] [%d]; MB2 Dental job [%d]; Upwork job [%d] (snippet); OnlineJobs.ph [%d]; Indeed UK salaries [%d] [%d]; Reed [%d]; Rodericks [%d] (snippet); BDJ Jobs [%d] (snippet). "
                               "Salaried US front-office roles $30,000-$80,000; UK receptionist £21,840-£24,465 and practice manager £28,000-£40,000 a year. Title counts are from the 188 DentalPost listings read, not board-wide statistics." % (
                                   ref("https://www.dentalpost.net/dental-jobs/dental-front-office-jobs/"), ref("https://www.dentalpost.net/dental-jobs/job-post/557606/dental-front-office-job-in-san-antonio-tx/"),
                                   ref("https://www.dentalpost.net/dental-jobs/job-post/557359/endodontic-dental-front-office-job-in-the-woodlands-tx/"),
                                   ref("https://dentalcareers-mb2dental.icims.com/jobs/21339/insurance-verification-specialist/job"), ref("https://www.upwork.com/jobs/~022067110157780444776"),
                                   ref("https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword=dental"), ref("https://uk.indeed.com/career/dental-nurse/salaries"),
                                   ref("https://uk.indeed.com/career/dental-receptionist/salaries"), ref("https://www.reed.co.uk/jobs/dental-nurse-jobs"),
                                   ref("https://careers.rodericksdentalpartners.co.uk/jobs/job/Receptionist/6952"), ref("https://www.bdjjobs.com/job/535611/practice-manager/")),
                               ncols=3, width_ratios=[1.1, 1.05, 0.85])
    items = [("DentalPost front office, hourly range", 15, 42, "$"), ("San Antonio front-office coordinator", 20, 25, "$"), ("Front office (BLS-cited ads)", 18, 30, "$"),
             ("DSO insurance verification specialist", 22, 27, "$"), ("Upwork breakdown-of-benefits sellers", 5, 20, "$"), ("Philippine dental VA", 5, 8, "$")]
    _range_bars(a1, items, lambda v: "%g" % v, 50, wrap=28)
    a1.set_xlabel("USD per hour", fontsize=7.2, color=INK_SEC)
    _panel_title(a1, "US ads: hourly pay")
    items2 = [("Dental receptionist (Indeed average)", 13.92, 13.92, "£"), ("Dental nurse (Indeed average)", 14.73, 14.73, "£"), ("Dental nurse in ads", 14, 17, "£"),
              ("Hygienist (Indeed average)", 38.96, 38.96, "£")]
    _range_bars(a2, items2, lambda v: "%g" % v, 48, wrap=26)
    a2.set_xlabel("GBP per hour", fontsize=7.2, color=INK_SEC)
    _panel_title(a2, "UK ads: hourly pay")
    _hbar(a3, ["'Treatment', financial or insurance coordinator", "'Patient Care' or 'New Patient Coordinator'", "Insurance, billing or financial"], [25, 15, 9],
          colors=[BLUE, BLUE, BLUE], xlim=30, wrap=22, fmt="{:.0f}", xlabel="Of 188 listings")
    _panel_title(a3, "US title counts")
    return _save(fig, "job_ads", FULL_W, h)


def chart_freelance():
    h = 3.9
    fig, (a1, a2) = _frame(FULL_W, h,
                           "Freelance market: posting and verification labour at $4-$8 an hour, AI-receptionist builders at $30-$61, and the only mid-four-figure budgets in custom voice-agent builds ($2,500-$8,000) and integration ($800-$3,000)",
                           "Sources: Upwork AI receptionist builders [%d] (snippet); Upwork dental voice agent gig [%d] (snippet); Upwork automation post [%d] (snippet); Upwork Open Dental posting [%d] (snippet); Upwork BOB job [%d] (snippet); Upwork SEO/PPC post [%d] (snippet); "
                           "OnlineJobs.ph 1335685 [%d]; Fiverr [%d] (snippet); PeoplePerHour [%d]; Open Dental fees [%d] (vendor); Clutch [%d]; Consulting Success [%d] (secondary); Dominate Dental [%d] (vendor)." % (
                               ref("https://www.upwork.com/hire/ai-receptionist-builders/"), ref("https://www.upwork.com/services/product/development-it-an-ai-voice-agent-for-a-dental-clinic-1879449985699609816"),
                               ref("https://www.upwork.com/freelance-jobs/apply/Automation-Specialist-for-Dental-Clinics_~022057415977014134702/"), ref("https://www.upwork.com/jobs/~022059644914653616103"),
                               ref("https://www.upwork.com/jobs/~022067110157780444776"), ref("https://www.upwork.com/freelance-jobs/apply/SEO-PPC-Specialist-for-Dental-Practice-Growth-Long-Term-Partnership_~022098259096248695102/"),
                               ref("https://www.onlinejobs.ph/jobseekers/job/1335685"), ref("https://block.fiverr.com/gigs/dentist"), ref("https://www.peopleperhour.com/hire-freelancers?q=dental"),
                               ref("https://www.opendental.com/site/fees.html"), ref("https://clutch.co/agencies/dental"), ref("https://www.consultingsuccess.com/consulting-hourly-rate"),
                               ref("https://cms.dominatedental.com/?p=467")),
                           ncols=2, width_ratios=[1, 1])
    hourly = [("Open Dental posting on Upwork (30+ h/wk)", 4, 7, "$"), ("Philippine dental VA", 5, 8, "$"), ("BOB sellers on Upwork (50+ proposals)", 5, 20, "$"),
              ("SEO/PPC for a practice, Upwork", 10, 35, "$"), ("Voice and chat receptionist, agency job", 20, 45, "$"), ("AI receptionist builders, Upwork", 30, 61, "$"),
              ("Open Dental training (vendor)", 80, 80, "$"), ("Dental agencies on Clutch", 100, 149, "$"), ("Open Dental custom SQL (vendor)", 110, 110, "$"),
              ("General IT consulting", 100, 300, "$"), ("UK marketing consultation", 75, 200, "£")]
    _range_bars(a1, hourly, lambda v: "%d" % v, 360, wrap=40)
    a1.set_xlabel("Per hour (USD or GBP as marked)", fontsize=7.2, color=INK_SEC)
    _panel_title(a1, "Hourly rates")
    fixed = [("Fiverr SEO articles, from", 10, 10, "$"), ("'Automation Specialist' post, Upwork", 50, 50, "$"), ("Fiverr dental websites", 80, 425, "$"),
             ("PeoplePerHour dental websites", 235, 1000, "$"), ("Google Ads management, PeoplePerHour", 450, 450, "$"), ("No-code AI receptionist set-up", 500, 1500, "$"),
             ("Philippine dental VA (monthly)", 600, 700, "$"), ("'AI Voice Agent for a Dental Clinic' gig", 700, 700, "$"), ("CRM and telephony integration", 800, 3000, "$"),
             ("Custom voice-agent build", 2500, 8000, "$"), ("Multi-location roll-out", 4000, 12000, "$")]
    _range_bars(a2, fixed, _k, 19000, wrap=40)
    a2.set_xlabel("Fixed price or monthly, USD", fontsize=7.2, color=INK_SEC)
    _panel_title(a2, "Fixed-price work")
    return _save(fig, "freelance", FULL_W, h)


def chart_platforms():
    h = 4.5
    fig, (a1, a2) = _frame(FULL_W, h,
                           "Platforms: review scores run from Fuse 3.2 to Oryx 4.9 and Open Dental is the only US PMS with fully published prices ($149-$199 a month); UK Dentally lists £125-£346 a surgery and everyone else quotes",
                           "Sources: Capterra, G2, GetApp, Software Advice and Trustpilot pages as seen in search snippets [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d]; vendor price pages [%d] [%d] [%d] [%d]; CostBench estimates [%d] (secondary); Whito [%d] (secondary)." % (
                               ref("https://www.capterra.com/p/2329/Dentrix/reviews/"), ref("https://capterra.com/p/177828/Dentrix-Ascend/reviews/"), ref("https://www.softwareadvice.com/dental/eaglesoft-profile/reviews/"),
                               ref("https://www.capterra.com/p/122350/Open-Dental/reviews/"), ref("https://www.capterra.com/p/98688/Curve-Dental-Hero/reviews/"), ref("https://www.capterra.ie/reviews/35009/denticon"),
                               ref("https://www.getapp.com/all-software/a/sensei-cloud/"), ref("https://www.g2.com/products/patterson-dental-fuse/reviews"), ref("https://www.trustpilot.com/review/getweave.com"),
                               ref("https://www.capterra.com/p/182271/NexHealth/reviews/"), ref("https://capterra.com/p/160916/Solutionreach/reviews/?page=5"), ref("https://www.capterra.co.uk/software/153816/dentally"),
                               ref("https://www.opendental.com/site/fees.html"), ref("https://www.getweave.com/pricing/"), ref("https://www.dentally.com/pricing"), ref("https://dengro.com/pricing"),
                               ref("https://costbench.com/stats/dental-software-pricing-2026/"), ref("https://whito.co.uk/for/dentists/best-software-for-uk-dentists/")),
                           ncols=2, width_ratios=[1, 1.1])
    tp = [("Oryx (G2, 22-29)", 4.85), ("Aerona UK (Capterra, 22)", 4.8), ("NexHealth (Capterra, 31)", 4.7), ("Adit (Capterra, 300)", 4.7), ("Zuub (Capterra, 38)", 4.7),
          ("Open Dental (Capterra, 88)", 4.6), ("Weave (Trustpilot, 956)", 4.6), ("Dental Intelligence (Capterra, 53)", 4.6), ("Denticon (Capterra, 118)", 4.5),
          ("Curve (Capterra, 285)", 4.4), ("RevenueWell (Capterra, 83)", 4.4), ("Dentrix (Capterra, 376)", 4.3), ("Dentrix Ascend (Capterra, 235)", 4.1),
          ("Eaglesoft (Software Advice)", 4.1), ("Exact UK (Capterra, 17)", 4.1), ("Solutionreach (Capterra, 236)", 3.8), ("Sensei Cloud (GetApp, 31)", 3.7),
          ("Dentally UK (Capterra, 18)", 3.6), ("Fuse (G2, 4)", 3.2)]
    _hbar(a1, [t[0] for t in tp], [t[1] for t in tp], colors=[BLUE] * 15 + [WARM] * 4, fmt="{:.1f}", xlim=5.5, wrap=36, height=0.6, xlabel="Score of 5 (review count in brackets)")
    _panel_title(a1, "Review scores")
    price = [("Open Dental, per location (published)", 149, 199, "$"), ("Dentrix on-premise (estimate)", 400, 1200, "$"), ("Dentrix Ascend (estimate)", 500, 500, "$"),
             ("Eaglesoft (estimate)", 350, 1000, "$"), ("Curve (estimate)", 299, 599, "$"), ("Denticon (estimates)", 199, 750, "$"), ("Weave, from (published)", 199, 199, "$"),
             ("Podium (about)", 299, 299, "$"), ("Jarvis, per user (listed)", 350, 350, "$"), ("Dental Intelligence, per user (est.)", 399, 399, "$"),
             ("AI receptionist, per location (est.)", 300, 900, "$"), ("Dentally, one surgery (ex VAT)", 125, 346, "£"), ("Sensei Cloud UK, per licence", 135, 185, "£"),
             ("DenGro, per practice (inc VAT)", 199, 249, "£"), ("Aerona (Capterra tiers)", 45, 110, "£"), ("Bridge-IT cloud, per surgery", 40, 80, "£")]
    _range_bars(a2, price, _k, 2000, wrap=38)
    a2.set_xlabel("Monthly, USD or GBP as marked", fontsize=7.2, color=INK_SEC)
    _panel_title(a2, "Monthly price points")
    return _save(fig, "platforms", FULL_W, h)


GAP_POS = [
    (1, "NHS contract reconciliation (FP17, Compass, 96% floor, urgent split)", 4.05, 3.05),
    (2, "Unscheduled-treatment follow-up and case-acceptance exceptions", 4.05, 2.0),
    (3, "Lead-to-seated-patient measurement across CRM, calls and PMS", 3.05, 3.1),
    (4, "Denial rework, appeal packs and timely-filing deadlines", 3.35, 2.0),
    (5, "Website and ad compliance checks (GDC, ASA, FTC, TCPA, Google)", 3.35, 2.72),
    (6, "Patient record requests and retention clocks", 3.0, 2.65),
    (7, "Eligibility breakdown reconciliation and difficult payers", 4.15, 1.55),
    (8, "Recall-list validation and reactivation segmentation", 3.3, 1.65),
    (9, "PMS data clean-up and cross-system reconciliation", 2.66, 2.85),
    (10, "UK exemption-evidence capture and PCN dispute handling", 2.36, 3.05),
    (11, "Estimate, good-faith estimate and consent completeness", 2.5, 2.55),
    (12, "Clinical-note quality and AI-scribe governance", 1.75, 2.7),
    (13, "Security baseline and cyber-insurance readiness evidence", 3.02, 2.0),
]
CROWDED_POS = [("a", "AI phone receptionists and call intelligence", 3.0, 0.5), ("b", "Dental SEO, websites and Google Ads management", 3.2, 0.5),
               ("c", "Review generation, monitoring and texting", 3.4, 0.5), ("d", "Appointment reminders and confirmations", 3.6, 0.5),
               ("e", "Insurance-verification keystrokes and outsourced billing", 4.05, 0.5), ("f", "Imaging AI (FDA-cleared, venture-funded)", 1.75, 0.5),
               ("g", "PMS set-up gigs and VA agencies", 1.75, 1.0), ("h", "Membership-plan platforms; credentialing services", 2.25, 1.0)]


def chart_gap_matrix():
    w, h = FULL_W, 5.0
    fig, (ax, key) = _frame(w, h,
                            "Gap map: the thirteen gaps placed by problem signal against vendor weakness, using the report's own ranking words; eight crowded areas in grey",
                            "Positions follow the wording of the ranking table in section 10 (very high / high / medium-high / medium signal; weak / thin / partial / strong on part / very strong coverage), not measured scores. "
                            "Warm = coverage weak or thin; blue = partial or strong on the easy part; grey letters = the crowded areas the report says are not gaps.",
                            ncols=2, width_ratios=[1.3, 1])
    ax.set_xlim(1.5, 4.5)
    ax.set_ylim(0.1, 3.5)
    ax.axhline(2.35, color=GRID, linewidth=0.8, zorder=0)
    ax.axvline(2.85, color=GRID, linewidth=0.8, zorder=0)
    ax.text(4.45, 3.44, "strong signal, weak vendor coverage", ha="right", va="top", fontsize=7, color=INK_SEC)
    ax.text(1.55, 0.16, "weaker signal, crowded", ha="left", va="bottom", fontsize=7, color=INK_SEC)
    for r, name, x, y in GAP_POS:
        ax.scatter([x], [y], s=210, color=WARM if y >= 2.5 else BLUE, zorder=3, edgecolor="white", linewidth=1.4)
        ax.text(x, y, str(r), ha="center", va="center", fontsize=7.2 if r < 10 else 6.4, color="white", fontweight="bold", zorder=4)
    for letter, name, x, y in CROWDED_POS:
        ax.scatter([x], [y], s=190, color=DEEMPH, zorder=3, edgecolor="white", linewidth=1.4)
        ax.text(x, y, letter, ha="center", va="center", fontsize=7.2, color=INK2, fontweight="bold", zorder=4)
    ax.set_xticks([1.75, 2.55, 3.2, 4.05])
    ax.set_xticklabels(["medium", "medium-high", "high", "very high"], fontsize=6.8)
    ax.set_yticks([0.5, 1.0, 1.6, 2.0, 2.7, 3.0])
    ax.set_yticklabels(["very strong\n(crowded)", "strong", "strong on\nthe easy part", "partial /\nmedium", "thin", "weak"], fontsize=7)
    ax.set_xlabel("Problem signal (findings, enforcement, complaints, demand)", fontsize=7.2, color=INK_SEC)
    ax.set_ylabel("Vendor coverage of the exact sub-problem", fontsize=7.2, color=INK_SEC)
    ax.tick_params(length=0)
    key.axis("off")
    key.set_xlim(0, 1)
    key.set_ylim(0, 1)
    key.text(0, 1.0, "Key (rank. gap)", fontsize=7.6, fontweight="bold", color=INK, va="top")
    yy = 0.945
    step = 0.041
    for r, name, x, y in GAP_POS:
        key.scatter([0.035], [yy], s=105, color=WARM if y >= 2.5 else BLUE, edgecolor="white", linewidth=1, clip_on=False)
        key.text(0.035, yy, str(r), ha="center", va="center", fontsize=6.9 if r < 10 else 6.2, color="white", fontweight="bold")
        key.text(0.1, yy, name, fontsize=7, color=INK2, va="center")
        yy -= step
    yy -= 0.01
    key.text(0, yy, "Crowded areas (not gaps)", fontsize=7.4, fontweight="bold", color=INK_SEC, va="center")
    yy -= step
    for letter, name, x, y in CROWDED_POS:
        key.scatter([0.035], [yy], s=85, color=DEEMPH, edgecolor="white", linewidth=1, clip_on=False)
        key.text(0.035, yy, letter, ha="center", va="center", fontsize=6.9, color=INK2, fontweight="bold")
        key.text(0.1, yy, name, fontsize=7, color=INK_SEC, va="center")
        yy -= step
    return _save(fig, "gap_matrix", w, h)


def chart_pay_employed():
    h = 4.4
    fig, ax = _frame(FULL_W, h,
                     "Employed pay: US dental-AI engineering at $145,000-$240,000 (Overjet median $195,000, VideaHealth $175,000), horizontal dental SaaS at $110,000-$170,000, DSO IT at $75,000-$190,000; UK dental software £46,000-£88,000",
                     "Sources: US Department of Labor H-1B filings via Ellis for Overjet [%d], VideaHealth [%d], Weave [%d], Henry Schein One [%d], PDS Health [%d], Heartland [%d], Dentsply Sirona [%d]; Glassdoor UK for Henry Schein One [%d] and Software of Excellence [%d] (snippets, self-reported). "
                     "Overjet listed 31 open roles on 16 Oct 2026, three in R&D engineering, all San Mateo or Lahore." % (
                         ref("https://www.ellis.com/visa-sponsors/overjet-inc/salaries"), ref("https://www.ellis.com/visa-sponsors/videahealth-inc/salaries"), ref("https://www.ellis.com/visa-sponsors/weave-communications-inc/salaries"),
                         ref("https://www.ellis.com/visa-sponsors/henry-schein-one-llc/salaries"), ref("https://www.ellis.com/visa-sponsors/pacific-dental-services-llc/salaries"), ref("https://www.ellis.com/visa-sponsors/heartland-dental-llc/salaries"),
                         ref("https://www.ellis.com/visa-sponsors/dentsply-sirona-inc/salaries"), ref("https://www.glassdoor.co.uk/Salary/Henry-Schein-One-Salaries-E7869334.htm"), ref("https://www.glassdoor.co.uk/Salary/Software-of-Excellence-Salaries-E3047761.htm")))
    items = [("Overjet, Staff Software Engineer", 225, 225, "$"), ("Overjet, Senior ML Scientist", 205, 205, "$"), ("Overjet, Data Engineer", 203, 203, "$"),
             ("Overjet, median of filings", 195, 195, "$"), ("Heartland Dental, Senior Data Engineer", 187.257, 187.257, "$"), ("VideaHealth, median of filings", 175, 175, "$"),
             ("Overjet, ML Engineer", 145.6, 160, "$"), ("Weave, median of filings", 147.183, 147.183, "$"), ("PDS Health, Engineer, AI Solutions", 140, 140, "$"),
             ("Delta Dental (insurer), range", 99, 154, "$"), ("Henry Schein One, median of filings", 120.7, 120.7, "$"), ("Henry Schein One, Staff SWE ad ('Remote from US')", 110, 145, "$"),
             ("Dentsply Sirona, AI/ML Engineer median", 90.854, 90.854, "$"), ("Heartland Dental, Data Integration Engineer", 75, 95, "$"),
             ("UK HSO and Software of Excellence, senior engineers", 63, 88, "£"), ("UK HSO and Software of Excellence, software engineers", 46, 75, "£")]
    _range_bars(ax, items, lambda v: ("%dk" % v) if v == int(v) else ("%.1fk" % v), 275, wrap=56)
    ax.set_xlabel("Annual base pay, thousands (USD or GBP as marked)", fontsize=7.2, color=INK_SEC)
    return _save(fig, "pay_employed", FULL_W, h)


def chart_flow():
    w, h = FULL_W, 5.2
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    title = _wrap("The UK exemption-to-clean-FP17 cycle: the software sends and flags, the practice reconciles, and four steps stay with a named person by law", TITLE_WRAP)
    src = _wrap("Sources: NHSBSA exemption checking guide [%d]; NHSBSA FAQ KA-01916 [%d], KA-01820 [%d], KA-01672 [%d]; FP17 completion guidance V11.4 [%d]; NHSBSA common errors [%d]; UDA Pulse [%d] (secondary); GDPUK, 13 Jul 2026 [%d]; "
                "ICLR, Balachandra 2026 [%d]; gov.uk algorithmic transparency record [%d]; NAO 2019 [%d]. US parallel: eligibility 270/271 pulls are electronic but the interpretation, the clinical narrative on an appeal and the signature stay human (section 6)." % (
                    ref("https://www.nhsbsa.nhs.uk/sites/default/files/2022-03/Patient_exemption_checking_guide_dental_V3%20_08_2021.pdf"), ref("https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01916/en-us"),
                    ref("https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01820/en-us"), ref("https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01672/en-us"),
                    ref("https://www.nhsbsa.nhs.uk/sites/default/files/2022-11/Completion_of_form_guidance-FP17-England_202210_V11.4_Final.pdf"),
                    ref("https://www.nhsbsa.nhs.uk/sites/default/files/2022-09/Common_Errors_FP17W_from_1_April_2022_FINAL.pdf"), ref("https://udapulse.co.uk/nhs-contract-guide/"),
                    ref("https://www.gdpuk.com/news/news-in-focus/compass-without-direction-practices-unclear-on-uda-achievement/"), ref("https://www.iclr.co.uk/document/2026001068/2026ewhc294kb_TNA/html"),
                    ref("https://www.gov.uk/algorithmic-transparency-records/nhsbsa-prescriptions-and-dental-exemption-check"), ref("https://www.nao.org.uk/report/investigation-into-healthcare-penalty-charge-notices/")), SRC_WRAP)
    fig.text(0.005, 0.99, title, ha="left", va="top", fontsize=8.6, fontweight="bold", color=INK, linespacing=1.25)
    fig.text(0.005, 0.01, src, ha="left", va="bottom", fontsize=7, color=MUTED, linespacing=1.2)
    steps = [
        ("1  Patient signs the FP17PR declaration", "HUMAN ACT. Before treatment begins; paper or certified e-signature only; kept two years; no scan-and-destroy. Liability for the exemption sits with the patient.", True),
        ("2  Exemption evidence asked, noted, 'evidence seen' ticked", "HUMAN ACT. Certificate and expiry noted; 'No' ticked if nothing shown; staff told not to advise on entitlement (DDU). Tax-credit exemption invalid from 6 Apr 2025.", True),
        ("3  Band charge collected or HC5(D) given", "£27.90 / £76.60 / £332.10; unsure patients pay and get a refund form. NHSBSA nets charges off the monthly contract payment.", False),
        ("4  Clinical data set, BPE, NICE interval, band; dentist's declaration", "HUMAN ACT. 'Must be completed by a qualified dentist on every form'; the band follows the clinical data set; one FP17 per course.", True),
        ("5  FP17 sent by EDI; Compass acknowledges or flags", "Within 2 months of completion or the UDAs are disallowed; corrected claims also inside the window; comment codes 011-014; errors 115 and 125 reject; 48 hours to process.", False),
        ("6  Monthly schedule, DCS129 and DCS127 reconciled", "Payment notification, UDA summary and patient-level activity checked against takings and performer splits; NHSBSA 'unable to advise on EDI transmission issues'.", False),
        ("7  Track the 96% floor, 102% cap and 8.2% urgent share", "Compass shows only the £15 element of the £75 urgent credit; 30 Sep checkpoint for 30% of the urgent requirement; below 96% recovered in full.", False),
        ("8  SD86c year-end statement; sample exemption checks; PCNs", "HUMAN ACT. SD86c arrives around July with two months to dispute; NHSBSA checks DWP records later and sends £100 penalties, about 30% withdrawn; enquiry letters return to the desk.", True),
    ]
    bw, bh = 22.6, 34
    xs = [1.5, 26.3, 51.1, 75.9]
    rows_y = [51, 12]
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
        ax.text(x + 1.3, y + bh - 1.6 - 2.9 * nl - 1.0, _wrap(sub, 27), ha="left", va="top", fontsize=7,
                color=INK2, zorder=3, linespacing=1.08)
    for i in range(3):
        ax.add_patch(FancyArrowPatch((xs[i] + bw + 0.3, rows_y[0] + bh / 2), (xs[i + 1] - 0.3, rows_y[0] + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    ax.add_patch(FancyArrowPatch((xs[3] + bw / 2, rows_y[0] - 0.3), (xs[3] + bw / 2, rows_y[1] + bh + 0.3),
                                 arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    for i in range(3, 0, -1):
        ax.add_patch(FancyArrowPatch((xs[i] - 0.3, rows_y[1] + bh / 2), (xs[i - 1] + bw + 0.3, rows_y[1] + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    ax.text(1.5, 48.5, "Warm box = a signature, declaration, tick or dispute that the law keeps with the patient or the dentist.",
            fontsize=7, color=WARM_TEXT, va="center")
    path = CHART_DIR / "flow.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return (path, w, h)


def build_charts():
    out = {}
    for fn in (chart_funnel, chart_ranges, chart_us_economics, chart_staffing, chart_nhs, chart_verification, chart_marketing,
               chart_ocr, chart_security, chart_job_ads, chart_freelance, chart_platforms, chart_gap_matrix, chart_pay_employed, chart_flow):
        path, w, h = fn()
        out[path.stem] = (path, w, h)
    return out


# ==========================================================================
# Content, part A: cover, contents, "Read this first", sections 1 to 4.
# ==========================================================================
U.update({
    "pp_report": "https://www.patientprism.com/report/dental-patient-access-report/",
    "hso_catalyst": "https://henryscheinone.com/insights/ebook/2026-catalyst-index",
    "hso_unsched": "https://www.henryscheinone.com/insights/blogs/average-providers-are-losing-hundreds-of-thousands-in-unscheduled-treatment",
    "ada_trends": "https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/dental-practice-trends",
    "beckers_goodbad": "https://www.beckersdental.com/dentists/good-news-bad-news-for-dentists/",
    "beckers_hpi": "https://www.beckersdental.com/?p=21392",
    "drb_models": "https://www.drbicuspid.com/dental-practice/office-management/practice-trends/article/15683050/how-dentistrys-practice-models-continue-to-evolve",
    "de_levin": "https://www.dentaleconomics.com/practice/overhead-and-profitability/article/55280684/higher-production-helps-offset-chronic-overhead-increases",
    "de_2025": "https://www.dentaleconomics.com/practice/article/55368689/findings-from-the-2025-dental-economics-levin-group-annual-practice-survey",
    "clerri_overhead": "https://clerri.com/blog/dental-practice-overhead-statistics/",
    "ada_q1": "https://www.ada.org/-/media/project/ada-organization/ada/ada-org/files/resources/research/hpi/state_us_dental_economy_q12026.pdf",
    "ohg": "https://www.oralhealthgroup.com/clinical/dental-industry-2/u-s-dental-practices-face-a-fiscal-squeeze-heading-into-2026-here-are-the-top-10-signals-1003993045/",
    "dentemax_faq": "https://www.dentemax.com/clients/resources/faq",
    "ada_medicaid": "https://adanews.ada.org/ada-news/2025/december/dental-care-utilization-stagnant-among-medicaid-beneficiaries/",
    "thriving": "https://www.thrivingdentist.com/the-less-obvious-practice-overhead-expenses-that-need-to-be-reviewed/",
    "ada_hyg": "https://www.ada.org/resources/research/health-policy-institute/dentist-workforce/dental-hygienist-shortage",
    "gdc_register": "https://www.gdc-uk.org/news-blogs/news/detail/2026/05/07/internationally-qualified-dentists-outnumber-uk-qualified-dentists-joining-gdc-register-for-first-time",
    "bda_ddrb": "https://www.bda.org/media/lm1nw32p/ddrb-26-27-round-bda-submission.pdf",
    "dent_vacancies": "https://dentistry.co.uk/2024/11/15/one-fifth-of-nhs-general-dentist-positions-unfilled-data-shows/",
    "dent_loyal": "https://dentistry.co.uk/2026/03/31/dentistry-is-the-uks-most-loyal-profession/",
    "indeed_nurse": "https://uk.indeed.com/career/dental-nurse/salaries",
    "dent_nurses2024": "https://dentistry.co.uk/?p=407492",
    "ada_covid": "https://adanews.ada.org/ada-news/2025/february/five-years-later-staffing-shortages-infection-control-since-the-covid-19-pandemic/",
    "ada_ai": "https://www.ada.org/resources/research/health-policy-institute/dental-practice-research/dentists-ai-usage-and-attitudes",
    "pmc_burnout": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12334352/",
    "gdpuk_tenth": "https://www.gdpuk.com/news/one-in-ten-practices-have-ceased-general-nhs-dentistry-since-2017/",
    "probe_oct": "https://the-probe.co.uk/blog/2026/10/the-system-is-moving-but-is-it-changing/",
    "nhsbsa_stats": "https://www.nhsbsa.nhs.uk/statistical-collections/dental-england/dental-statistics-england-202425",
    "gpps": "https://www.england.nhs.uk/statistics/statistical-work-areas/gp-patient-survey-dental-statistics-january-to-march-2025-england/",
    "gdpuk_uda": "https://www.gdpuk.com/news/news-in-focus/does-size-matter-corporate-versus-independent-uda-rates/",
    "ka_01672": "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01672/en-us",
    "dent_clawback": "https://dentistry.co.uk/2026/03/05/nhs-contract-clawback-at-900-million-in-past-two-years/",
    "gdpuk_blog": "https://www.gdpuk.com/blogs/guest-contributors/entry/2391-nhs-contract-changes-what-they-said-and-what-they-meant",
    "pmc_focus": "https://pmc.ncbi.nlm.nih.gov/articles/PMC12065166/",
    "dent_income": "https://dentistry.co.uk/2026/08/03/dentists-taxable-income-rises-across-uk-with-scotland-nearing-100000/",
    "gdpuk_compass": "https://www.gdpuk.com/news/news-in-focus/compass-without-direction-practices-unclear-on-uda-achievement/",
    "pricebailey": "https://www.pricebailey.co.uk/blog/nhs-contract-changes-cma-review-dental-practices/",
    "gdpuk_reduce": "https://www.gdpuk.com/news/nearly-two-thirds-of-dentists-expect-to-reduce-nhs-work-bda-finds/",
    "gdpuk_private": "https://www.gdpuk.com/news/latest-news/4858-61-of-nhs-patients-would-consider-private-alternatives",
    "dent_safer": "https://dentistry.co.uk/2025/10/27/has-there-ever-been-a-safer-time-to-leave-nhs-dentistry/",
    "dent_dcs": "https://dentistry.co.uk/2025/03/20/complaints-about-private-dentistry-rise-by-133-in-one-year/",
    "dent_ftp": "https://dentistry.co.uk/2026/06/03/gdc-fitness-to-practise-concerns-rise-2025/",
    "gdpuk_which": "https://www.gdpuk.com/news/which-raises-concerns-over-private-dental-complaints-process/",
    "treatcompare": "https://www.treatcompare.com/articles/private-dental-check-up-cost-uk",
    "bdj_stress": "https://www.nature.com/articles/s41415-026-9615-9",
    "dentemax_calls": "https://www.dentemax.com/dentists/blog-articles/2025/Why_missed_phone_calls_are_dental_offices_largest_revenue_loss",
    "dt_frontdesk": "https://www.dentaltown.com/channel/post/26399/your-marketing-isnt-broken-your-front-desk-is",
    "peerlogic": "https://www.peerlogic.com/post/peerlogic-dso-case-study",
    "ainora_noshow": "https://ainora.lt/blog/dental-no-show-statistics-ai-reduction",
    "hw_sussex": "https://nds.healthwatch.co.uk/sites/default/files/reports_library/20220311_East%20Sussex_Mystery%20Shopping%20of%20Dental%20Practices%20in%20East%20Sussex.pdf",
    "dent_dengro": "https://dentistry.co.uk/2019/05/22/half-dental-practices-missing-leads/",
    "ainora_recall": "https://ainora.lt/blog/dental-recall-reactivation-statistics-benchmarks",
    "act_unsched": "https://www.actdental.com/blog/data-snapshot-unscheduled-active-patients",
    # section 2
    "reed_nurse": "https://www.reed.co.uk/jobs/dental-nurse-jobs",
    "dentalpost_fo": "https://www.dentalpost.net/dental-jobs/dental-front-office-jobs/",
    "nhsbsa_activity": "https://www.nhsbsa.nhs.uk/activity-processing-and-payment-services",
    "ada_cdt_gloss": "https://www.ada.org/publications/cdt/glossary-of-dental-clinical-terms",
    "gs_fta": "https://suggestqueries.google.com/complete/search?client=firefox&hl=en-GB&gl=uk&q=dental+fta",
    "gs_noshow": "https://suggestqueries.google.com/complete/search?client=firefox&q=dental+office+no+shows",
    "dp_557606": "https://www.dentalpost.net/dental-jobs/job-post/557606/dental-front-office-job-in-san-antonio-tx/",
    "dp_557359": "https://www.dentalpost.net/dental-jobs/job-post/557359/endodontic-dental-front-office-job-in-the-woodlands-tx/",
    "rodericks_rec": "https://careers.rodericksdentalpartners.co.uk/jobs/job/Receptionist/6952",
    "findajob": "https://findajob.dwp.gov.uk/details/17683574",
    "bdj_pm": "https://www.bdjjobs.com/job/535611/practice-manager/",
    "indeed_cqc": "https://uk.indeed.com/Cqc-Registered-Manager-Dental-jobs",
    "oj_1491618": "https://www.onlinejobs.ph/jobseekers/job/1491618",
    "oj_1505586": "https://www.onlinejobs.ph/jobseekers/job/1505586",
    "oj_search": "https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword=dental",
    "gs_marketing": "https://suggestqueries.google.com/complete/search?client=firefox&q=dental%20marketing",
    "whito_data": "https://whito.co.uk/research/uk-dentist-marketing-data/",
    "upwork_bob_cat": "https://www.upwork.com/services/product/admin-customer-support-insurance-verification-and-breakdown-of-benefits-bob-1954649303002039626",
    "upwork_bob_job": "https://www.upwork.com/jobs/~022067110157780444776",
    "pph": "https://www.peopleperhour.com/hire-freelancers?q=dental",
    "fiverr_setup": "https://fiverr.com/prosalesfinders/setup-dentrix-eaglesoft-open-dental-curve-denticon-carestack-tab32-identalsoft",
    "fiverr_dental4": "https://block.fiverr.com/gigs/dental?page=4",
    "yahoo_sislow": "https://www.yahoo.com/news/articles/actually-speechless-dentist-spends-90-180000173.html",
    "dt_ppo_tax": "https://www.dentaltown.com/channel/post/26496/the-ppo-staffing-tax",
    "gdpuk_wong": "https://www.gdpuk.com/news/volume-of-ai-notes-in-patient-records-becoming-incredibly-scary-warns-wong/",
    "dt_grift": "https://www.dentaltown.com/channel/post/22270/ai-dental-receptionists-the-latest-grift",
    "dent_drain": "https://dentistry.co.uk/2021/12/29/marketing-money-down-the-drain/",
    # section 3
    "nhsbsa_exempt_guide": "https://www.nhsbsa.nhs.uk/sites/default/files/2022-03/Patient_exemption_checking_guide_dental_V3%20_08_2021.pdf",
    "ka_01916": "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01916/en-us",
    "nhs_charges": "https://www.nhs.uk/nhs-services/dentists/how-much-nhs-dental-treatment-costs/",
    "udapulse": "https://udapulse.co.uk/nhs-contract-guide/",
    "ka_01820": "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01820/en-us",
    "iclr": "https://www.iclr.co.uk/document/2026001068/2026ewhc294kb_TNA/html",
    "dspt169": "https://www.dsptoolkit.nhs.uk/News/169",
    "dnn_cqc": "https://www.dentalnursenetwork.com/news-articles/experiencing-a-cqc-inspection",
    "gdc_standards": "https://www.gdc-uk.org/standards-guidance/standards-and-guidance/standards-for-the-dental-team",
    "spadental": "https://www.spadental.co.uk/plymouth/fees/",
    "dent_consent": "https://dentistry.co.uk/2021/02/15/informed-patient-consent/",
    "dent_2026contract": "https://dentistry.co.uk/2026/02/02/what-does-the-2026-nhs-contract-amendment-mean-for-dentists/",
    "burkhart": "https://www.burkhartdental.com/practice-guide/front-office-systems/front-office-task-flow-guidelines/",
    "curve_verify": "https://www.curvedental.com/blog/verifying-dental-insurance",
    "ada_caqh": "https://adanews.ada.org/ada-news/2025/march/benefit-verification-drives-increased-administrative-spending-in-dental-offices/",
    "dt_eligibility": "https://www.dentaltown.com/channel/post/7458/is-dental-insurance-eligibility-taking-too-much-time",
    "xldent": "https://www.xldent.com/whats-new/update-regarding-change-healthcare-and-recommended-options-2-2-2-2-2-2-2",
    "od_era": "https://opendental.com/manual/era.html",
    "curve_denials": "https://www.curvedental.com/dental-blog/dental-claim-denials-whats-causing-them-and-how-to-stop-the-cycle",
    "diq_eod": "https://www.dentistryiq.com/front-office/collections/article/16353145/what-happens-at-the-end-of-the-day-in-the-life-of-your-business-coordinator",
    "ada_cred": "https://adanews.ada.org/new-dentist/2026/june/credentialing-101-what-new-dentists-need-to-know",
    "ada_cdt2026": "https://adanews.ada.org/ada-news/2025/september/new-cdt-codes-you-should-know-for-2026/",
    "ada_nsa": "https://adanews.ada.org/ada-news/2022/march/ada-addresses-no-surprises-act-questions/",
    "lund": "https://www.lunddental.co.uk/",
    "mose": "https://www.mosefamilydentistry.com/",
    "pp_blog": "https://www.patientprism.com/blog/missed-calls-medical-practice-revenue/",
    "nhs_doncaster": "https://www.nhs.uk/service-search/find-a-dentist/results/DN1+2EX",
    # section 4
    "drb_prosites": "https://www.drbicuspid.com/dental-practice/patient-communication/marketing/article/15379233/marketing-spending-reaches-new-high-in-2022-survey",
    "hip": "https://hip.agency/dental-marketing-budget-guide-investing-the-right-amount-in-growth/",
    "ainora_cac": "https://ainora.lt/blog/dental-patient-acquisition-cost-statistics",
    "rankai": "https://rankai.ai/articles/dental-seo-pricing-guide-costs-factors-roi",
    "delmain": "https://delmain.co/blog/dental-patient-acquisition/",
    "dominate_cost": "https://www.dominatedental.com/dental-advertising-cost-uk-guide/",
    "dominate_cms": "https://cms.dominatedental.com/?p=467",
    "clutch": "https://clutch.co/agencies/dental",
    "clicksgeek": "https://clicksgeek.com/white-label-seo-reseller-pricing/",
    "upcity_firegang": "https://agencyapp.dmbx.aws.gartner.com/local-marketing-agencies/profiles/firegang-dental-marketing-0",
    "tp_dentology": "https://se.trustpilot.com/review/dentology.ai",
    "socialperks": "https://socialperks.onrender.com/stories/why-i-fired-my-marketing-agency-and-results-improved",
    "aba": "https://www.abajournal.com/news/article/unhappy_patient_sues_when_dentist_seeks_to_enforce_contract_banning_bad_rev/",
    "dt_page1": "https://www.dentaltown.com/channel/post/25616/the-best-dental-marketing-company-breaks-down-the-cost-of-ranking-on-page-1-of-google",
    "viva_stats": "https://www.getviva.ai/lead-response-time-statistics-dental-2026/",
    "li_mickus": "https://lt.linkedin.com/in/laurynas-mickus",
    "dent_2011": "https://dentistry.co.uk/2011/07/01/44-cent-phone-calls-fail-reach-practice-team/",
    "hj_tracking": "https://www.hipaajournal.com/texas-judge-vacates-ocr-website-tracking-technology-guidance/",
    "diq_aspen": "https://www.dentistryiq.com/dentistry/research-and-news/news/55307953/aspen-dental-reaches-187m-settlement-in-data-tracking-case",
    "ftc_rule": "https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials",
    "cda_ftc": "https://www.cda.org/newsroom/practice-management/promoting-a-fake-or-purchased-review-youre-violating-the-ftc-rule/",
    "crowell": "https://www.crowell.com/en/insights/client-alerts/keeping-it-real-ftc-targets-fake-reviews-in-first-consumer-review-rule",
    "ar_tcpa": "https://appointmentreminder.com/guides/tcpa-compliance",
    "mofo": "https://mofo.com/resources/insights/250130-eleventh-circuit-vacates-fcc-s-tcpa-one-to-one-consent-rule",
    "hawksem": "https://hawksem.com/blog/healthcare-ad-restrictions/",
    "hj_fines": "https://www.hipaajournal.com/hipaa-violation-fines/",
    "gdc_adv": "https://www.gdc-uk.org/standards-guidance/standards-and-guidance/gdc-guidance-for-dental-professionals/guidance-on-advertising",
    "pubmed_bdj": "https://pubmed.ncbi.nlm.nih.gov/33767368/",
    "asa_dental": "https://www.asa.org.uk/advice-online/dental-general.html",
    "asa_turkey": "https://www.asa.org.uk/rulings/dental-centre-turkey-uk-ltd-a22-1157178-dental-centre-turkey-ltd.html",
    "ico_storage": "https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guidance-on-the-use-of-storage-and-access-technologies/",
    "gdc_social": "https://www.gdc-uk.org/docs/default-source/guidance-documents/guidance-on-using-social-media",
    "upwork_reviews": "https://www.upwork.com/freelance-jobs/apply/Google-Reviews-for-Business_~022109311663876127830/",
    "gs_airec": "https://suggestqueries.google.com/complete/search?client=firefox&q=ai%20receptionist%20dental",
    "paubox_shen": "https://www.paubox.com/blog/dental-practice-agrees-to-140k-settlement-after-records-complaint",
    "diq_gaps": "https://www.dentistryiq.com/revenue-cycle-management/article/55409403/the-7-revenue-cycle-gaps-most-dental-practices-dont-know-they-have",
})

BLOCKED_HOSTS = ("reddit.com on every mirror; Dentaltown's message board and GDPUK's forum beyond titles; Capterra, G2, Software Advice, GetApp and TrustRadius review bodies; Fiverr entirely; "
                 "Upwork job, hire and catalog pages; Dental Economics; Becker's; DentistryIQ in part; RDH Magazine; hhs.gov and federalregister.gov; the ICO enforcement list; several NHSBSA guidance PDFs; "
                 "NHS England's ambient-scribe, quality-and-payment and Recovery Plan pages; CQC mythbusters in part; the GDC's news pages; the Commons Library briefing; Indeed, NHS Jobs, BDJ Jobs and Reed ad bodies; "
                 "most practice websites in the sweep.")


def cover_page():
    out = [NextPageTemplate("cover"), Spacer(1, 14 * mm)]
    band = Table([[Paragraph("Small dental practices miss calls, rework claims and fear clawback", S["cover_title"])],
                  [Paragraph("Problems, workflows, numbers, vocabulary and service gaps in small UK and US dental practices: independent practices of one to five dentists, "
                             "NHS, private and mixed in the UK, fee-for-service, PPO and Medicaid in the US, and the agencies, vendors and freelancers that sell to them", S["cover_sub"])]],
                 colWidths=[FRAME_W])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 18), ("BOTTOMPADDING", (0, 0), (0, 0), 6),
        ("TOPPADDING", (0, 1), (0, 1), 2), ("BOTTOMPADDING", (0, 1), (0, 1), 18),
    ]))
    out.append(band)
    out.append(Spacer(1, 5 * mm))
    out.append(Paragraph("Research report, 16 October 2026", S["cover_meta"]))
    out.append(Spacer(1, 2 * mm))
    warn = Table([[Paragraph("Problems and gaps only. This document adds no solutions and no recommendations.", S["cover_warn"])]], colWidths=[FRAME_W])
    warn.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C_WARM_TINT), ("LINEBEFORE", (0, 0), (0, -1), 3, C_WARM),
                              ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    out.append(warn)
    out.append(Spacer(1, 5 * mm))
    scope_rows = [
        ["Scope", "UK (England mainly, with Scotland, Wales and Northern Ireland noted where the rules differ) and US small dental practices: the front desk, insurance and NHS claiming, "
                  "marketing and the agencies behind it, security and AI limits, the practice-software stack, the handoffs between products, and the job market for the people who could serve them."],
        ["Inputs", "Research note files compiled by the research team, one per section: economics, staffing, NHS access and leakage benchmarks; practitioners' vocabulary; workflows step by step; "
                   "the marketing market and its rules; security and AI limits; verification and claiming; the platform audit angle; handoffs; platform reviews; the thirteen-gap ranking; and the employed-versus-freelance market. "
                   "Autocomplete, job boards and careers pages were read on 16 October 2026."],
        ["Sources blocked", "Reddit on every mirror; Dentaltown's board and GDPUK's forum beyond titles; Capterra, G2, Software Advice, GetApp and TrustRadius review bodies; Fiverr; Upwork job, hire and catalog pages; "
                            "Dental Economics; Becker's; hhs.gov and federalregister.gov; the ICO enforcement list; several NHSBSA and NHS England guidance pages; CQC mythbusters in part; the GDC's news pages; most job-ad bodies and practice websites (full list in section 12). "
                            "The shared web-search budget ran out part-way through every workstream; facts from blocked hosts rest on search snippets, secondary reports or vendor claims and are tagged."],
        ["Currency and dates", "All currency as published: GBP for UK figures, USD for US figures. Dates are given so freshness can be judged; NHS figures are financial years ending 31 March unless stated."],
    ]
    st = Table([[Paragraph(a, S["cover_label"]), Paragraph(b, S["cover_small"])] for a, b in scope_rows], colWidths=[30 * mm, FRAME_W - 30 * mm])
    st.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.3, C_GRID),
                            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out.append(st)
    out.append(Spacer(1, 5 * mm))
    out.append(Paragraph("How to read the evidence tags", S["cover_label"]))
    tags = [
        ("[snippet]", "the fact was seen only in a search-engine summary because the page blocked the researcher"),
        ("[vendor]", "the vendor's, agency's or consultant's own claim or a vendor-run survey; no independent source confirmed it"),
        ("[user, date]", "a dated user review, forum post or verbatim survey comment"),
        ("[secondary]", "the figure was relayed by trade press, an aggregator or a blog rather than read from the primary report"),
        ("[official]", "a regulator's, public body's or association's own page"),
        ("[n]", "a numbered source; the URL is in the Sources appendix"),
    ]
    tt = Table([[Paragraph("<b>%s</b>" % esc(a), S["legend_tag"]), Paragraph(esc(b), S["legend_tag"])] for a, b in tags], colWidths=[26 * mm, FRAME_W - 26 * mm])
    tt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out.append(tt)
    out.append(Spacer(1, 5 * mm))
    out.append(Paragraph("Prepared for Mustafa Shoukat. Built from the research report <i>Small dental practice problems UK US</i> "
                         "(12 numbered sections, 41 tables, 13 gap cards, a 25-row unverified list). %d numbered sources." % len(URLS), S["cover_small"]))
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
    out.append(Paragraph("The eight numbers that carry the report, then the thirteen service gaps in rank order. Each gap has a full card in section 10.", S["lead"]))
    tiles = [
        stat_tile("31 of 100", "US callers hang up before reaching anyone; 21 book, 13 walk away unbooked, 4.8 get a call back, 0.7 return and book",
                  "Patient Prism, 11.55m calls, 8,280 locations, 2025 [Patient Prism](@pp_report) [vendor]"),
        stat_tile("42–46%", "of diagnosed treatment accepted at the average US practice against 75–83% for the top 10%",
                  "[Henry Schein One](@hso_catalyst) [vendor]; [Henry Schein One](@hso_unsched) [vendor]"),
        stat_tile("$215,320", "average US general dentist net income in 2025, about $60,000 below 2010 in real terms; overhead 60–65%",
                  "[ADA HPI](@ada_trends) [snippet]; [Becker's](@beckers_goodbad) [secondary]; [ADA HPI Q1 2026](@ada_q1)"),
        stat_tile("£900m", "clawed back from NHS dentists in England over two years for under-delivered UDAs (£479m, £457m); delivery below 96% recovered in full",
                  "[Dentistry.co.uk](@dent_clawback) [secondary]; [NHSBSA KA-01672](@ka_01672)"),
        stat_tile("40%", "of adults in England seen by an NHS dentist in 24 months; one general NHS contract in ten given up since 2017",
                  "[NHSBSA 2024/25](@nhsbsa_stats); [GDPUK](@gdpuk_tenth) [secondary]"),
        stat_tile("$2.1bn", "US dental spend on benefit verification in 2023; about 12 minutes by phone against 4 electronic; first-pass denials 8–15% against a 4% benchmark",
                  "[ADA News](@ada_caqh); [DentistryIQ](@diq_gaps) [snippet]"),
        stat_tile("91% / 77%", "US dentists who call hygienist recruiting very or extremely hard / UK owners who had difficulty hiring a dental nurse",
                  "[ADA HPI](@ada_hyg); [BDA DDRB 2026-27](@bda_ddrb)"),
        stat_tile("$140,000", "OCR's October 2026 settlement with a dental practice over unmet record requests; eleven dental penalties since 2019, from $5,000",
                  "[Paubox](@paubox_shen) [vendor]; [HIPAA Journal](@hj_fines)"),
    ]
    rows = [tiles[0:4], tiles[4:8]]
    tw = (FRAME_W - 3 * 3 * mm) / 4
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
    sty = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
           ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]
    for c in (0, 2, 4, 6):
        sty += [("BACKGROUND", (c, 0), (c, -1), C_ZEBRA), ("LINEABOVE", (c, 0), (c, 0), 2.2, C_ACCENT), ("LINEABOVE", (c, 1), (c, 1), 2.2, C_ACCENT)]
    t.setStyle(TableStyle(sty))
    out.append(t)
    out.append(Spacer(1, 2 * mm))
    out.append(Paragraph("The thirteen gaps, ranked by problem signal and vendor weakness", S["h2"]))
    header, rows_ = T(10, 0)
    compact = []
    for r in rows_[:13]:
        rank, gap, signal, cov, fit, agency, country, auto = r
        a = auto.split(":")[0].split(";")[0].split(" for ")[0]
        compact.append([rank, gap, signal.split(":")[0], cov.split(":")[0].split(" (")[0], a, country.split(";")[0]])
    out.append(tbl(["#", "Gap", "Problem signal", "Vendor coverage", "Automatable", "Country"], compact,
                   widths=[7, 73, 22, 30, 24, 20], font="cell_small"))
    out.append(Paragraph("Crowded areas that are <b>not</b> gaps: AI phone receptionists; SEO, websites and Google Ads; review tools and texting; reminders; verification keystrokes and outsourced billing; "
                         "imaging AI; PMS set-up gigs and VA agencies; membership-plan and credentialing services (section 10).", S["note"]))
    return out


# --------------------------------------------------------------------------
# Section 1
# --------------------------------------------------------------------------
def section_1(CH):
    out = chapter(1, SEC[1]["title"],
                  "In both countries the practice's income arrives through a payer it does not control and a desk it cannot fully staff: the US dentist nets $215,320 on a 62% overhead while a third of the schedule sits empty; "
                  "the English NHS dentist delivers UDAs against a target and loses the shortfall in full below 96%. Every leakage number in between (missed calls, no-shows, unaccepted treatment) is a vendor's.")
    out.append(H2("The US practice: still owner-run, thinner than it looks"))
    out += bullets([
        "<b>72.5% of US dentists owned a practice in 2023</b> (84.7% in 2005), DSO affiliation rose from <b>7.2% in 2015 to 16.1% in 2024</b>, and about 34% worked alone in a single location, so roughly 85% of dentists sit outside a DSO and carry billing, marketing and HR in-house ([Becker's on ADA HPI](@beckers_hpi) [snippet]; [DrBicuspid](@drb_models)).",
        "Average net income for a private-practice general dentist was <b>$207,980 in 2024 and $215,320 in 2025</b>; in real terms the average is down nearly $60,000 since 2010 and the median down more than $64,000 ([ADA HPI](@ada_trends) [snippet]; [Becker's](@beckers_goodbad) [secondary]). "
        "Overhead runs <b>60-65% of collections</b> (61.8% at 100-plus general practices in 2024), 65% of practices reported higher overhead at about +5.1%, and 55% named rising overhead the biggest challenge of 2025 ([Clerri](@clerri_overhead) [vendor]; [Dental Economics/Levin](@de_levin) [snippet]; [Dental Economics 2025](@de_2025)).",
        "Payers have not moved: dentists told the ADA in early 2026 that reimbursement is 'downright abysmal' and that 'those payers have not increased reimbursement in over 20 years but these asking salaries have now almost tripled'; reimbursement indexes stood at 131-134 against inflation at 138 (2016 = 100), and <b>35% planned to drop some networks</b> ([ADA HPI Q1 2026](@ada_q1) [user, 2026]).",
        "Demand softened too: <b>one-third of dentists report they are 'not busy enough'</b> (one-quarter in Q1 2024), new-patient wait time fell to 12.4 days, one in five lack enough administrative staff, 41% participate in Medicaid, and about 64% of active dentists sit in PPO networks with write-offs of 21-30% of fees ([ADA HPI Q1 2026](@ada_q1); [ADA News, Dec 2025](@ada_medicaid); [DenteMax](@dentemax_faq) [vendor]).",
        "The software bill creeps: a consultant describes practices with '20 to 25 connected software tools', a $300-a-month reminder program 'barely used', $450 a month still paid to Dentrix for texting after switching to Weave, and merchant fees of $2,500-$3,000 a month ([Thriving Dentist, 14 Oct 2026](@thriving) [vendor]).",
    ])
    out.append(fig_image(*CH["us_economics"]))
    out.append(H3("Table 1.1  US practice measures"))
    h, r = T(1, 0)
    out.append(tbl(h, r, widths=[30, 70, 34, 42], font="cell_small"))
    out.append(H2("Staffing: a retention problem, not a supply problem"))
    out += bullets([
        "<b>Only 60% of US dentists have enough hygienists and 91% of those recruiting call it very or extremely challenging</b>, even though 2025 produced the most hygiene graduates ever; about 70% say the same of assistants, 37.6% recruited a hygienist in the last three months ([ADA HPI, Apr 2026](@ada_hyg); [ADA HPI Q1 2026](@ada_q1)). "
        "Owners' words: 'Not a single application in 9 months'; '3 months of sponsored advertising... and one tattoo artist applied'; 'We now have to use a recruiter and pay 17% of first year's wage' ([ADA HPI Q1 2026](@ada_q1) [user, 2026]).",
        "In the UK the GDC register grew to 131,680 in 2025 with international joiners outnumbering UK graduates for the first time, yet <b>77% of owners who tried to recruit dental nurses had difficulty, 63% of owners with vacancies had posts open more than six months</b> (76% at high-NHS practices), the NHS general-dentist vacancy rate was 19% in the survey the BDA cites (10% in December 2025), and <b>75% of dental nurses who change jobs leave dentistry altogether</b> "
        "([GDC, 7 May 2026](@gdc_register) [snippet]; [BDA DDRB 2026-27](@bda_ddrb); [Dentistry.co.uk, 15 Nov 2024](@dent_vacancies); [Dentistry.co.uk, 31 Mar 2026](@dent_loyal)).",
        "A UK dental nurse earns <b>£14.73 an hour</b>, within about £2 of a receptionist (£13.92), and nurses call themselves 'glorified cleaners', 'hidden' and 'overworked and underpaid'; every dentist appointment needs a nurse, so an empty nurse post removes surgery sessions and UDA delivery with them ([Indeed UK](@indeed_nurse); [Dentistry.co.uk, 8 Apr 2024](@dent_nurses2024) [user, 2024]).",
        "Morale: 32.4% of US dentists report being overworked; <b>69.8% of UK dentists scored high emotional exhaustion</b> (n=1,507, 2023), 56% of owners report low morale, 42% intend to retire or leave within five years, and 63% of GDPs expect to reduce NHS work against 1% who expect to increase it ([ADA HPI, Jul 2026](@ada_ai); [PMC12334352](@pmc_burnout); [BDA DDRB](@bda_ddrb); [GDPUK, 15 Sep 2026](@gdpuk_reduce)).",
    ])
    out.append(fig_image(*CH["staffing"]))
    out.append(H3("Table 1.2  Staffing measures, US against UK"))
    h, r = T(1, 1)
    out.append(tbl(h, r, widths=[30, 52, 50, 44], font="cell_small"))
    out.append(H2("The NHS contract: a tenth of practices gone, £900m clawed back"))
    out += bullets([
        "NHS general dental contracts in England fell from <b>about 6,260 in March 2017 to about 5,650 in March 2026</b> while total practices rose by more than 400, so the share with a general NHS contract fell from about 65% to 56% and roughly 1,000 more practices are now private-only ([GDPUK, 24 Aug 2026](@gdpuk_tenth) [secondary]; [The Probe, 1 Oct 2026](@probe_oct) [secondary]).",
        "Activity rises, coverage does not: 76.8 million UDAs and 37.6 million courses in 2025/26, yet <b>18.8 million adults (40%) seen in 24 months</b>, the same 40% as the year before; 78% of those who tried for an NHS appointment succeeded but only 38% of those seeking a new appointment did ([NHSBSA 2024/25](@nhsbsa_stats); [NHS England GP Patient Survey](@gpps)).",
        "The money mechanism is the UDA: the average contract pays <b>£36.22 per UDA</b> (£28 minimum), delivery below <b>96%</b> of target is clawed back in full with a breach notice, 96-100% is carried forward, above 102% is not paid, and about £1 in every £7 paid to NHS dentists was recovered over two years (<b>£479m in 2024, £457m in 2025</b>) "
        "([GDPUK](@gdpuk_uda); [NHSBSA KA-01672](@ka_01672); [Dentistry.co.uk, 5 Mar 2026](@dent_clawback) [secondary]). One owner 'slightly under 96%' asked for leeway and was told 'no, you'll need to pay the clawback money'; focus-group dentists call the contract a 'hamster on the wheel' ([GDPUK blog](@gdpuk_blog) [snippet]; [PMC12065166](@pmc_focus) [user, 2023]).",
        "The April 2026 amendment added an urgent-care course credit of <b>£75 (£15 fixed plus £60 activity) with a minimum of 8.2% of contract value</b>, complex-care pathways at £284, £709 and £248, a £3,400 quality-improvement payment and £213 funded appraisals; Compass shows only the £15 element, so 'you cannot look at Compass and know where you are anymore' "
        "([Price Bailey](@pricebailey) [secondary]; [GDPUK, 13 Jul 2026](@gdpuk_compass)). NHS-active dentists in England earned £83,000 taxable in 2024/25 after a fall of almost 35% over the decade to about 2022 ([Dentistry.co.uk, 3 Aug 2026](@dent_income)).",
    ])
    out.append(fig_image(*CH["nhs"]))
    out.append(H3("Table 1.3  UK NHS and access measures"))
    h, r = T(1, 2)
    out.append(tbl(h, r, widths=[28, 72, 32, 44], font="cell_small"))
    out.append(H2("Private UK dentistry grows, and brings a complaint load the NHS never carried"))
    out += bullets([
        "<b>20% of Britons now use private dental care</b>; one practice went 'from around 440 patients on plan to more than 2,000 in just six months'; the Dental Complaints Service resolved <b>985 cases in 2024, up 111%</b>, access complaints rose 384%, and GDC fitness-to-practise concerns rose 26% to 1,766 in 2025 with an average assessment stage of 78 working weeks "
        "([GDPUK](@gdpuk_private) [snippet]; [Dentistry.co.uk, 27 Oct 2025](@dent_safer) [vendor]; [Dentistry.co.uk, 20 Mar 2025](@dent_dcs); [Dentistry.co.uk, 3 Jun 2026](@dent_ftp)).",
        "Which? surveyed 1,009 private patients with a problem: <b>22% 'paid more than they had been quoted'</b>, 21% found prices unclear before treatment, 16% felt pressured to agree to treatment and 11% to sign up to a payment plan; six in ten did not complain ([GDPUK, 6 Oct 2026](@gdpuk_which)). "
        "A private consultation runs a median £65 across 2,233 practices, hygiene £83, emergency £75, plans £15-£50 a month ([TreatCompare, Mar-Apr 2026](@treatcompare)).",
        "Regulator fear is measurable: 79% of dentists name complaints or litigation as their top stressor and 72.8% are concerned about the GDC; fewer than half find fitness-to-practise fair ([BDJ 2026](@bdj_stress)).",
    ])
    out.append(H3("Table 1.4  UK private and complaints measures"))
    h, r = T(1, 3)
    out.append(tbl(h, r, widths=[32, 68, 32, 44], font="cell_small"))
    out.append(H2("Leakage: every number is a vendor's, and they roughly agree"))
    out += bullets([
        "No regulator or academic body publishes a dental missed-call, lead-response or recall rate in either country. The largest dataset, <b>Patient Prism's 11.55 million calls across 8,280 US locations in 2025</b>, shows 31 of 100 callers hanging up before reaching anyone, 21 booking, 13 walking away unbooked, 4.8 getting a follow-up call and 0.7 coming back to book; "
        "reasons for not booking were timing 45.2%, money and insurance 34.4%, service fit 10.3% and connection failed 9.3% ([Patient Prism, 2 Jul 2026](@pp_report) [vendor]). Three other vendors put unanswered calls at 35%, 37% and 38% on different denominators ([DenteMax](@dentemax_calls) [vendor]; [Dentaltown, 5 Aug 2026](@dt_frontdesk) [vendor]; [Peerlogic, Feb 2026](@peerlogic) [vendor]).",
        "No-shows run <b>4%</b> on Henry Schein One's data (top 10% under 1%), 6.9% on Planet DDS's 2025 data plus 12.9% cancellations, and 9.1-14.3% in peer-reviewed studies; the spread is definitions and payer mix ([Henry Schein One](@hso_catalyst) [vendor]; [Ainora on Planet DDS](@ainora_noshow) [vendor]). "
        "Once in the chair, <b>42% (2026) to 46% (2024) of diagnosed treatment is accepted against 75-83% for the top 10%</b>, leaving '$1 to $1.5 million' unscheduled per average practice; hygiene reappointment runs 42-81% against 94%, recall 60-70% against 85-95%, collection 80% against 97% ([Henry Schein One](@hso_unsched) [vendor]; [Ainora](@ainora_recall) [vendor]).",
        "The UK has no published DNA rate. The only primary enquiry data are a 2021 mystery-shop of all 74 East Sussex practices (<b>13.5% could not be contacted</b> even after a follow-up call; some 'did not log enquiries or keep waiting lists at all') and a 2017 survey of 167 principals (almost two-thirds track leads on paper diaries, Post-its or nothing; 'two to three weeks between an enquiry and first contact') "
        "([Healthwatch East Sussex, Mar 2022](@hw_sussex); [Dentistry.co.uk, 22 May 2019](@dent_dengro) [vendor]). Dormant lists run 800-2,000 patients per practice and reactivation recovers 10-25% ([ACT Dental, 24 Jul 2026](@act_unsched) [vendor]).",
    ])
    out.append(fig_image(*CH["funnel"]))
    out.append(fig_image(*CH["ranges"]))
    out.append(H3("Table 1.5  Leakage measures, all vendor-measured"))
    h, r = T(1, 4)
    out.append(tbl(h, r, widths=[28, 62, 40, 46], font="cell_small"))
    return out


# --------------------------------------------------------------------------
# Section 2
# --------------------------------------------------------------------------
def section_2(CH):
    out = chapter(2, SEC[2]["title"],
                  "The two markets describe the same desk with different nouns, and the switch matters for every keyword list: the UK employs a dental nurse and a practice manager, claims UDAs on an FP17 through Compass and fears clawback and the GDC; "
                  "the US employs a dental assistant and an office manager, verifies eligibility, gets a breakdown of benefits, works denials and calls a missed visit a no-show.")
    out += bullets([
        "<b>UK</b>: 'dental nurse', 'practice manager' (often 'CQC registered manager'), 'diary', 'rota', 'UDAs', 'FP17', 'Compass', 'exemption', 'course of treatment', 'Band 1, 2 or 3', 'clawback', 'GDC', 'CQC inspection', 'Denplan', 'practice plan', 'FTA' ('failed to attend', 'dental fta policy', 'nhs dental fta policy') "
        "([Reed](@reed_nurse); [NHSBSA activity and payments](@nhsbsa_activity); [Google autocomplete, UK](@gs_fta)).",
        "<b>US</b>: 'dental assistant', 'office manager', 'schedule', 'eligibility', 'breakdown of benefits (BOB)', 'claims', 'CDT codes', 'denials', 'appeals', 'no-show' ('no show fee', 'no show policy', 'no show code'), 'in-network', 'fee-for-service', 'membership plan' ([DentalPost](@dentalpost_fo); [ADA CDT glossary](@ada_cdt_gloss); [Google autocomplete, US](@gs_noshow)).",
        "The strongest dated voices are from association surveys, focus groups and trade press rather than forums, because Reddit, Dentaltown's board and GDPUK's forum were closed to the researcher; the five pains they cluster around are phones and no-shows, insurance phone work, money, staff, and (UK) the NHS contract and regulation.",
    ])
    out.append(H3("Table 2.1  Concept by concept: UK words against US words"))
    h, r = T(2, 0)
    out.append(tbl(h, r, widths=[26, 75, 75], font="cell_small", first_col_bold=True))
    out.append(H2("Verbatim pains, dated"))
    out += bullets([
        "US insurance work: 'denied three times, and she didn't know why'; 'over an hour and a half' on the phone; 'Claim denied,' 'Resubmit,' 'Appeal,' 'Sit on hold'; 'The insurance company doesn't pay this employee. You do.'; calls are 'soul-crushing' ([Yahoo/Daily Dot, 2026](@yahoo_sislow) [user, 2026]; [Dentaltown, 13 Aug 2026](@dt_ppo_tax) [vendor]).",
        "UK contract and records: 'hamster on the wheel'; 'Universally Detested Acronym'; 'unknowingly driving a car with a faulty speedometer'; 'The volume of AI notes is getting incredibly scary'; 'computer files that are the length of textbooks'; a missed note could be 'career-ending' ([PMC12065166](@pmc_focus) [user, 2023]; [GDPUK, 13 Jul 2026](@gdpuk_compass); [GDPUK, 16 Oct 2026](@gdpuk_wong)).",
        "AI tools: 'the latest grift' (AI receptionists); 'confidently made things up'; 'Patients hung up on robot voice'; 'They are using AI to try to upsell you on dental procedures.' ([Dentaltown, 7 Mar 2025](@dt_grift) [vendor]). Marketing: 'no idea' of ROI; 'You need to give it more time'; 'your marketing isn't broken, your front desk is' ([Dentistry.co.uk, 29 Dec 2021](@dent_drain); [Dentaltown, 5 Aug 2026](@dt_frontdesk) [vendor]).",
    ])
    out.append(H3("Table 2.2  Practitioners' words by pain, with who said them and when"))
    h, r = T(2, 1)
    out.append(tbl(h, r, widths=[24, 76, 36, 40], font="cell_small"))
    out.append(H2("The duty vocabulary, from job ads and VA listings"))
    out += bullets([
        "A San Antonio front-office post at $20-$25 an hour wants the coordinator 'verifying patient dental insurance benefits before appointments and confirming eligibility, deductibles, annual maximums, frequencies, waiting periods, and limitations', 'submitting claims, tracking their status, and appealing denials' and 'submitting pre-treatment estimates and pre-authorizations as needed'; others require 'dental insurance verification experience (required)' and 'OpenDental experience required' "
        "([DentalPost 557606](@dp_557606); [DentalPost 557359](@dp_557359)). Of 188 DentalPost front-office listings, about 25 carry 'Treatment' in the title, 15 'Patient Care' or 'New Patient Coordinator', 9 insurance, billing or financial; pay runs <b>$15-$42 an hour and $30,000-$80,000 salaried</b> ([DentalPost](@dentalpost_fo)).",
        "UK receptionist ads list 'completing NHS and private scheme forms', 'chasing outstanding patient debt', a 'monthly debtors list' and 'liaising with dental labs and suppliers' at <b>£21,840-£24,465</b>; practice-manager ads lead with 'Ensure compliance with CQC, GDC, HTM 01-05 and NHS standards', 'Manage diaries, rotas, and daily operations', 'banking reconciliation' and profit and loss at <b>£28,000-£40,000</b>; Indeed UK keeps a landing page called 'Cqc Registered Manager Dental jobs' "
        "([Rodericks](@rodericks_rec) [snippet]; [findajob 17683574](@findajob) [snippet]; [BDJ Jobs 535611](@bdj_pm) [snippet]; [Indeed UK](@indeed_cqc)).",
        "Offshore VA ads list what the in-office desk cannot keep up with: 'Make recall and reminder calls for upcoming or overdue appointments'; 'Contact patients with pending treatment plans or unscheduled visits'; 'call new potential patients from the practice's lead system to get them scheduled'; 'dental insurance verification: confirming eligibility, getting benefit breakdowns, and updating patient records', at <b>$5 an hour plus $3 per new patient lead booked</b>, $2.50 an hour plus $2 per qualifying appointment, or $400-$700 a month "
        "([OnlineJobs.ph 1491618](@oj_1491618); [OnlineJobs.ph 1505586](@oj_1505586); [OnlineJobs.ph search](@oj_search)).",
    ])
    out.append(fig_image(*CH["job_ads"]))
    out.append(H2("What autocompletes and what does not"))
    out += bullets([
        "The US has a full 'ai receptionist for dental office' cluster with cost, reviews, Reddit and country modifiers (a crowded, late-stage category), an insurance cluster in job-seeker and vendor language ('dental insurance verification jobs remote', 'outsource dental billing services', 'dental claim denied due to frequency', 'dental claim denial codes') and a recall cluster ('dental recall text message sample', 'dental reactivation letter') ([Google autocomplete](@gs_noshow); [Google autocomplete, marketing](@gs_marketing)).",
        "UK practice-side phrases are logins and deadlines ('compass nhs dental login', 'nhs dental compass cut off dates', 'nhs dental contract uplift 2026/27'), compliance ('cqc dental inspection checklist', 'gdc social media guidance', 'gdc advertising guidance') and staffing ('dental nurse shortage occupation list', 'why are dental nurses paid so little'); patient phrases dominate NHS roots ('can i get an nhs dentist', 'nhs dental exemption checker').",
        "Phrases with <b>no suggestion at all</b>, and so living in forums and guidance rather than search: 'how to reduce no shows dental', 'can dentists use chatgpt', 'hipaa compliant ai for dentists', 'fp17 claim rejected', 'nhs dental udas explained', 'gdc advertising rules', 'dental billing company cost', 'dental membership plan uk', 'dentist google ads cost'. "
        "One UK vendor's Keyword Planner pull (Q1 2026): 'dentist near me' 165,000+ a month, 'emergency dentist' 90,000+, 'NHS dentist accepting patients' 74,000+, 'Invisalign [city]' 27,000+ ([Whito](@whito_data) [vendor]).",
    ])
    out.append(H3("Table 2.3  Autocomplete by topic: US, UK, and phrases with no suggestions"))
    h, r = T(2, 2)
    out.append(tbl(h, r, widths=[22, 56, 56, 42], font="cell_small", first_col_bold=True))
    out.append(H2("Marketplace selling phrases"))
    out += bullets([
        "The admin side sells on 'breakdown of benefits (BOB)', 'error-free', 'exact copay', 'before appointments', 'via portals (Availity, Skygen, Delta Dental portals and many more) or direct calls to payers', 'Dental Xchange experience', 'OpenDental experience (preferred)', 'Curve Dental experience required' and 'persistent follow-up on denied and aged claims' ([Upwork catalog](@upwork_bob_cat) [snippet]; [Upwork job](@upwork_bob_job) [snippet]).",
        "The marketing side sells 'Dental SEO and AI Visibility Services', 'Modern Dental Website with Online Booking Integration', 'Give database of 4K+ UK Dentists & Dental Clinics' and 'I will setup dentrix eaglesoft open dental curve denticon carestack tab32 identalsoft' covering 'account creation, provider profiles, patient data migration, insurance setup, and recall systems' ([PeoplePerHour](@pph); [Fiverr prosalesfinders](@fiverr_setup) [snippet]).",
        "Fiverr's dental pages are 'mostly dominated by website design, Google Ads, and SEO gigs, with few VA-style listings'; the admin and insurance work lives on Upwork's Project Catalog and OnlineJobs.ph; the only UK-specific offers found were dentist contact databases for cold outreach at $65, which says UK practices are an agency target rather than active freelance buyers ([Fiverr /gigs/dental](@fiverr_dental4) [snippet]).",
    ])
    return out


# --------------------------------------------------------------------------
# Section 3
# --------------------------------------------------------------------------
def section_3(CH):
    out = chapter(3, SEC[3]["title"],
                  "The UK mixed practice runs an NHS flow and a private flow through one receptionist, with the NHS side governed by a signed declaration, a two-month claim window and a year-end statement; "
                  "the US front desk runs a six-stage loop from eligibility check to denial rework, with every per-patient minute measured by a firm selling verification. No independent time-and-motion study of a dental desk exists in either country.")
    out.append(H2("The UK NHS flow: declaration, evidence, band, claim, reconcile, dispute"))
    out += bullets([
        "For an NHS patient the desk must have the <b>FP17PR declaration completed and signed before treatment begins</b>, ask for exemption evidence, note a valid certificate and its expiry, and if nothing is shown mark 'No' in the 'evidence seen' box and tell the patient checks are routine; an unsure patient pays and is given an HC5(D) refund form ([NHSBSA exemption guide](@nhsbsa_exempt_guide)). "
        "The signed form 'must be retained by the practice as part of the patient record for a period of two years', only a certified e-signature system replaces paper, and 'a practice cannot scan an original paper PR form and destroy the original' ([NHSBSA FAQ KA-01916](@ka_01916)).",
        "The desk collects the band charge (£27.90, £76.60 or £332.10) and NHSBSA nets patient charges off the monthly contract payment, so any mismatch between what reception took and what the FP17 declared shows up on the monthly schedule and has to be chased ([NHS.uk charges](@nhs_charges); [UDA Pulse](@udapulse) [secondary]).",
        "The clinician completes the clinical data set and signs the dentist's declaration, one FP17 per course; the claim must reach Compass <b>within two months of completion</b> or its UDAs are disallowed and marked 'Late Submitted Claim', corrected claims must also land inside the window, and electronic claims need 48 hours to process ([NHSBSA FAQ KA-01820](@ka_01820)). "
        "The practice then works from Compass outputs (monthly payment notification, DCS129 UDA summary, DCS127 patient-level activity, a mid-year review) and the <b>SD86c year-end statement around July with two months to dispute it</b> ([UDA Pulse](@udapulse) [secondary]; [ICLR, Balachandra 2026](@iclr)).",
        "Three more calendars sit on top: a 30 September checkpoint for 30% of the urgent-care requirement, the DSPT self-assessment by 30 June, and the CQC's expectation of staff files, decontamination logbooks under HTM 01-05, fire and IR(ME)R records and audit cycles with 'about two weeks' warning' of an inspection ([DSPT news 169](@dspt169); [Dental Nurse Network](@dnn_cqc)).",
        "The private flow runs beside it: a <b>written treatment plan and cost estimate before treatment</b> (GDC standard 1.6) and a fresh estimate if the plan changes (1.7), a deposit of 50-100% at booking at one Plymouth practice, an up-to-date medical history each time, and consent that after Montgomery must cover material risks and alternatives, since a signature 'does not indicate valid consent' ([GDC Standards](@gdc_standards); [SpaDental Plymouth](@spadental); [Dentistry.co.uk, Feb 2021](@dent_consent)). "
        "The 2026 contract adds funded appraisals (£213 each), a quality-improvement audit (£3,400), an urgent-care volume to track (8.2% of contract value) and complex-care claims, summed up by one consultant as 'increased admin, monitoring, benchmarking' for a practice that gains no administrative staff ([Dentistry.co.uk, 2 Feb 2026](@dent_2026contract); [Price Bailey](@pricebailey) [secondary]).",
    ])
    out.append(fig_image(*CH["flow"]))
    h, r = T(3, 0)
    parts = split_cols(h, r, [[1, 2, 3], [4, 5, 6]])
    out.append(H3("Table 3.1  UK steps, part 1: who, manual, repetitive"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[66, 30, 36, 44], font="cell_small"))
    out.append(H3("Table 3.2  UK steps, part 2: documents, deadlines, sources"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[58, 36, 40, 42], font="cell_small"))
    out.append(H2("The US front desk: a six-stage loop"))
    out += bullets([
        "Before the day the desk checks the answering service, email and portals, arrives at the huddle with open slots, overdue accounts and lab cases, and <b>verifies eligibility and benefits one to three days ahead at 5 to 30 minutes per patient</b>, with holds 'sometimes up to 30 minutes or more' at peak and at the start of the year ([Burkhart Dental](@burkhart); [Curve Dental, 8 Sep 2025](@curve_verify) [vendor]). "
        "The CAQH Index puts the average at <b>about 12 minutes per manual verification, 7 per portal check and 4 fully electronic</b>, with dental spending on verification up 15% to $2.1 billion and a $580 million savings opportunity unrealised because 270/271 responses 'often don't return data robust enough to be reliable' ([ADA News, 24 Mar 2025](@ada_caqh)).",
        "A 2017 outsourcer put it at 'an average of two hours a day' and noted staff put eligibility last 'because it is the most time-consuming task', so easy payers get checked and hard ones slip, and the slip 'surfaces later as a denial or patient balance' ([Dentaltown, 28 Jun 2017](@dt_eligibility) [vendor]).",
        "Check-in uses a print-ahead or online form bundling demographics, financial agreement, cancellation policy ('$25 charge for broken appointments without 24-hour notice') and medical history; check-out collects the balance identified that morning; claims go out next day through a clearinghouse at about <b>$0.50 per claim</b> with X-rays, perio charts and narratives attached; the EOB or ERA is posted (Open Dental 'attempts to automatically match claims' and detaches the ones it cannot); "
        "denials are worked within <b>90-180 days</b>, a simple one taking about 30 minutes and one example 'three hours chasing a $28 reimbursement' ([XLDent, 27 Mar 2024](@xldent); [Open Dental ERA manual](@od_era); [Curve Dental, 1 Jul 2026](@curve_denials) [vendor]).",
        "The day closes on paper: day sheet, transaction report, card settlement report and deposit slip, often not closed until the next morning because card transactions are still pending ([DentistryIQ](@diq_eod)). Around the loop sit credentialing packets with <b>CAQH re-attestation every 120 days</b> and Medicaid enrolment that 'can take months', the CDT update every 1 January (60 changes for 2026), the OSHA plan, DEA registration every three years at $888, state X-ray registrations, HIPAA notices and risk analysis, TCPA consent records and a <b>good-faith estimate within three business days</b> of a self-pay request "
        "([ADA News, 6 Jul 2026](@ada_cred); [ADA News, 29 Sep 2025](@ada_cdt2026); [ADA News, Mar 2022](@ada_nsa)).",
    ])
    h, r = T(3, 1)
    parts = split_cols(h, r, [[1, 2, 3], [4, 5, 6]])
    out.append(H3("Table 3.3  US steps, part 1: who, manual, repetitive"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[66, 30, 36, 44], font="cell_small"))
    out.append(H3("Table 3.4  US steps, part 2: documents, deadlines, sources"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[58, 36, 40, 42], font="cell_small"))
    out.append(H2("The marketing and new-patient flow is phone-first and brochure-shaped"))
    out += bullets([
        "Of five UK independent sites read directly (Hull, Plymouth, Carlisle, Wolverhampton), every one leads with a phone number, three add third-party online booking, none has a chat widget, <b>none offers online registration or a medical-history form, none takes online payment</b>, all present plans and finance as links that withhold provider and price, <b>no home page shows a GDC number</b> and no site shows the 'date last updated' the GDC requires ([Lund Dental](@lund)). "
        "NHS.uk status lines are self-reported snapshots that disagree for the same practice ('when availability allows' in one, 'children only' in another; hours 'last updated 2019'), so the first contact is a call to ask whether the list is open ([NHS.uk Doncaster results](@nhs_doncaster)).",
        "Of 13 US practices profiled across eleven cities, every independent site gives phone first, three use a web 'request' form that staff confirm, two state phone-only booking, insurance pages say 'most major insurance plans' or 'call us today to verify your benefits' while the in-network lists live only in third-party directories, financing is CareCredit or an unnamed in-house plan, and the only live scheduling, portal and texting set-up was on the one DSO-affiliated site ([Mose Family Dentistry](@mose)).",
        "The lead is handled by hand: fewer than half of UK practices check for new leads daily and reception handles them between calls; in the US the front desk is 'splitting attention between phones and in-office patients' and only 4.8 of 100 non-bookers get a call back ([Dentistry.co.uk, 22 May 2019](@dent_dengro) [vendor]; [Patient Prism blog, 1 Sep 2026](@pp_blog) [vendor]).",
    ])
    out.append(H3("Table 3.5  Marketing and new-patient steps, UK against US"))
    h, r = T(3, 2)
    out.append(tbl(h, r, widths=[34, 40, 40, 30, 32], font="cell_small"))
    return out


# --------------------------------------------------------------------------
# Section 4
# --------------------------------------------------------------------------
def section_4(CH):
    out = chapter(4, SEC[4]["title"],
                  "Spend is small, vendor-measured and badly defined; agencies charge $1,000-$2,500 a month in the US and £1,500-£8,000 in the UK; owners say they get 'no idea' of return; agencies answer that the front desk drops the lead; "
                  "and the pages that bring in private patients are the pages the GDC, the ASA, the FTC and Google check.")
    out.append(H2("How much is spent, and what a lead costs"))
    out += bullets([
        "The only survey-based US figure is ProSites' 2022 report (110 practices, October 2021): <b>61% spent $501 or more a month, 35% more than $1,000, under 4% more than $5,000</b>; word of mouth (80%), online reviews (57%), website and SEO (46-51%) were rated important, TV, radio and mailers unimportant ([DrBicuspid, 21 Mar 2022](@drb_prosites) [vendor survey]). "
        "Agencies recommend 3-6% of gross revenue (5-8% in growth mode), which for a $1M practice is $2,500-$5,000 a month, well above the median, so the agencies' addressable market is the top third by spend ([HIP Agency, 16 Jul 2026](@hip) [vendor]).",
        "Cost per new general-dentistry patient is quoted at <b>$150-$300</b> (implant and cosmetic $400-$800; SEO-sourced $50-$150 against Google Ads $150-$350) and lifetime value at $5,500-$10,000, all by agencies ([Ainora](@ainora_cac) [vendor]; [RankAI, 7 Dec 2025](@rankai) [vendor]). "
        "The one treatment-level dataset is Delmain's own 187 search campaigns (June 2026): cost per tracked lead, a call or a form and not a booked patient, of <b>$7.64 branded, $50.60 general, $77.62 emergency, $87.01 dentures, $107.63 implants, $119.62 cosmetic and $212.63 Invisalign</b>, the last three rows 'thin and directional' ([Delmain, Jun 2026](@delmain) [vendor]).",
        "UK figures come from one self-described research publisher ('directional benchmarks'): spend 5-10% of revenue for private-focused practices, under 2% NHS-heavy; monthly budgets <b>£500-£1,500 for a sole dentist, £3,000-£8,000 for four to six</b>; cost to acquire £30-£150 from Google search; annual new-patient value £300-£500 NHS-heavy, £1,000-£2,500 private ([Whito, May-Oct 2026](@whito_data) [vendor]). "
        "UK agencies quote cost per lead by treatment that does not reconcile between them (implants £100-£350, Invisalign £80-£200, emergency £25-£40) and £295 per new patient ([Dominate Dental](@dominate_cost) [vendor]).",
    ])
    out.append(fig_image(*CH["marketing"]))
    out.append(H3("Table 4.1  Marketing money measures, US against UK"))
    h, r = T(4, 0)
    out.append(tbl(h, r, widths=[30, 56, 46, 44], font="cell_small"))
    out.append(H2("What agencies charge, and what owners say about them"))
    out += bullets([
        "US dental SEO and marketing retainers cluster at <b>$1,000-$2,500 a month</b> (basic $750-$1,500, premium $3,000-$5,000+; small DSO $5,000-$15,000; ad spend billed separately), Clutch-listed dental agencies run $100-$149 an hour with $1,000+ minimums, and pricing guides say a 'full service' quote under $750-$800 'suggests subcontracting overseas or skipping the reporting layer' ([RankAI](@rankai) [vendor]; [Clutch](@clutch)). "
        "White-label local SEO for 'a dentist' costs an agency <b>$500-$1,500 a month</b>, which implies a 2-5x markup on subcontracted work ([ClicksGeek](@clicksgeek) [vendor]).",
        "UK dental SEO runs <b>£1,500-£8,000+ a month</b> (consultations £75-£200 an hour; technical audit about £3,000; 'AI-focused agencies charge 20-30% premiums') on an agency page that showed a 'Hacked by Panataran' header when read ([Dominate Dental](@dominate_cms) [vendor]). Named-agency data are thin and conflicting: Firegang lists a $2,000+ minimum with 5.0 from 8 reviews and claims '$10-15 back for every $1'; Roadside is listed at both under $500 and $5,000-$14,000 a month by different aggregators; Dental Focus (UK) claims 'over 5,000 dentists and practices' and shows no prices ([UpCity, Firegang](@upcity_firegang)).",
        "Owners' side: a UK principal paying £18,000 a year had 'no idea' of return and heard 'incomprehensible excuses'; a Trustpilot reviewer of a UK lead-gen agency said prospects 'turned up not even knowing the cost or what they wanted'; one US owner says that after firing a $4,200-a-month agency 'the week after, our lead flow went up'; an older case shows an agency threatening a cancelling dentist over a non-disparagement clause, now barred by the Consumer Review Fairness Act "
        "([Dentistry.co.uk, 29 Dec 2021](@dent_drain); [Trustpilot, Dentology](@tp_dentology) [user]; [socialperks](@socialperks) [user, unverified]; [ABA Journal](@aba)).",
        "The agencies' answer is that the practice loses the lead: <b>37% of 55,000+ tracked client calls went unanswered</b>, 'your marketing isn't broken, your front desk is', and answering phones 'requires a special set of skills that has to be taught'; Dentaltown's marketing channel itself is agency-written sponsored posts ('$2,500-$7,500 a month and 6-12 months' to reach page 1) ([Dentaltown, 5 Aug 2026](@dt_frontdesk) [vendor]; [Dentaltown](@dt_page1) [vendor]).",
    ])
    out.append(H3("Table 4.2  Agencies and vendors: price, reviews and criticism"))
    h, r = T(4, 1)
    out.append(tbl(h, r, widths=[30, 50, 50, 46], font="cell_small"))
    out.append(H2("Lead to seated patient: the number nobody reports"))
    out += bullets([
        "Using Patient Prism's 2025 funnel, about a fifth of inbound calls become bookings and under 1% of lost opportunities are recovered by callbacks; <b>1,445,814 patients walked away without an appointment and 890,621 never got a callback</b> across 8,280 locations ([Patient Prism, 2 Jul 2026](@pp_report) [vendor]). "
        "One AI-lead-response vendor claims, without a source, that 60-70% of paid dental leads are never successfully contacted and that 53% of prospects give up after one missed callback ([Viva](@viva_stats) [vendor, unsourced]).",
        "<b>No source in either country reports cost per seated patient or cost per registered patient</b>, the metric one agency commentator calls the only one that matters, and no public data exist on agency contract terms, churn or client-reported ROI ([LinkedIn commentary](@li_mickus)). The UK leak is older and less measured: a 2011 test found 44% of 3,557 calls failed to reach the team ([Dentistry.co.uk, 1 Jul 2011](@dent_2011) [snippet]).",
    ])
    out.append(H2("The rules that sit on the marketing pages"))
    out += bullets([
        "<b>US.</b> OCR's tracking-pixel bulletin was partly vacated on 20 June 2024 but guidance on authenticated pages stands and private wiretap suits continue: Aspen Dental settled a Meta Pixel and booking-data class action for <b>$18.7 million</b> ([HIPAA Journal, 21 Jun 2024](@hj_tracking); [DentistryIQ](@diq_aspen)). The FTC's consumer-review rule took effect 21 October 2024: fake or AI reviews, sentiment-conditioned incentives and suppression draw penalties of about <b>$51,744-$53,088 per violation</b>; first warning letters 22 December 2025; no dental case yet ([FTC](@ftc_rule); [CDA, 17 Apr 2025](@cda_ftc); [Crowell](@crowell)). "
        "Under the TCPA, reminders need prior express consent and marketing texts prior express <i>written</i> consent, at <b>$500-$1,500 per message with no cap</b>; the FCC's one-to-one consent rule was vacated on 24 January 2025 ([Appointment Reminder](@ar_tcpa) [vendor]; [Morrison Foerster](@mofo)). Google bars remarketing on invasive and cosmetic procedure pages ([HawkSEM](@hawksem) [vendor]). Replying to a review with any patient detail is a HIPAA breach: three dental OCR cases ($10,000, $23,000, $50,000) were for review responses ([HIPAA Journal](@hj_fines)).",
        "<b>UK.</b> The GDC's 2013 advertising guidance is still current: a practice website must show the practice name and address, the GDC's contact details, the complaints procedure and the <b>date the website was last updated</b>; every named professional must show qualification, country and GDC number; only dentists on a GDC specialist list may use 'specialist'; social posts must say the treatment 'may not be appropriate for every patient'; and the registrant 'is responsible for checking that it is correct', with no mention of agencies ([GDC advertising guidance](@gdc_adv)). "
        "A peer-reviewed audit of practice websites in North East England found <b>only 1.8% fully compliant</b> ([PubMed, BDJ 2021](@pubmed_bdj)). CAP requires before-and-after images 'genuine and representative' with 'signed and dated proof', says 'Dr' must not imply a medical qualification and that Botox cannot be advertised; no 2024-2025 ASA ruling against a UK dental practice was located ([ASA/CAP, Dental: General](@asa_dental); [ASA ruling A22-1157178](@asa_turkey)). "
        "The ICO finalised cookie and pixel guidance on 29 April 2026, and the GDC's social-media guidance forbids any patient-identifying post or reply ([ICO](@ico_storage); [GDC social media guidance](@gdc_social)).",
    ])
    out.append(H3("Table 4.3  Rules on marketing pages: what they require and what happened"))
    h, r = T(4, 2)
    out.append(tbl(h, r, widths=[30, 14, 54, 40, 38], font="cell_small"))
    out.append(note_box("<b>Crowded and thin.</b> Crowded: AI phone receptionists and call intelligence (Peerlogic, Patient Prism, VoiceStack, Viva, Convirza, Weave and Adit all publishing near-identical missed-call statistics; 'ai dental receptionist' already carrying cost, reviews, Reddit and five country modifiers in autocomplete), dental SEO and websites (dozens of agencies; Fiverr gigs from $10), "
                        "review tools (including a $500 Upwork post asking for 'genuine 5-star' reviews that the FTC rule prohibits), social content packages and agency-written 'the front desk is the problem' content. Thin: any independent measurement of leakage; UK enquiry-handling data newer than 2017-2021; agency contract terms, churn or ROI; cost per seated patient by treatment; "
                        "enforcement against small practices (the only US pixel case and the only UK ASA dental ruling are against a DSO and a facilitator); and compliance checking of practice websites and social posts against GDC, ASA and FTC rules, which no agency in the sample advertises and which the 1.8% figure says is not being done ([Google autocomplete](@gs_airec); [Upwork review job](@upwork_reviews) [snippet]).", warm=True))
    return out


# ==========================================================================
# Content, part B: sections 5 to 9
# ==========================================================================
U.update({
    "cda_abyde": "https://www.cda.org/newsroom/endorsed-services/ai-in-dentistry-what-are-the-hipaa-violation-risks/",
    "intuition": "https://intuitionlabs.ai/articles/is-chatgpt-hipaa-compliant",
    "msp_hipaa": "https://mysocialpractice.com/2025/09/ai-and-hipaa-compliance-in-dentistry/",
    "aae": "https://www.aae.org/specialty/why-dentists-should-be-careful-when-using-ai-to-make-insurance-decisions/",
    "hj_westend": "https://www.hipaajournal.com/indiana-ag-westend-dental-hipaa-violations/",
    "lexblog": "https://www.lexblog.com/2025/11/18/dental-practice-settles-data-breach-lawsuit-for-1-2-million/",
    "wsda": "https://www.wsda.org/news/blog/2026/04/29/hipaa-security-rule---proposed-rulemaking-update",
    "gda": "https://gadental.org/news/what-dental-practices-need-to-know-about-the-proposed-hipaa-security-rule-changes",
    "physpractice": "https://www.physicianspractice.com/view/small-practices-face-growing-cybersecurity-burden-as-federal-rules-tighten",
    "ada_standards": "https://adanews.ada.org/ada-news/2025/february/what-are-the-standards-for-ai-use-in-dentistry/",
    "fda_list": "https://www.fda.gov/medical-devices/artificial-intelligence-enabled-medical-devices/list-artificial-intelligence-enabled-medical-devices",
    "cda_tdic": "https://www.cda.org/newsroom/practice-management/ai-in-dentistry-strategies-for-managing-risks-and-potential-for-malpractice-claims",
    "afs": "https://www.afslaw.com/perspectives/alerts/california-requires-disclaimers-health-care-providers-ai-generated-patient",
    "gdpuk_aisurvey": "https://www.gdpuk.com/news/one-in-three-dentists-now-using-ai-tools-survey-finds/",
    "futurism": "https://futurism.com/health-medicine/dentists-ai-unnecessary-dental-work",
    "dent_gdc_ai": "https://dentistry.co.uk/2026/09/17/gdc-to-develop-rules-for-ethical-ai-use-in-healthcare/",
    "gdpuk_dp": "https://www.gdpuk.com/top-news/dental-protection-calls-on-regulator-to-deliver-clear-guidance-on-ai-use/",
    "dent_mhra": "https://dentistry.co.uk/2026/08/02/ai-scribes-guidance-dental-practices/",
    "gpce": "https://www.essexlmc.org.uk/wp-content/uploads/2025/05/GPCE-Guidance-on-the-use-of-AI-enabled-ambient-scribing-products-in-health-and-care-settings-A-Summ.pdf",
    "jfh": "https://jfhlaw.co.uk/ai-and-gdpr-compliance-are-dental-practices-in-breach-of-their-own-data-protection-policies/",
    "freevacy": "https://www.freevacy.com/news/ico/ico-reprimands-gp-surgery-over-excessive-disclosure-of-medical-records/7095",
    "ka_01913": "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01913/en-us",
    "mddus_call": "https://www.mddus.com/resources/publications-library/insight-dental/q2-2021/call-log-dentolegal-dilemmas",
    "krebs": "https://krebsonsecurity.com/2019/08/ransomware-bites-dental-data-backup-firm/",
    "csdive": "https://www.cybersecuritydive.com/news/henry-schein-cyberattack-29k-affected/702036/",
    "ortho_delta": "https://orthodonticproductsonline.com/practice-management/it/delta-dental-hack-exposes-sensitive-data/",
    "ada_change": "https://adanews.ada.org/ada-news/2024/april/ada-comments-on-congressional-cyberattack-hearing/",
    "ama_survey": "https://www.ama-assn.org/system/files/change-healthcare-follow-up-survey-results.pdf",
    "dentalit": "https://www.dentalit.ltd.uk/assets/files/state-of-dental-practice-it.pdf",
    "practiceplan": "https://www.practiceplan.co.uk/blog/cyber-security-in-dental-practices-why-it-matters/",
    "techvera": "https://techvera.com/resources/blog/what-dental-practices-need-to-know-before-renewing-cyber-insurance-in-2026",
    "fda_blog": "https://blog.floridadental.org/2025/07/17/hackers-dont-care-youre-a-dentist-why-cyber-insurance-matters-now/",
    "dsit": "https://www.gov.uk/government/statistics/cyber-security-breaches-survey-2025",
    # section 6
    "deepgram": "https://deepgram.com/learn/ai-voice-agent-benefits-verification",
    "od_ebenefits": "https://opendental.com/manual/ebenefits.html",
    "ainora_verify": "https://ainora.lt/blog/dental-insurance-verification-ai-statistics",
    "capterra_zuub": "https://capterra.com/p/200040/Zuub/reviews/?page=2",
    "nexhealth_help": "https://www.nexhealth.com/help/how-does-automated-insurance-verification-work",
    "eassist": "https://dentalbilling.com/pricing-dental-insurance-verification/",
    "mb2": "https://dentalcareers-mb2dental.icims.com/jobs/21339/insurance-verification-specialist/job",
    "hso_nightmare": "https://www.henryscheinone.com/insights/blogs/the-nightmare-of-eligibility-and-verification-in-dentistry/",
    "podcast": "https://thedentalbillingpodcast.buzzsprout.com/1783772/episodes/19634075-27-837-denials-zero-appeals-make-this-make-sense",
    "beckers_zentist": "https://beckersdental.com/revenue-cycle-management/78-of-dental-offices-see-uptick-in-claim-denials-report",
    "doaj": "https://oalib-perpustakaan.upi.edu/Record/doaj_f6a7b7d2bd974390a2df2a59c1fa211f/Details?print=1",
    "dentalbilling": "https://dentalbilling.com/?p=31917",
    "dba_kpis": "https://dentalbillingassist.com/blog/posts/dental-billing-kpis-benchmarks",
    "medsdental_charge": "https://medsdental.com/how-much-do-dental-billing-services-companies-charge",
    "fp17_v14": "https://cms.nhsbsa.nhs.uk/sites/default/files/2025-07/Completion_of_form_guidance_FP17-England_20250801_%28V14%29.pdf",
    "gov_atr": "https://www.gov.uk/algorithmic-transparency-records/nhsbsa-prescriptions-and-dental-exemption-check",
    "foi_02776": "https://opendata.nhsbsa.net/dataset/foi-02776",
    "nao": "https://www.nao.org.uk/report/investigation-into-healthcare-penalty-charge-notices/",
    "tender": "https://www.find-tender.service.gov.uk/Notice/081407-2025",
    "ddu": "https://ddujournal.theddu.com/issue-archive/autumn-2017/handling-patient-complaints-around-bsa-fines",
    "gdpuk_bsa": "https://www.gdpuk.com/news/latest-news/3201-bsa-slated-for-fining-disabled-person-with-mental-age-of-two",
    "fp17_v114": "https://www.nhsbsa.nhs.uk/sites/default/files/2022-11/Completion_of_form_guidance-FP17-England_202210_V11.4_Final.pdf",
    "nhsbsa_errors": "https://www.nhsbsa.nhs.uk/sites/default/files/2022-09/Common_Errors_FP17W_from_1_April_2022_FINAL.pdf",
    "dent_reform": "https://dentistry.co.uk/2026/07/20/nhs-dental-contract-reform-whats-changed-and-where-do-we-go-from-here/",
    "dentally_help": "https://help.dentally.com/en/articles/3563621-dealing-with-nhs-england-claim-problems",
    "dentally_comm": "https://community.dentally.com/other-54/lack-of-functionality-for-scottish-users-598",
    "ka_01797": "https://faq.nhsbsa.nhs.uk/knowledgebase/article/KA-01797/en-us",
    # section 7
    "od_fees": "https://www.opendental.com/site/fees.html",
    "od_conv": "https://www.opendental.com/site/conversions.html",
    "costbench_change": "https://costbench.com/changelog/dentrix-price-increase-2026-02/",
    "costbench_hidden": "https://costbench.com/software/dental-software/dentrix/hidden-costs/",
    "dt_revup": "https://www.dentaltown.com/channel/post/25865/what-dentists-are-saying-about-practice-management-software",
    "costbench_2026": "https://costbench.com/stats/dental-software-pricing-2026/",
    "weave_pricing": "https://www.getweave.com/pricing/",
    "tp_weave": "https://www.trustpilot.com/review/getweave.com",
    "nexhealth_pricing": "https://www.nexhealth.com/pricing",
    "capterra_nexhealth": "https://www.capterra.com/p/182271/NexHealth/reviews/",
    "capterra_rw": "https://www.capterra.com/p/160904/RevenueWell/reviews/?page=3",
    "capterra_sr": "https://capterra.com/p/160916/Solutionreach/reviews/?page=5",
    "di_aging": "https://educate.dentalintel.com/en/articles/15481262-why-the-claims-aging-metric-doesn-t-match-dentrix-s-insurance-aging-report",
    "g2_di": "https://www.g2.com/products/dental-intelligence-dental-intelligence/pricing",
    "aifd_arini": "https://www.myaifrontdesk.com/blogs/arini-ai-dental-receptionist-pricing-what-dentists-need-to-know-in-2025",
    "sagnik": "https://sagnikbhattacharya.com/blog/ai-receptionist-cost-dental-practice-2026",
    "ustech": "https://ustechautomations.com/resources/blog/automate-zapier-alternatives-for-dental-practices-2026",
    "dentally_pricing": "https://www.dentally.com/pricing",
    "whito_sw": "https://whito.co.uk/for/dentists/best-software-for-uk-dentists/",
    "capterra_exact": "https://www.capterra.com/p/6364/EXACT-V12/reviews/",
    "dengro_pricing": "https://dengro.com/pricing",
    "gcloud": "https://www.applytosupply.digitalmarketplace.service.gov.uk/g-cloud-14/services/713936219092976",
    "lilach": "https://www.lilachbullock.com/how-much-does-a-dental-ai-receptionist-cost/",
    "carestack_lab": "https://carestack.com/en-GB/dental-software/features/lab-case-management",
    "dentrix_ent": "https://blog.dentrixenterprise.com/?p=1818",
    "schedkit": "https://schedulingkit.com/hub/industry-guides/dental-scheduling-statistics",
    "upwork_od": "https://www.upwork.com/jobs/~022059644914653616103",
    "aapc": "https://aapc.com/discuss/threads/charges-for-chart-auditing.19646",
    "dominate_training": "https://cms.dominatedental.com/?p=2923",
    "greenhouse": "https://job-boards.greenhouse.io/pcdm/jobs/8002811003",
    "medsdental_audit": "https://medsdental.com/services/dental-auditing-service",
    "capterra_dentrix": "https://www.capterra.com/p/2329/Dentrix/reviews/",
})


# --------------------------------------------------------------------------
# Section 5
# --------------------------------------------------------------------------
def section_5(CH):
    out = chapter(5, SEC[5]["title"],
                  "OCR's record against dental practices is a record of paper and policy failures, not of hacking; the biggest breaches arrive through vendors and stop the money; consumer ChatGPT offers no business associate agreement; "
                  "the UK has a device line from the MHRA, a DPIA expectation from NHS England and no GDC rule; and a UK IT provider's 192 on-site audits show what 'everyday security' looks like at three surgeries.")
    out.append(H2("HIPAA, business associates and the consumer AI app"))
    out += bullets([
        "A US practice is a covered entity, so any AI vendor touching PHI is a business associate and must sign a BAA; the CDA's endorsed compliance partner tells dentists to 'never use the free, public version of ChatGPT with patient data' and to 'avoid vendors that refuse to sign a BAA' ([CDA/Abyde, 27 Aug 2025](@cda_abyde) [vendor]). "
        "OpenAI's help centre, quoted second-hand, says 'we don't offer a BAA for ChatGPT Business'; civil penalties run <b>$145 to $2,190,294 per violation</b> by culpability tier ([IntuitionLabs](@intuition) [secondary]).",
        "Three separate disclosure paths: an AI receptionist that answers, transcribes or books is a business associate, not a conduit; a website chat widget's free-text box 'should be assumed to collect PHI'; and staff 'pasting claim narratives or chart details into unapproved AI tools' ([My Social Practice, Sep 2025](@msp_hipaa) [vendor]). "
        "The endodontists' association adds that general AI tools 'lack knowledge of carrier claims histories, state rules, and policy exclusions' and give confident but unreliable coverage answers ([AAE](@aae)).",
    ])
    out.append(H2("OCR's dental record: records, review replies and missing policies"))
    out += bullets([
        "HIPAA Journal's penalty list carries <b>eleven dental entries since 2019, from $5,000 to $140,000</b>: refusing or delaying record requests (six cases), disclosing patient details in review replies (three), and having no privacy officer, policies or training. The latest, Shen Smiles (Pennsylvania), announced 8 October 2026 at <b>$140,000</b>, began with a 2020 complaint about unfulfilled record requests and ended with records found 'in plastic boxes, the floor, and a private bathroom' ([HIPAA Journal](@hj_fines); [Paubox, 12 Oct 2026](@paubox_shen) [vendor]).",
        "The largest dental sum came from a state attorney general: Westend Dental (Indianapolis, about 17,000 patients) paid <b>$350,000</b> after a 2020 ransomware attack it reported two years late and described as 'not a ransomware attack'; investigators found plain-text passwords, no risk analysis, no training before November 2023, no BAA with the non-employee running the practices and servers 'in employee break rooms and bathrooms' ([HIPAA Journal, 2 Jan 2025](@hj_westend)). "
        "First Choice Dental (Wisconsin) paid <b>$1.2 million</b> to settle a class action over an October 2023 hack affecting 150,000-plus patients ([LexBlog, 18 Nov 2025](@lexblog)).",
    ])
    out.append(fig_image(*CH["ocr"]))
    out.append(H3("Table 5.1  OCR and state penalties on dental practices, 2019-2026"))
    h, r = T(5, 0)
    out.append(tbl(h, r, widths=[38, 20, 26, 52, 40], font="cell_small"))
    out.append(H2("The proposed Security Rule and US AI governance"))
    out += bullets([
        "Published in the Federal Register on 6 January 2025, the Security Rule rewrite would make nearly all specifications mandatory: <b>encryption at rest and in transit, MFA for all access to ePHI systems 'with no size exceptions'</b>, a written asset inventory, network segmentation, vulnerability scans every six months, an annual penetration test, tested recovery plans with 72-hour restoration, and direct obligations on business associates ([WSDA, 29 Apr 2026](@wsda); [Georgia Dental Association, 26 May 2026](@gda)). "
        "The ADA joined a coalition letter asking OCR to rescind it; status reports conflict (final action May 2026, July 2027, or 'final' per one vendor) and hhs.gov blocked reading. Not in dispute: OCR's line that 'the size of a practice is irrelevant', that in 2022 more than half of OCR penalties targeted small practices, and a Senate committee's 22-1 vote in February 2026 to advance a bill codifying MFA and encryption ([Physicians Practice, 10 Mar 2026](@physpractice)).",
        "US AI governance is standards and insurer caution: the ADA's white paper (1106:2022), a technical report on evaluating image-analysis systems (1109:2025) and the first ANSI-approved dental AI standard (1110-1:2025); the FDA list shows a steady run of dental radiograph 510(k) clearances (Overjet, Pearl, VideaHealth, Diagnocat), so imaging is the one dental AI category with a clear regulatory status while scribes, chatbots and phone AI sit under HIPAA contract rules only ([ADA News, 3 Feb 2025](@ada_standards); [FDA list](@fda_list)). "
        "The main dental malpractice insurer says liability for AI decisions is 'a legal gray area' and tells dentists to 'obtain informed consents that explicitly cover AI use' ([CDA/TDIC, 27 Jan 2025](@cda_tdic)); California's AB 3030 requires a disclaimer on generative-AI clinical messages unless a licensed provider reviews them, exempting scheduling and billing ([ArentFox Schiff](@afs)).",
        "Adoption is real and uneven: <b>43.3% of US dentists use AI for at least one task</b> (imaging 22.8%, insurance verification 13.6%, reception 10.1%), 34.8% plan charting and note-taking, 32.6% plan verification, 82.6% never plan to use it for treatment recommendations; a three-country survey found 12% who tried and stopped (cost 28%, poor PMS integration 22%, accuracy 18%) ([ADA HPI, Jul 2026](@ada_ai); [GDPUK, 1 Jun 2026](@gdpuk_aisurvey)). "
        "The reputational limit is public: a columnist's AI-read X-ray led to a four-session periodontal plan 'costing thousands of dollars' that three other dentists said home care would handle; staff said owners asked 'Why didn't you drill it?' ([Futurism, 16 May 2026](@futurism)).",
    ])
    out.append(H2("The UK: no GDC rule yet, a device line, and record clocks"))
    out += bullets([
        "As of 16 October 2026 the GDC has published a literature review ('No UK-based studies were included') and, on 17 September 2026, a joint statement of intent with the medical, nursing and social-work regulators to develop 'high-level principles' with no timeline; Dental Protection asked the GDC to clarify 'professional accountability' ([Dentistry.co.uk, 17 Sep 2026](@dent_gdc_ai); [GDPUK, 9 Sep 2026](@gdpuk_dp)).",
        "The MHRA, with NHS England, drew the device line on 2 August 2026: tools used only for 'transcription, consultation summaries, draft referral letters or suggested clinical codes' for clinician review 'are not medical devices', while products supporting 'diagnosis, treatment or prevention' or taking 'automated action without clinician review' are, and 'clinicians remain responsible for checking AI-generated transcripts' ([Dentistry.co.uk, 2 Aug 2026](@dent_mhra)). "
        "NHS England's ambient-scribe guidance (v3, 29 July 2026) with a template DPIA expects DCB0160 documentation, explicit consent, and 'CQC inspection teams will consider if: Technologies are safely deployed' ([GPCE summary](@gpce)). The Chief Dental Officer's 9 October 2026 warning that 'the volume of AI notes is getting incredibly scary' is the first regulator-level signal that note volume itself is a problem ([GDPUK, 16 Oct 2026](@gdpuk_wong)).",
        "Under UK GDPR a dental law firm warns that US AI vendors' user terms 'may put the dentist in breach of their own data protection policies' and that pseudonymised data 'is still personal data' ([JFH Law](@jfh)); the DSPT is due every 30 June and NHS contracts 'may not be renewed or commenced' without it ([DSPT news 169](@dspt169)). "
        "The ICO issues reprimands rather than fines to health bodies; none against a dental practice was found, the nearest being a GP surgery reprimanded in February 2026 for sending 23 years of records to an insurer that asked for five ([Freevacy, 3 Feb 2026](@freevacy)). Dental records are kept <b>11 years minimum</b>, a subject access request is answered <b>within one month, free</b>, and at least one practice site still advertises £10 and £50 fees ([NHSBSA KA-01913](@ka_01913); [MDDUS](@mddus_call)).",
    ])
    out.append(H2("Hit through vendors: when the clearinghouse stops, the money stops"))
    out += bullets([
        "The 2019 ransomware attack on the backup firm DDS Safe encrypted files at about <b>400 dental practices</b>; Henry Schein's 2023 attack notified 29,112 people and cost an estimated 10-15% of customers who 'went elsewhere'; Delta Dental's MOVEit breach exposed about <b>7 million</b> people's claims data; and the 21 February 2024 Change Healthcare attack (<b>190 million</b> people) left dental services 'not fully restored' nearly ten weeks later, with dentists mailing paper claims and paying for postage and call-centre time "
        "([KrebsOnSecurity, 29 Aug 2019](@krebs); [Cybersecurity Dive](@csdive); [Orthodontic Products, 18 Dec 2023](@ortho_delta); [ADA News, 16 Apr 2024](@ada_change)).",
        "In the physician proxy survey after Change Healthcare, <b>36% suspended claim payments, 32% could not submit claims, 22% could not verify eligibility</b> and 90% were still losing revenue two months later ([AMA follow-up survey](@ama_survey)). Absolute Dental's 1,223,635-patient breach came through its managed-service provider's account ([HIPAA Journal](@hj_fines)).",
    ])
    out.append(H3("Table 5.2  Incidents that reached dental practices, 2019-2026"))
    h, r = T(5, 1)
    out.append(tbl(h, r, widths=[40, 24, 26, 46, 40], font="cell_small"))
    out.append(H2("Everyday security at three surgeries"))
    out += bullets([
        "A UK IT provider's <b>192 on-site audits at 184 dental and orthodontic practices</b> (median three surgeries): 48% ran out-of-date Windows or server software (Windows 7 in 40 practices, a couple on XP), 45% slow or unreliable internet, 29% no proper server, <b>25% generic shared logins or weak passwords, 20% exposed or unmanaged remote access, 17% backups failing, partial or absent</b>, 9% Wi-Fi shared with patients, antivirus 'inadequate / none' at 43% of sites where assessable; "
        "anonymised cases include RDP 'left open to the entire internet', 'Every member of staff logged in with the same password: Password1!... no backup system at all', and nightly backup logs reading 'backed up files: 0' ([Dental IT, 30 Jul 2026](@dentalit) [vendor]). A UK practice adviser says 'a huge number of dental practices still aren't using Multi-factor Authentication' although most software offers it free ([Practice Plan, 27 Mar 2026](@practiceplan) [vendor]).",
        "Insurance now enforces what the rule proposes: carriers probe MFA on email, remote access and the PMS, EDR, full-disk encryption and immutable offline backups, 'most carriers will not even issue a policy unless a practice proves it has implemented' them, misattesting lets the carrier deny a claim, and premiums run about <b>$1,000-$2,500 a year for a solo US practice</b> ([Techvera](@techvera) [vendor]; [Florida Dental Association, 17 Jul 2025](@fda_blog)). "
        "Across all UK businesses, 43% identified a breach or attack in the year to April 2025 and phishing hit 35% of micro businesses ([DSIT Cyber Security Breaches Survey 2025](@dsit)).",
    ])
    out.append(fig_image(*CH["security"]))
    out.append(H3("Table 5.3  Everyday security findings and the clocks around records"))
    h, r = T(5, 2)
    out.append(tbl(h, r, widths=[40, 86, 50], font="cell_small"))
    return out


# --------------------------------------------------------------------------
# Section 6
# --------------------------------------------------------------------------
def section_6(CH):
    out = chapter(6, SEC[6]["title"],
                  "The US cycle has six stages and the automation sits unevenly across them: the eligibility pull is electronic for easy payers and a phone call for hard ones, the claim is cheap, the posting is semi-automatic and the denial rework is where the hours go. "
                  "The UK cycle is one claim per course against a contract target, and its risks are deadlines and reconciliation rather than per-procedure adjudication. On both sides a signature, a declaration or a narrative stays human by law.")
    out.append(H2("The US cycle: the pull takes minutes, the call takes an hour"))
    out += bullets([
        "Collecting insurance details and verifying eligibility is where the money goes: <b>$2.1 billion</b> of dental administrative spend in 2023 (+15%) across <b>1.2 billion verifications</b>, about 12 minutes each by phone, fax or mail, 7 by portal and 4 fully electronic, with <b>82% electronic adoption for dental against 96% for medical and 15% still fully manual</b> ([ADA News, 24 Mar 2025](@ada_caqh); [Deepgram on CAQH CORE](@deepgram) [secondary]).",
        "The 270/271 transaction is inside the PMS, but carriers 'frequently' send 'nothing more than a single yes or no response', so a person 'must still interpret the data before importing'; '30-40% of plans still require phone calls', complex cases (Medicaid, HMO, dual coverage) take 30-45 minutes, and one practice described checks taking '30 minutes to 4 hours per patient' ([Open Dental manual](@od_ebenefits); [Ainora](@ainora_verify) [vendor]).",
        "The products that automate it differentiate on portal scraping and breakdown compilation, not on the EDI transaction: Zuub (Capterra 4.7 from 38; cannot search by insurer, name or date of birth), Pearl Precheck, Curve Eligibility+, NexHealth Verification (insurance details 'not written to the EHR'), Weave, Overjet and Verrific; none publishes a price ([Capterra, Zuub](@capterra_zuub) [user, 2026]; [NexHealth help](@nexhealth_help) [vendor]). "
        "The human alternative is priced: eAssist at <b>$250 a month per location for under 30 checks, $650 for 31-75, plus $299 set-up</b>; others at $2.50-$3.00 per check; a DSO employs verification specialists at $22-$27 an hour; Upwork sellers offer 'Breakdown of Benefits' at $5-$20 an hour with 50-plus proposals per post ([eAssist](@eassist) [vendor, snippet]; [MB2 Dental job](@mb2); [Upwork job](@upwork_bob_job) [snippet]).",
        "The claim is cheap (about <b>$0.51 per claim</b> through DentalXChange; Vyne Trellis on one flat fee; Change Healthcare 'not recommended' by Open Dental since the 2024 attack) and posting is semi-automatic (ERA auto-match with detached exceptions); the rework lives in stage six ([XLDent, 27 Mar 2024](@xldent)).",
        "Denial rates have no regulator source: the defensible statement is a <b>4% benchmark against 8-15% at most practices</b>, with vendor and podcast figures of 10-19.3%, a podcast's reading of Delta Dental transparency files at <b>22.5% of 932,795 in-network claims denied in 2024</b>, and a 2026 survey in which nearly 80% of practices reported more denials ([DentistryIQ](@diq_gaps) [snippet]; [Henry Schein One, 10 Sep 2024](@hso_nightmare) [vendor]; [The Dental Billing Podcast](@podcast) [secondary]; [Becker's on Zentist](@beckers_zentist) [snippet]). "
        "A study of one large insurer found <b>72.88% of denials administrative</b>: bundling, thin narratives, frequency limits, coordination-of-benefits errors and wrong identifiers ([DOAJ record](@doaj); [Curve Dental, 1 Jul 2026](@curve_denials) [vendor]).",
        "Only about <b>5% of claims reach appeal and about 50% of those are reversed</b>; 54% of denied claims are eventually paid after an average of three resubmission cycles of 45-60 days; an appeal needs the original claim, the EOB with the reason highlighted, clinical notes, radiographs and a cover letter within 90-180 days, with 'a new, more detailed narrative' each round ([dentalbilling.com](@dentalbilling) [snippet]). "
        "Days in AR run <b>32-45 on average, 40-60 at solo practices</b>, AR over 90 days is 18% against a 5-10% target, outsourced billing costs 4-10% of collections, and credentialing runs 30-120 days per carrier with CAQH re-attestation every 120 days ([Dental Billing Assist](@dba_kpis) [vendor]; [MedsDental](@medsdental_charge) [vendor]; [ADA News, 6 Jul 2026](@ada_cred)).",
    ])
    out.append(fig_image(*CH["verification"]))
    out.append(H3("Table 6.1  US verification and claims measures"))
    h, r = T(6, 0)
    out.append(tbl(h, r, widths=[36, 90, 50], font="cell_small"))
    out.append(H2("The UK cycle: one claim per course against a target"))
    out += bullets([
        "At the desk the patient signs the PR form; an exemption needs the 'evidence seen' box ticked; the tax-credit exemption is no longer accepted for courses accepted on or after 6 April 2025 ([NHSBSA FP17 guidance V14](@fp17_v14)). NHSBSA then sample-checks after the event through DWP records (about <b>1.2 million checks a month</b> across prescriptions and dental), posts an enquiry letter where it cannot confirm, and issues a <b>penalty charge notice of five times the charge up to £100 plus the charge</b>, with a 50% surcharge after 28 days ([gov.uk transparency record](@gov_atr)).",
        "The volumes: <b>115,463 dental PCNs to Universal Credit claimants alone in the year to 16 May 2025</b>; the NAO found about <b>30% of PCNs (1.7 million, £188m) later withdrawn</b> because a valid exemption was confirmed after challenge; NHS England pays NHSBSA £7.59 million for six months of checking ([NHSBSA FOI-02776](@foi_02776); [NAO 2019](@nao); [Find a Tender](@tender)). "
        "Liability sits with the patient 'regardless of whether the FP17PR form is completed by the patient, someone on the patient's behalf, or dental practice staff', the DDU advises staff not to advise on entitlement, and the BDA objects that eligible people 'shouldn't face £100 penalties by default just for ticking the wrong box' ([DDU Journal](@ddu); [GDPUK](@gdpuk_bsa)).",
        "The FP17 is validated against band rules: since 1 April 2022 the clinical data set must match the band claimed, failures first produce <b>comment codes 011-014</b> on the schedule, error 115 and 125 reject outright, BPE and NICE recall interval are mandatory on adult banded claims, and the dentist's declaration 'must be completed by a qualified dentist on every form' ([NHSBSA FP17 guidance V11.4](@fp17_v114); [NHSBSA common errors](@nhsbsa_errors)).",
        "Year-end reconciliation 'is completed by September each year': <b>below 96% delivery, clawback up to 100% of the shortfall plus a breach notice; 96-100% carried forward; above 102% not paid</b> ([NHSBSA KA-01672](@ka_01672)). The April 2026 reforms converted urgent care to a £75 credit per course (£15 fixed, £60 activity) with a minimum of 8.2% of contract value and converted all cash items back to UDAs at each practice's own rate, 'a redistribution of the current contract base' ([Price Bailey](@pricebailey) [secondary]; [Dentistry.co.uk, 21 Jul 2026](@dent_reform)).",
        "The reporting gap followed: Compass's 'Unscheduled' figure shows only the £15 element, the £60 element 'cannot be identified on Compass', associates cannot see the split because eDEN is limited to commissioners and providers, and an LDC motion called it 'a fundamental contract management failure' ([GDPUK, 13 Jul 2026](@gdpuk_compass)). "
        "The practice software sends and flags but does not reconcile: Dentally marks a rejected claim 'Invalid' with a notification found through the NHS Claims report filter and fixed by hand, cannot invalidate a claim once an exemption is linked, and for Scotland requires each dentist to 'manually count teeth present, filled, and extracted for every check-up claim'; NHSBSA 'are unable to advise on EDI transmission issues' ([Dentally help](@dentally_help); [Dentally community, Feb-Apr 2026](@dentally_comm) [user, 2026]; [NHSBSA KA-01797](@ka_01797)). No NHSBSA statistic for the share of FP17s rejected or late was found, and no minutes-per-claim figure exists for UK desks.",
    ])
    out.append(H3("Table 6.2  UK claiming measures"))
    h, r = T(6, 1)
    out.append(tbl(h, r, widths=[34, 92, 50], font="cell_small"))
    out.append(H2("What a machine may not do"))
    out.append(P("What stays human is fixed by law, consent or clinical judgement on both sides of the Atlantic, and it is the boundary every service has to be designed around rather than a gap to fill."))
    out.append(H3("Table 6.3  Steps that stay human, and why"))
    h, r = T(6, 2)
    out.append(tbl(h, r, widths=[50, 16, 66, 44], font="cell_small"))
    out.append(note_box("<b>The pattern:</b> the automatable layer is the data pull, the comparison and the exception list (eligibility responses against coverage tables, FP17 status against the two-month clock and the 96% floor, denial reason codes against appeal deadlines); the non-delegable layer is a named person accountable for a declaration or a decision "
                        "(the dentist's FP17 declaration and clinical band, the patient's signed exemption form, the clinician's narrative and signature on an appeal, Montgomery-standard consent, the review of any AI transcript) and a contract the consumer AI app does not offer (the BAA). Reviews put the pain in the hand-back: bare yes/no responses that a person must interpret, breakdowns that live outside the ledger, and rejections flagged 'Invalid' that a person must find and fix.", warm=True))
    return out


# --------------------------------------------------------------------------
# Section 7
# --------------------------------------------------------------------------
def section_7(CH):
    out = chapter(7, SEC[7]["title"],
                  "Every US practice management system in scope draws the same four complaint clusters in 2024-2026 reviews: support hold times and inconsistent answers, reporting that will not export or disagrees with the analytics add-on, opaque and rising prices with add-ons, and painful migration. "
                  "Open Dental is the only vendor with fully published pricing; UK pricing is almost entirely behind a demo; and nobody sells the reconciliation between the systems.")
    out.append(H2("US practice management systems: prices and limits"))
    out += bullets([
        "<b>Open Dental publishes everything</b>: $199 a month per location for the first year then $149 (up to three providers), eReminders, portal, web forms and payment portal free, eConfirmations $25-$40 a month plus $0.04 a text, Web Sched Recall $75, AI image analysis $149, custom SQL queries <b>$110 an hour</b>, online training $80 an hour, on-site training $4,325 a day, conversions about $1,450 per database plus $850 for documents and $900 for X-rays, non-refundable once complete ([Open Dental fees](@od_fees) [vendor]; [Open Dental conversions](@od_conv) [vendor]).",
        "Dentrix restructured its plans on 4 February 2026; third parties estimate $400-$1,200 a month on an annual contract plus $5,000-$15,000 of server hardware, support $100-$300 a month, modules $50-$300 each, and third-party API access at <b>$1,750 registration plus $25 per site per month for read access and $5,000 plus $38 for write</b> (user-reported) ([CostBench changelog](@costbench_change) [secondary]; [CostBench hidden costs](@costbench_hidden) [secondary]). "
        "Eaglesoft is estimated at $400-$600 a month with payment processing tied to Global Payments 'at above-market rates' and imaging in proprietary formats; Curve, Denticon, Sensei, Fuse, Oryx and tab32 are quote-only with aggregator guesses of $299-$750 ([Dentaltown/RevUp, 4 Jun 2026](@dt_revup) [vendor]; [CostBench pricing 2026](@costbench_2026) [secondary]).",
        "The functional limits that matter to an auditor are specific: Dentrix Ascend cannot print route slips more than three days ahead, sends preauthorisations only to the primary insurer, and its Power Reporting is 'unnecessarily clumsy' so users buy Jarvis 'at additional cost'; Dentrix reports 'are generic and most don't allow importing them to Excel'; Fuse reporting 'falls short for when adjustments were made or refunds were applied'; Sensei Cloud has no online booking; Denticon required 're-charting the entire chart' to move a patient between accounts; Open Dental has 'allocated/unallocated/hidden payments in the ledger' that users find hard to read ([Capterra, Dentrix](@capterra_dentrix) [snippet]; [Dentaltown/RevUp](@dt_revup) [vendor]).",
    ])
    h, r = T(7, 0)
    parts = split_cols(h, r, [[1, 2], [3, 4]])
    out.append(H3("Table 7.1  US PMS, part 1: published price and rating"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[34, 96, 46], font="cell_small"))
    out.append(H3("Table 7.2  US PMS, part 2: what it does not do, per users and vendor"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[30, 100, 46], font="cell_small"))
    out.append(H2("The communication, analytics and AI-receptionist layer"))
    out += bullets([
        "Weave starts 'from $199 per month' with tiers priced on request and holds a Trustpilot 4.6 from 956 reviews with 9% one-star: 'no way to cancel on the website', 'left on hold', a promised $1,600 buy-out credit never issued and a number 'ported incorrectly' (January 2026), charged after giving 60 days' notice ([Weave pricing](@weave_pricing) [vendor]; [Trustpilot, Weave](@tp_weave) [user, 2026]). "
        "NexHealth (Capterra 4.7 from 31) has no public prices, annual plans paid up front with 90 days' non-renewal notice, and complaints that with Curve it 'didn't integrate as nicely' and support is 'hard to get in touch with... once we were an established customer' ([NexHealth pricing](@nexhealth_pricing) [vendor]; [Capterra, NexHealth](@capterra_nexhealth) [snippet]).",
        "RevenueWell's pricing page returns 404 and reviews say 'Very hard to get away from contarct' and set-up 'took over three months'; Solutionreach scores 3.8 from 236 with a five-day outage 'without a callback' and auto-renewal ([Capterra, RevenueWell](@capterra_rw) [snippet]; [Capterra, Solutionreach](@capterra_sr) [snippet]). "
        "The analytics layer sells the number but not the follow-up: Dental Intelligence (4.6 from 53; start-up fee, no refunds, auto-renewal; SelectHub guesses $399 a user a month) documents an 'Unscheduled Patients' board as a paid layer, one reviewer says 'the numbers were always inaccurate and DI wouldn't/couldn't fix it', and DI's own help centre explains its claims-aging figure will not match Dentrix's Insurance Aging Report, both 'valid', with no reconciliation method given ([G2, DI](@g2_di) [snippet]; [DI vs Dentrix aging](@di_aging) [vendor]).",
        "AI receptionists have <b>no public pricing and no independent reviews</b>: Arini's, Viva's and Peerlogic's pricing pages are 404, dental-specific platforms are estimated at <b>$300-$900 per location per month plus $0-$2,000 set-up and $50-$300 a month for PMS integration</b>, and vendors concede 'limitations exist in handling complex nuances or accents' ([AI Frontdesk on Arini](@aifd_arini) [vendor]; [Sagnik Bhattacharya, 27 Sep 2026](@sagnik) [secondary]). "
        "Integration depth is thin: Zapier app pages for Open Dental and Dentally return 404, Sensei's API needs Carestream approval, and Dentally is the only in-scope PMS with its own Zapier page ([US Tech Automations](@ustech) [vendor]).",
    ])
    out.append(H2("UK pricing behind a demo, and the first-hand pain on Dentally's own community"))
    out += bullets([
        "Dentally publishes tiers excluding VAT, <b>Starter about £125-£134 for one surgery, Essentials £220-£238, Pro £320-£346</b>; Starter has chat-only support and no portal (no digital forms, online booking or kiosk); AI clinical notes are capped at 45 or 90 transcriptions per surgery per month; recalls, SMS costs, migration fees and contract terms are not on the page ([Dentally pricing](@dentally_pricing) [vendor]; [Whito](@whito_sw) [secondary]). "
        "Scottish users wrote (February to April 2026) that the software is 'clunkier than older softwares especially for use within the Scottish NHS SDR', that the GP17 DMF count is manual 'for every check-up claim', that 'phone support is a paid add-on' and that sister practices were trained 'with wrong information' that delayed claims 'by at least a month'; the product director replied that 'Auto-add fees and GP17 DMF are known gaps' ([Dentally community](@dentally_comm) [user, 2026]).",
        "Exact (Software of Excellence) publishes no price and scores Capterra 4.1 from 17 with value for money at 3.3; Aerona lists £45-£110 tiers on Capterra (4.8 from 22); Bridge-IT cloud is £40-£80 per surgery; DenGro (lead CRM) <b>£199 or £249 per practice per month including VAT</b>, rolling 30 days; both Exact's and Dentally's Trustpilot pages have zero reviews ([Capterra, EXACT](@capterra_exact) [snippet]; [DenGro pricing](@dengro_pricing) [vendor]). "
        "Sensei Cloud's UK G-Cloud terms are the clearest statement of exit cost in the sample: 12-month rolling contract with 90 days' notice, data export on exit <b>CSV only, on written request and advance payment, available for 60 days</b>, API access requiring Carestream approval ([G-Cloud 14](@gcloud) [vendor]).",
        "UK AI receptionists are priced by a consultant at <b>£150-£800 a month plus £500-£3,000 set-up</b>, with the caveats that they 'occasionally say something inappropriate', fail on complex multi-surgery scheduling, and below about 50 convertible missed calls a month may cost more than they recover ([Lilach Bullock](@lilach) [vendor]). "
        "Nothing in the UK stack reconciles FP17 submissions to Compass or eDEN for the 2026 unscheduled target or per-performer pay, no Denplan reconciliation feature was found in Exact or Dentally, and lab tracking in CareStack 'can be used only to keep track of orders internally. There is no communication to the labs' ([GDPUK, 13 Jul 2026](@gdpuk_compass); [CareStack](@carestack_lab) [vendor]).",
    ])
    out.append(fig_image(*CH["platforms"]))
    out.append(H3("Table 7.3  The stack for a two-dentist practice, 2026"))
    h, r = T(7, 1)
    out.append(tbl(h, r, widths=[44, 70, 26, 36], font="cell_small"))
    out.append(H2("Misconfiguration, underuse, and the audit nobody prices"))
    out += bullets([
        "Dentrix Enterprise's own clean-up checklist (2020) is the de facto audit scope: duplicate insurance plans and employers, departed providers still active, patients never inactivated, <b>multiple continuing-care types that 'cause recall dates to reset incorrectly and patients to be missed on lists'</b>, procedures not billed, claims not sent, outdated fee schedules ([Dentrix Enterprise blog](@dentrix_ent) [vendor]). "
        "Other evidence of underuse: only 26% of practices offered online booking in NexHealth's 2022 survey; eligibility is 'almost always going to be last'; two-thirds of UK practices track leads on paper; a two-doctor practice paid $300 a month for a reminder program 'it had barely used for months'; two analytics products reading the same Dentrix database show different claims-aging totals ([SchedulingKit](@schedkit) [secondary]; [Thriving Dentist, 14 Oct 2026](@thriving) [vendor]).",
        "The audit and consultant market is unpriced because it is unbundled: vendors give the checklist away, analytics vendors sell the dashboard, offshore labour sells the keystrokes, and nobody sells the validation step. <b>No published price for a 'Dentrix audit', 'Exact health check', 'recall audit' or 'database cleanup' was found.</b> The anchors that exist are Open Dental's $110 an hour for custom queries and $4,325 a day on site; an Upwork Open Dental posting at <b>$4-$7 an hour</b> (30+ hours a week); Philippine dental VAs at $600-$700 a month; managed IT at $1,200-$1,500 a month per office; coder-forum anchors of consulting 'from $75 hourly' and audits 'from $500 and my biggest one was $15,000'; and a UK trainer day at <b>£600-£1,500</b> "
        "([Open Dental fees](@od_fees) [vendor]; [Upwork listing](@upwork_od) [snippet]; [AAPC forum](@aapc) [user]; [Dominate Dental training](@dominate_training) [vendor]). A DSO job ad for a 'Fee Schedule Administrator' auditing 'fee schedules against contracted reimbursement terms' shows the work exists as an in-house role at group level and not as a product for a three-chair practice ([Greenhouse, PCDM](@greenhouse); [MedsDental audit](@medsdental_audit) [vendor]).",
    ])
    out.append(H3("Table 7.4  Audit and consultant price anchors"))
    h, r = T(7, 2)
    out.append(tbl(h, r, widths=[50, 80, 46], font="cell_small"))
    out.append(note_box("<b>The audit angle:</b> set-up is a paid line item at every vendor and the 'configured but not working' complaints are all failures a periodic check would have caught before a patient or an auditor did: a recall type that resets dates, an eligibility add-on that never writes back, a claims-aging total that disagrees with the analytics layer, an FP17 flagged 'Invalid' in a filter nobody opens, a reminder program paid for and unused. "
                        "No vendor in scope documents a misconfiguration rate, publishes a utilisation statistic or sells independent validation after go-live; the only priced anchors are a vendor's hourly SQL rate, an offshore poster's $4 an hour and a UK trainer's day rate.", warm=True))
    return out


# --------------------------------------------------------------------------
# Section 8
# --------------------------------------------------------------------------
def section_8(CH):
    out = chapter(8, SEC[8]["title"],
                  "Each handoff in the patient and payment chain is owned by a different product, and none owns the step before or after it: the lead CRM stops at 'new patient created', the PMS stops at 'treatment planned', the analytics layer surfaces 'unscheduled' but relies on a human to call, and the comms layer only knows about appointments that already exist. "
                  "The numbers practices trust (case acceptance, aging, recall) differ by product because each defines the denominator differently, so the gap is definitional before it is operational. Every handoff statistic is vendor or consultant data; no practitioner forum post on any handoff was retrievable.")
    h, r = T(8, 0)
    parts = split_cols(h, r, [[1, 2], [3, 4]])
    out.append(H3("Table 8.1  Twelve handoffs, part 1: what drops, and the numbers"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[34, 72, 70], font="cell_small", first_col_bold=True))
    out.append(H3("Table 8.2  Twelve handoffs, part 2: products that claim the step, and sources"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[34, 82, 60], font="cell_small", first_col_bold=True))
    out.append(source_line("Definitional mismatch example: Dental Intelligence's claims-aging figure will not match Dentrix's Insurance Aging Report because Dentrix recalculates estimates each run and includes inactive patients while DI snapshots at claim creation; both are 'valid' and no reconciliation method is given [%d]." % ref(U["di_aging"])))
    return out


# --------------------------------------------------------------------------
# Section 9
# --------------------------------------------------------------------------
def section_9(CH):
    out = chapter(9, SEC[9]["title"],
                  "The dated quotes below are what the reader can put in front of a practice owner; most come from search-engine summaries of review sites that blocked direct reading, so exact dates are given only where the summary carried them.")
    out.append(H3("Table 9.1  Platforms: rating, dated user words, source"))
    h, r = T(9, 0)
    out.append(tbl(h, r, widths=[28, 26, 86, 36], font="cell_small", first_col_bold=True))
    out.append(H2("Seven gaps that recur regardless of vendor or country"))
    out += bullets([
        "Reporting that cannot be exported or trusted without a paid analytics layer (Dentrix, Ascend, Fuse, Sensei, Denticon, the DI-versus-Dentrix aging mismatch).",
        "Unscheduled-treatment follow-up left to a human list (46% acceptance; DI, Adit and Planet DDS boards; '60-70% no systematic follow-up').",
        "Recall lists unworked and corrupted by duplicate continuing-care types.",
        "Insurance eligibility and claims aging handled outside the PMS at hours a day (Weave, NexHealth and Curve add-ons that do not write back to the ledger).",
        "Contract lock-in and opaque pricing with add-on creep (Weave, Solutionreach, RevenueWell, NexHealth, DI, Sensei, Eaglesoft subscription, Dentrix API fees).",
        "Migration loss of images and in-flight claims with non-refundable conversion fees (Curve, Open Dental, Sensei's CSV-only export).",
        "UK-specific: NHS claim validation and UDA-to-Compass reconciliation left to the practice while leads are handled on paper (Dentally community, GDPUK, DenGro). The consultant-shaped work in all seven is reconciliation, not configuration: aging report against analytics, Compass against the PMS, lead CRM against the PMS patient list, recall types against continuing-care lists ([Dentaltown/RevUp](@dt_revup) [vendor]; [Dentally community](@dentally_comm) [user, 2026]; [GDPUK, 13 Jul 2026](@gdpuk_compass)).",
    ])
    return out


# ==========================================================================
# Content, part C: section 10 (ranking and gap cards), 11, 12, conclusion, sources
# ==========================================================================
U.update({
    "ellis_overjet": "https://www.ellis.com/visa-sponsors/overjet-inc/salaries",
    "ellis_videa": "https://www.ellis.com/visa-sponsors/videahealth-inc/salaries",
    "ellis_weave": "https://www.ellis.com/visa-sponsors/weave-communications-inc/salaries",
    "ellis_hso": "https://www.ellis.com/visa-sponsors/henry-schein-one-llc/salaries",
    "ellis_pds": "https://www.ellis.com/visa-sponsors/pacific-dental-services-llc/salaries",
    "ellis_heartland": "https://www.ellis.com/visa-sponsors/heartland-dental-llc/salaries",
    "ellis_dentsply": "https://www.ellis.com/visa-sponsors/dentsply-sirona-inc/salaries",
    "gd_hso": "https://www.glassdoor.co.uk/Salary/Henry-Schein-One-Salaries-E7869334.htm",
    "gd_soe": "https://www.glassdoor.co.uk/Salary/Software-of-Excellence-Salaries-E3047761.htm",
    "overjet_careers": "https://www.overjet.com/careers",
    "videa_careers": "https://www.videa.ai/careers",
    "dentalpost_jobs": "https://www.dentalpost.net/dental-jobs/",
    "gc_overjet": "https://jobs.generalcatalyst.com/companies/overjet/jobs/58574662-staff-machine-learning-engineer",
    "builtin_pearl": "https://www.builtinchicago.org/job/senior-data-scientist/9970279",
    "wttj_hso": "https://app.welcometothejungle.com/jobs/CsvSzjDP/company",
    "ellis_overjet_h1b": "https://www.ellis.com/visa-sponsors/overjet-inc/h1b",
    "weave_careers": "https://www.getweave.com/careers/",
    "nexhealth_careers": "https://www.nexhealth.com/careers",
    "bw_videa": "https://www.businesswire.com/news/home/20250128195626/en/VideaHealth-Raises-$40M-in-Oversubscribed-Series-B-Funding-to-Revolutionize-Dental-Care-with-AI-Driven-Solutions",
    "cbi_overjet": "https://www.cbinsights.com/company/overjet/financials",
    "hs_kkr": "https://investor.henryschein.com/news-releases/news-release-details/henry-schein-announces-strategic-investment-kkr-board-changes",
    "hso_voice": "https://investor.henryschein.com/news-releases/news-release-details/2025/Henry-Schein-One-Unveils-Industry-first-Natively-Embedded-Voice-Workflow-at-2025-Greater-New-York-Dental-Meeting/default.aspx",
    "dentsply_10q": "https://www.sec.gov/Archives/edgar/data/818479/000081847925000257/xray-20250930.htm",
    "align_10q": "https://www.sec.gov/Archives/edgar/data/1097149/000109714925000079/algn-20250930.htm",
    "beckers_dso": "https://beckersdental.com/dso-dpms/how-dental-ma-is-evolving-in-2026",
    "oj_1335685": "https://www.onlinejobs.ph/jobseekers/job/1335685",
    "remotive": "https://remotive.com/remote/jobs/all-others/dental-insurance-revenue-cycle-virtual-assistant-5325835",
    "beckers_sa": "https://www.beckersdental.com/uncategorized/66-of-dental-practices-budget-up-to-500-per-month-for-workflow-software-5-insights/",
    "upwork_auto": "https://www.upwork.com/freelance-jobs/apply/Automation-Specialist-for-Dental-Clinics_~022057415977014134702/",
    "upwork_airec": "https://www.upwork.com/hire/ai-receptionist-builders/",
    "upwork_voice_gig": "https://www.upwork.com/services/product/development-it-an-ai-voice-agent-for-a-dental-clinic-1879449985699609816",
    "fiverr_dental2": "https://block.fiverr.com/gigs/dental?page=2",
    "consulting_success": "https://www.consultingsuccess.com/consulting-hourly-rate",
    "upwork_highnote": "https://www.upwork.com/freelance-jobs/apply/HubSpot-Specialist-Long-Term-Partner_~022068117293050896612/",
    "swydo": "https://www.swydo.com/?p=21674",
})

GAP_FIELDS = ["Problem", "Who has it", "Evidence", "Their words", "How they handle it today", "Vendors already covering it", "Automatable?", "What the reader would need to learn"]


def _badge_values(rank_row):
    signal, cov, auto = rank_row[2], rank_row[3], rank_row[7]
    s = signal.split(":")[0].split(",")[0].strip().lower()
    sig = s if s else "medium"
    sig_warm = s.startswith(("very high", "high"))
    c = cov.split(":")[0].strip().lower()
    if c.startswith(("weak", "thin", "unknown", "unpriced")):
        cv = "weak" if c.startswith("weak") else c.split(" ")[0]
        cv_warm = True
    elif c.startswith("strong on"):
        cv = "strong on the easy part"
        cv_warm = False
    elif c.startswith("very strong"):
        cv = "crowded"
        cv_warm = False
    else:
        cv = c.split(" ")[0] if c else "partial"
        cv_warm = False
    a = auto.split(":")[0].split(";")[0].strip().lower()
    au = a.split()[0] if a else "partly"
    return (sig, sig_warm), (cv, cv_warm), au


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
    (sig, sig_warm), (cv, cv_warm), au = badges
    head = Table([[Paragraph(str(rank), S["card_rank"]),
                   Paragraph(inl(title, refs=False), S["card_title"]),
                   Paragraph("<b>%s</b>" % esc(country), ParagraphStyle("cc", parent=S["badge"], textColor=white, alignment=2))]],
                 colWidths=[13 * mm, FRAME_W - 13 * mm - 34 * mm, 34 * mm])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    chips = Table([[_chip("Problem signal", sig, sig_warm), "", _chip("Vendor coverage", cv, cv_warm), "", _chip("Automatable", au, False)]],
                  colWidths=[(FRAME_W - 8 * mm) / 3, 4 * mm, (FRAME_W - 8 * mm) / 3, 4 * mm, (FRAME_W - 8 * mm) / 3])
    chips.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                               ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    rows = []
    for label in GAP_FIELDS:
        rows.append([Paragraph(esc(label), S["cell_label"]), Paragraph(inl(fields.get(label, "")), S["card_cell"])])
    body = Table(rows, colWidths=[34 * mm, FRAME_W - 34 * mm], splitByRow=1)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, C_GRID), ("LINEBELOW", (0, -1), (-1, -1), 0.8, C_ACCENT),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5)]
    for i in range(len(rows)):
        if i % 2 == 1:
            st.append(("BACKGROUND", (0, i), (-1, i), C_ZEBRA))
    body.setStyle(TableStyle(st))
    return [KeepTogether([head, chips, body]), Spacer(1, 7 * mm)]


def ranking_table(h, r):
    grey = ParagraphStyle("cell_grey", parent=S["cell_small"], textColor=C_MUTED)
    heads = ["#", "Gap", "Problem signal", "Vendor coverage of the exact sub-problem", "Private data fit", "Agency sale", "Country", "Automatable"]
    data = [[Paragraph(esc(x), S["cell_head"]) for x in heads]]
    for row in r:
        crowded = row[0].strip().lower().startswith("crowded")
        st = grey if crowded else S["cell_small"]
        cells = [Paragraph(inl(c), st) for c in row]
        if crowded:
            cells[0] = Paragraph("<i>crowded</i>", grey)
        data.append(cells)
    widths = [w * mm for w in [14, 32, 31, 32, 17, 14, 14, 22]]
    t = Table(data, colWidths=widths, repeatRows=1, splitByRow=1)
    style = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, 0), C_TINT),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, C_ACCENT),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, C_GRID),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, C_LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 3.5), ("RIGHTPADDING", (0, 0), (-1, -1), 3.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
    ]
    for ri in range(1, len(data)):
        if ri % 2 == 0:
            style.append(("BACKGROUND", (0, ri), (-1, ri), C_ZEBRA))
    first_crowded = next((i for i, row in enumerate(r) if row[0].strip().lower().startswith("crowded")), None)
    if first_crowded is not None:
        style.append(("LINEABOVE", (0, first_crowded + 1), (-1, first_crowded + 1), 0.9, C_LINE))
    t.setStyle(TableStyle(style))
    t.spaceBefore = 3
    t.spaceAfter = 5
    return t


def section_10(CH):
    out = chapter(10, SEC[10]["title"],
                  "The ranking scores each gap on how strong and recent the problem signal is (regulator findings, enforcement, dated user complaints, job-ad and freelance demand, search phrases) and how weak the vendor coverage of the exact sub-problem is (whether a named product claims it and whether any independent source confirms it). "
                  "A third column marks fit with a self-hosted or private-data angle, strongest where the work touches patient, claim or NHS records that the law keeps under a BAA, UK GDPR and the DSPT; a fourth marks whether the natural buyer is a dental marketing agency rather than a practice. "
                  "Staffing shortage, the problem owners name first, is not listed because no software or data gap describes it. Crowded problems that are not gaps follow the thirteen in grey. The report describes existing products factually and does not design or recommend solutions.")
    out.append(H3("Table 10.1  The ranking, with the eight crowded areas in grey at the end"))
    h, r = T(10, 0)
    out.append(ranking_table(h, r))
    out.append(fig_image(*CH["gap_matrix"]))
    out.append(H2("The thirteen gap cards"))
    out.append(Paragraph("Every card has the same eight fields in the same order. The three badges summarise the ranking table: problem signal (the report's own grade, warm when very high or high), vendor coverage "
                         "(warm when weak, thin or unpriced; 'strong on the easy part' where vendors cover the check but not the reconciliation), and the report's own first word on automation (fully or partly).", S["body"]))
    titles = SEC[10]["h3"]
    for title, table in zip(titles, SEC[10]["tables"][1:14]):
        m = re.match(r"^Gap (\d+)\.\s+(.*)$", title)
        rank = int(m.group(1))
        name = m.group(2)
        fields = {row[0].strip(): row[1] for row in table["rows"]}
        rank_row = r[rank - 1]
        out += gap_card(rank, name, rank_row[6], fields, _badge_values(rank_row))
    out.append(H2("Private-data fit, the agency sale, and the crowded areas"))
    out += bullets([
        "The self-hosted or private-data angle is strongest for gaps 1, 2, 4, 6, 7, 9, 12 and 13: each touches claim, patient, NHS or clinical records that the law keeps under a BAA, UK GDPR and the DSPT, that consumer AI tools cannot lawfully hold, and that staff today paste into free tools or key by hand.",
        "The agency sale is strongest for gaps 3 and 5 and partly 8: agencies lose clients over unproven ROI and write the pages that break the GDC, ASA and FTC rules, their margin leaves 'a few hundred dollars' a month per client for subcontracted work, and they already buy tracking and HubSpot set-up on Upwork before a dental client launches ([Upwork, HighNote](@upwork_highnote) [snippet]; [Swydo on Promethean](@swydo) [secondary]).",
        "The crowded areas that are not gaps: AI phone receptionists and call intelligence (no public prices, no independent reviews, 'the latest grift' in practitioner circles); dental SEO, websites and Google Ads management; review generation and texting tools; appointment reminders and confirmations; insurance-verification keystrokes and outsourced billing at $5-$8 an hour or 4-10% of collections; imaging AI (FDA-cleared, venture-funded); PMS set-up gigs and VA agencies; membership-plan platforms and credentialing services.",
    ])
    return out


def section_11(CH):
    out = chapter(11, SEC[11]["title"],
                  "The employed path pays well and is small: a handful of R&D seats per vendor in named hubs, H-1B medians of $175,000-$195,000, and ads that ask for mainstream depth rather than dentistry. "
                  "The freelance path is open to anyone and priced against offshore labour: a $600-$700-a-month Philippine VA who already lists Open Dental, posting gigs at $4-$7 an hour, and the only mid-four-figure budgets in AI-receptionist builds and PMS integration.")
    out.append(H2("The employed path: pay by employer"))
    out += bullets([
        "US Department of Labor H-1B filings put dental-AI engineering at <b>$145,000-$240,000 base</b> (Overjet median $195,000: Senior ML Scientist $205,000, Data Engineer $203,000, Staff Software Engineer $225,000; VideaHealth median $175,000), horizontal dental SaaS at <b>$110,000-$170,000</b> (Weave median $147,183; Henry Schein One median $120,700 and a Staff Software Engineer ad at $110,000-$145,000 'Remote from US'), DSO internal IT at <b>$75,000-$190,000</b> (PDS Health 'Engineer, AI Solutions' $140,000; Heartland Senior Data Engineer $187,257), insurers around $99,000-$154,000 and device makers lower (Dentsply Sirona AI/ML Engineer median $90,854) "
        "([Ellis, Overjet](@ellis_overjet); [Ellis, VideaHealth](@ellis_videa); [Ellis, Weave](@ellis_weave); [Ellis, Henry Schein One](@ellis_hso); [Ellis, PDS](@ellis_pds); [Ellis, Heartland](@ellis_heartland); [Ellis, Dentsply](@ellis_dentsply)). UK dental-software pay is <b>£46,000-£75,000 for software engineers and £63,000-£88,000 for seniors</b> at Henry Schein One and Software of Excellence, roughly a third to a half of US dental-AI pay ([Glassdoor UK, HSO](@gd_hso) [snippet]; [Glassdoor UK, SOE](@gd_soe) [snippet]).",
        "The seats are few: Overjet's careers page on 16 October 2026 listed <b>31 open roles of which three were R&D engineering</b>, all in San Mateo or Lahore; VideaHealth and Dental Intelligence listed no roles; DentalPost's 1,600-plus jobs have no technology category ([Overjet careers](@overjet_careers); [Videa careers](@videa_careers); [DentalPost](@dentalpost_jobs)). "
        "The ads ask for mainstream depth, not dentistry: Overjet's Staff ML Engineer wanted 10+ years in Python, Go, C++ or Java, PyTorch, computer vision or LLMs, 6+ years on GCP or AWS, Kubernetes and Terraform, with no degree stated; dental knowledge is hired separately as 'Dental Consultant' clinician roles; FHIR, HL7, RAG, vector databases and PMS APIs appeared in no engineering ad found ([General Catalyst board, Overjet](@gc_overjet); [Built In, Pearl](@builtin_pearl) [snippet]; [Welcome to the Jungle, HSO](@wttj_hso)).",
        "Remote means remote inside the US or a named hub: Overjet is hybrid two days a week in San Mateo, New York, Salt Lake City or Boston with Lahore as a geo-hub; Weave opened a second HQ in Noida; NexHealth has 'remote Nexers across the US, South America, and Europe'; sponsorship is small (Overjet 42 H-1B filings 2020-2026, 4-13 a year; VideaHealth 12; Henry Schein One 9; Weave 18; PDS 59) and no ad stated a sponsorship policy ([Ellis, Overjet H-1B](@ellis_overjet_h1b); [Weave careers](@weave_careers); [NexHealth careers](@nexhealth_careers)).",
        "The 2025-2026 moves favour incumbents embedding others' AI over new ML teams: VideaHealth $40m Series B (Jan 2025), an Overjet Series C-II of $24.56m (one aggregator), KKR's $250m into Henry Schein, Henry Schein One's AWS partnership and embedded Voice Notes, forms and eligibility in Dentrix (Nov 2025), Open Dental adding $149 AI image analysis; against that, Dentsply Sirona's 2-4% workforce cut, Align's Q3 2025 restructuring, nearly 200 DSO transactions in H1 2026, and no 2025-2026 venture money found for Zuub, NexHealth, Dental Intelligence or Curve "
        "([Business Wire, VideaHealth](@bw_videa); [CB Insights, Overjet](@cbi_overjet) [snippet]; [Henry Schein, KKR](@hs_kkr); [Henry Schein One, 25 Nov 2025](@hso_voice); [Dentsply 10-Q](@dentsply_10q); [Align 10-Q](@align_10q); [Becker's, DSO M&A](@beckers_dso) [snippet]).",
    ])
    out.append(fig_image(*CH["pay_employed"]))
    out.append(H2("The freelance path is priced against offshore labour"))
    out += bullets([
        "The buyer-side anchors are the Philippine dental VA at <b>$600-$700 a month or $5-$8 an hour</b>, already listing Open Dental, Flex, insurance verification and claims; the AI-receptionist subscription at $300-$900 per location per month; the agency retainer at $1,000-$2,500 a month with a management allocation of $400-$700; billing firms at 4-10% of collections; and the $401-$500 a month that 66% of practices budget for workflow software ([OnlineJobs.ph 1335685](@oj_1335685); [Remotive](@remotive) [snippet]; [Sagnik Bhattacharya](@sagnik) [secondary]; [Becker's on Software Advice](@beckers_sa) [snippet]).",
        "Visible freelance demand for generic 'dental automation' is thin and cheap (one 'Automation Specialist for Dental Clinics' post at $50 fixed; posting at $4-$7 an hour), but the AI-receptionist build market has defined budgets: builders at <b>$30-$61 an hour</b>, a $20-$45 an hour agency job for 'Medical/Dental Virtual Receptionist (Voice & Chat)', no-code set-up $500-$1,500, <b>custom voice-agent build $2,500-$8,000</b>, CRM and telephony integration $800-$3,000, multi-location roll-out $4,000-$12,000, and a productised 'AI Voice Agent For A Dental Clinic' gig at $700 with three-day delivery "
        "([Upwork, automation post](@upwork_auto) [snippet]; [Upwork AI receptionist builders](@upwork_airec) [snippet]; [Upwork dental voice agent gig](@upwork_voice_gig) [snippet]).",
        "Marketing gigs are commoditised (Fiverr dental websites $80-$425, SEO articles from $10, category pages showing roughly 300-3,100 listings; PeoplePerHour dental websites $235-$1,000, Google Ads management $450) and Upwork insurance posts draw 50-plus proposals at $5-$20 an hour ([Fiverr](@fiverr_dental2) [snippet]; [PeoplePerHour](@pph); [Upwork](@upwork_bob_job) [snippet]). "
        "Consulting rates that exist are Open Dental's $110 an hour for custom SQL and $4,325 a day on site, UK marketing consultations at £75-£200 an hour and a trainer day at £600-£1,500, and general IT consulting at $100-$300 an hour; <b>no Dentrix, Exact or Dentally independent consultant rate is published anywhere</b> ([Open Dental fees](@od_fees) [vendor]; [Dominate Dental](@dominate_cms) [vendor]; [Consulting Success](@consulting_success) [secondary]).",
        "Practices buy subscription-first and vendor-bundled (PMS add-ons, an AI receptionist, a billing service, a VA), so what the market visibly buys from a freelancer is implementation or integration of those subscriptions, or a replacement for a VA or billing-service cost line, not bespoke AI engineering; dentists name poor PMS integration (22%) as the second reason they abandon AI tools and better integration (22%) as the second reason they adopt ([GDPUK, 1 Jun 2026](@gdpuk_aisurvey)).",
    ])
    out.append(fig_image(*CH["freelance"]))
    out.append(H3("Table 11.1  Employed path against freelance path, dimension by dimension"))
    h, r = T(11, 0)
    out.append(tbl(h, r, widths=[26, 76, 74], font="cell_small", first_col_bold=True))
    out.append(note_box("<b>The practical reading in the report's own words:</b> an employed US dental-AI engineer earns in a month what the visible freelance market pays for one custom voice-agent build; the UK employed figure equals a year or two of a single agency retainer; the seats are a handful per vendor in named hubs with low sponsorship volumes; "
                        "the freelance floor is set by a $700-a-month VA who already knows Open Dental; and the only budgets above that floor found in the open market are integration and reconciliation work, which is also the work the practices, the agencies and the regulators have all, in different words, said is missing. Neither path needs a clinical background; both need PMS integration, Python and SQL, insurance or NHS claiming workflow knowledge, and HIPAA or UK GDPR handling, which the ads do not state but the fines and the vendor terms make unavoidable."))
    return out


def section_12(CH):
    out = chapter(12, SEC[12]["title"],
                  "The researchers were blocked by many primary hosts (" + BLOCKED_HOSTS.rstrip(".") + "), so a large share of quotes come from search summaries and secondary coverage, and the web-search budget ran out part-way through every workstream. "
                  "The items below are the ones a reader should treat as unconfirmed before repeating them to a client.")
    out.append(H3("Table 12.1  Items that rest on snippets, secondary reports, vendor claims or conflicting sources"))
    h, r = T(12, 0)
    out.append(tbl(h, r, widths=[74, 102], font="cell"))
    return out


def conclusion_page(CH):
    out = chapter(None, "Conclusion", None)
    out.append(Paragraph("What the research changes", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("<b>The problem a small dental practice will pay to remove is not dentistry and not even 'the phone'.</b> It is the chain of handoffs that each product owns one link of and nobody reconciles: the lead the agency delivered against the patient the PMS seated, the treatment the dentist planned against the appointment nobody booked, the breakdown the add-on produced against the ledger the biller works, "
            "the FP17 the software sent against the UDA target Compass can no longer show, the record request the patient made against the thirty-day clock."),
        inl("In 2025-2026 that chain came under outside pressure in both countries at once: the NHS reforms of April 2026 and a reporting system that cannot show the new target; the FTC review rule, the proposed Security Rule and OCR's October 2026 dental settlement; the MHRA's device line and the Chief Dental Officer's warning about AI note volume; insurers that will not bind cover without MFA and backups; "
            "and a marketing market in which neither the practice nor the agency can prove what the money bought. The strongest language is therefore reconciliation and evidence, not answering or generating."),
    ]]
    out.append(Paragraph("Where the vendors already sit, and what the law reserves to a person", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("AI receptionists, SEO, review tools, reminders, offshore verification labour and imaging AI are where the vendors, the gigs and the venture money already sit, and their users complain about contracts, prices, accents and upselling, not absence."),
        inl("The steps the law reserves to a person (the dentist's FP17 declaration and the clinical band, the patient's signed exemption form, Montgomery-standard consent, the clinician's narrative and signature on an appeal, the review of any AI transcript, the release decision on a record request, the BAA that consumer ChatGPT does not offer) are boundaries, and every one of the thirteen gaps stops at one of them."),
    ]]
    out.append(Paragraph("Two vocabularies, two markets for the same skills", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("The vocabulary is split by country: 'clawback', 'UDAs', 'FP17', 'FTA', 'exemption', 'CQC', 'GDC' and 'Denplan' for the UK; 'no-show', 'breakdown of benefits', 'claim denied', 'PPO', 'office manager', 'HIPAA' and 'membership plan' for the US. The same service will need two sets of words, and sections 2 and 10 give them verbatim."),
        inl("On money, an employed US dental-AI engineer earns in a month what the visible freelance market pays for one custom voice-agent build, the UK employed figure equals a year or two of a single agency retainer, the seats are a handful per vendor in named hubs with low sponsorship volumes, and the freelance floor is set by a $700-a-month VA who already knows Open Dental; "
            "the only budgets above that floor found in the open market are integration and reconciliation work, which is also the work the practices, the agencies and the regulators have all, in different words, said is missing."),
    ]]
    out.append(Spacer(1, 6 * mm))
    out.append(note_box("This document reports problems, workflows, numbers, vocabulary and gaps only. It contains no solutions and no recommendations. The Sources appendix lists every URL the research cited; section 12 lists what could not be verified.", warm=False))
    return out


def sources_appendix():
    out = chapter(None, "Sources", "Every URL cited in the research report, numbered in order of first appearance. Body references [n] point here. "
                                   "Hosts that blocked the researcher are listed in section 12, which follows this appendix; facts from them carry the [snippet] or [secondary] tag.")
    rows = []
    for i, url in enumerate(URLS, 1):
        label = URL_LABEL.get(url, "")
        rows.append([Paragraph("[%d]" % i, S["src_num"]),
                     Paragraph("<b>%s</b> &nbsp; <font color='%s'>%s</font>" % (esc(label), INK_SEC, esc(url)), S["src_entry"])])
    t = Table(rows, colWidths=[11 * mm, FRAME_W - 11 * mm], repeatRows=0, splitByRow=1)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.25, C_GRID),
                           ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                           ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6)]))
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
                                 title="Small dental practice problems UK and US (16 Oct 2026)",
                                 author="Research for Mustafa Shoukat",
                                 subject="Problems, workflows, numbers, vocabulary and service gaps in small UK and US dental practices")
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
    story += section_11(CH)
    # closing order asked for: Sources appendix, then what could not be verified, then the conclusion as the closing page
    story += sources_appendix()
    story += section_12(CH)
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
