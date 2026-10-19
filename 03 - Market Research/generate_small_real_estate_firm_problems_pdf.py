"""Generate the designed PDF of the research report
"Small real estate firm problems UK US" (reports/Small real estate firm problems UK US.md).

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

Run:  python generate_small_real_estate_firm_problems_pdf.py
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
REPORT = Path(r"D:\Mustafa AI\reports\Small real estate firm problems UK US.md")
OUT_PDF = Path(r"D:\Mustafa AI\03 - Market Research\Small Real Estate Firm Problems UK-US (12 Oct 2026).pdf")
CHART_DIR = Path(r"C:\Users\MICROS~1\AppData\Local\Temp\claude\d--Mustafa-AI\ed3e6955-5f88-400b-a9f5-fd8bdbc9bceb\scratchpad\pdfcharts_re")
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
FOOTER_TEXT = "Small real estate firm problems UK and US, research 12 Oct 2026"

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
TAG_RE = re.compile(r"\[((?:snippet|snippets|vendor|user|users|secondary|3p|tribunal|reported claim|self-reported|sponsored|competitor|unverified|member-only|listing, not fetched)[^\[\]]*)\]")
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

plt.rcParams["text.parse_math"] = False   # "$223" is a price, not mathtext

FULL_W = 6.9
TITLE_WRAP = 92
SRC_WRAP = 124


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
    renderer = fig.canvas.get_renderer()
    last_right = -1.0
    for ax in sorted(fig.axes, key=lambda a: a.get_position().x0):
        t = getattr(ax, "_ptitle", None)
        if not t:
            continue
        ax.set_title("")
        bb = ax.get_tightbbox(renderer).transformed(fig.transFigure.inverted())
        pos = ax.get_position()
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


def _panel_title(ax, text):
    ax.set_title(text, fontsize=7.8, color=INK_SEC, loc="left", fontweight="bold")
    ax._ptitle = text


def _range_bars(ax, items, unit_fmt, xlim, wrap=34, point_color=BLUE_RAMP[3]):
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


# ---------------------------------------------------------------- charts
def chart_uk_sale_timeline():
    h = 3.1
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "A UK sale now takes 216 days from listing (62 to find a buyer plus 154 to complete), 36 days longer than 2019, and 23.7% of agreed sales fall through at about £3,550 each",
                               "Sources: Rightmove via Property Industry Eye, 31 Jul 2026 [%d]; TwentyEA via Property Reporter, 15 Dec 2025 [%d]; Property Industry Eye 17 Apr 2026 [%d], 10 Apr 2026 [%d] and 29 Sep 2026 [%d]. "
                               "2025: 1,257,053 sales agreed, 303,538 fell through (£1.065bn)." % (
                                   ref("https://propertyindustryeye.com/estate-agents-face-longest-wait-on-record-to-get-paid/"),
                                   ref("https://www.propertyreporter.co.uk/time-to-exchange-stretches-to-123-days-twentyea.html"),
                                   ref("https://propertyindustryeye.com/fall-through-rates-edge-down-across-most-regions-year-on-year/"),
                                   ref("https://propertyindustryeye.com/?p=162331"),
                                   ref("https://propertyindustryeye.com/property-fall-throughs-jump-as-cost-of-failed-sales-climbs/")),
                               ncols=3, width_ratios=[1.7, 0.75, 0.8])
    # (a) stacked listing-to-completion
    a1.barh([1], [62], color=BLUE_RAMP[1], height=0.5, edgecolor="white")
    a1.barh([1], [154], left=[62], color=BLUE_RAMP[3], height=0.5, edgecolor="white")
    a1.barh([0], [180], color=DEEMPH, height=0.5, edgecolor="white")
    a1.text(31, 1.42, "62 to find\na buyer", ha="center", va="bottom", fontsize=7, color=INK_SEC, linespacing=1.05)
    a1.text(62 + 77, 1.42, "154 sale agreed to completion", ha="center", va="bottom", fontsize=7, color=INK_SEC)
    a1.text(216 + 4, 1, "216 days", va="center", fontsize=7.2, color=INK2)
    a1.text(180 + 4, 0, "180 days (36 fewer)", va="center", fontsize=7.2, color=INK2)
    a1.set_yticks([1, 0])
    a1.set_yticklabels(["Jul 2026", "2019"], fontsize=7.2, color=INK2)
    a1.set_xlim(0, 285)
    a1.set_ylim(-0.6, 2.2)
    a1.set_xticks([])
    a1.spines["bottom"].set_visible(False)
    a1.spines["left"].set_color(DEEMPH)
    a1.tick_params(axis="y", length=0)
    a1.set_xlabel("Days, Great Britain (London 244; flats 169; houses about 149)", fontsize=7.2, color=INK_SEC)
    _panel_title(a1, "Listing to completion")
    # (b) sale agreed to exchange
    _cols(a2, ["2019", "2024", "2025"], [91, 121, 123], [BLUE_RAMP[0], BLUE_RAMP[2], BLUE_RAMP[3]], fmt="{:.0f}")
    _panel_title(a2, "Sale agreed to\nexchange (days)")
    # (c) fall-through
    _cols(a3, ["Q1 2025", "Q1 2026"], [24.0, 23.7], [BLUE_RAMP[1], WARM], fmt="{:.1f}%", ylim=30)
    a3.set_xlabel("£3,550 per fall-through\n(£3,584 in Q2 2026)", fontsize=7, color=INK_SEC)
    _panel_title(a3, "Fall-through rate")
    return _save(fig, "uk_sale_timeline", FULL_W, h)


def chart_us_contracts():
    h = 2.6
    fig, (a1, a2) = _frame(FULL_W, h,
                           "US contracts: 14% are delayed and 5% to 7% terminated; the median close is 30 days while lenders average 43",
                           "Sources: NAR Realtors Confidence Index, Dec 2025 [%d] and Aug 2026 page [%d]; ICE via GoBankingRates, 5 Aug 2025 [%d] (secondary). "
                           "Appraisal issues caused 6%% of delays; 39 days on market." % (
                               ref("https://cms.nar.realtor/sites/default/files/2026-01/2025-12-realtors-confidence-index-01-21-2026.pdf"),
                               ref("https://www.nar.realtor/research-and-statistics/research-reports/realtors-confidence-index"),
                               ref("https://www.gobankingrates.com/home-loans/home-loans-advice/how-long-does-it-take-to-close-on-a-house/")),
                           ncols=2, width_ratios=[1.25, 1])
    _hbar(a1, ["Contracts delayed (Dec 2025 and Aug 2026)", "Terminated, Aug 2026", "Terminated, Dec 2025", "Delayed by appraisal issues (Dec 2025)"],
          [14, 7, 5, 6], colors=[WARM, WARM, BLUE, BLUE], xlim=18, wrap=30, xlabel="Share of contracts")
    _panel_title(a1, "Contract outcomes (NAR RCI)")
    _cols(a2, ["Median close\n(NAR RCI)", "Lender average\n(ICE, Feb 2025)", "VA loans\n(upper)"], [30, 43, 50],
          [BLUE_RAMP[2], BLUE_RAMP[3], DEEMPH], fmt="{:.0f} days", ann=["30 days", "43 days", "40-50 days"])
    _panel_title(a2, "Days to close")
    return _save(fig, "us_contracts", FULL_W, h)


def chart_lead_economics():
    h = 2.8
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "Lead economics: a Zillow lead costs about $223 in major metros, a closing from paid leads $7,433 to $22,300, and half of brokerage enquiries were never answered",
                               "Sources: Clever, 14 Sep 2026 [%d] (secondary; close rates 1-3%%, break-even 3.19%%, Zillow Preferred requires a predicted 4%%); WAV Group 2013 [%d] (384 brokerages); Prospeo [%d] (vendor, snippet)." % (
                                   ref("https://listwithclever.com/real-estate-blog/how-much-are-zillow-leads/"),
                                   ref("https://www.wavgroup.com/wp-content/uploads/2014/01/AgentResponsivenessStudy2013Final.pdf"),
                                   ref("https://prospeo.io/s/speed-to-lead")),
                               ncols=3, width_ratios=[0.85, 0.85, 1.5])
    _cols(a1, ["Major\nmetros", "Elsewhere"], [223, 139], [BLUE_RAMP[3], BLUE_RAMP[1]], ann=["$223", "$139"])
    _panel_title(a1, "Zillow cost per lead")
    _cols(a2, ["3% close", "1% close"], [7433, 22300], [BLUE_RAMP[2], WARM], ann=["$7,433", "$22,300"])
    _panel_title(a2, "Cost per closing\nfrom paid leads")
    _hbar(a3, ["Enquiries never answered (2013)", "Consumers who hire the first to answer (2013)"], [48, 68],
          colors=[WARM, BLUE], xlim=80, wrap=24, xlabel="Share of enquiries or consumers")
    _panel_title(a3, "Response to enquiries (2026 vendor average: 15 h)")
    return _save(fig, "lead_economics", FULL_W, h)


def chart_nar_income():
    h = 2.7
    fig, (a1, a2) = _frame(FULL_W, h,
                           "The median US Realtor closes 9 sides a year for $59,200 gross and $37,000 net; members in their first two years earn a median $8,000",
                           "Sources: NAR 2026 Member Profile (2025 data, 5,116 responses) via Florida Realtors PDF [%d]; BLS May 2025 [%d] [%d]. "
                           "86%% independent contractors; 35 hours a week; median expenses $9,520; 48%% say real estate is the household's main income." % (
                               ref("https://www.floridarealtors.org/sites/default/files/basic-page/attachments/2026-08/2026%20Florida%20Member%20Profile%20Oversample.pdf"),
                               ref("https://www.bls.gov/ooh/sales/real-estate-brokers-and-sales-agents.htm"),
                               ref("https://www.bls.gov/ooh/management/property-real-estate-and-community-association-managers.htm")),
                           ncols=2, width_ratios=[1.3, 1])
    items = ["Median gross income (NAR)", "Median net income (NAR)", "First two years in the business, median (15% of members)",
             "Median business expenses (NAR)", "Sales agents median pay (BLS)", "Brokers median pay (BLS)", "Property managers median pay (BLS)"]
    vals = [59200, 37000, 8000, 9520, 52830, 73220, 69990]
    _hbar(a1, items, vals, colors=[BLUE, BLUE, WARM, DEEMPH, BLUE_RAMP[1], BLUE_RAMP[1], BLUE_RAMP[1]], xlim=80000, wrap=34,
          labels_override=["$%s" % format(v, ",") for v in vals], xlabel="USD per year")
    _panel_title(a1, "Income, 2025")
    _cols(a2, ["Sides a year\n(median)", "Hours a week\n(median)"], [9, 35], [BLUE_RAMP[3], BLUE_RAMP[1]], ann=["9", "35"], ylim=40)
    _panel_title(a2, "Volume")
    return _save(fig, "nar_income", FULL_W, h)


def chart_uk_lettings():
    h = 3.3
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "UK lettings: the average agency runs 340 properties with 14 staff; since 1 May 2026, 73% report more admin, 61% re-key data between systems, and complaints rose 47% and 65%",
                               "Sources: Goodlord SOLI 2025 [%d] (vendor survey, 350+ agents); Propoly via Property Industry Eye, 3 Sep 2026 [%d] (vendor survey); Property Reporter, 4 Sep 2026 [%d]; "
                               "Property Industry Eye, 12 Jun 2026 [%d]; Propertymark, 13 Mar 2026 [%d]; The Intermediary, 20 May 2025 [%d]; LandlordZONE 18 Sep 2026 [%d]." % (
                                   ref("https://www.goodlord.com/state-of-the-lettings-industry-report-2025"),
                                   ref("https://propertyindustryeye.com/renters-rights-act-piles-more-work-on-letting-agents/"),
                                   ref("https://www.propertyreporter.co.uk/renters-rights-act-drives-compliance-surge-as-landlord-sentiment-turns-negative.html"),
                                   ref("https://propertyindustryeye.com/complaints-against-agents-surge-by-almost-50/"),
                                   ref("https://www.propertymark.co.uk/resource/ombudsman-s-casework-highlights-practical-lessons-for-property-professionals.html"),
                                   ref("https://theintermediary.co.uk/?p=68135"),
                                   ref("https://www.landlordzone.co.uk/news/two-thirds-of-letting-agents-have-no-formal-qualifications")),
                               ncols=3, width_ratios=[1, 1.1, 1.05])
    _hbar(a1, ["Agencies with five or fewer staff", "Revenue from tenancy renewals before fixed terms ended", "Letting agents with no formal qualification",
               "Landlords using an agent mainly to stay compliant", "Agencies with more than 100 staff"],
          [54, 27, 65, 34, 4], xlim=75, wrap=26, xlabel="Share (340 properties, 14 staff on average)")
    _panel_title(a1, "Agency profile")
    _hbar(a2, ["Report more administration", "Run 'several disconnected systems'", "Staff re-enter data between systems", "Spend more time on compliance and admin (second survey)",
               "Rely on 'emails, spreadsheets and separate processes'"],
          [73, 66.7, 61, 62.5, 17], colors=[WARM, BLUE, WARM, BLUE, BLUE], xlim=85, wrap=28,
          labels_override=["73%", "two-thirds", "61%", "62.5%", "17%"], xlabel="Share of letting professionals, Sep 2026")
    _panel_title(a2, "Four months after 1 May 2026")
    _hbar(a3, ["Property Redress enquiries, 2025 vs 2024 (2,863 to 4,220)", "TPO lettings disputes, 2025 vs 2024", "TPO contacts, 2024 (record 73,035)"],
          [47.4, 65, 27], colors=[WARM, WARM, BLUE], xlim=92, wrap=22, fmt="+{:.0f}%", xlabel="Change")
    _panel_title(a3, "Complaints, year on year")
    return _save(fig, "uk_lettings", FULL_W, h)


def chart_fraud():
    h = 3.5
    fig, (a1, a2, a3, a4) = _frame(FULL_W, h,
                                   "Fraud: FBI real estate losses rose to $275.1m in 2025, seller-impersonation attempts hit 59% of title firms, 6.4% of US rental applications were fraudulent, and UK tenancy fraud rose 40% at £9,601 per case",
                                   "Sources: FBI IC3 2025 [%d] and 2024 [%d] annual reports; ALTA 2024 [%d] (783 firms) and 2026 [%d] (245 firms) studies; Snappt via Multifamily Executive [%d] (vendor data, about 5m documents); "
                                   "Goodlord via Property Reporter, 7 Aug 2026 [%d] (vendor data, 1m+ references)." % (
                                       ref("https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf"), ref("https://www.ic3.gov/AnnualReport/Reports/2024_IC3Report.pdf"),
                                       ref("https://alta.org/news-and-publications/news/20240730-Seller-Impersonation-Fraud-Attempts-Increase-Study-Shows"),
                                       ref("https://alta.org/file/Seller-Impersonation-Fraud-Study-Report.pdf"),
                                       ref("https://www.multifamilyexecutive.com/technology/snappt-report-6-4-of-rental-applications-were-fraudulent-in-2024_o"),
                                       ref("https://www.propertyreporter.co.uk/rental-fraud-up-40-as-ai-generated-fake-identities-target-letting-agents-and-landlords.html")),
                                   ncols=4, width_ratios=[1.75, 0.6, 0.6, 1.25])
    _cols(a1, ["2022\n11,727", "2023\n9,521", "2024\n9,359", "2025\n12,368"], [396.9, 145.2, 173.6, 275.1], [DEEMPH, BLUE_RAMP[1], BLUE_RAMP[2], WARM],
          ann=["$396.9m", "$145.2m", "$173.6m", "$275.1m"], ylim=430)
    a1.set_xlabel("Year; complaints under the year", fontsize=7, color=INK_SEC)
    _panel_title(a1, "FBI IC3 real estate losses (US$m)")
    _cols(a2, ["2024\nstudy", "2026\nstudy"], [28, 59], [BLUE_RAMP[1], WARM], ann=["28%", "59%"], ylim=70)
    _panel_title(a2, "Title firms\nwith attempt")
    _cols(a3, ["2023", "2024"], [7.9, 6.4], [BLUE_RAMP[1], BLUE_RAMP[3]], ann=["7.9%", "6.4%"], ylim=10)
    _panel_title(a3, "US rental apps\nfraudulent")
    _hbar(a4, ["Fake employment refs", "Referee fraud", "Identity manipulation", "Suspected fraud overall"], [226.6, 146.4, 140.4, 40],
          colors=[WARM, WARM, WARM, BLUE], xlim=310, wrap=16, fmt="+{:.1f}%", xlabel="Change in 2025")
    _panel_title(a4, "UK tenancy fraud\n(Goodlord; £9,601 a case)")
    return _save(fig, "fraud", FULL_W, h)


def chart_penalties():
    h = 4.2
    fig, (a1, a2) = _frame(FULL_W, h,
                           "HMRC fined 170 estate agencies £835,842 in six months, mostly for never registering (332 of 369 penalties across all sectors); the Renters' Rights Act and Right to Rent add penalties of £3,000 to £40,000 per breach",
                           "Sources: Comsure on HMRC list Apr-Sep 2025 [%d]; Estate Agent Today, Jun 2025 [%d] (snippet); Property Industry Eye, 12 Oct 2022 [%d]; GOV.UK Right to Rent penalties [%d]; "
                           "Anthony Collins, 17 Dec 2025 [%d] (indicative schedule; Act text not read, see section 11); Landlord Today, 29 May 2024 [%d]: agent fines for Right to Rent in Q1 2024 alone (£165,680) exceeded the whole of 2023." % (
                               ref("https://www.comsuregroup.com/news/aml-fails-in-six-months-hmrc-fined-estate-agents-836-000-most-never-even-registered/"),
                               ref("https://www.estateagenttoday.co.uk/breaking-news/2025/06/agents-make-up-majority-of-latest-aml-fines-hmrc/"),
                               ref("https://propertyindustryeye.com/hmrc-fines-estate-agents-more-than-500000-for-aml-breaches/"),
                               ref("https://www.gov.uk/penalties-illegal-renting"),
                               ref("https://www.anthonycollins.com/blog/102lxyr/renters-rights-act-guidance-and-fines-for-private-landlords/"),
                               ref("https://landlordtoday.co.uk/breaking-news/2024/5/huge-surge-in-right-to-rent-checks-as-non-compliance-fines-soar")),
                           ncols=2, width_ratios=[0.85, 1.3])
    _cols(a1, ["Oct 2022\nround", "Jun 2025\nlist", "Apr-Sep\n2025 list"], [0.5196, 1.09, 0.8358], [BLUE_RAMP[1], BLUE_RAMP[2], WARM],
          ann=["£519,645\n68 agents", "about £1.09m\n194 agents", "£835,842\n170 agents"], ylim=1.3)
    _panel_title(a1, "HMRC AML penalties on\nestate agencies (£m)")
    labels = ["Advert without a rent (RRA, indicative)", "Info sheet, fixed term or offer above the advert (RRA, indicative)",
              "Discrimination; Section 21 after 1 May 2026 (RRA, indicative)", "RRA minor breach, council maximum", "Right to Rent, first breach, per occupier",
              "Right to Rent, repeat breach, per occupier", "Re-letting in the 12-month no-let period (RRA, indicative)", "RRA serious or repeat breach, council maximum"]
    vals = [3000, 4000, 6000, 7000, 10000, 20000, 25000, 40000]
    _hbar(a2, labels, vals, colors=[BLUE, BLUE, BLUE, BLUE, WARM, WARM, BLUE, WARM], xlim=48000, wrap=36, height=0.58,
          labels_override=["£%s" % format(v, ",") for v in vals], xlabel="Penalty per breach, England")
    _panel_title(a2, "Penalty ceilings an English letting agent faces")
    return _save(fig, "penalties", FULL_W, h)


def chart_job_ads():
    h = 4.9
    fig, (a1, a2) = _frame(FULL_W, h,
                           "UK ads are about maintenance, viewings, deposits and certificates; US ads about lead follow-up, keeping the CRM clean and contract to close, with an AI tool named in 13 of 35",
                           "Sources: 18 UK ads read 11-12 Oct 2026 (Indeed UK templates, three Connells-group ads on Reed [%d], one Workable ad, a Propertymark snippet, six OnlineJobs.ph posts [%d]); "
                           "35 US ads (WizeHire [%d], Indeed US, nine OnlineJobs.ph posts, two ProsMarketplace posts, one South African staffing site, 16 Upwork posts [%d]). Counts of phrase families, not board-wide statistics." % (
                               ref("https://www.reed.co.uk/jobs/sales-progresser/57397576"),
                               ref("https://www.onlinejobs.ph/jobseekers/job/compliance-maintenance-coordinator-uk-property-part-time-with-a-view-to-full-time-1740481"),
                               ref("https://wizehire.com/real-estate-transaction-coordinator-job-description"),
                               ref("https://www.upwork.com/nx/search/jobs/?q=follow%20up%20boss")),
                           ncols=2, width_ratios=[1, 1])
    uk = [("maintenance / repairs / contractors / tradespeople", 10), ("viewings (arrange, conduct, book)", 8),
          ("deposit (registration, protection, release, deductions)", 8), ("gas safety / CP12 / EICR / EPC / safety certificates", 7),
          ("referencing / reference checks", 6), ("compliance / licensing / HMO", 6), ("arrears / rent collection", 5),
          ("check-in / check-out / inventory", 5), ("right to rent", 4), ("inspections", 4),
          ("exchange and completion / sales progression / solicitors", 4), ("CRM or system updated (Goodlord, Fixflo, 10ninety, NRLA)", 4),
          ("valuations / market appraisals", 3), ("landlord updates / landlord statements", 3), ("Rightmove / Zoopla / portals named", 2)]
    _hbar(a1, [u[0] for u in uk], [u[1] for u in uk], fmt="{:.0f}", xlim=12, wrap=36, height=0.6, xlabel="Ads with the phrase family (of 18)")
    _panel_title(a1, "UK: 18 ads")
    us = [("follow up / lead follow-up / nurture", 24), ("CRM (update, clean, organise, tags, stages, pipelines)", 22),
          ("contract to close / contract through closing", 13), ("ChatGPT / AI named inside the duty list", 13),
          ("skip tracing (investor and wholesaler ads)", 12), ("cold calling / outbound calls / dials per shift", 12),
          ("MLS entry, uploads, status changes", 10), ("maintenance requests / work orders / vendors / tickets", 10),
          ("drip campaigns / action plans / smart lists / automations", 10), ("social media / Canva / reels", 10),
          ("schedule showings / showings", 6), ("tenant screening / background checks", 3), ("evictions", 2)]
    _hbar(a2, [u[0] for u in us], [u[1] for u in us], fmt="{:.0f}", xlim=28, wrap=36, height=0.6,
          colors=[BLUE, BLUE, BLUE, WARM] + [BLUE] * 9, xlabel="Ads with the phrase family (of 35)")
    _panel_title(a2, "US: 35 ads")
    return _save(fig, "job_ads", FULL_W, h)


def chart_pay_tiers():
    h = 5.3
    fig, (a1, a2) = _frame(FULL_W, h,
                           "The same duties pay £22,657 to £43,000 onshore in the UK and $33,000 to $69,398 in the US, and $2 to $12 an hour or $450 to $1,500 a month when posted offshore",
                           "Sources: Reed Sep-Oct 2026 [%d] [%d] [%d]; Indeed UK [%d] [%d] (self-reported); WizeHire [%d] [%d]; Indeed US [%d]; Wise Pelican [%d] (secondary); "
                           "OnlineJobs.ph posts [%d] [%d] [%d] [%d]; ProsMarketplace [%d] [%d]; Upwork posts [%d]." % (
                               ref("https://www.reed.co.uk/jobs/lettings-negotiator-jobs"), ref("https://www.reed.co.uk/jobs/sales-progressor-jobs"),
                               ref("https://www.reed.co.uk/jobs/lettings-administrator-jobs"),
                               ref("https://uk.indeed.com/career/lettings-negotiator/salaries"), ref("https://uk.indeed.com/career/property-manager/salaries"),
                               ref("https://wizehire.com/real-estate-transaction-coordinator-job-description"), ref("https://wizehire.com/listing-coordinator-job-description"),
                               ref("https://www.indeed.com/hire/job-description/leasing-agent"), ref("https://wisepelican.com/real-estate-inside-sales/"),
                               ref("https://www.onlinejobs.ph/jobseekers/job/property-management-virtual-assistant-uk-hours-for-uk-based-real-estate-agency-1734802"),
                               ref("https://www.onlinejobs.ph/jobseekers/job/compliance-maintenance-coordinator-uk-property-part-time-with-a-view-to-full-time-1740481"),
                               ref("https://www.onlinejobs.ph/jobseekers/job/part-time-uk-property-tenancy-coordinator-1731573"),
                               ref("https://www.onlinejobs.ph/jobseekers/job/experienced-uk-property-manager-property-operations-coordinator-x2-1742926"),
                               ref("https://prosmarketplace.com/job/job-detail/transaction-coordinator-real-estate-3"),
                               ref("https://prosmarketplace.com/job/job-detail/seeking-real-estate-va-experienced-with-fub-and-crm-spanish-and-english-speaking"),
                               ref("https://www.upwork.com/nx/search/jobs/?q=follow%20up%20boss")),
                           ncols=2, width_ratios=[1.05, 1])
    items = [("UK lettings negotiator, Indeed average", 22.657, 22.657, "£"), ("UK lettings negotiator, modal basic (15 of 24 ads)", 25, 25, "£"),
             ("UK sales negotiator (Reed)", 25, 30, "£"), ("UK sales progressor (Reed)", 19, 43, "£"), ("UK lettings administrator (Reed)", 26, 34, "£"),
             ("UK lettings property manager (Reed)", 30, 35, "£"), ("UK property manager, Indeed average", 33.785, 33.785, "£"),
             ("UK Head of Lettings (Propertymark)", 70, 70, "£"),
             ("US listing coordinator (WizeHire)", 33, 33, "$"), ("US transaction coordinator (WizeHire)", 39, 39, "$"),
             ("US marketing coordinator (WizeHire)", 48, 48, "$"), ("US ISA base, plus 5-15% of GCI", 57.686, 69.398, "$"),
             ("US property manager (BLS median)", 69.99, 69.99, "$")]
    _range_bars(a1, items, lambda v: ("%dk" % v) if v == int(v) else ("%.1fk" % v), 90, wrap=34)
    a1.set_xlabel("Annual pay, thousands (GBP or USD as marked)", fontsize=7.2, color=INK_SEC)
    _panel_title(a1, "Onshore: UK and US job boards")
    items2 = [("'CRM Lead Follow-Up Specialist' (US post)", 2, 2, "$"), ("ISA (US post)", 4, 4, "$"), ("Keller Williams team VA (US post)", 5, 5, "$"),
              ("Tenancy coordinator for a UK landlord", 5, 5, "$"), ("MLS drafting (US post)", 5, 7.5, "$"), ("Cold caller, plus $150-$300 per deal", 3, 6, "$"),
              ("Leasing and collections specialist, Atlanta", 6, 6, "$"), ("CRM clean-up and upkeep (Upwork)", 7, 10, "$"),
              ("Property-management VA (Upwork, OnlineJobs.ph)", 5, 12, "$"), ("Transaction coordinator (Upwork range)", 3, 20, "$"),
              ("'Compliance & Maintenance Coordinator', UK", 4.5, 5, "£"), ("US onshore leasing agent, for scale", 19.45, 19.45, "$")]
    _range_bars(a2, items2, lambda v: ("%g" % v), 26, wrap=34)
    a2.set_xlabel("Hourly rate (USD or GBP)", fontsize=7.2, color=INK_SEC)
    _panel_title(a2, "Offshore posts by UK and US small firms\n(monthly posts: $450-$1,500)")
    return _save(fig, "pay_tiers", FULL_W, h)


def chart_platforms():
    h = 4.3
    fig, (a1, a2, a3) = _frame(FULL_W, h,
                               "Platforms: Trustpilot runs from AppFolio 2.0 to Alto 4.5, published prices from $62 to $1,000 a month, and Zapier exposes 36 operations on DoorLoop but none on AppFolio, Buildium or Reapit",
                               "Sources: Trustpilot pages for AppFolio [%d], Buildium [%d], Reapit [%d], Alto [%d], Arthur [%d], Goodlord [%d], Fixflo [%d], PayProp (4 reviews) [%d]; vendor price pages [%d] [%d] [%d] [%d] [%d] [%d]; "
                               "Zapier app pages [%d] [%d] [%d] [%d] [%d] [%d]. Quote-only vendors (AppFolio, BoldTrail, Lofty, Reapit, Alto, Goodlord, Rent Manager) are not plotted on price." % (
                                   ref("https://www.trustpilot.com/review/appfolio.com"), ref("https://www.trustpilot.com/review/buildium.com"), ref("https://uk.trustpilot.com/review/reapit.com"),
                                   ref("https://uk.trustpilot.com/review/altosoftware.co.uk"), ref("https://uk.trustpilot.com/review/arthuronline.co.uk"), ref("https://uk.trustpilot.com/review/www.goodlord.co"),
                                   ref("https://uk.trustpilot.com/review/www.fixflo.com"), ref("https://www.rfp.wiki/vendors/payprop"),
                                   ref("https://www.followupboss.com/pricing"), ref("https://www.buildium.com/pricing/"), ref("https://www.doorloop.com/pricing"), ref("https://www.arthuronline.co.uk/pricing/"),
                                   ref("https://www.payprop.com/uk/pricing"), ref("https://www.fixflo.com/pricing"),
                                   ref("https://zapier.com/apps/follow-up-boss/integrations"), ref("https://zapier.com/apps/doorloop/integrations"), ref("https://zapier.com/apps/lofty/integrations"),
                                   ref("https://zapier.com/apps/boomtown/integrations"), ref("https://zapier.com/apps/kvcore/integrations"), ref("https://zapier.com/apps/fixflo/integrations")),
                               ncols=3, width_ratios=[0.95, 1.15, 1.0])
    tp = [("Alto (206 reviews)", 4.5), ("Buildium (819)", 4.4), ("Goodlord (45,020)", 4.4), ("Fixflo (239)", 4.0), ("Arthur (538)", 3.5),
          ("Reapit (119)", 3.2), ("PayProp (4)", 2.5), ("AppFolio (786)", 2.0)]
    _hbar(a1, [t[0] for t in tp], [t[1] for t in tp], colors=[BLUE] * 6 + [WARM, WARM], fmt="{:.1f}", xlim=5, wrap=20, xlabel="Score of 5, Oct 2026")
    _panel_title(a1, "Trustpilot score")
    price = [("Follow Up Boss Grow, per user", 69, 69, "$"), ("Buildium Essential to Premium", 62, 400, "$"), ("DoorLoop Starter to Premium", 99, 239, "$"),
             ("BoomTown single plan (Capterra)", 1000, 1000, "$"), ("Arthur Standard to Enterprise", 82.5, 126, "£"), ("PayProp licence, from", 79, 79, "£"),
             ("Fixflo software fee, plus quote", 75, 75, "£"), ("Street minimum (£6 per property, £2.20 per tenancy)", 500, 500, "£")]
    _range_bars(a2, price, lambda v: ("%g" % v), 1300, wrap=24)
    a2.set_xlabel("Monthly price (USD or GBP as marked)", fontsize=7.2, color=INK_SEC)
    _panel_title(a2, "Published price, Oct 2026")
    zap = [("DoorLoop (Premium only)", 36), ("Follow Up Boss", 22), ("Lofty", 12), ("BoomTown (9 read triggers)", 10), ("kvCORE / BoldTrail", 4), ("Fixflo", 4),
           ("Sierra Interactive", 2), ("Real Geeks", 2), ("dotloop", 2), ("AppFolio, Buildium, Rent Manager, Reapit", 0)]
    _hbar(a3, [z[0] for z in zap], [z[1] for z in zap], colors=[BLUE] * 9 + [WARM], fmt="{:.0f}", xlim=40, wrap=20, xlabel="Zapier operations")
    _panel_title(a3, "Zapier surface")
    return _save(fig, "platforms", FULL_W, h)


GAP_POS = [
    (1, "Renters' Rights Act compliance-date and record validation", 4.0, 3.0, True),
    (2, "Owner-statement and trust-ledger validation against the bank", 2.9, 2.0, True),
    (3, "AML source-of-funds reasoning and written risk assessment", 2.95, 3.12, True),
    (4, "Sales-progression log and fall-through cause tracking", 3.85, 2.0, True),
    (5, "Maintenance ticket ownership, report to confirmed completion", 4.15, 2.22, True),
    (6, "Material Information assembly and listing checks", 3.55, 3.05, True),
    (7, "Tenant application fraud triage and referencing exceptions", 3.2, 2.17, True),
    (8, "CRM configuration validation and dormant-lead exception reports", 3.25, 2.8, True),
    (9, "Contract-to-close deadline and document-completeness tracking", 3.5, 1.95, True),
    (10, "Deposit deduction evidence and dispute packs", 2.55, 1.95, True),
    (11, "Wholesaler list hygiene, record matching, consent and DNC logging", 2.35, 2.2, True),
    (12, "AI-written content compliance checks", 2.0, 2.65, True),
    (13, "CRM migration and data-cleanup validation", 2.5, 3.0, True),
]
CROWDED_POS = [("a", "Listing descriptions and social posts", 3.0, 0.5), ("b", "AI receptionist and phone answering", 3.3, 1.0),
               ("c", "CRM set-up gigs (Follow Up Boss, kvCORE, Lofty)", 3.27, 0.5), ("d", "Commodity tenant screening reports", 3.55, 0.5),
               ("e", "Wire-fraud and seller-identity tools for title companies", 4.0, 1.0), ("f", "Promo video, photo editing, floorplans", 2.0, 0.5),
               ("g", "Skip-trace data vending", 3.0, 1.0), ("h", "AppFolio bookkeeping as a human service", 3.62, 1.0),
               ("i", "Cold-calling VAs and ISAs", 3.83, 0.5)]


def chart_gap_matrix():
    w, h = FULL_W, 5.0
    fig, (ax, key) = _frame(w, h,
                            "Gap map: the thirteen gaps placed by problem signal against vendor weakness, using the report's own ranking words; nine crowded areas in grey",
                            "Positions follow the wording of the ranking table in section 9 (very high / high / medium-high / medium signal; weak / thin / medium / strong / very strong coverage), not measured scores. "
                            "Warm = coverage weak or thin; blue = medium coverage; grey letters = the nine crowded areas the report says are not gaps.",
                            ncols=2, width_ratios=[1.3, 1])
    ax.set_xlim(1.5, 4.5)
    ax.set_ylim(0.1, 3.5)
    ax.axhline(2.4, color=GRID, linewidth=0.8, zorder=0)
    ax.axvline(2.75, color=GRID, linewidth=0.8, zorder=0)
    ax.text(4.45, 3.44, "strong signal, weak vendor coverage", ha="right", va="top", fontsize=7, color=INK_SEC)
    ax.text(1.55, 0.16, "weaker signal, crowded", ha="left", va="bottom", fontsize=7, color=INK_SEC)
    for r, name, x, y, known in GAP_POS:
        ax.scatter([x], [y], s=210, color=WARM if y >= 2.5 else BLUE, zorder=3, edgecolor="white", linewidth=1.4)
        ax.text(x, y, str(r), ha="center", va="center", fontsize=7.2, color="white", fontweight="bold", zorder=4)
    for letter, name, x, y in CROWDED_POS:
        ax.scatter([x], [y], s=190, color=DEEMPH, zorder=3, edgecolor="white", linewidth=1.4)
        ax.text(x, y, letter, ha="center", va="center", fontsize=7.2, color=INK2, fontweight="bold", zorder=4)
    ax.set_xticks([2.0, 2.5, 3.0, 4.0])
    ax.set_xticklabels(["medium", "medium-\nhigh", "high", "very\nhigh"], fontsize=7)
    ax.set_yticks([0.5, 1.0, 2.0, 2.7, 3.0])
    ax.set_yticklabels(["very strong\n(crowded)", "strong", "medium", "thin", "weak"], fontsize=7)
    ax.set_xlabel("Problem signal (findings, fraud data, complaints, demand)", fontsize=7.2, color=INK_SEC)
    ax.set_ylabel("Vendor coverage of the exact sub-problem", fontsize=7.2, color=INK_SEC)
    ax.tick_params(length=0)
    key.axis("off")
    key.set_xlim(0, 1)
    key.set_ylim(0, 1)
    key.text(0, 1.0, "Key (rank. gap)", fontsize=7.6, fontweight="bold", color=INK, va="top")
    yy = 0.945
    step = 0.04
    for r, name, x, y, known in GAP_POS:
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


def chart_salary_employed():
    h = 4.2
    fig, ax = _frame(FULL_W, h,
                     "Employed pay: US PropTech software-engineer medians run from $100,000 at Yardi to $290,000 for a Zillow ML engineer; UK AI Engineer ads pay a median £87,500 while PropTech-tagged roles pay £65,000",
                     "Sources: Levels.fyi, 11 Oct 2026 [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] [%d] (self-reported); IT Jobs Watch, six months to 11 Oct 2026 [%d] [%d] [%d] [%d] [%d]; "
                     "Rightmove and Zoopla on Levels.fyi [%d] [%d]; DOL LCA data via Ellis [%d]." % (
                         ref("https://www.levels.fyi/companies/zillow/salaries/software-engineer/title/machine-learning-engineer"),
                         ref("https://www.levels.fyi/companies/opendoor/salaries/software-engineer"), ref("https://www.levels.fyi/companies/redfin/salaries/software-engineer"),
                         ref("https://www.levels.fyi/companies/realpage/salaries/software-engineer"), ref("https://www.levels.fyi/companies/appfolio/salaries/software-engineer"),
                         ref("https://www.levels.fyi/companies/realtor.com/salaries/software-engineer"), ref("https://www.levels.fyi/companies/entrata/salaries/software-engineer"),
                         ref("https://www.levels.fyi/companies/compass/salaries/software-engineer"), ref("https://www.levels.fyi/companies/costar-group/salaries/software-engineer"),
                         ref("https://www.levels.fyi/companies/yardi/salaries/software-engineer"),
                         ref("https://www.itjobswatch.co.uk/jobs/uk/artificial%20intelligence%20engineer.do"), ref("https://www.itjobswatch.co.uk/jobs/uk/retrieval-augmented%20generation.do"),
                         ref("https://www.itjobswatch.co.uk/jobs/uk/data%20engineer.do"), ref("https://www.itjobswatch.co.uk/jobs/uk/machine%20learning%20engineer.do"),
                         ref("https://www.itjobswatch.co.uk/jobs/uk/proptech.do"),
                         ref("https://www.levels.fyi/companies/rightmove/salaries/software-engineer"), ref("https://www.levels.fyi/companies/zoopla/salaries/software-engineer"),
                         ref("https://www.ellis.com/visa-sponsors/zillow-inc")))
    items = [("Zillow machine learning engineer, median total (10 submissions)", 290, 290, "$"), ("Opendoor software engineer, median", 243, 243, "$"),
             ("Redfin software engineer, median", 218, 218, "$"), ("RealPage software engineer, median", 212, 212, "$"),
             ("AppFolio software engineer, median", 183, 183, "$"), ("Realtor.com software engineer, median", 170, 170, "$"),
             ("Entrata software engineer, median", 152, 152, "$"), ("Compass software engineer, median", 137, 137, "$"),
             ("CoStar software engineer, median", 126, 126, "$"), ("Yardi software engineer, median", 100, 100, "$"),
             ("Visa-sponsored offered wages, medians (Redfin to CoStar)", 135, 148.05, "$"),
             ("UK AI Engineer ads, median (10th-90th pct £53,250-£113,500)", 87.5, 87.5, "£"), ("UK RAG-tagged ads, median (316 salaries)", 85, 85, "£"),
             ("Zoopla software engineer, median (11 submissions)", 83.1, 83.1, "£"), ("Rightmove software engineer, median (32 submissions)", 70.6, 70.6, "£"),
             ("UK Data Engineer ads, median (flat three years)", 70, 70, "£"), ("UK PropTech-tagged ads, median (London £85,000)", 65, 65, "£"),
             ("UK Machine Learning Engineer ads, median (down 23.5%)", 65, 65, "£")]
    _range_bars(ax, items, lambda v: ("%dk" % v) if v == int(v) else ("%.1fk" % v), 330, wrap=56)
    ax.set_xlabel("Annual pay, thousands (USD or GBP as marked)", fontsize=7.2, color=INK_SEC)
    return _save(fig, "salary_employed", FULL_W, h)


def chart_freelance_rates():
    h = 3.9
    fig, ax = _frame(FULL_W, h,
                     "Freelance rates: Philippine VAs at $5 to $8 an hour and Fiverr set-ups from $10 set the floor; Python and automation posts pay $25 to $75, AppFolio bookkeeping firms $34 to $45, vetted API developers $60 to $100-plus",
                     "Sources: Upwork rate guide [%d] (snippet); Upwork posts [%d] [%d] (snippets, 50-plus proposals each); Upwork searches [%d] [%d] [%d]; Upwork AppFolio freelancers [%d] [%d] (snippets); "
                     "OJO Bookkeeping [%d]; HireTalent.ph [%d] [%d]; Arc.dev [%d]; Fiverr [%d] (snippet)." % (
                         ref("https://www.upwork.com/resources/upwork-hourly-rates"),
                         ref("https://www.upwork.com/freelance-jobs/apply/agent-automation-expert-for-real-estate-investment-company_~022105698179776894846/"),
                         ref("https://www.upwork.com/jobs/~022067181627045320907"),
                         ref("https://www.upwork.com/nx/search/jobs/?q=real%20estate%20ai%20chatbot"), ref("https://www.upwork.com/nx/search/jobs/?q=real%20estate%20listing%20description"),
                         ref("https://www.upwork.com/nx/search/jobs/?q=real%20estate%20transaction%20coordinator"),
                         ref("https://www.upwork.com/hire/appfolio-freelancers/california-us/"), ref("https://www.upwork.com/hire/appfolio-freelancers/"),
                         ref("https://ojobookkeeping.com/appfolio-bookkeeping/"), ref("https://hiretalent.ph/industry/real-estate"), ref("https://hiretalent.ph/tool/appfolio"),
                         ref("https://arc.dev/hire-developers/reso-web-api"), ref("https://www.fiverr.com/gigs/follow-up-boss")))
    items = [("Philippine real-estate VA profiles, 1,437 (median $6)", 5, 8, "$"), ("Offshore AppFolio freelancers, 'historical cleanup'", 10, 10, "$"),
             ("Upwork entry-level admin (rate guide)", 10, 25, "$"), ("Transaction coordination, Expert tier", 15, 20, "$"),
             ("'Agent automation expert', real estate investment company (post)", 5, 50, "$"), ("'AI agent' design and automation posts", 20, 60, "$"),
             ("'Senior python engineer ... real estate automations' (post)", 25, 75, "$"), ("Upwork intermediate (rate guide)", 25, 75, "$"),
             ("US AppFolio consultants on Upwork", 30, 75, "$"), ("AppFolio bookkeeping firms, ongoing to cleanup ($300 a month minimum)", 34, 45, "$"),
             ("Local SEO and 'GEO/AEO' for a brokerage", 35, 60, "$"), ("Vetted API developers on Arc", 60, 100, "$"),
             ("Upwork specialised development, AI and consulting (rate guide)", 75, 150, "$")]
    _range_bars(ax, items, lambda v: ("%d" % v), 180, wrap=60)
    ax.set_xlabel("Hourly rate, USD; gigs: CRM set-up $10-$35, top Follow Up Boss gig $399, builds $100-$2,300 fixed, voice agent $500", fontsize=7.2, color=INK_SEC)
    return _save(fig, "freelance_rates", FULL_W, h)


def chart_itjobswatch():
    h = 3.0
    fig, ax = _frame(FULL_W, h,
                     "UK permanent ads, six months to 11 Oct 2026: AI Engineer 808 (91 a year earlier), RAG 505 (84), Data Engineer 2,087 (637), PropTech 137 (17, mostly sales titles)",
                     "Source: IT Jobs Watch [%d] [%d] [%d] [%d] [%d] [%d] [%d]. PropTech's top titles are Sales Manager (36) and Account Executive (34), not engineers; no tracked page exists for 'Reapit', 'estate agency' or 'property'." % (
                         ref("https://www.itjobswatch.co.uk/jobs/uk/proptech.do"), ref("https://www.itjobswatch.co.uk/jobs/uk/artificial%20intelligence%20engineer.do"),
                         ref("https://www.itjobswatch.co.uk/jobs/uk/retrieval-augmented%20generation.do"), ref("https://www.itjobswatch.co.uk/jobs/uk/data%20engineer.do"),
                         ref("https://www.itjobswatch.co.uk/jobs/uk/machine%20learning%20engineer.do"), ref("https://www.itjobswatch.co.uk/jobs/uk/zapier.do"),
                         ref("https://www.itjobswatch.co.uk/jobs/uk/n8n.do")))
    rows = [("Data Engineer", 637, 2087), ("Artificial Intelligence Engineer", 91, 808), ("Retrieval-augmented generation", 84, 505),
            ("HubSpot", None, 488), ("PropTech", 17, 137), ("Machine Learning Engineer", None, 92), ("Zapier", None, 50), ("n8n", 9, 43)]
    n = len(rows)
    y = list(range(n))[::-1]
    for yi, (lab, prev, now) in zip(y, rows):
        if prev is not None:
            ax.barh(yi + 0.17, prev, height=0.3, color=DEEMPH, edgecolor="white")
            ax.text(prev + 20, yi + 0.17, format(prev, ","), va="center", fontsize=7, color=INK_SEC)
        ax.barh(yi - 0.17, now, height=0.3, color=BLUE, edgecolor="white")
        ax.text(now + 20, yi - 0.17, format(now, ","), va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontsize=7.2, color=INK2)
    ax.tick_params(axis="y", length=0)
    ax.set_xlim(0, 2500)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_color(DEEMPH)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("Permanent UK ads citing the term in six months", fontsize=7.2, color=INK_SEC)
    ax.barh([-5], [1], color=DEEMPH, label="six months to Oct 2025")
    ax.barh([-5], [1], color=BLUE, label="six months to Oct 2026")
    ax.legend(loc="lower right", frameon=False, fontsize=7.2)
    return _save(fig, "itjobswatch", FULL_W, h)


def chart_lettings_flow():
    w, h = FULL_W, 5.0
    fig = plt.figure(figsize=(w, h))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    title = _wrap("UK lettings, application to move-in: the data pulls take minutes, the references take days, and three steps stay with a named person by law", TITLE_WRAP)
    src = _wrap("Sources: Home Office landlord's guide, 1 Oct 2026 [%d]; LetSafe UK [%d]; NRLA referencing [%d]; Canopy [%d] (vendor); GOV.UK landlord guidance [%d]; GOV.UK deposits [%d]; OFSI guidance [%d]. "
                "US parallel: the same-day screening report ($17-$49) is automated; the landlord's permissible-purpose certification and the FCRA adverse-action notice are human acts [%d]." % (
                    ref("https://www.gov.uk/government/publications/landlords-guide-to-right-to-rent-checks/landlords-guide-to-right-to-rent-checks-1-october-2026-accessible"),
                    ref("https://letsafeuk.co.uk/tenant-reference-check-uk"), ref("https://www.nrla.org.uk/services/tenant-referencing"), ref("https://www.canopy.rent/agents"),
                    ref("https://www.gov.uk/guidance/renting-out-your-property-guidance-for-landlords-and-letting-agents"), ref("https://www.gov.uk/deposit-protection-schemes-and-landlords"),
                    ref("https://www.gov.uk/government/publications/financial-sanctions-guidance-for-letting-agents/financial-sanctions-guidance-for-letting-agents"),
                    ref("https://www.ftc.gov/business-guidance/resources/using-consumer-reports-what-landlords-need-know")), SRC_WRAP)
    fig.text(0.005, 0.99, title, ha="left", va="top", fontsize=8.6, fontweight="bold", color=INK, linespacing=1.25)
    fig.text(0.005, 0.01, src, ha="left", va="bottom", fontsize=7, color=MUTED, linespacing=1.2)
    steps = [
        ("1  Enquiry and viewing", "Advert states a rent; no bidding; no refusal for children or benefits. Viewings booked by phone at most swept sites.", False),
        ("2  Privacy notice and consent", "Consent before any credit check: 'running a credit check without consent is a data protection breach'. Applicant-controlled gate.", False),
        ("3  Right to Rent on every adult", "HUMAN ACT. Manual check with originals and the holder present (in person or live video); or GOV.UK share code (R..., 90 days); registered provider for British and Irish passports only. Landlord or agent 'remains responsible'; £10,000-£20,000 per occupier.", True),
        ("4  Referencing data pulls", "Credit, ID document, open-banking or HMRC income, PEP and sanctions: £5 (Canopy) to £23-£40 (NRLA/Goodlord); 30% instant, most within 24-72 h.", False),
        ("5  Manual residue", "Employer and previous-landlord references ('manual verification'); document re-requests; guarantor referenced and agreement in writing before the tenancy.", False),
        ("6  Decision and sanctions report", "HUMAN ACT. 'Recommended / referred / declined' decided by the agent or landlord; report to OFSI on known or suspected sanctioned persons (from 14 May 2025); no blanket 'no DSS'.", True),
        ("7  Holding deposit and terms", "No more than one month's rent before signing, nothing until all have signed; written terms with no end date; deposit protected within 30 days with prescribed information.", False),
        ("8  Move-in evidence", "HUMAN ACT. Gas record before move-in; inventory with photos; information sheet to every named tenant; follow-up Right to Rent check before a time-limited status expires.", True),
    ]
    bw, bh = 22.6, 33
    xs = [1.5, 26.3, 51.1, 75.9]
    rows_y = [52, 13]
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
        ax.text(x + 1.3, y + bh - 1.6 - 3.0 * nl - 1.0, _wrap(sub, 27), ha="left", va="top", fontsize=7,
                color=INK2, zorder=3, linespacing=1.08)
    for i in range(3):
        ax.add_patch(FancyArrowPatch((xs[i] + bw + 0.3, rows_y[0] + bh / 2), (xs[i + 1] - 0.3, rows_y[0] + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    ax.add_patch(FancyArrowPatch((xs[3] + bw / 2, rows_y[0] - 0.3), (xs[3] + bw / 2, rows_y[1] + bh + 0.3),
                                 arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    for i in range(3, 0, -1):
        ax.add_patch(FancyArrowPatch((xs[i] - 0.3, rows_y[1] + bh / 2), (xs[i - 1] + bw + 0.3, rows_y[1] + bh / 2),
                                     arrowstyle="-|>", mutation_scale=9, color=INK_SEC, linewidth=0.9, zorder=1))
    ax.text(1.5, 49.3, "Warm box = a step the law or the applicant's consent keeps with a named person; a tool can produce the audit trail, not the decision.",
            fontsize=7, color=WARM_TEXT, va="center")
    path = CHART_DIR / "lettings_flow.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return (path, w, h)


def build_charts():
    out = {}
    for fn in (chart_uk_sale_timeline, chart_us_contracts, chart_lead_economics, chart_nar_income, chart_uk_lettings, chart_fraud,
               chart_penalties, chart_job_ads, chart_pay_tiers, chart_platforms, chart_gap_matrix, chart_salary_employed,
               chart_freelance_rates, chart_itjobswatch, chart_lettings_flow):
        path, w, h = fn()
        out[path.stem] = (path, w, h)
    return out


# ==========================================================================
# Content, part A: cover, contents, "Read this first", sections 1 to 4.
# ==========================================================================
U.update({
    "pie_216": "https://propertyindustryeye.com/estate-agents-face-longest-wait-on-record-to-get-paid/",
    "pie_ft": "https://propertyindustryeye.com/fall-through-rates-edge-down-across-most-regions-year-on-year/",
    "pie_cost": "https://propertyindustryeye.com/?p=162331",
    "pie_cost2": "https://propertyindustryeye.com/property-fall-throughs-jump-as-cost-of-failed-sales-climbs/",
    "pr_123": "https://www.propertyreporter.co.uk/time-to-exchange-stretches-to-123-days-twentyea.html",
    "pie_6m": "https://propertyindustryeye.com/the-property-markets-biggest-challenge-getting-sales-to-completion/",
    "pie_blame": "https://propertyindustryeye.com/estate-agents-escape-blame-as-almost-three-quarters-of-home-movers-face-delays/",
    "ms_2025": "https://www.mortgagesolutions.co.uk/mortgage-news/2026/01/19/exchanges-in-2025-nearly-hit-one-million/",
    "hoa_ft": "https://hoa.org.uk/advice/guides-for-homeowners/i-am-buying/why-do-house-sales-fall-through/",
    "pie_fee": "https://propertyindustryeye.com/higher-house-prices-drive-up-estate-agent-fees/",
    "hoa_fee": "https://hoa.org.uk/advice/guides-for-homeowners/i-am-selling/how-do-i-lower-my-estate-agent-fees-use-online-agents/",
    "conv_pod": "https://conveyancingmatters.buzzsprout.com/1282232/episodes/15699837-do-sales-progressors-actually-progress-conveyancing-transactions",
    "pie_franchise": "https://propertyindustryeye.com/ex-estate-agent-launches-uks-first-sales-progression-franchise/",
    "goodlord_soli": "https://www.goodlord.com/state-of-the-lettings-industry-report-2025",
    "pm_dec25": "https://www.propertymark.co.uk/resource/housing-insight-report-december-2025.html",
    "goodlord_index": "https://www.goodlord.com/rental-index",
    "pie_rra_admin": "https://propertyindustryeye.com/renters-rights-act-piles-more-work-on-letting-agents/",
    "pr_compliance": "https://www.propertyreporter.co.uk/renters-rights-act-drives-compliance-surge-as-landlord-sentiment-turns-negative.html",
    "pie_complaints": "https://propertyindustryeye.com/complaints-against-agents-surge-by-almost-50/",
    "pm_tpo": "https://www.propertymark.co.uk/resource/ombudsman-s-casework-highlights-practical-lessons-for-property-professionals.html",
    "ti_tpo": "https://theintermediary.co.uk/?p=68135",
    "lz_maint": "https://www.landlordzone.co.uk/news/portfolio-landlords-delay-maintenance-as-workload-mounts",
    "indeed_ln": "https://uk.indeed.com/career/lettings-negotiator/salaries",
    "indeed_pm": "https://uk.indeed.com/career/property-manager/salaries",
    "lz_qual": "https://www.landlordzone.co.uk/news/two-thirds-of-letting-agents-have-no-formal-qualifications",
    "nar_profile": "https://www.floridarealtors.org/sites/default/files/basic-page/attachments/2026-08/2026%20Florida%20Member%20Profile%20Oversample.pdf",
    "nar_rci_dec": "https://cms.nar.realtor/sites/default/files/2026-01/2025-12-realtors-confidence-index-01-21-2026.pdf",
    "nar_rci": "https://www.nar.realtor/research-and-statistics/research-reports/realtors-confidence-index",
    "wav": "https://www.wavgroup.com/wp-content/uploads/2014/01/AgentResponsivenessStudy2013Final.pdf",
    "prospeo": "https://prospeo.io/s/speed-to-lead",
    "clever_z": "https://listwithclever.com/real-estate-blog/how-much-are-zillow-leads/",
    "tp_realtor": "https://www.trustpilot.com/review/realtor.com?stars=1",
    "bp_7250481": "https://www.biggerpockets.com/posts/7250481",
    "listedkit": "https://www.listedkit.com/resources/real-estate-transaction-management-cost",
    "bp_1303079": "https://www.biggerpockets.com/forums/52/topics/1303079-self-managing-your-rental-what-part-takes-the-most-time",
    "bp_1286268": "https://www.biggerpockets.com/forums/93/topics/1286268-skip-tracing-and-cold-calling-with-batchleads-expectations",
    "formsimp": "https://www.formsimplicity.com/blog/the-real-cost-of-manual-real-estate-transactions-time-errors-and-compliance-risk/",
    "stealth": "https://stealthagents.com/research/real-estate-virtual-assistant-hiring-cost-what-agents-actually-pay-in-2025",
    "pm_gloss": "https://www.propertymark.co.uk/professional-standards/consumer-guides/estate-agency-terms.html",
    "wizehire_tc": "https://wizehire.com/real-estate-transaction-coordinator-job-description",
    "indeed_leasing": "https://www.indeed.com/hire/job-description/leasing-agent",
    "gs_us": "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q=ai+for+real+estate+agents",
    "gs_uk": "https://suggestqueries.google.com/complete/search?client=firefox&hl=en-GB&gl=uk&q=estate+agent+ai",
    "indeed_uk_ln": "https://uk.indeed.com/hire/job-description/lettings-negotiator",
    "reed_57397576": "https://www.reed.co.uk/jobs/sales-progresser/57397576",
    "oj_1491810": "https://www.onlinejobs.ph/jobseekers/job/1491810",
    "upwork_fub": "https://www.upwork.com/nx/search/jobs/?q=follow%20up%20boss",
    "oj_1734802": "https://www.onlinejobs.ph/jobseekers/job/property-management-virtual-assistant-uk-hours-for-uk-based-real-estate-agency-1734802",
    "reed_57348677": "https://www.reed.co.uk/jobs/sales-negotiator/57348677",
    "reed_ln": "https://www.reed.co.uk/jobs/lettings-negotiator-jobs",
    "reed_sp": "https://www.reed.co.uk/jobs/sales-progressor-jobs",
    "reed_la": "https://www.reed.co.uk/jobs/lettings-administrator-jobs",
    "pm_jobs": "https://jobs.propertymark.co.uk/jobs/",
    "indeed_uk_pm": "https://uk.indeed.com/hire/job-description/property-manager",
    "wizehire_lc": "https://wizehire.com/listing-coordinator-job-description",
    "wisepelican": "https://wisepelican.com/real-estate-inside-sales/",
    "oj_1740481": "https://www.onlinejobs.ph/jobseekers/job/compliance-maintenance-coordinator-uk-property-part-time-with-a-view-to-full-time-1740481",
    "oj_1731573": "https://www.onlinejobs.ph/jobseekers/job/part-time-uk-property-tenancy-coordinator-1731573",
    "oj_1742926": "https://www.onlinejobs.ph/jobseekers/job/experienced-uk-property-manager-property-operations-coordinator-x2-1742926",
    "oj_1329666": "https://www.onlinejobs.ph/jobseekers/job/1329666",
    "oj_847141": "https://www.onlinejobs.ph/jobseekers/job/847141",
    "pros_tc": "https://prosmarketplace.com/job/job-detail/transaction-coordinator-real-estate-3",
    "pros_fub": "https://prosmarketplace.com/job/job-detail/seeking-real-estate-va-experienced-with-fub-and-crm-spanish-and-english-speaking",
    "oj_tc": "https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword=transaction+coordinator",
    "oj_ukprop": "https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword=UK+property",
    "upwork_tc": "https://www.upwork.com/nx/search/jobs/?q=real%20estate%20transaction%20coordinator",
    "upwork_ai": "https://www.upwork.com/nx/search/jobs/?q=real%20estate%20ai%20chatbot",
    "wfh_isa": "https://wfh.team/job/20346-inside-sales-agent-isa-real-estate-cold-calling-assist-world",
    "upwork_kv": "https://www.upwork.com/nx/search/jobs/?q=kvcore",
    "upwork_pmva": "https://www.upwork.com/nx/search/jobs/?q=property%20management%20virtual%20assistant",
    "pph_ea": "https://www.peopleperhour.com/freelance-jobs?keyword=estate%20agent",
    "upwork_svc_pm": "https://www.upwork.com/services/search?q=property%20management",
    "upwork_svc_re": "https://www.upwork.com/services/search?q=real%20estate",
    "bp_1302426": "https://www.biggerpockets.com/forums/52/topics/1302426-how-do-you-hand-off-an-unresolved-tenant-call",
    "pie_fines_agents": "https://propertyindustryeye.com/landlords-could-still-face-fines-for-letting-agent-failures/",
    "ic3_2025": "https://www.ic3.gov/AnnualReport/Reports/2025_IC3Report.pdf",
    "ic3_2024": "https://www.ic3.gov/AnnualReport/Reports/2024_IC3Report.pdf",
    "rnr_wire": "https://realtynewsreport.com/one-in-four-consumers-targeted-by-real-estate-wire-fraudsters/",
    "certifid_sow": "https://www.certifid.com/state-of-wire-fraud",
    "alta_2026": "https://alta.org/file/Seller-Impersonation-Fraud-Study-Report.pdf",
    "hw_sif": "https://www.housingwire.com/articles/seller-impersonation-fraud-more-than-doubled-since-2024/",
    "hw_deepfake": "https://www.housingwire.com/articles/an-endless-battle-how-real-estate-pros-can-stay-ahead-of-deepfake-fraudsters/",
    "nar_deed": "https://www.nar.realtor/research-and-statistics/research-reports/deed-and-title-fraud-survey",
    "certifid_sif": "https://www.certifid.com/article/seller-impersonation-fraud",
    "mfe_snappt": "https://www.multifamilyexecutive.com/technology/snappt-report-6-4-of-rental-applications-were-fraudulent-in-2024_o",
    "nar_ci_fraud": "https://www.nar.realtor/news/commercial-insights/countering-fraud-in-the-apartment-application-process",
    "buildium_2026": "https://www.buildium.com/resource/2026-property-management-industry-report/",
    "pr_fraud40": "https://www.propertyreporter.co.uk/rental-fraud-up-40-as-ai-generated-fake-identities-target-letting-agents-and-landlords.html",
    "pr_scams": "https://www.propertyreporter.co.uk/rental-fraud-falls-by-18-but-losses-increase.html",
    "hmlr_fraud": "https://hmlandregistry.blog.gov.uk/2025/09/17/the-true-picture-of-property-fraud-in-england-and-wales",
    "cts": "https://www.intelligentcio.com/eu/2023/11/27/cyber-attack-causes-delays-to-house-sales-and-purchases-across-the-uk/",
    "ms_80k": "https://www.mortgagesolutions.co.uk/mortgage-news/2019/07/22/estate-agent-fined-80k-for-exposing-thousands-of-customers-personal-data/",
    "csbs": "https://www.gov.uk/government/statistics/cyber-security-breaches-survey-2025/cyber-security-breaches-survey-2025",
    "comsure": "https://www.comsuregroup.com/news/aml-fails-in-six-months-hmrc-fined-estate-agents-836-000-most-never-even-registered/",
    "pietax": "https://pie.tax/tax-pible/estate-agents-fined-money-laundering-aml-breaches",
    "eat_jun25": "https://www.estateagenttoday.co.uk/breaking-news/2025/06/agents-make-up-majority-of-latest-aml-fines-hmrc/",
    "pie_2022": "https://propertyindustryeye.com/hmrc-fines-estate-agents-more-than-500000-for-aml-breaches/",
    "gov_crack": "https://www.gov.uk/government/news/hmrc-cracks-down-on-unlawful-estate-agents",
    "devonshires": "https://insights.devonshires.com/post/102nbd1/hmrc-updates-anti-money-laundering-guidance-for-estate-agency-businesses-key-tak",
    "pm_aml_fee": "https://www.propertymark.co.uk/resource/unaffordable-aml-fees-could-drive-greater-non-compliance.html",
    "pie_sof": "https://propertyindustryeye.com/new-data-brings-significant-operational-burden-for-conveyancers-and-estate-agents/",
    "pr_credas": "https://www.propertyreporter.co.uk/estate-agents-change-approach-as-id-check-costs-rise.html",
    "pie_idview": "https://propertyindustryeye.com/estate-agents-warned-over-demanding-id-ahead-of-property-viewings/",
    "lt_rtr": "https://landlordtoday.co.uk/breaking-news/2024/5/huge-surge-in-right-to-rent-checks-as-non-compliance-fines-soar",
    "gov_rtr_pen": "https://www.gov.uk/penalties-illegal-renting",
    "ho_guide": "https://www.gov.uk/government/publications/landlords-guide-to-right-to-rent-checks/landlords-guide-to-right-to-rent-checks-1-october-2026-accessible",
    "pm_rtr_cost": "https://www.propertymark.co.uk/resource/cost-increases-faced-with-end-of-adjusted-right-to-rent-checks.html",
    "gov_ll": "https://www.gov.uk/guidance/renting-out-your-property-guidance-for-landlords-and-letting-agents",
    "gov_tenants": "https://www.gov.uk/guidance/renters-rights-act-overview-for-tenants",
    "woking": "https://www.woking.gov.uk/housing/private-rented-housing/renters-rights-act-information-landlords-letting-agents",
    "ac_rra": "https://www.anthonycollins.com/blog/102lxyr/renters-rights-act-guidance-and-fines-for-private-landlords/",
    "lz_fine": "https://www.landlordzone.co.uk/news/agent-fined-after-issuing-banned-six-month-tenancy",
    "lz_4m": "https://www.landlordzone.co.uk/news/renters-rights-act-a-look-at-the-first-4-months",
    "pie_mi_cma": "https://propertyindustryeye.com/competition-watchdog-warned-of-unfair-and-damaging-material-information-rules/",
    "gov_mi": "https://www.gov.uk/government/consultations/material-information-in-property-listings",
    "negotiator_ai": "https://thenegotiator.co.uk/news/regulation-law-news/trouble-brewing-over-estate-agents-use-of-ai-photography/",
    "pie_ai_left": "https://propertyindustryeye.com/could-estate-agencies-that-fail-to-embrace-ai-be-left-behind/",
    "pie_ai_free": "https://propertyindustryeye.com/agents-are-paying-for-tools-ai-now-does-for-free-new-rightmove-resistance-tour-launches/",
    "pm_course": "https://www.propertymark.co.uk/course/managing-ai-generated-complaints.html",
    "pie_alto_ai": "https://propertyindustryeye.com/estate-agents-turn-to-ai-amid-rising-compliance-pressures/",
    "nar_policy": "https://www.nar.realtor/news/broker-news/why-every-brokerage-needs-an-ai-use-policy",
    "hw_fh": "https://housingwire.com/articles/ai-fair-housing-remarks-checklist",
    "nar_tech": "https://www.nar.realtor/research-and-statistics/research-reports/realtor-technology-survey",
    "aicareer": "https://theaicareerlab.com/blog/ai-real-estate-listings-rules-fair-housing/",
    "hw_hud": "https://housingwire.com/articles/hud-issues-fair-housing-act-guidance-on-ai-use",
    "orrick": "https://infobytes.orrick.com/2024-05-10/hud-guidance-ai-prevent-housing-discrimination/",
    "cohen": "https://cohenmilstein.com/ai-landlord-screening-tool-will-stop-scoring-low-income-tenants-after-discrimination-suit",
    "propmodo": "https://www.propmodo.com/the-realpage-settlement-wont-end-the-fight-over-revenue-management-software/",
    "northstar": "https://northstarmls.com/insights/guidelines-for-virtual-staging-and-ai-enhanced-listing-photos/",
    "close_photo": "https://theclose.com/news-ai-listing-photo-rules/",
    "close_ab723": "https://theclose.com/news-ai-listing-photo-disclosure/",
    "nar_tcpa": "https://www.nar.realtor/sites/default/files/2025-03/TCPA-Best-Practices-NAR-One-Sheet-2025-03-17.pdf",
    "nar_tele": "https://www.nar.realtor/telemarketing-cold-calling",
    "hw_fcc": "https://housingwire.com/articles/fcc-says-new-rules-for-robocall-and-text-opt-outs-will-take-effect-in-april-2025",
    "bam_tcpa": "https://nowbam.com/what-you-need-to-know-about-the-new-rules-for-cold-calls-texts/",
    "co_sb205": "https://leg.colorado.gov/bills/sb24-205",
    "ftc_reviews": "https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials",
    "pearl": "https://pearlinsurance.com/how-does-your-eo-coverage-handle-ai-navigating-risk-alongside-evolving-technology/",
    "pie_rightmove_alto": "https://propertyindustryeye.com/rightmove-enhanced-leads-now-integrated-with-popular-agency-crm/",
    "bp_1303197": "https://www.biggerpockets.com/forums/52/topics/1303197-how-do-you-keep-tenant-requests-from-getting-lost",
})

BLOCKED_HOSTS = ("reddit.com on every mirror; Property118; Property Tribes thread bodies; Inman; The Negotiator; Estate Agent Today; Landlord Today in part; ConsumerAffairs; "
                 "G2, Capterra, Software Advice, GetApp and AllAgents; Fiverr entirely; Upwork client fields and proposal counts; Zillow; HUD PDFs; the FCC; the ICO enforcement search; "
                 "several GOV.UK HMRC and client-money pages; TPO's annual reports; Goodlord's report pages; Totaljobs, ZipRecruiter, Craigslist, Glassdoor and the Indeed US job-description pages for coordinator roles.")


def cover_page():
    out = [NextPageTemplate("cover"), Spacer(1, 26 * mm)]
    band = Table([[Paragraph("Small property firms chase, re-key and get fined", S["cover_title"])],
                  [Paragraph("Problems, workflows, numbers, vocabulary and service gaps in small UK and US real estate businesses: independent estate and letting agencies "
                             "of one to three branches, small property managers, brokerages and teams of 1 to 30 agents, solo agents, small landlords, investors and wholesalers", S["cover_sub"])]],
                 colWidths=[FRAME_W])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (0, 0), 18), ("BOTTOMPADDING", (0, 0), (0, 0), 6),
        ("TOPPADDING", (0, 1), (0, 1), 2), ("BOTTOMPADDING", (0, 1), (0, 1), 18),
    ]))
    out.append(band)
    out.append(Spacer(1, 7 * mm))
    out.append(Paragraph("Research report, 12 October 2026", S["cover_meta"]))
    out.append(Spacer(1, 2 * mm))
    warn = Table([[Paragraph("Problems and gaps only. This document adds no solutions and no recommendations.", S["cover_warn"])]], colWidths=[FRAME_W])
    warn.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C_WARM_TINT), ("LINEBEFORE", (0, 0), (0, -1), 3, C_WARM),
                              ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    out.append(warn)
    out.append(Spacer(1, 8 * mm))
    scope_rows = [
        ["Scope", "UK (England mainly, with Scotland and Wales noted) and US small real estate businesses: sales agencies, lettings and property management, brokerages and "
                  "agent teams, contract-to-close, investors and wholesalers. Five lines of business in two countries."],
        ["Inputs", "Research note files compiled by the research team, one per section: time and money benchmarks, practitioners' vocabulary, workflows by line of business, "
                   "fraud and rules, verification, platforms and the audit angle, handoffs, platform comparison, the thirteen-gap ranking, and the employed-versus-freelance market. "
                   "Relative dates on BiggerPockets threads were captured on 11-12 October 2026."],
        ["Sources blocked", BLOCKED_HOSTS + " The shared web-search budget ran out part-way through every notes file; research continued by direct fetch of known URLs. "
                            "Facts from blocked hosts rest on search snippets, secondary reports, vendor claims or sponsored comparisons and are tagged."],
        ["Currency and dates", "All currency as published: GBP for UK figures, USD for US figures. Dates are given so freshness can be judged."],
    ]
    st = Table([[Paragraph(a, S["cover_label"]), Paragraph(b, S["cover_small"])] for a, b in scope_rows], colWidths=[30 * mm, FRAME_W - 30 * mm])
    st.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -2), 0.3, C_GRID),
                            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out.append(st)
    out.append(Spacer(1, 7 * mm))
    out.append(Paragraph("How to read the evidence tags", S["cover_label"]))
    tags = [
        ("[snippet]", "the fact was seen only in a search-engine summary because the page blocked the researcher"),
        ("[vendor]", "the vendor's own claim or a vendor-run survey; no independent source confirmed it"),
        ("[user, date]", "a dated user review or forum post"),
        ("[secondary]", "the figure was relayed by a news site, aggregator or blog rather than read from the primary report"),
        ("[sponsored]", "a comparison paid for by a rival vendor"),
        ("[n]", "a numbered source; the URL is in the Sources appendix"),
    ]
    tt = Table([[Paragraph("<b>%s</b>" % esc(a), S["legend_tag"]), Paragraph(esc(b), S["legend_tag"])] for a, b in tags], colWidths=[26 * mm, FRAME_W - 26 * mm])
    tt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    out.append(tt)
    out.append(Spacer(1, 8 * mm))
    out.append(Paragraph("Prepared for Mustafa Shoukat. Built from the research report <i>Small real estate firm problems UK US</i> "
                         "(11 numbered sections, 40 tables, 13 gap cards, a 40-row unverified list). %d numbered sources." % len(URLS), S["cover_small"]))
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
    out.append(Paragraph("The eight numbers that carry the report, then the thirteen service gaps in rank order. Each gap has a full card in section 9.", S["lead"]))
    tiles = [
        stat_tile("216 days", "UK listing to completion: 62 to find a buyer + 154 to complete; record, +36 vs 2019",
                  "Rightmove, Great Britain, Jul 2026 [Property Industry Eye](@pie_216)"),
        stat_tile("23.7%", "of UK agreed sales fall through, at about £3,550 each (£1.065bn in 2025)",
                  "TwentyEA Q1 2026 [Property Industry Eye](@pie_ft); cost [Property Industry Eye](@pie_cost)"),
        stat_tile("9 sides", "median US Realtor: $59,200 gross, $37,000 net; first two years $8,000",
                  "NAR 2026 Member Profile, 5,116 responses [NAR](@nar_profile)"),
        stat_tile("14% / 5–7%", "US contracts delayed / terminated; $223 per Zillow lead, $7,433–$22,300 per closing",
                  "[NAR RCI](@nar_rci_dec); [Clever](@clever_z) [secondary]"),
        stat_tile("73% / 61%", "UK letting professionals report more admin / re-key data since 1 May 2026; complaints +47%",
                  "Propoly via [Property Industry Eye](@pie_rra_admin) [vendor survey]; [Property Industry Eye](@pie_complaints)"),
        stat_tile("$275.1m", "FBI real estate fraud losses 2025 (12,368 complaints); seller impersonation at 59% of title firms",
                  "[FBI IC3 2025](@ic3_2025); [ALTA 2026](@alta_2026)"),
        stat_tile("£9,601", "per fraudulent UK tenancy; suspected fraud +40% with AI-built identities; 6.4% of US applications",
                  "Goodlord via [Property Reporter](@pr_fraud40) [vendor data]; Snappt [Multifamily Executive](@mfe_snappt)"),
        stat_tile("170 / £835,842", "HMRC AML penalties on estate agencies in six months; 332 of 369 for never registering",
                  "HMRC list Apr–Sep 2025 via [Comsure](@comsure)"),
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
    header, rows_ = T(9, 0)
    compact = []
    for r in rows_[:13]:
        rank, gap, signal, cov, fit, country, auto = r
        compact.append([rank, gap, signal.split(":")[0], cov.split(":")[0].split(" (")[0], auto.split(":")[0].split(";")[0], country])
    out.append(tbl(["#", "Gap", "Problem signal", "Vendor coverage", "Automatable", "Country"], compact,
                   widths=[7, 72, 22, 30, 28, 17], font="cell_small"))
    out.append(Paragraph("Crowded areas that are <b>not</b> gaps: listing descriptions and social posts; AI receptionists; CRM set-up gigs; commodity tenant screening reports; "
                         "wire-fraud tools for title companies; promo video and photo editing; skip-trace data; AppFolio bookkeeping as a human service; cold-calling VAs and ISAs (section 9).", S["note"]))
    return out


# --------------------------------------------------------------------------
# Section 1
# --------------------------------------------------------------------------
def section_1(CH):
    out = chapter(1, SEC[1]["title"],
                  "In both countries the firm's income arrives at the end of a chain it does not control: a UK agent is paid only at completion after 216 days and one agreed sale in four never pays; "
                  "a US agent closes nine sides a year, so each delayed or terminated contract is a large share of annual output, and purchased leads cost more than most of them return.")
    out.append(fig_image(*CH["uk_sale_timeline"]))
    out.append(H2("UK sales: the longest wait on record, then a one-in-four loss"))
    out += bullets([
        "A seller in Great Britain now waits <b>62 days to find a buyer and a further 154 days from sale agreed to completion, 216 days in all</b>, which Rightmove called the 'longest wait on record' and 36 days longer than 2019; "
        "London takes 244 days, flats 169 against about 149 for houses, Slough is the slowest local authority at 229 legal days ([Property Industry Eye, 31 Jul 2026](@pie_216)).",
        "TwentyEA measures <b>123 days from sale agreed to exchange in 2025 (91 in 2019)</b> ([Property Reporter, 15 Dec 2025](@pr_123)); a sales-progression firm says <b>60.8% of exchanges now take more than six months from instruction, against 36.1% in 2019</b> ([Property Industry Eye, 1 Oct 2026](@pie_6m)).",
        "The agent is paid only at completion: 'Estate agents do not get their commission until completion so it makes sense for them to have a quick completion' ([Property Industry Eye, 3 Sep 2026](@pie_blame) [user, Sep 2026]).",
        "The loss rate: of <b>1,257,053 sales agreed in 2025, 303,538 fell through</b> and 986,665 exchanged, with 1,125,158 price changes and 803,612 withdrawals on 1,710,950 new instructions ([Mortgage Solutions, 19 Jan 2026](@ms_2025)); "
        "the fall-through rate was <b>23.7% in Q1 2026</b> (24.0% a year earlier), 38% of failures happen within four weeks of sale agreed ([Property Industry Eye, 17 Apr 2026](@pie_ft)); each one costs about <b>£3,550 (£3,584 in Q2 2026)</b>, £1.065bn across 2025 "
        "([Property Industry Eye, 10 Apr 2026](@pie_cost); [Property Industry Eye, 29 Sep 2026](@pie_cost2)).",
        "Quick Move Now's smaller sample puts failures far higher, <b>41% of sales in April-June 2025</b>, with mortgage difficulties (45%), chain breakdowns (18%) and the buyer changing mind (14%) as causes ([HomeOwners Alliance](@hoa_ft) [secondary]); the two bases differ and should not be averaged.",
        "The average fee per completed sale is <b>£3,909</b> (London £9,378, Liverpool £2,585) ([Property Industry Eye, 17 Mar 2026](@pie_fee) [vendor data, GetAgent]), about 1.42% including VAT ([HomeOwners Alliance](@hoa_fee)): roughly one agreed sale in four produces nothing after five months of progression work.",
    ])
    out.append(H2("The chasing, measured from the other side of the phone"))
    out += bullets([
        "Conveyancers 'probably spend on average 2 hours per day dealing with chaser calls and emails from estate agents', 'a whole working day per week when conveyancers are not doing conveyancing work', and many sales progressors 'do not speed the progress of a matter' ([Conveyancing Matters podcast, 5 Sep 2024](@conv_pod)).",
        "Movers blame the other way round: <b>72% experienced a delay; of those who named a party 50% blamed the conveyancer, 40% the buyer or seller and 5% the agent</b> ([Property Industry Eye, 3 Sep 2026](@pie_blame) [vendor survey]).",
        "At large firms a sales progressor carries '150 to 250 cases at once' ([Property Industry Eye, 24 Sep 2026](@pie_franchise)); the record-keeping gap in one commenter's words: 'Without the log, every fall-through just feels like bad luck' ([Property Industry Eye, 1 Oct 2026](@pie_6m) [user, Oct 2026]).",
    ])
    out.append(H3("Table 1.1  UK sales measures"))
    h, r = T(1, 0)
    out.append(tbl(h, r, widths=[32, 62, 34, 48], font="cell_small"))
    out.append(H2("UK lettings has a different clock"))
    out += bullets([
        "The average letting agency manages <b>340 properties with 14 staff; 54% of agencies have five or fewer staff</b>; each property draws <b>6 to 9 applicants</b>, voids run about <b>20 days</b>, and until May 2026 <b>27% of agency revenue came from tenancy renewals</b>, which the Renters' Rights Act removed by abolishing fixed terms "
        "([Goodlord SOLI 2025](@goodlord_soli) [vendor survey, 2,750+ respondents]; [Propertymark, Dec 2025](@pm_dec25); [Goodlord Rental Index, Sep 2026](@goodlord_index) [vendor]).",
        "Four months into the Act, <b>73% of property professionals report more administration</b>, two-thirds run 'several disconnected systems', 17% rely on 'emails, spreadsheets and separate processes' and <b>61% say staff must 'transfer, re-enter or duplicate information between systems during a tenancy'</b> "
        "([Property Industry Eye, 3 Sep 2026](@pie_rra_admin) [vendor survey, Propoly]); a second small survey found 62.5% spending more time on compliance and administration ([Property Reporter, 4 Sep 2026](@pr_compliance)).",
        "Complaints moved with it: Property Redress complaint enquiries rose from <b>2,863 (2024) to 4,220 (2025), +47.4%</b>, the cause being 'agents having less time to devote to tenant experience as compliance and administrative workloads grow' ([Property Industry Eye, 12 Jun 2026](@pie_complaints)); "
        "The Property Ombudsman reported <b>lettings disputes up 65% on 2024</b> with 'poor or delayed communication and management' the top cause ([Propertymark, 13 Mar 2026](@pm_tpo)); TPO's 2024 contacts hit a record <b>73,035, up 27%</b> ([The Intermediary, 20 May 2025](@ti_tpo)).",
        "Self-managing portfolio landlords, the group agents compete with and recruit from: <b>52% find maintenance the most time-consuming task, 77% put off non-urgent maintenance for lack of time, 68% spend 31 or more hours a month</b> ([LandlordZONE, 23 Sep 2026](@lz_maint) [vendor survey, 525 landlords]).",
        "Staff are cheap: a lettings negotiator averages <b>£28,492</b> and a property manager <b>£33,785</b> ([Indeed UK, lettings negotiator](@indeed_ln); [Indeed UK, property manager](@indeed_pm) [self-reported]); <b>65% of letting agents hold no formal property qualification</b> ([LandlordZONE, 18 Sep 2026](@lz_qual)).",
    ])
    out.append(fig_image(*CH["uk_lettings"]))
    out.append(H3("Table 1.2  UK lettings measures"))
    h, r = T(1, 1)
    out.append(tbl(h, r, widths=[30, 66, 32, 48], font="cell_small"))
    out.append(H2("The US agent's problem is volume, not waiting"))
    out += bullets([
        "NAR's 2026 Member Profile (2025 data, 5,116 responses): median <b>9 transaction sides, 35 hours a week, $59,200 gross and $37,000 net</b>; 86% independent contractors; 15% of members in their first two years earning a median <b>$8,000</b>; median business expenses $9,520; only 48% say real estate is the household's main income ([NAR 2026 Member Profile](@nar_profile)).",
        "Contract failure is steady: December 2025 confidence index <b>5% of contracts terminated and 14% delayed</b>, 6% of delays appraisal issues, median close 30 days ([NAR RCI, Dec 2025](@nar_rci_dec)); by August 2026, 7% terminated and 14% delayed ([NAR RCI](@nar_rci)).",
        "The lead side is the money sink. The only independent audit of response time (2013) found <b>48% of 384 buyer enquiries to brokerages were never answered</b> and 68% of consumers work with the first professional who answers ([WAV Group 2013](@wav)); a 2026 vendor benchmark puts the real estate average at <b>15 hours</b> ([Prospeo](@prospeo) [vendor, snippet]).",
        "Zillow's published average lead cost is <b>$223 in major metros and $139 elsewhere</b>; purchased leads close at roughly 1 to 3%, so the cost per closing is <b>$7,433 at 3% and $22,300 at 1%</b>; Zillow's Preferred standard requires a predicted 4% conversion ([Clever, 14 Sep 2026](@clever_z) [secondary]).",
        "Agents' reviews of paid leads: 'I DID NOT SEE MY ROI', 'I paid over a thousand dollars for completely dead data', 'they promised me 1-3 leads a month but I've barely gotten any... 0 showings 0 meetings 0 future business' ([Trustpilot, Realtor.com](@tp_realtor) [user, Jan-Oct 2026]).",
        "Behind the contract: agents carrying '15-20 files' lose track of 'inspection objections, lender conditions and signatures'; missed option-period and earnest-money release deadlines are 'still the biggest bleed I see' ([BiggerPockets post 7250481](@bp_7250481) [user, about Aug 2026]); "
        "a transaction coordinator's file takes 3 to 6 hours when clean and 8 to 15 when complex, with 20 to 30 dates per contract, at $350 to $500 a file ([ListedKit](@listedkit) [vendor]).",
    ])
    out.append(fig_image(*CH["nar_income"]))
    out.append(fig_image(*CH["us_contracts"]))
    out.append(fig_image(*CH["lead_economics"]))
    out.append(H3("Table 1.3  US measures"))
    h, r = T(1, 2)
    out.append(tbl(h, r, widths=[30, 68, 30, 48], font="cell_small"))
    out.append(H2("The shape of the work, in practitioners' own small numbers"))
    out += bullets([
        "15 to 20 open files per US agent; 150 to 250 cases per UK sales progressor; two hours a day of agent chasers on a conveyancer's desk; five message rounds per maintenance text 'because no written answer is on file'; 31 or more hours a month for a UK portfolio landlord; "
        "1,000-plus dials for two sellers in follow-up; a two-hour evening calling shift for a part-time wholesaler ([BiggerPockets 1303079](@bp_1303079) [user, Oct 2026]; [BiggerPockets 1286268](@bp_1286268) [user, about May 2026]).",
        "Nobody in the reachable threads gives a weekly admin-hours figure for themselves; the only such numbers ('8 to 15 hours per file', '13-15 hours a week reclaimed', '45 hours per transaction with 30 on paperwork') are vendor claims with unverified attributions "
        "([Form Simplicity](@formsimp) [vendor]; [Stealth Agents](@stealth) [vendor]; [ListedKit](@listedkit) [vendor]).",
    ])
    return out


# --------------------------------------------------------------------------
# Section 2
# --------------------------------------------------------------------------
def section_2(CH):
    out = chapter(2, SEC[2]["title"],
                  "The two markets describe the same labour with nouns that almost never appear in the same document, and the difference decides which keywords work: "
                  "the UK speaks in laws, bodies and forms; the US in tools, deadlines and money.")
    out += bullets([
        "<b>UK</b>: 'vendor', 'instruction', 'particulars', 'viewing', 'sale agreed', 'sold STC', 'exchange and completion', 'sales progression', 'chain', 'solicitors', 'memorandum of sale', 'referencing', 'right to rent', 'deposit protection', 'prescribed information', 'inventory', "
        "'check-in and check-out', 'gas safety (CP12)', 'EICR', 'EPC', 'HMO licensing', 'section 8', 'section 13', 'section 21', 'arrears', 'landlord statement', 'let-only', 'fully managed', 'Rightmove', 'Propertymark', 'TPO', 'AML', 'Material Information', 'Renters' Rights Act'.",
        "<b>US</b>: 'seller', 'listing agreement', 'MLS remarks', 'showing', 'under contract', 'closing', 'escrow', 'title company', 'transaction coordinator', 'contract to close', 'CMA', 'leasing', 'screening', 'security deposit', 'work orders', 'vendors', 'HOA', 'Fair Housing', '3-day notice', "
        "'owner statement', 'Zillow', 'IDX', 'ISA', 'skip tracing', 'TCPA', 'DNC', 'trust account', '1099' ([Propertymark glossary](@pm_gloss); [WizeHire TC](@wizehire_tc); [Indeed US leasing agent](@indeed_leasing)).",
        "Autocomplete confirms the split: US searchers compare tools ('follow up boss vs lofty', 'kvcore vs boldtrail', 'claude vs chatgpt for realtors') and ask about fees and checklists; UK searchers name statutes and forms ('renters rights act section 8 ground 1a', 'section 13 notice form 4a', 'material information part b'); "
        "'reapit vs' and 'alto vs' return nothing; 'overwhelmed', 'overload' and 'burnout' phrasings return almost nothing in either country, because the pain is expressed through process nouns ('checklist', 'fee', 'how long', 'vs') rather than feelings ([Google suggest, US](@gs_us); [Google suggest, UK](@gs_uk)).",
    ])
    out.append(H3("Table 2.1  Concept by concept: UK words against US words (keyword list)"))
    h, r = T(2, 0)
    out.append(tbl(h, r, widths=[26, 75, 75], font="cell_small"))
    out.append(source_line("Sources: Propertymark glossary [%d]; Propertymark on advertising terms [%d]; GOV.UK How to let [%d]; Reed estate agency jobs [%d]; Indeed UK property manager [%d]; OnlineJobs.ph compliance coordinator post [%d]; WizeHire listing coordinator [%d]; "
                           "Indeed US property manager [%d]; Upwork jobs: follow up boss [%d]; BiggerPockets 1303197 [%d]; Property Industry Eye, 5 Mar 2025 [%d]; Trustpilot Realtor.com [%d]." % tuple(ref(u) for u in (
                               "https://www.propertymark.co.uk/professional-standards/consumer-guides/estate-agency-terms.html", "https://www.propertymark.co.uk/resource/clarity-provided-on-advertising-terms.html",
                               "https://www.gov.uk/government/publications/how-to-let/how-to-let", "https://www.reed.co.uk/jobs/estate-agent-jobs", "https://uk.indeed.com/hire/job-description/property-manager",
                               "https://www.onlinejobs.ph/jobseekers/job/compliance-maintenance-coordinator-uk-property-part-time-with-a-view-to-full-time-1740481", "https://wizehire.com/listing-coordinator-job-description",
                               "https://www.indeed.com/hire/job-description/property-manager", "https://www.upwork.com/nx/search/jobs/?q=follow%20up%20boss",
                               "https://www.biggerpockets.com/forums/52/topics/1303197-how-do-you-keep-tenant-requests-from-getting-lost", "https://propertyindustryeye.com/rightmoves-hike-in-fees-sparks-another-petition/",
                               "https://www.trustpilot.com/review/realtor.com?stars=1"))))
    out.append(H2("What job advertisements pay people to do"))
    out += bullets([
        "Across <b>18 UK ads</b> read on 11-12 October 2026 (Indeed UK templates and examples, three Connells-group ads on Reed, one Workable ad, a Propertymark snippet, six posts by small UK agencies on OnlineJobs.ph) the duty families are maintenance and contractors, viewings, deposit administration and safety certificates; "
        "across <b>35 US ads</b> (WizeHire templates, Indeed US templates, nine OnlineJobs.ph posts, two ProsMarketplace posts, one South African staffing site, 16 Upwork posts) they are lead follow-up, keeping the CRM clean, contract to close, and, in <b>13 of 35, an AI tool named inside the duty list</b> "
        "('Create post captions with ChatGPT', 'use AI to draft replies', 'creating high-quality AI prompts for real estate follow-up') ([Indeed UK lettings negotiator](@indeed_uk_ln); [Reed 57397576](@reed_57397576); [WizeHire TC](@wizehire_tc); [OnlineJobs.ph 1491810](@oj_1491810); [Upwork jobs: follow up boss](@upwork_fub)). Both tallies are counts of phrase families in the ads fetched, not board-wide statistics.",
        "'No lead falls through the cracks' appears in three separate US posts; 'fall-through' never appears in UK ads but does in UK autocomplete; 'chasing' appears in UK posts by small firms ('chasing unresponsive contacts through multiple channels until resolved', 'Chase every job to completion and close it out with photos and invoices') "
        "but not in the Connells-group ads, which write around process stages ('Progressing sales through to exchange and completion') ([OnlineJobs.ph 1734802](@oj_1734802); [Reed 57348677](@reed_57348677)).",
    ])
    out.append(fig_image(*CH["job_ads"]))
    out.append(H3("Table 2.2  Phrase families in UK and US ads"))
    h, r = T(2, 1)
    out.append(tbl(h, r, widths=[70, 12, 82, 12], align_right_cols=(1, 3)))
    out.append(source_line("Sources: UK tally over Indeed UK lettings negotiator [%d], estate agent [%d] and property manager [%d], Reed 57341662 [%d], 57348677 [%d] and 57397576 [%d], Workable St John Lettings [%d], OnlineJobs.ph 1740481 [%d], 1731573 [%d] and 1742926 [%d]; "
                           "US tally over WizeHire TC [%d] and admin assistant [%d], Indeed US leasing agent [%d], OnlineJobs.ph 1329666 [%d] and 1658028 [%d], wfh.team ISA [%d], Upwork jobs: kvcore [%d], transaction coordinator [%d] and property management VA [%d]." % tuple(ref(u) for u in (
                               "https://uk.indeed.com/hire/job-description/lettings-negotiator", "https://uk.indeed.com/hire/job-description/estate-agent", "https://uk.indeed.com/hire/job-description/property-manager",
                               "https://www.reed.co.uk/jobs/lettings-negotiator/57341662", "https://www.reed.co.uk/jobs/sales-negotiator/57348677", "https://www.reed.co.uk/jobs/sales-progresser/57397576",
                               "https://apply.workable.com/oryx-1/jobs/view/0CE326B0C4.md", "https://www.onlinejobs.ph/jobseekers/job/compliance-maintenance-coordinator-uk-property-part-time-with-a-view-to-full-time-1740481",
                               "https://www.onlinejobs.ph/jobseekers/job/part-time-uk-property-tenancy-coordinator-1731573", "https://www.onlinejobs.ph/jobseekers/job/experienced-uk-property-manager-property-operations-coordinator-x2-1742926",
                               "https://wizehire.com/real-estate-transaction-coordinator-job-description", "https://wizehire.com/real-estate-administrative-assistant-job-description", "https://www.indeed.com/hire/job-description/leasing-agent",
                               "https://www.onlinejobs.ph/jobseekers/job/1329666", "https://www.onlinejobs.ph/jobseekers/job/1658028", "https://wfh.team/job/20346-inside-sales-agent-isa-real-estate-cold-calling-assist-world",
                               "https://www.upwork.com/nx/search/jobs/?q=kvcore", "https://www.upwork.com/nx/search/jobs/?q=real%20estate%20transaction%20coordinator", "https://www.upwork.com/nx/search/jobs/?q=property%20management%20virtual%20assistant"))))
    out.append(H2("The pay attached to those duties sets the ceiling"))
    out += bullets([
        "Reed, September-October 2026: <b>15 of 24 lettings negotiator ads state £25,000 basic</b> (Connells, William H Brown, Dixons, Frank Innes and others); sales negotiators cluster at £25,000 to £30,000; sales progressors run from £19,000-£22,000 (Connells, Wolverhampton, part time) to £37,000-£43,000 (Blackburn); "
        "lettings administrators £26,000-£34,000; lettings property managers £30,000-£35,000; the only salaried ad on Propertymark's board was a Head of Lettings at £70,000 ([Reed lettings negotiator](@reed_ln); [Reed sales progressor](@reed_sp); [Reed lettings administrator](@reed_la); [Propertymark jobs](@pm_jobs)); "
        "Indeed's UK averages are £22,657 for a lettings negotiator and £27,979 for an estate agent; a part-time block-management property manager in Aylesbury is offered 'Up to £12.00 per hour' ([Indeed UK lettings negotiator](@indeed_uk_ln); [Indeed UK property manager](@indeed_uk_pm)).",
        "US: WizeHire's national averages are <b>$39,000 for a transaction coordinator, $33,000 for a listing coordinator, $48,000 for a marketing coordinator and $15 an hour for an administrative assistant</b>; Indeed's common leasing-agent rate is $19.45 an hour; an ISA is benchmarked at $57,686 to $69,398 plus 5 to 15% of gross commission "
        "([WizeHire TC](@wizehire_tc); [WizeHire listing coordinator](@wizehire_lc); [Indeed US leasing agent](@indeed_leasing); [Wise Pelican](@wisepelican) [secondary]).",
        "The same duty lists posted offshore pay a tenth of that: a West London single-branch agency offers a property-management VA 'From $1,050/month' for 45 hours a week including Saturday mornings; a UK lettings and HMO agency offers a 'Compliance &amp; Maintenance Coordinator' at 'GBP 4.50 - 5.00+ per hour'; "
        "a UK landlord offers 'US$5 per hour' for a tenancy coordinator to 'build and maintain an auditable property-management system' showing 'what needed doing, what was done, when, by whom and the supporting evidence'; a 200-property UK portfolio offers two remote property managers at $700-$850 a month; "
        "US posts offer $2 an hour for a 'CRM Lead Follow-Up Specialist', $4 for an ISA, $5 for a Keller Williams team VA, $5-$7.50 for MLS drafting, $700-$1,500 a month for a transaction coordinator and $450-$800 a month for a bilingual Follow Up Boss VA "
        "([OnlineJobs.ph 1734802](@oj_1734802); [OnlineJobs.ph 1740481](@oj_1740481); [OnlineJobs.ph 1731573](@oj_1731573); [OnlineJobs.ph 1742926](@oj_1742926); [OnlineJobs.ph 1329666](@oj_1329666); [OnlineJobs.ph 847141](@oj_847141); [ProsMarketplace TC](@pros_tc); [ProsMarketplace FUB VA](@pros_fub)).",
        "OnlineJobs.ph search volumes on 11 October 2026 (the search caps at 300): <b>'transaction coordinator' 300, 'skip tracing' 298, 'follow up boss' 296, 'real estate cold calling' 292, 'property management' 287, 'real estate' 263, 'UK property' 190</b>, 'listing description' 18 (mostly e-commerce): "
        "the titles the small US firm already outsources, and UK property work a sizeable minority on the same board ([OnlineJobs.ph: transaction coordinator](@oj_tc); [OnlineJobs.ph: UK property](@oj_ukprop)).",
    ])
    out.append(fig_image(*CH["pay_tiers"]))
    out.append(H3("Table 2.3  Pay for the duty, where posted"))
    h, r = T(2, 2)
    out.append(tbl(h, r, widths=[28, 36, 30, 42, 40], font="cell_small"))
    out.append(H2("Freelance posts carry the pain in plainer words"))
    out += bullets([
        "Upwork (81 live posts read across nine searches, August-October 2026): a Wilmington team hiring a 'Follow Up Boss Lead Backstop' at $5-$7 an hour writes 'Your job is to make sure no lead falls through the cracks' and 'When our agents don't work a lead fast enough, you step in'; a broker wants someone to 'Clean up duplicate or outdated contacts' and "
        "'take ownership of keeping my CRM clean, organized, and current'; a sole agent types, verbatim, 'set up my follow-up bus to where the clients that I have worked with are being touched on a 30 day basis or 90 day basis or some kind of touch point I don't know exactly what I'm needing'; "
        "an owner-finance investor needs a TC who 'proactively identifies missing documents, follows up with the appropriate parties, and keeps every transaction moving without waiting for management to notice a problem'; a Denver founder wants 'someone to take the day-to-day off my plate so I can stay focused on deals'; "
        "a two-agent team says '840-850 leads are sitting dormant in the team's CRM' while warm leads 'go unworked while he is out on showings'; a Miami brokerage owner budgets $1,000 fixed for the whole BoldTrail stack "
        "([Upwork jobs: follow up boss](@upwork_fub); [Upwork jobs: transaction coordinator](@upwork_tc); [Upwork jobs: real estate ai chatbot](@upwork_ai); [wfh.team ISA](@wfh_isa); [Upwork jobs: kvcore](@upwork_kv)).",
        "Property-management posts: the 'day to day runs on maintenance getting handled, vendors staying coordinated, and leases renewing on schedule'; 'Coordinate open maintenance tickets end to end, from intake to vendor dispatch to close out'; 'Track vendor response time and flag delays before they become resident complaints' ([Upwork jobs: property management VA](@upwork_pmva)).",
        "The 2026 posts fold AI into the admin role ('use AI to draft replies', 'I'll provide the AI instructions (my voice, the questions to ask, fair housing rules, and when to hand off to me)') and a new 'AI agent / automation / voice bot' category pays $20-$60 an hour or $500 fixed, with one buyer saying 'I'm not looking for someone who only connects apps' ([Upwork jobs: real estate ai chatbot](@upwork_ai)).",
        "UK buyers are almost absent: PeoplePerHour's 'estate agent' search returned 23 results of which three were property-related and none a lettings or progression admin post; the one UK-worded gig among 192 Upwork catalogue gigs read was 'property management VA for UK landlords and agents' from $25 with 35 feedback ([PeoplePerHour jobs: estate agent](@pph_ea); [Upwork services: property management](@upwork_svc_pm)).",
    ])
    out.append(H3("Table 2.4  Work bought on freelance boards, Aug-Oct 2026"))
    h, r = T(2, 3)
    out.append(tbl(h, r, widths=[58, 52, 28, 38], font="cell_small"))
    out.append(H2("How practitioners phrase their own searches (Google autocomplete, 11-12 October 2026)"))
    out.append(Paragraph("Volumes are unknown; only the suggestion order was captured; question-type suggestions are marked PAA. The seeds below returned the most practitioner-specific tails.", S["body"]))
    out.append(H3("Table 2.5  US seeds and suggestions, verbatim"))
    h, r = T(2, 4)
    out.append(tbl(h, r, widths=[40, 136], first_col_bold=True, font="cell_small"))
    out.append(H3("Table 2.6  UK seeds and suggestions, verbatim"))
    h, r = T(2, 5)
    out.append(tbl(h, r, widths=[40, 136], first_col_bold=True, font="cell_small"))
    out.append(source_line("Sources: Google suggest, US locale [%d] and UK locale [%d]; listing coordinator job description [%d]; fiverr real estate [%d]; upwork real estate [%d]. Buyers typing a marketplace name search for media first: 'fiverr real estate' suggests photo editing, video editing, leads, website, marketing and cold calling; "
                           "'upwork real estate' suggests virtual assistant, video editor, cold caller, photo editor, VA and transaction coordinator; 'fiverr realtor' returns nothing." % tuple(ref(u) for u in (
                               "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q=ai+for+real+estate+agents", "https://suggestqueries.google.com/complete/search?client=firefox&hl=en-GB&gl=uk&q=estate+agent+ai",
                               "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q=listing+coordinator+job+description", "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q=fiverr+real+estate",
                               "https://suggestqueries.google.com/complete/search?client=firefox&hl=en&gl=us&q=upwork+real+estate"))))
    out.append(H2("Three practical rules for targeting"))
    out += bullets([
        "US buyers find operations help by typing a product name ('follow up boss', 'kvcore', 'appfolio', 'gohighlevel') or a role name ('transaction coordinator', 'ISA', 'maintenance coordinator'), not 'real estate', which on Upwork and Fiverr returns promo videos and logos; the long 'follow up boss vs' and 'transaction coordinator fee' tails are where the comparison happens because review counts on operations gigs are thin (1 to 146 feedback).",
        "UK buyers get almost nothing when they type their own words ('estate agent', 'lettings', 'rightmove') into Upwork, PeoplePerHour or OnlineJobs.ph; the demand that exists is served under US-style titles ('property management virtual assistant') or under compliance titles invented by the small firms themselves ('Compliance &amp; Maintenance Coordinator', 'Property &amp; Tenancy Coordinator'), "
        "so a UK offer must carry the statute and form names the searcher uses ('renters rights act compliance checklist', 'material information checklist', 'section 13 notice form 4a', 'right to rent share code', 'sales progression checklist', 'aml risk assessment').",
        "'AI receptionist' is now a stable phrase on both sides while 'chatbot' phrasings barely register; the consumer-side complaint searches ('estate agent not answering calls', 'letting agent not responding to emails') describe the same gap from the other end ([Google suggest, UK](@gs_uk); [Upwork services: real estate](@upwork_svc_re)).",
    ])
    return out


# --------------------------------------------------------------------------
# Section 3
# --------------------------------------------------------------------------
def section_3(CH):
    out = chapter(3, SEC[3]["title"],
                  "In all five lines of business the firm's controllable work sits at the start (instruction, onboarding, application, contract) and the end (completion, move-in, closing, statement); "
                  "the middle is weeks of waiting on conveyancers, lenders, contractors, referencing providers, title companies and owners, during which the file must be chased, the deadline watched and the same data re-typed into the next system.")
    out.append(note_box("Step marks in the five workflow tables: <b>M</b> manual, <b>R</b> repetitive, <b>D</b> document-heavy, <b>T</b> deadline-driven. The marks are the researcher's reading of the sources, not a survey result."))
    out.append(H3("Table 3.1  UK sales (independent agency)"))
    h, r = T(3, 0)
    out.append(tbl(h, r, widths=[22, 64, 54, 36], font="cell_small"))
    out.append(H3("Table 3.2  UK lettings and management"))
    h, r = T(3, 1)
    out.append(tbl(h, r, widths=[22, 64, 54, 36], font="cell_small"))
    out.append(H3("Table 3.3  US sales and contract-to-close (small brokerage, team, solo agent)"))
    h, r = T(3, 2)
    out.append(tbl(h, r, widths=[22, 64, 54, 36], font="cell_small"))
    out.append(H3("Table 3.4  US property management (50-1,500 units)"))
    h, r = T(3, 3)
    out.append(tbl(h, r, widths=[22, 64, 54, 36], font="cell_small"))
    out.append(H3("Table 3.5  Investors and wholesalers"))
    h, r = T(3, 4)
    out.append(tbl(h, r, widths=[22, 64, 54, 36], font="cell_small"))
    out.append(H2("Two patterns across the five tables"))
    out += bullets([
        "The document-heavy steps cluster at the gates the law has added recently: Material Information before a UK listing (2022-23), the written buyer agreement before a US tour (August 2024), the written statement of terms and the information sheet under the Renters' Rights Act (May 2026), the FCC revocation rules (April 2025) and the delayed-marketing form (2025). "
        "Each is a new piece of paper that must exist before a step the firm used to take informally.",
        "The deadline-driven steps are short and state- or scheme-specific (30-day deposit protection, 28-day pet response, 14 to 60-day deposit returns, 3 to 20-day eviction notices, the 72-hour contract set-up window, the three-day Closing Disclosure rule, the 31-day DNC scrub, 31 January 1099s), which is why practitioners describe the failure not as ignorance of the rule but as "
        "'No follow-up date means it falls through the cracks' ([BiggerPockets 1302426](@bp_1302426) [user, Oct 2026]) and 'A reminder being sent is not the same as the work being completed' ([Property Industry Eye, 28 Sep 2026](@pie_fines_agents) [vendor comment]).",
    ])
    return out


# --------------------------------------------------------------------------
# Section 4
# --------------------------------------------------------------------------
def section_4(CH):
    out = chapter(4, SEC[4]["title"],
                  "Fraud is the cost line that grew fastest between 2023 and 2026, and it lands on the smallest operators because they hold the email account, the deposit and the ID copy; "
                  "the compliance penalties small UK agencies actually pay are for not registering, not for complex laundering; and in both countries the AI rules bite on the output and the records, not the tool.")
    out.append(fig_image(*CH["fraud"]))
    out.append(H2("US: wire fraud, seller impersonation, application fraud"))
    out += bullets([
        "The FBI's 'Real Estate' crime type recorded <b>12,368 complaints and $275.1m of losses in 2025</b>, up from $173.6m (2024) and $145.2m (2023), with victims over 60 losing $123.7m; business email compromise across all sectors cost $3.05bn; the new 'AI Related' tag counted 115 real estate complaints ($2.7m) and $30.3m of AI-assisted BEC; "
        "'Chat generators can quickly create official-sounding emails' ([FBI IC3 2025](@ic3_2025); [FBI IC3 2024](@ic3_2024)). The category is not just wire fraud, so the derived average of about <b>$22,200 per complaint</b> blends closing-fund theft with rental listing scams.",
        "CertifID's consumer survey: more than one in four consumers were targeted in a transaction, nearly one in 20 victimised, only 47% were warned by their real estate professional, <b>58% of victims said the fraudulent message appeared to come from their agent</b> ([Realty News Report, 6 Feb 2025](@rnr_wire) [vendor survey]); "
        "its 2026 edition: 22% of homebuyers receive fraudulent communications and 60% of title professionals say fraud is increasing ([CertifID](@certifid_sow) [vendor]).",
        "Seller impersonation moved from rare to routine: ALTA's spring 2026 study of 245 title firms found <b>59% had at least one attempt in the prior year (28% in 2024), 45% in the prior month, 23% three or more in a month</b>; one in four firms with an attempt paid a claim and 'half reported costs above $100,000'; "
        "targets were vacant land (82%), absentee-owned (72%), free-and-clear (68%) and recently deceased owners (55%); 87% saw spoofed contact information; 58% rated deepfake image or voice at least somewhat common; <b>87% of catches happened in clearance or curative review</b>, not at first contact ([ALTA 2026 study](@alta_2026); [HousingWire, 14 Sep 2026](@hw_sif)).",
        "A Maryland vacant-land sale of about $100,000 was nearly completed by someone using AI to impersonate the owner on a live remote-notarisation video; one title agent covered a $1m loss personally ([HousingWire, 10 Apr 2026](@hw_deepfake)). NAR's deed-fraud survey: 63% of association staff aware of such fraud in their market, 52% of cases on residential land, 12% on owner-occupied homes ([NAR](@nar_deed)); "
        "CertifID puts the median seller-net-proceeds loss at $343,497 and lists 'a new lead from an online portal or lead service with no prior relationship' and 'requests a remote notary or refuses an in-person closing' as red flags ([CertifID](@certifid_sif) [vendor]).",
        "Tenant application fraud: Snappt's analysis of nearly 5 million documents found <b>6.4% of US rental applications fraudulent in 2024</b> (7.9% in 2023), over 80,000 manipulated documents, methods 'fraudulent PDF creators', 'text insertion' and 'font fail' ([Multifamily Executive, 6 Feb 2025](@mfe_snappt) [vendor data, multifamily]); "
        "institutional managers say 85% have been targeted (66% pre-pandemic) and staff spend most screening time verifying bank statements (72%) and pay stubs (67%) by hand ([NAR Commercial Insights, 26 Sep 2022](@nar_ci_fraud)); 75% of property managers reported more rental fraud last year ([Buildium 2026](@buildium_2026) [vendor]).",
    ])
    out.append(H2("UK: AI-built tenant identities, rental scams, title fraud, document handling"))
    out += bullets([
        "Goodlord's million-plus references: <b>41 applications per 1,000 flagged for suspected fraud</b> (peak 46.6 in late 2024), suspected fraud up almost 40% across 2025, <b>fake employment references up 226.6%, referee fraud up 146.4%, identity manipulation up 140.4%</b>, an average direct cost of <b>£9,601 per fraudulent tenancy</b>, London at nearly double the national rate, fraudsters who 'use AI to build entire false identities' "
        "([Property Reporter, 7 Aug 2026](@pr_fraud40) [vendor data]).",
        "Rental scams reported to Action Fraud fell to 4,092 in FY2025/26 (from 4,982) while the average loss rose 46% to <b>£3,138</b> and the total to <b>£12.84m</b> ([Property Reporter, 17 Aug 2026](@pr_scams)); HM Land Registry stopped 86 fraudulent applications against more than £59m of property in 2024-25 and paid four indemnity claims totalling £398,964 ([HM Land Registry, 17 Sep 2025](@hmlr_fraud)).",
        "The documented UK breaches are about third parties and document handling: the CTS managed-service attack of November 2023 delayed sales nationally with 'no precise timeline for full restoration' ([Intelligent CIO, 27 Nov 2023](@cts)); a London letting agent was fined £80,000 after a file-transfer set-up left tenants' and landlords' bank statements, passport copies and salary details open online for about two years ([Mortgage Solutions, 22 Jul 2019](@ms_80k) [snippet]). "
        "Across UK small businesses generally, 42% identified phishing, only 17% hold a specific cyber policy and 40% use two-factor authentication ([Cyber Security Breaches Survey 2025](@csbs)).",
    ])
    out.append(H3("Table 4.1  Fraud measures"))
    h, r = T(4, 0)
    out.append(tbl(h, r, widths=[30, 70, 34, 42], font="cell_small"))
    out.append(H2("The penalties small UK agencies actually pay"))
    out += bullets([
        "HMRC's list for 1 April to 30 September 2025: <b>170 penalties on estate agency businesses totalling £835,842</b> (about £4,900 each), the largest group of any sector; <b>332 of the 369 penalties across all sectors were for trading without AML registration</b>, 'an avoidable administrative failure, not a complex due-diligence issue' ([Comsure](@comsure); [Pie Tax](@pietax) [secondary]). "
        "The June 2025 list fined 194 agents about £1.09m ([Estate Agent Today, Jun 2025](@eat_jun25) [snippet]); the October 2022 round fined 68 agents £519,645, the largest single fine (£53,400, Horton) for failing to apply for registration, plus the first prosecution of an unregistered agent ([Property Industry Eye, 12 Oct 2022](@pie_2022); [GOV.UK](@gov_crack)).",
        "HMRC's updated guidance of 8 July 2026 (Money Laundering Regulations amendments in force 30 June 2026) requires CDD on all parties, source-of-funds work that documents 'both the steps taken and the rationale for their conclusions', an 'up-to-date written risk assessment' covering money laundering, terrorist financing and proliferation financing, extra care with cash buyers, and says that with third-party ID tools "
        "'responsibility for compliance with the MLRs remains with the estate agency business' and providers not on the DVS register 'cannot be relied upon' ([Devonshires, 7 Oct 2026](@devonshires)).",
        "Propertymark's members, mostly single-branch, called the AML fee rise (premises fee £300 to £400 plus a new £400 application fee) unreasonable (92%), said 'Letting agents cannot recover compliance costs through tenant fees', and <b>96% want more prescriptive guidance, especially on 'how to identify beneficial owners' and 'sources of funds'</b> ([Propertymark, 15 Sep 2025](@pm_aml_fee)).",
        "A vendor's 415,000-plus source-of-funds checks found <b>57.7% of cases had at least one red flag, averaging two per report</b> ([Property Industry Eye, 19 Mar 2026](@pie_sof) [vendor data]); a Credas survey of 250 agents found 79% use digital ID verification but <b>64% 'still rely on manual document checks to some extent'</b>, 63% pass ID-check fees to clients, and small independents spend about £16,000 a year on compliance-related activity ([Property Reporter, 23 Jul 2025](@pr_credas) [vendor survey]). "
        "Even asking for ID before a viewing is contested: 'This has \"GDPR breach\" written all over it' ([Property Industry Eye, 12 May 2026](@pie_idview) [user, May 2026]).",
        "<b>Right to Rent</b> carries the largest single penalty an English letting agent can face: since February 2024 <b>up to £10,000 per occupier for a first breach and £20,000 for a repeat</b> (lodgers £5,000 and £10,000); agent fines in Q1 2024 alone (£165,680) exceeded the whole of 2023; checks rose 577% year on year; since October 2022 documents 'can no longer be accepted by email' ([Landlord Today, 29 May 2024](@lt_rtr); [GOV.UK penalties](@gov_rtr_pen)). "
        "The Home Office guide updated 1 October 2026 allows three routes (manual check with original documents and the holder present in person or on live video; the online service with a share code; a registered digital provider for British and Irish passport holders only), mandates registered providers for digital checks from that date, and states the landlord 'remains responsible for ensuring that the check is carried out in accordance with the prescribed requirements' ([Home Office guide, 1 Oct 2026](@ho_guide)); "
        "a certified provider 'does not remove all risk' and the cost cannot be passed to applicants under the Tenant Fees Act 2019 ([Propertymark, 14 Jul 2022](@pm_rtr_cost)).",
        "<b>The Renters' Rights Act 2025</b> (Royal Assent 27 October 2025, Phase 1 in force <b>1 May 2026</b>) rewrote the lettings calendar: every assured shorthold tenancy became periodic, no end dates, Section 21 gone, rent rises once a year on Form 4A with two months' notice, adverts must state a rent and no offer above it may be accepted, no more than one month's rent in advance, no refusal of applicants with children or on benefits, pet requests answered within 28 days, "
        "the exact GOV.UK information sheet to every tenant by 31 May 2026, and councils may fine <b>up to £7,000 for minor and £40,000 for serious or repeat breaches</b> with rent repayment orders of up to two years' rent; council investigatory powers, including 'entering a letting business without notice', started 27 December 2025; the PRS database and landlord ombudsman follow in late 2026 "
        "([GOV.UK landlord guidance](@gov_ll); [GOV.UK tenants overview](@gov_tenants); [Woking Borough Council](@woking); [Anthony Collins, 17 Dec 2025](@ac_rra)).",
        "The first enforcement case against an agent came within five months: a Chesterfield letting agent was fined £8,652 for issuing a banned six-month fixed term and telling the tenants to leave ([LandlordZONE, 2 Oct 2026](@lz_fine)). A large agency's four-month review: the one-month advance cap 'has been difficult for international students', two-month tenant notices create overlapping tenancies of 'five or six weeks', "
        "'Some tenants believe they are automatically entitled to have a pet', and 'advertised rents don't always reflect the final agreed rent' ([LandlordZONE, 25 Sep 2026](@lz_4m)); councils have warned that 'outsourcing the job doesn't automatically mean you've outsourced the risk' ([Property Industry Eye, 28 Sep 2026](@pie_fines_agents)).",
    ])
    out.append(fig_image(*CH["penalties"]))
    out.append(H3("Table 4.2  UK penalties and duties"))
    h, r = T(4, 1)
    out.append(tbl(h, r, widths=[34, 78, 22, 42], font="cell_small"))
    out.append(H2("Material Information: a legal vacuum that worries agents more than any AI rule"))
    out += bullets([
        "The Property Lawyers Alliance told the CMA that full compliance 'poses a significant burden for agents', that agents should not become 'quasi-lawyers' and that the regime is 'a fertile breeding ground for misrepresentation and other civil claims'; agents agreed that 'most will not have the legal knowledge to complete some of the Material Information' and that vendors 'have forgotten the answers to many the \"additional enquiries\"' "
        "([Property Industry Eye, 23 Jan 2025](@pie_mi_cma) [user, Jan 2025]). The government consulted on new guidance from 6 October to 29 December 2025, noting that problems such as damp or missing planning permission 'only emerge after their offer has been accepted' ([GOV.UK consultation](@gov_mi)).",
        "On AI-edited photos, National Trading Standards is reported to say deceptive edits may breach the Consumer Protection from Unfair Trading Regulations 2008 and the DMCC Act, that 'clear labelling is the bare minimum', and Rightmove removed virtually staged images from an Eaglescliffe listing even though the staging was disclosed ([The Negotiator](@negotiator_ai) [snippet]).",
        "Agents' recorded views of AI are sceptical and cost-focused: 'AI is a useful took for work, but nothing revolutionary', 'I'd much rather have competent staff than an AI tool (as would my clients)' ([Property Industry Eye, 8 Sep 2026](@pie_ai_left) [user, Sep 2026]); 'Most agents are still paying for tools and time that AI now does for free' ([Property Industry Eye, 29 May 2026](@pie_ai_free)); "
        "the one AI item Propertymark lists is a course on 'Managing AI-generated complaints' dated 2 November 2026 ([Propertymark course](@pm_course)). Alto's survey says 52% of agents plan to adopt AI within 12 months and 66% expect to rely on compliance and AML automation, with about a third nervous or unsure, most often independents ([Property Industry Eye, 16 Jan 2026](@pie_alto_ai) [vendor survey]).",
    ])
    out.append(H2("US: no single AI rule; existing law applied to AI output"))
    out += bullets([
        "NAR's March 2026 guidance lists the risks every brokerage policy should cover: hallucination ('wrong square footage or invented property features'), fair-housing drift ('who a home is \"perfect for\"'), privacy ('Entering client, financial, or transaction information into an unapproved tool could expose that data'), and the rule that AI content 'should not go straight from prompt to publication' ([NAR, 24 Mar 2026](@nar_policy)).",
        "The fair-housing checklist for AI-written remarks flags 'perfect for young professionals', 'ideal for families', 'quiet neighborhood', 'walking distance to church', 'safe' and 'exclusive', but cites no enforcement action tied to AI copy ([HousingWire, 15 May 2026](@hw_fh)); the risk is real because <b>75% of AI-using agents write listing descriptions with it</b> and 23% use AI daily ([NAR Technology Survey 2026](@nar_tech)); a thread titled 'Our house got AI-ed' drew nearly 900 upvotes ([The AI Career Lab, 5 Jul 2026](@aicareer) [secondary]).",
        "HUD's May 2024 guidance applies the Fair Housing Act to AI tenant screening and ad targeting and says providers 'may remain liable even when they have outsourced screening to a third-party screening company' ([HousingWire, 2 May 2024](@hw_hud); [Orrick, 10 May 2024](@orrick)); the SafeRent settlement (about $2.3m, final approval 20 Nov 2024) bars scores and accept-or-deny recommendations for voucher holders for five years ([Cohen Milstein](@cohen)); "
        "the RealPage litigation ended in a November 2025 DOJ settlement banning real-time competitor data, plus city and state bans on rent-setting software and more than 40 bills in 22 states ([Propmodo, 22 Feb 2026](@propmodo)).",
        "Photo rules are fragmenting by MLS and state: NorthstarMLS proposes labels plus an unaltered 'Before' image for every altered room; CRMLS requires the original next to the enhanced image, SmartMLS a watermark, MRED bans removing power lines ([NorthstarMLS](@northstar); [The Close](@close_photo) [snippet]); California AB 723 (effective 1 January 2026) requires a conspicuous disclosure and access to the unaltered original by website or QR code ([The Close, 25 Jun 2026](@close_ab723)).",
        "Calling and texting: the FCC and NAR treat AI voices including 'voice cloning' as 'artificial or prerecorded voice' under the TCPA; the Do-Not-Call registry must be checked every 31 days; consent revocations honoured within 10 business days from 11 April 2025; the one-to-one consent rule was vacated by the Eleventh Circuit on 24 January 2025 although NAR's standing page still says it 'took effect', a contradiction to check against the FCC record "
        "([NAR TCPA one-sheet, 17 Mar 2025](@nar_tcpa); [NAR telemarketing](@nar_tele); [HousingWire](@hw_fcc)); penalties run $500 to $1,500 per violation with a four-year limitation period ([BAM](@bam_tcpa) [secondary]).",
        "Colorado's SB24-205 imposes deployer duties for high-risk AI from 1 February 2026 ([Colorado General Assembly](@co_sb205)); the FTC's 2024 rule bans fake reviews 'including AI-generated ones' ([FTC](@ftc_reviews)); an E&amp;O insurer calls AI 'a grey area within most E&amp;O policies' where 'E&amp;O policies might not cover technology failures or unregulated AI tools' ([Pearl Insurance, 5 Jun 2026](@pearl)).",
    ])
    out.append(H3("Table 4.3  AI and data rules and what they require of a small firm"))
    h, r = T(4, 2)
    out.append(tbl(h, r, widths=[36, 30, 70, 40], font="cell_small"))
    out.append(H2("Three things follow"))
    out += bullets([
        "The money a small firm actually loses is in the low five figures per incident (a £3,138 rental scam, a £9,601 fraudulent tenancy, a £4,900 HMRC penalty, a £8,652 tenancy fine, $500 to $1,500 per TCPA violation) with a long tail of catastrophic single events (seller-impersonation claims over $100,000; a $6.66m BEC case in the FBI record) against insurance that costs under $1,000 a year and may exclude AI errors.",
        "Email is both the main attack channel (phishing, BEC that looks like the agent) and, for UK agents, a prohibited channel for ID documents, so the everyday workflow sits inside the biggest risk.",
        "In both countries the rules that bite are about the output and the records (the listing wording, the photo, the consent log, the written risk assessment, the adverse-action notice), which is why every AI question a small firm asks comes back to 'can we show what we did and why'.",
    ])
    return out


# ==========================================================================
# Content, part B: sections 5 to 8
# ==========================================================================
U.update({
    "letsafe": "https://letsafeuk.co.uk/tenant-reference-check-uk",
    "davidson": "https://www.davidsonmorris.com/right-to-rent-share-code/",
    "nrla_ref": "https://www.nrla.org.uk/services/tenant-referencing",
    "goodlord_vouch": "https://www.goodlord.com/letting-agent-solutions/tenant-referencing-vouch",
    "canopy_price": "https://www.canopy.rent/pricing",
    "canopy_agents": "https://www.canopy.rent/agents",
    "homelet": "https://homelet.co.uk/letting-agents/tenant-referencing",
    "ll_studio": "https://www.landlordstudio.com/uk-blog/rent-in-advance-rules-renters-rights-act",
    "baker": "https://www.bakermckenzie.com/en/insight/publications/2026/01/united-kingdom-renters-rights-act-2025",
    "ofsi": "https://www.gov.uk/government/publications/financial-sanctions-guidance-for-letting-agents/financial-sanctions-guidance-for-letting-agents",
    "tp_goodlord": "https://uk.trustpilot.com/review/goodlord.co",
    "tp_canopy": "https://uk.trustpilot.com/review/canopy.rent",
    "tp_homeppl": "https://uk.trustpilot.com/review/homeppl.com",
    "pm_pof": "https://www.propertymark.co.uk/professional-standards/consumer-guides/buying-selling-houses/aml-proof-of-funds.html",
    "pg81": "https://www.gov.uk/government/publications/encouraging-the-use-of-digital-technology-in-identity-verification-pg81/practice-guide-81-encouraging-the-use-of-digital-technology-in-identity-verification",
    "id1": "https://assets.publishing.service.gov.uk/media/698c6c10048fe5f7c6475fe3/ID1__2026-02-16_.pdf",
    "thirdfort": "https://www.thirdfort.com/estate-agents/",
    "thirdfort_price": "https://www.thirdfort.com/pricing/",
    "thirdfort_sup": "https://support.thirdfort.com/hc/en-gb/articles/28359965339805-Can-I-pass-on-the-cost-of-a-Thirdfort-check-to-a-Client",
    "credas": "https://credas.com/pricing/",
    "alto_aml": "https://support.altosoftware.co.uk/hc/en-gb/articles/5048081601055",
    "tp_thirdfort": "https://uk.trustpilot.com/review/thirdfort.com",
    "tp_credas": "https://uk.trustpilot.com/review/credas.co.uk",
    "tp_smartsearch": "https://uk.trustpilot.com/review/smartsearch.com",
    "gov_fraud": "https://www.gov.uk/protect-land-property-from-fraud",
    "gov_alert": "https://www.gov.uk/guidance/property-alert",
    "forsters": "https://www.forsters.co.uk/p/102h9ty/is-the-seller-who-you-think-they-are",
    "ftc_ll": "https://www.ftc.gov/business-guidance/resources/using-consumer-reports-what-landlords-need-know",
    "smartmove": "https://www.mysmartmove.com/pricing",
    "rentspree": "https://www.rentspree.com/pricing",
    "buildium_scr": "https://www.buildium.com/features/tenant-screening/",
    "doorloop_zrm": "https://www.doorloop.com/blog/zillow-rental-manager-review",
    "plaid": "https://plaid.com/check/income/",
    "twn": "https://theworknumber.com/",
    "snappt_price": "https://snappt.com/pricing/",
    "findigs": "https://www.findigs.com/pricing",
    "snappt_jan": "https://snappt.com/?p=134",
    "tenantcloud_fees": "https://www.tenantcloud.com/tenant-screening/state-by-state-guide-on-application-fees",
    "turbotenant_fcra": "https://www.turbotenant.com/rental-screening/fcra-background-check/",
    "signal": "https://www.signalrents.com/",
    "continental": "https://continentalrealtyteam.com/",
    "nar_wire": "https://www.nar.realtor/wire-fraud",
    "fnf": "https://nationalagency.fnf.com/getmedia/e53922cc-3250-4c16-a303-8c8e506d69e7/FNF-WiringInstructions-Flyer-2026-(1).pdf",
    "alta_wire": "https://www.alta.org/business-tools/wire-fraud",
    "certifid_price": "https://www.certifid.com/pricing",
    "qualia": "https://www.qualia.com/shield/",
    "co_dre": "https://dre.colorado.gov/sites/dre/files/documents/Closing%20Instructions%20%20CLEAN.pdf",
    "whito": "https://whito.co.uk/letting-agents/tools/best-software-for-uk-letting-agents/",
    "zap_fub": "https://zapier.com/apps/follow-up-boss/integrations",
    "zap_doorloop": "https://zapier.com/apps/doorloop/integrations",
    "zap_appfolio": "https://zapier.com/apps/appfolio/integrations",
    "appfolio_price": "https://www.appfolio.com/pricing",
    "buildium_price": "https://www.buildium.com/pricing/",
    "propertyware": "https://www.propertyware.com/pricing/",
    "kerfuffle_agentos": "https://www.kerfuffle.com/suppliers/agentos",
    "superb": "https://superb.digital/estate-agents/our-top-10-estate-agent-crms/",
    "hw_ai2026": "https://www.housingwire.com/articles/realtors-ai-use-2026/",
    "nar_tech_pdf": "https://cms.nar.realtor/sites/default/files/2025-09/2025-realtors-technology-survey-report-09-18-2025.pdf",
    "tb_2025": "https://www.totalbrokerage.com/blog/brokerage-technology-strategy-2025-survey-roadmap",
    "tb_2024": "https://www.totalbrokerage.com/blog/brokerage-technology-cost-per-agent-2024-benchmark",
    "beepic": "https://beepicllc.com/crm-management-for-realtors-why-your-va-should-own-your-pipeline/",
    "tomba": "https://tomba.io/blog/follow-up-boss-pricing-reviews-pros-and-cons",
    "protoolkit": "https://theprotoolkit.com/follow-up-boss-review-2026/",
    "wpm": "https://www.wpmaccounting.com/post/appfolio-trust-account-reconciliation-common-errors-and-how-to-prevent-them",
    "capterra_bt": "https://www.capterra.com/p/176447/BoldTrail/reviews/",
    "sa_lofty": "https://www.softwareadvice.com/crm/chime-profile/reviews/",
    "tp_alto": "https://uk.trustpilot.com/review/altosoftware.co.uk",
    "cb_buildium": "https://www.complaintsboard.com/buildium-b165135",
    "tp_arthur": "https://uk.trustpilot.com/review/arthuronline.co.uk",
    "ojo": "https://ojobookkeeping.com/appfolio-bookkeeping/",
    "afb": "https://www.appfoliobookkeeping.com/",
    "pmb": "https://www.pmbookkeeper.com/",
    "bas": "https://www.balancedassetsolutions.com/services/appfolio-consulting/",
    "wpm_svc": "https://www.wpmaccounting.com/appfolio-accounting-services",
    "upwork_af_ca": "https://www.upwork.com/hire/appfolio-freelancers/california-us/",
    "upwork_af": "https://www.upwork.com/hire/appfolio-freelancers/",
    "fiverr_fub2": "https://block.fiverr.com/gigs/follow-up-boss?page=2",
    "aitb": "https://aitoolsbakery.com/blog/boldtrail-pricing-2026/",
    "reapit_au": "https://www.reapit.com.au/services/training",
    "pm_sme": "https://www.propertymark.co.uk/membership/industry-suppliers/sme-professional.html",
    "kerfuffle_street": "https://www.kerfuffle.com/suppliers/street",
    "fixflo_price": "https://www.fixflo.com/pricing",
    "esre": "https://esremedia.co.uk/blog/estate-agent-crm-software-uk",
    "icloudready": "https://www.icloud-ready.com/blog/pipeline-visibility-real-estate-crm",
    "bbb_lofty": "https://www.bbb.org/us/az/phoenix/profile/sales-lead-generation/lofty-1126-1000129313/customer-reviews",
    "tp_reapit": "https://uk.trustpilot.com/review/reapit.com",
    "tp_fixflo": "https://uk.trustpilot.com/review/www.fixflo.com",
    "wpm_bank": "https://www.wpmaccounting.com/post/appfolio-bank-reconciliation-common-errors-property-managers-should-check",
    "capterra_rg": "https://www.capterra.co.nz/software/1002952/real-geeks",
    "sc_appfolio": "https://softwareconnect.com/reviews/appfolio/",
    "close_fub": "https://theclose.com/follow-up-boss-review/",
    "realatic": "https://realatic.com/blog/real-estate-crm-weekly-sales-review-india",
})


def section_5(CH):
    out = chapter(5, SEC[5]["title"],
                  "Once the verification steps are separated into three layers the answer is the same in both countries: the data pulls are automated, priced as a commodity and returned in minutes; "
                  "the residue the vendors themselves label 'manual' takes 24 to 72 hours or weeks; and the law pins the decision and the liability to a named person who cannot delegate it to a tool.")
    out.append(fig_image(*CH["lettings_flow"]))
    out.append(H2("The three layers"))
    out += bullets([
        "<b>Layer one, automated</b>: credit history, document authenticity, open-banking or payroll income, PEP and sanctions lists, US criminal and eviction records; priced as a commodity, returned in minutes or the same day.",
        "<b>Layer two, the manual residue</b>: employer and previous-landlord references, document re-requests when the automated check fails, source-of-funds reasoning, the phone call to confirm a wire instruction or a seller's intent; where the 24-to-72-hour turnarounds and the week-long delays come from.",
        "<b>Layer three, fixed by law or consent</b>: a named person must hold the original documents, make the decision, give the notice and carry the penalty.",
    ])
    out.append(H2("UK letting agent: consent, Right to Rent, referencing"))
    out += bullets([
        "The sequence starts with a privacy notice and consent, because 'running a credit check without consent is a data protection breach' ([LetSafe UK](@letsafe)), then Right to Rent on every adult who will live there.",
        "Home Office guide, 1 October 2026, three routes: a manual check where documents are seen 'in the presence of the holder, either in person or by live video call' and the checker is 'in physical possession of the original documents'; the GOV.UK online service using a nine-character share code beginning with R, valid 90 days, with the date of birth; or a registered digital provider, limited to British and Irish passport holders. "
        "eVisa-only holders must be checked online; time-limited permission checked no earlier than 28 days before the tenancy and re-checked before the statutory excuse expires; records kept for the tenancy plus a year; the Landlord Checking Service answers within two working days; the written agent agreement must say whether it covers initial checks, follow-up checks or both ([Home Office guide, 1 Oct 2026](@ho_guide)).",
        "Share-code failures seen in practice: tenants using a right-to-work code, expired codes, name or date-of-birth mismatches, lost access to the Home Office account; landlords 'should not automatically refuse or delay the tenancy' on a failed code ([Davidson Morris, 1 Apr 2026](@davidson)).",
        "Referencing packages: NRLA's Goodlord-powered service checks 'credit, residential history, identification, and income and affordability' with free PEP and sanctions screening for <b>£23.40 to £40.20 per reference</b>, returned 'in about 26 hours on average, and one in three is completed instantly' ([NRLA](@nrla_ref)); Goodlord's own tiers add open banking, HMRC and payroll income and claim 30% instant, 70% within 24 hours and 90% within 72 hours against 'a typical industry timeframe of two to five working days' ([Goodlord/Vouch](@goodlord_vouch) [vendor]); "
        "Canopy charges <b>£5 plus VAT per reference</b>, averages 1.75 days, and labels 'manual verification of current employment and rental history' as a distinct step ([Canopy pricing](@canopy_price); [Canopy for agents](@canopy_agents) [vendor]); HomeLet claims over 70% within 24 hours, with the National Fraud Database, sold only through agents with no public price ([HomeLet](@homelet) [vendor]).",
        "Affordability rule of thumb: rent no more than 33 to 40% of gross income, three months of payslips and statements, two years of accounts for the self-employed, a previous (not current) landlord reference, outcomes 'recommended', 'referred' or 'declined'; a guarantor must be a UK homeowner earning three times the annual rent, referenced as fully as the tenant, on a written agreement signed before the tenancy because 'a verbal guarantee is not enforceable' ([LetSafe UK](@letsafe)).",
        "Since 1 May 2026 no more than one month's rent may be taken before signing and nothing until every party has signed, which removes the old 'six months up front' workaround for a failed reference ([Landlord Studio](@ll_studio); [Baker McKenzie, Jan 2026](@baker)); from 14 May 2025 agents must report to OFSI when they know or suspect a tenant or landlord is sanctioned ([OFSI guidance](@ofsi)).",
        "Where the automation breaks, in reviews: Goodlord's 'automated referencing software is deeply flawed' and 'failed every category' despite open-banking data, a landlord 'would like to recall and change my reference but no option to do so', a guarantor's 'AI bot just keeps asking me over and over to upload my documents' ([Trustpilot, Goodlord](@tp_goodlord) [user, Aug-Oct 2026]); "
        "Canopy returned '5 to 6 days of requests for more documents, some two years old' after open banking was submitted ([Trustpilot, Canopy](@tp_canopy) [user, 21 Sep 2026]); Homeppl 'took 4 weeks to do our referencing' and asked for the same document four times ([Trustpilot, Homeppl](@tp_homeppl) [user, Aug-Sep 2026]).",
    ])
    out.append(H2("UK estate agent: the same buyer checked three times"))
    out += bullets([
        "The seller is registered as a customer at instruction (ID, address, beneficial ownership, title) and the buyer at offer. Propertymark tells buyers 'you don't have to provide proof of funds before putting an offer in', lists acceptable proof of name (passport, residence permit, photo licence, HMRC notice) and address (council tax bill, bank statement, non-mobile utility bill), lists sources of funds (mortgage in principle, statements showing the deposit, older statements showing savings building up, evidence of a property sale, gift letter, inheritance, share-sale receipts), "
        "and warns that 'the mortgage lender and solicitor or conveyancer will also ask where the money came from' ([Propertymark proof of funds](@pm_pof)).",
        "The duplication is structural: HMRC says reliance on a third party does not reduce the agency's responsibility; Land Registry Practice Guide 81 covers only the conveyancer's own digital check (NFC chip read with signature verification; 'a photo of the document or MRZ does not meet the requirement'; biometric liveness with a false-match rate of at most 0.01%) and offers no reliance on an estate agent's check; "
        "form ID1 'must be verified by a conveyancer', 'A paralegal cannot verify identity', within three months of lodgement ([HMLR Practice Guide 81](@pg81); [HMLR ID1](@id1)).",
        "Tools sold to agents: Thirdfort (NFC ID, PEP and sanctions, source of funds from bank statements, address checks, lettings sanctions screening; 'over 1,500 regulated firms'; remote ID averages '17 hours'; monthly platform fee plus credits on 12-month contracts; recommended client recharges of £30 for an ID check, £15 for source of funds, £5 for lite screening) ([Thirdfort](@thirdfort); [Thirdfort pricing](@thirdfort_price) [vendor]; [Thirdfort support](@thirdfort_sup) [snippet]); "
        "Credas (ID, AML, Right to Rent, source of funds, KYB; tiered, unpriced) ([Credas](@credas) [vendor]); SmartSearch; Alto's built-in AML at £4.50 pay-as-you-go or £7 plus VAT ([Alto support](@alto_aml) [snippet]).",
        "Their reviews complain about the capture step rather than the data: Thirdfort 'app crashes on older phones', camera 'failed to work first 2 times', the same details re-entered per transaction, 'they can access my account anytime they want' on open banking ([Trustpilot, Thirdfort](@tp_thirdfort) [user, Oct 2026]); Credas has 32% one-star reviews for crashes, timeouts and 'every time there was an issue I was taken back to the beginning' ([Trustpilot, Credas](@tp_credas) [user, 18 Sep 2026]); "
        "SmartSearch has 55% one-star reviews on a three-year contract lock-in and about £1,200 exit fees ([Trustpilot, SmartSearch](@tp_smartsearch) [user]).",
        "Seller identity is protected mainly by the owner: HM Land Registry's free Property Alert covers ten properties but 'won't automatically stop fraud'; a restriction (form RX1 at £40 if living there, RQ free if not) stops a sale registering unless a conveyancer certifies the applicant ([GOV.UK property fraud](@gov_fraud); [GOV.UK Property Alert](@gov_alert)); "
        "conveyancers' red flags for an impersonated seller: a vacant property, a seller address different from the searches, email-only remote clients, recently issued ID and quick cash sales ([Forsters](@forsters) [snippet]).",
    ])
    out.append(H2("US property manager: the FCRA frame"))
    out += bullets([
        "The landlord must certify to the consumer reporting agency that the report is for housing; any adverse action (denial, co-signer, larger deposit, higher rent) requires a notice naming the agency, stating that the agency did not make the decision and 'can't give specific reasons for it', and giving the right to dispute and to a free report within 60 days; required 'even if the report played only a small part'; reports must be securely destroyed ([FTC, Using Consumer Reports](@ftc_ll)).",
        "The report is commoditised and same-day: TransUnion SmartMove $25 to $49 ('Most reports delivered same day after the applicant verifies their identity'; 'Choose who pays (where permitted)') ([SmartMove pricing](@smartmove) [vendor]); RentSpree $39.99 or $49.99 with bank-verified income and reference checks, landlord free ([RentSpree pricing](@rentspree) [vendor]); "
        "Buildium $17 landlord-paid, $35 applicant-paid, 'typically generated within 24 hours', income verification excluded so landlords 'verify employment themselves' ([Buildium screening](@buildium_scr) [vendor]); Zillow $29 per applicant ([DoorLoop review, 2 Jun 2026](@doorloop_zrm) [secondary]).",
        "Income is the slow part: Plaid's bank-linked income, The Work Number's 839 million payroll records (credentialed verifiers with a permissible purpose only) and Snappt's and Findigs' document forensics sell on quotes and integrate with Yardi, RealPage and Entrata, not with Buildium or AppFolio-sized tools ([Plaid](@plaid); [The Work Number](@twn); [Snappt pricing](@snappt_price); [Findigs](@findigs) [vendor]). "
        "Snappt's own advice is to pair its tool with manual steps: two months of pay stubs or statements, pay-stub dates matched to deposit dates, employer calls 'using a number found independently rather than the one on the application' ([Snappt, 6 Jan 2026](@snappt_jan) [vendor]).",
        "State law shapes the gate: application fees capped at $20 in New York, $50 in New Jersey from 1 May 2026, actual cost in California, Colorado and Washington, banned in Vermont and for Massachusetts landlords; Colorado, Illinois and New York require acceptance of a reusable report; Cook County, Seattle and D.C. restrict criminal-history questions; California bars eviction records over seven years ([TenantCloud](@tenantcloud_fees); [TurboTenant](@turbotenant_fcra) [secondary]).",
        "In a lower-tech city: a Birmingham manager requires applicants to view before approval, routes applications through an outside agency taking 'up to 7 business days', and asks for a driver's licence, Social Security card and the last four pay stubs 'as a PDF file, as screenshots are usually illegible' ([Signal PM](@signal)); another issues a Word application and takes 'a minimum of 48 hours' ([Continental Realty Management](@continental)).",
    ])
    out.append(H2("US brokerage: wires are a title-company function; the agent warns and calls"))
    out += bullets([
        "NAR's rule: 'Never send wire instructions (or any personal or financial information) via e-mail'; confirm by phone 'using a number you obtained independently'; some brokers require a signed wire-fraud disclosure; if fraud happens, call the bank and file with IC3 within 24 to 72 hours ([NAR wire fraud](@nar_wire)). "
        "Title underwriters add a second person: 'Have a second person review and require a secondary signer for outgoing wires' ([FNF 2026 flyer](@fnf) [snippet]); ALTA's Outgoing Wire Preparation Checklist has three sections (identify the source of instructions; verify instructions received by email or from anyone other than the payee; verify delivery) ([ALTA wire fraud](@alta_wire)).",
        "Title firms now use about five tools (device analytics, biometrics, government-ID database checks, live facial match, direct seller contact with multi-factor authentication) and rate 'direct seller contact and multifactor authentication' the most effective; one practical check is mailing a letter to the property address; 'One of the biggest red flags is somebody who never wants to get on the phone' ([HousingWire, 14 Sep 2026](@hw_sif)).",
        "The automated products are sold to title agents, not brokerages: CertifID (identity, business and payoff verification, insured wires, earnest-money payment; integrations with SoftPro, Resware, RamQuest; no price; zero Trustpilot reviews) ([CertifID pricing](@certifid_price) [vendor]); Qualia Shield (risk score when wire instructions are entered; '$2 million in coverage, backed by Lloyd's of London' for wires rated low risk only; sellers connect a bank through Stripe) ([Qualia Shield](@qualia) [vendor]); "
        "FNF's ionFraud with an account-verification module added 10 September 2026 ([ALTA](@alta_wire)). The insurance covers only what the model rates low risk, so the call-back still decides the risky cases; 87% of impersonation catches happen in curative review.",
        "Earnest money is verified by the closing company before any release (Colorado closing instructions) ([Colorado DRE](@co_dre) [snippet]); no primary source was found on how a listing agent verifies a lender pre-approval or proof-of-funds letter.",
    ])
    out.append(H3("Table 5.1  Verification steps: automated today, manual residue, what the law keeps human"))
    h, r = T(5, 0)
    out.append(tbl(h, r, widths=[22, 40, 36, 46, 32], font="cell_small"))
    out.append(note_box("<b>The pattern:</b> the automatable layer is evidence collection and database matching; the non-delegable layer is a named human accountable for the decision and its records (landlord or agent for Right to Rent, nominated officer for AML, conveyancer for ID1, landlord for the FCRA notice), "
                        "a consent gate the applicant controls (credit consent, open-banking consent, share-code generation), and an out-of-band confirmation (a phone call to an employer, a seller or a title company on a number the firm already knew). "
                        "Software for a small firm therefore has to produce the audit trail, the exception list and the notices, not the decision. Reviews put the pain in case handling: 'rigid automated fails that a human cannot override', the same document requested four times, applicants stuck at the camera, the NFC chip or the open-banking consent screen.", warm=True))
    return out


def section_6(CH):
    out = chapter(6, SEC[6]["title"],
                  "Fifteen named systems split into three groups with one shared shape: price-opaque or fee-stacked, integration gated to the top tier, and alert-only on compliance. "
                  "None sells independent validation after go-live; the one priced audit market (AppFolio trust accounting) exists because the systems let a bank reconciliation pass while owner statements are wrong.")
    out += bullets([
        "A US sales CRM group (Follow Up Boss, kvCORE/BoldTrail, Lofty, BoomTown): per-seat priced with paid add-ons or quote-gated with annual terms and ad-management percentages.",
        "A US property-management group (AppFolio, Buildium, Rent Manager, DoorLoop): the list price is only the start of a fee stack and integration is gated to the top tier.",
        "A UK agency and lettings group (Reapit, Alto, Street, Goodlord, Fixflo, Arthur, PayProp): a review of 27 vendors found only 9 publish a pound price, and lettings software is 'below that average' ([Whito, 4 Sep 2026](@whito) [secondary]).",
    ])
    out.append(fig_image(*CH["platforms"]))
    h, r = T(6, 0)
    parts = split_cols(h, r, [[1, 2, 3], [4, 5, 6]])
    out.append(H3("Table 6.1  Platforms, part 1: published price, automation surface, reporting and alerts"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[26, 56, 46, 48], font="cell_small"))
    out.append(H3("Table 6.1  Platforms, part 2: compliance tracking, documented limits, sources"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[26, 38, 68, 44], font="cell_small"))
    out.append(H2("The Zapier count is the quickest proxy for what a consultant can automate"))
    out += bullets([
        "Follow Up Boss (22) and DoorLoop Premium (36) are automatable; Lofty (12) and BoomTown (10, mostly read triggers) partly; kvCORE (4), Fixflo (4), Sierra Interactive (2), Real Geeks (2) and dotloop (2) barely; AppFolio, Buildium, Rent Manager, TenantCloud, SkySlope and Reapit return no Zapier app at the expected address ([Zapier FUB](@zap_fub); [Zapier DoorLoop](@zap_doorloop); [Zapier AppFolio, 404](@zap_appfolio)).",
        "API access is tier-gated on AppFolio (read-only Plus, read and write Max), Buildium (Premium), DoorLoop (Premium) and Propertyware ('Add $1 per unit/month') ([AppFolio pricing](@appfolio_price); [Buildium pricing](@buildium_price); [Propertyware pricing](@propertyware) [vendor]). For a small US manager on AppFolio Core or Buildium Essential, automation beyond native features is spreadsheets, VAs and bookkeepers; "
        "in the UK, Reapit's Foundations and agentOS's open API are the two integration platforms and the rest rely on vendor-chosen partners ([Kerfuffle agentOS](@kerfuffle_agentos); [Superb Digital](@superb) [secondary]).",
    ])
    out.append(H2("Underuse and misconfiguration, documented from three directions"))
    out += bullets([
        "The adoption base rate is low: <b>46% of Realtors use a CRM at all</b>, only 23% call it their top source of quality leads, 36% have the CRM paid for by a brokerage they did not choose it through, and the barriers are 'learning curve' (63%) and 'cost' (59%) ([HousingWire, 2026](@hw_ai2026); [NAR 2025 Technology Survey PDF](@nar_tech_pdf)). "
        "Brokerage leaders say about 40% of their firms have technology adoption below 50%, about 30% say their technology 'just checks a box', CRM satisfaction fell from about 3.7 to 3.2 stars, 55% train in-house and 10% give no training ([TotalBrokerage 2025](@tb_2025); [TotalBrokerage 2024](@tb_2024) [vendor survey, 100+ leaders]).",
        "The consultants who sell around the CRMs describe the decay: 'keeping a CRM current is nobody's dedicated job', leads 'sit untagged, follow-ups get missed, and notes go unlogged', 'Once agents stop trusting the system, they use it even less', the CRM becomes 'an expensive, outdated contact list' ([Be Epic Assistant, 22 Jul 2026](@beepic) [vendor]); 'Importing a messy database is where teams lose weeks' of 'duplicate records, dead email addresses, and missing phone numbers' ([Tomba, Aug 2026](@tomba) [secondary]); "
        "value 'depends on clean sources, tags, routing, and reporting' and 'a CRM only helps if the team actually follows the workflow' ([The Pro Toolkit, Jul 2026](@protoolkit) [secondary]).",
        "On the accounting side an AppFolio bookkeeping firm lists the errors it is paid to find: duplicate transaction entries from imports plus manual entry, missing deposits, incorrect owner distributions, misclassified security deposits, unrecorded bank fees and unresolved timing differences; 'a $3,200 vendor payment entered against the wrong property' leaves the bank reconciled while 'The owner statements can therefore be incorrect even though the bank account appears reconciled'; "
        "'Many property managers discover trust account issues only after an owner questions a statement' ([WPM Accounting](@wpm)).",
        "Users confirm the 'configured but not working' pattern across vendors: BoldTrail campaigns and IDX, Lofty campaign emails, Follow Up Boss tags, Alto portal leads after migration, Buildium auto-reconciliation after renewal, Arthur's Xero sync ([Capterra BoldTrail](@capterra_bt) [snippet]; [Software Advice Lofty](@sa_lofty) [snippet]; [Trustpilot Alto](@tp_alto) [user, 2026]; [ComplaintsBoard Buildium](@cb_buildium); [Trustpilot Arthur](@tp_arthur) [user, Jan 2026]).",
    ])
    out.append(H2("The consultant market is mature and priced in exactly one place"))
    out += bullets([
        "AppFolio and Buildium trust accounting is sold by OJO Bookkeeping at <b>$34 an hour ongoing, $45 an hour for 'cleanup and corrective work', $300 a month minimum</b>, aimed at 50-plus units and opened with a free 'AppFolio Health Check' for 'Misposted invoices', 'Unapplied tenant credits', 'Trust accounts that drift out of balance', 'Skipped monthly trust reconciliations' and 'Owner statements that don't match the bank balance' ([OJO Bookkeeping](@ojo)); "
        "by appfoliobookkeeping.com per active unit per month on a custom proposal ([appfoliobookkeeping.com](@afb)); by PM Bookkeeper on a flat monthly quote with forecasts at 500 and 1,000 units after an initial audit ('Before we touch anything, we review the current state of your books') ([PM Bookkeeper](@pmb)); and by Balanced Asset Solutions and WPM as setup, 'regular system audits', cleanup and migration on flat-fee proposals ([Balanced Asset Solutions](@bas); [WPM services](@wpm_svc)).",
        "Upwork lists US AppFolio consultants at <b>$30 to $75 an hour</b> (a California property-management consultant at $55, a bookkeeper at $75, a QuickBooks bookkeeper at $30) and offshore freelancers 'around $10/hour' offering 'historical cleanup'; buyer posts offer $25 an hour for a part-time AppFolio bookkeeper and $1,300 to $1,500 a month for multi-entity bookkeeping ([Upwork AppFolio California](@upwork_af_ca); [Upwork AppFolio](@upwork_af) [snippet]).",
        "The CRM side is a commodity gig market: Fiverr sells 'expertly setup real estate crm lofty, follow up boss, kvcore, idx website chime' from <b>$15</b>, Follow Up Boss and kvCORE set-ups from $10 and $20, Zapier automation from $25, Make and n8n from $35, with the Follow Up Boss tag running to at least 19 pages ([Fiverr FUB gigs](@fiverr_fub2) [snippet]); VA firms sell a 'cleanup pass, then ongoing maintenance' with no published rates ([Be Epic](@beepic) [vendor]); "
        "third-party estimates put BoldTrail setup at about $999 and implementation at $1,000 to $5,000 ([AI Tools Bakery](@aitb) [secondary]).",
        "In the UK no independent consultant market around Reapit, Alto, Street or Jupix was found; training and onboarding are vendor-delivered (Reapit runs 'over 50 classroom training sessions every month' in Australia) or discounted through trade bodies (Propertymark members get 25% off SME Professional's onboarding; Kerfuffle members get £500 waived from Street's set-up fee); the exception is Fixflo selling its own professional services at £300 plus VAT each "
        "([Reapit AU training](@reapit_au) [vendor]; [Propertymark SME Professional](@pm_sme); [Kerfuffle Street](@kerfuffle_street); [Fixflo pricing](@fixflo_price) [vendor]). A UK consultancy's rule of thumb is '£100 to £500 per branch per month, plus setup and migration fees' and 'Training usually slows an office for 2 to 4 weeks' ([ESRE Media, 30 Jul 2026](@esre) [secondary]).",
    ])
    out.append(H3("Table 6.2  Vendor-side set-up fees (the anchor a consultant's quote is compared with)"))
    h, r = T(6, 1)
    out.append(tbl(h, r, widths=[46, 82, 48], font="cell_small"))
    out.append(H3("Table 6.3  Real monthly cost, 2025-26 (researcher's arithmetic from the cited price pages)"))
    h, r = T(6, 2)
    out.append(tbl(h, r, widths=[40, 92, 44], font="cell_small"))
    out.append(note_box("<b>The audit angle:</b> set-up is already a paid line item at every vendor, and the 'configured but not working' complaints are all failures a periodic check would have caught before a customer did: a campaign that never fired, a portal feed that stopped after migration, an owner statement that does not tie to the bank, a certificate date that was alerted but never actioned. "
                        "No vendor in scope documents an error or misconfiguration rate, publishes a utilisation statistic (seats active, leads with no follow-up), or sells independent validation after go-live; the AppFolio bookkeeping niche, with its hourly and per-unit prices and free health check, is the proof that this is paid for when someone offers it.", warm=True))
    return out


def section_7(CH):
    out = chapter(7, SEC[7]["title"],
                  "Across US sales, US property management and UK sales and lettings, what gets dropped between stages is the same four items: context (the history stays in one person's inbox, voicemail or phone), timing ('No follow-up date means it falls through the cracks'), "
                  "money mapping (a payment posted to the wrong ledger or property), and compliance dates (tracked by alert rather than by a workflow with an owner and a completion check).")
    out += bullets([
        "The strongest quantified evidence is UK fall-through (23 to 30% of agreed sales) and the fact that fewer than half of Realtors use a CRM; the rest is practitioner and consultant testimony ([BiggerPockets 1302426](@bp_1302426) [user, Oct 2026]; [iCloudReady, 2 May 2026](@icloudready) [vendor]).",
    ])
    h, r = T(7, 0)
    parts = split_cols(h, r, [[1, 2], [3, 4, 5]])
    out.append(H3("Table 7.1  Seven handoffs, part 1: what gets dropped, in practitioners' words, and the numbers"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[26, 94, 56], font="cell_small"))
    out.append(H3("Table 7.1  Seven handoffs, part 2: what vendors claim to catch, what reviews confirm, sources"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[24, 50, 56, 46], font="cell_small"))
    out.append(H2("Three handoffs where vendor claims sit furthest from what reviews confirm"))
    out += bullets([
        "In US sales the handoff products say they catch is contract-to-close (Lone Wolf's 'carries over when a deal falls through'), while lead-to-appointment is claimed by every CRM through action plans and practitioners say the failure is adoption: 'logging is optional', 'nobody's dedicated job', and the follow-up stops at two touches.",
        "In UK lettings the compliance-renewal cycle is about to get heavier (PRS database, ombudsman, Awaab's Law timescales, written terms), and the two best-known CRMs are described, by a rival's sponsored comparison, as alert-only; the clearest near-term unmet need, but it needs non-sponsored confirmation.",
        "In both countries the maintenance ticket is the handoff where the software stops at the edge of its own screen: Fixflo, Property Meld and the AppFolio portal log the request, but who triages it, who approves it, who confirms the job is done and who tells the tenant the next step are, by the vendors' own replies, the agent's problem.",
    ])
    return out


def section_8(CH):
    out = chapter(8, SEC[8]["title"],
                  "The dated user quotes below are the only first-person evidence the researchers could reach, because Reddit, Facebook groups and most of G2 and Capterra were blocked; where a Capterra or G2 line appears it came from a search snippet. "
                  "The comparison is organised by the choice a small firm actually faces inside each group, and ends with the seven gaps all fifteen platforms share.")
    h, r = T(8, 0)
    parts = split_cols(h, r, [[1, 2, 3], [4, 5]])
    out.append(H3("Table 8.1  Platforms, part 1: rating and base, praise (dated), complaint (dated)"))
    out.append(tbl(parts[0][0], parts[0][1], widths=[22, 32, 46, 76], font="cell_small"))
    out.append(H3("Table 8.1  Platforms, part 2: what it does not do, sources"))
    out.append(tbl(parts[1][0], parts[1][1], widths=[24, 76, 76], font="cell_small"))
    out.append(H2("Seven gaps recur across all three groups"))
    out += bullets([
        "<b>Price opacity and contract lock-in</b>: AppFolio, Rent Manager, BoldTrail, Lofty, BoomTown, Reapit, Alto, Jupix, Goodlord and SME Professional publish no price; the vendors with the most one-star complaints about contracts (Reapit, Fixflo, Lofty, BoomTown) run 12-month to three-year terms with auto-renewal ([BBB Lofty](@bbb_lofty); [Trustpilot Reapit](@tp_reapit); [Trustpilot Fixflo](@tp_fixflo) [user, 2026]).",
        "<b>Post-setup validation</b>: nobody checks that routing fires, campaigns send, feeds deliver, statements tie out and compliance dates are complete; every 'configured but not working' review is a failure a periodic audit would have caught.",
        "<b>Dirty data on import</b>: duplicates and dead emails in Follow Up Boss, duplicate imports and misposting in AppFolio, 'corrupted data records' in Reapit, 'fake' leads in Real Geeks; pre-migration cleanup is the one step every source treats as the time sink and none of the vendors prices ([Tomba](@tomba) [secondary]; [WPM](@wpm_bank); [Capterra NZ Real Geeks](@capterra_rg) [snippet]).",
        "<b>Tier-gated integration</b>: AppFolio, Buildium, DoorLoop and Propertyware put the API behind the top tier or a per-unit surcharge, so the firms small enough to need help cannot connect anything.",
        "<b>A reporting ceiling</b> at standard dashboards, named by users for Sierra, Street, Fixflo, Yardi Breeze, Propertyware, Jupix and AppFolio.",
        "<b>Compliance tracked as alerts rather than workflows</b> (Reapit and Street certificate handling, Arthur's outdated templates, AppFolio's unreadable insurance uploads) at the moment the UK has added the heaviest statutory calendar in a generation.",
        "<b>Support that is ticket-only or 'by appointment' at the tiers small firms buy</b> (Buildium Essential, AppFolio, Arthur, Follow Up Boss without live chat, Sierra by ticket and business hours) ([Buildium pricing](@buildium_price); [Software Connect AppFolio](@sc_appfolio) [secondary]; [The Close](@close_fub) [secondary]).",
        "The phrases 'we only use it as an address book', 'leads go into a black hole' and 'nobody updates the pipeline' were not found verbatim in any reachable source; the closest practitioner language is 'an expensive, outdated contact list' ([Be Epic](@beepic) [vendor]) and 'if every agent updates their CRM only when the team leader asks, the data is always stale' ([Realatic](@realatic) [secondary, India]).",
    ])
    return out


# ==========================================================================
# Content, part C: section 9 (gap cards), 10, 11, conclusion, sources
# ==========================================================================
U.update({
    "li_proptech": "https://www.linkedin.com/jobs/proptech-jobs",
    "li_fub": "https://www.linkedin.com/jobs/follow-up-boss-jobs",
    "ijw_proptech": "https://www.itjobswatch.co.uk/jobs/uk/proptech.do",
    "ijw_ai": "https://www.itjobswatch.co.uk/jobs/uk/artificial%20intelligence%20engineer.do",
    "ijw_rag": "https://www.itjobswatch.co.uk/jobs/uk/retrieval-augmented%20generation.do",
    "ijw_de": "https://www.itjobswatch.co.uk/jobs/uk/data%20engineer.do",
    "ijw_n8n": "https://www.itjobswatch.co.uk/jobs/uk/n8n.do",
    "li_reai": "https://www.linkedin.com/jobs/real-estate-ai-jobs",
    "li_rede": "https://www.linkedin.com/jobs/real-estate-data-engineer-jobs",
    "li_uk": "https://uk.linkedin.com/jobs/proptech-jobs",
    "reapit_careers": "https://careers.reapit.com/",
    "indeed_reapit": "https://uk.indeed.com/cmp/Reapit/jobs",
    "hirist": "https://www.hirist.tech/j/idx-developer-php-nodejs-1632700?jobPos=8",
    "arc": "https://arc.dev/hire-developers/reso-web-api",
    "builtin_rm": "https://builtinlondon.uk/job/senior-data-engineer-ii-data-platforms/10625920",
    "fortune": "https://www.fortune.com/2025/09/16/opendoor-chairman-keith-rabois-layoffs-opendoor",
    "ellis_zillow": "https://www.ellis.com/visa-sponsors/zillow-inc",
    "f1jobs": "https://www.f1jobs.io/companies/zillow-inc",
    "mfd": "https://www.multifamilydive.com/news/proptech-investment-venture-capital-funding/809517/",
    "bisnow": "https://www.bisnow.com/national/news/proptech/proptech-funding-slows-sharply-uneven-venture-capital-market-135336",
    "inman_fund": "https://www.inman.com/2026/04/09/the-proptech-funding-rebound-is-real-but-more-selective-than-ever/",
    "hw_rocket": "https://www.housingwire.com/articles/rocket-lays-off-2-of-workforce-after-closing-redfin-acquisition/",
    "compass_10k": "https://www.sec.gov/Archives/edgar/data/1563190/000156319026000057/comp-20251231.htm",
    "njbiz": "https://njbiz.com/compass-110-jobs-madison-anywhere-merger",
    "ren_zillow": "https://www.realestatenews.com/2026/08/04/zillow-cuts-500-roles-ahead-of-q2-earnings-release",
    "ren_zpro": "https://www.realestatenews.com/2025/10/15/zillow-unveils-zillow-pro-uniting-top-tools-for-agents",
    "bw_costar": "https://www.businesswire.com/news/home/20260217810823/en/CoStar-Group-Launches-Transformative-AI-Experience-on-Homes.com-Redefining-the-Future-of-Home-Shopping",
    "hw_liondesk": "https://www.housingwire.com/articles/lone-wolf-liondesk-crm-platform-to-be-discontinued/",
    "alto_intel": "https://www.altosoftware.co.uk/the-last-crm-youll-ever-need-alto/",
    "inman_certifid": "https://www.inman.com/2026/10/01/certifid-acquires-closinglock/",
    "upwork_rates": "https://www.upwork.com/resources/upwork-hourly-rates",
    "upwork_post1": "https://www.upwork.com/freelance-jobs/apply/agent-automation-expert-for-real-estate-investment-company_~022105698179776894846/",
    "upwork_post2": "https://www.upwork.com/jobs/~022067181627045320907",
    "fiverr_fub": "https://www.fiverr.com/gigs/follow-up-boss",
    "upwork_svc_fub": "https://www.upwork.com/services/search?q=follow%20up%20boss",
    "upwork_svc_tc": "https://www.upwork.com/services/search?q=transaction%20coordinator",
    "upwork_svc_bot": "https://www.upwork.com/services/search?q=real%20estate%20chatbot",
    "ht_re": "https://hiretalent.ph/industry/real-estate",
    "ht_af": "https://hiretalent.ph/tool/appfolio",
    "oj_953418": "https://www.onlinejobs.ph/jobseekers/job/Real-Estate-Virtual-Assistant-with-experience-only-953418",
    "upwork_intl": "https://www.upwork.com/jobs/~022066298414597178655",
    "oj_1640648": "https://www.onlinejobs.ph/jobseekers/job/seeking-a-rockstar-admin-transaction-coordinating-and-listing-management-experience-required-1640648",
    "costbench_af": "https://costbench.com/software/property-management/appfolio/hidden-costs/",
    "lp_lofty": "https://www.luxurypresence.com/blogs/lofty-pricing/",
    "nar_newsroom": "https://www.nar.realtor/newsroom/realtors-embrace-ai-digital-tools-to-enhance-client-service-nar-survey-finds",
    "eat_cautious": "https://www.estateagenttoday.co.uk/breaking-news/2026/04/estate-agents-remain-cautiously-competent-about-ai-report/",
    "alto_blog": "https://www.altosoftware.co.uk/blog/best-estate-agency-crms-in-2026-alto-vs-reapit-vs-street/",
    "neg_crm": "https://thenegotiator.co.uk/news/proptech/estate-agency-consultancy-releases-first-ever-crm-guide/",
})

GAP_FIELDS = ["Problem", "Who has it", "Evidence", "Their words", "How they handle it today",
              "Vendors already covering it", "Automatable?", "What the reader would need to learn"]


def _badge_values(rank_row):
    signal, cov, auto = rank_row[2], rank_row[3], rank_row[6]
    s = signal.split(":")[0].strip().lower()
    sig = "strong" if s.startswith(("very high", "high")) else "medium"
    c = cov.split(":")[0].strip().lower()
    if c.startswith(("weak", "medium-weak", "unknown", "thin")):
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
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    chips = Table([[_chip("Problem signal", sig, sig == "strong"), "", _chip("Vendor coverage", cv, cv == "weak"), "", _chip("Automatable", au, False)]],
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


def section_9(CH):
    out = chapter(9, SEC[9]["title"],
                  "Each gap is scored on how strong and recent the problem signal is (regulator findings, fraud data, dated user complaints, job-ad and freelance demand, search phrases) and how weak the vendor coverage is "
                  "(whether a named product claims to solve the exact sub-problem and whether any independent source confirms it). A third column marks fit with a self-hosted or private-data angle, strongest where the work touches tenant, client or financial records "
                  "that regulators say the firm must control and that staff today paste into free tools. The report describes existing products factually and does not design or recommend solutions.")
    out.append(H3("Table 9.1  The ranking, with the nine crowded problems at the end"))
    h, r = T(9, 0)
    out.append(tbl(["#"] + h[1:], r, widths=[13, 34, 36, 39, 19, 14, 21], font="cell_small"))
    out.append(fig_image(*CH["gap_matrix"]))
    out.append(H2("The thirteen gap cards"))
    out.append(Paragraph("Every card has the same eight fields in the same order. The three badges summarise the ranking table: problem signal (strong = very high or high), vendor coverage "
                         "(weak = weak, thin or unknown; partial = medium), and the report's own word on automation (fully, largely, partly).", S["body"]))
    titles = SEC[9]["h3"]
    for title, table in zip(titles, SEC[9]["tables"][1:14]):
        m = re.match(r"^Gap (\d+)\.\s+(.*)$", title)
        rank = int(m.group(1))
        name = m.group(2)
        fields = {row[0].strip(): row[1] for row in table["rows"]}
        rank_row = r[rank - 1]
        out += gap_card(rank, name, rank_row[5], fields, _badge_values(rank_row))
    out.append(H2("Crowded areas that are not gaps, and the three strongest private-data fits"))
    out += bullets([
        "The three strongest gaps for a self-hosted or private-data angle are gaps 1, 3 and 2: they touch tenant files and certificates, bank statements and ID, and owner ledgers, all of which regulators say the firm must control and all of which are being pasted into free tools or shipped to offshore coordinators today; gaps 6, 7 and 9 (title documents, application documents, executed contracts) sit just behind them.",
        "The crowded areas are the ones a buyer finds first when typing 'real estate' into a marketplace: listing copy, promo video, CRM set-up gigs, screening reports, cold callers, and, on the title side, wire-fraud tools; their reviews complain about quality, contracts and price, not absence.",
        "Nine crowded problems in the ranking table: listing descriptions and social posts (ChatGPT, generators, $15-$40 gigs); AI receptionist and phone answering (many vendors; Charisma's 'Jane'; vendor-adjacent caveats about hang-ups); CRM set-up gigs (about 1,160 Fiverr gigs, Upwork $20-$399, 50+ bidders); commodity tenant screening reports (TransUnion, Experian via SmartMove, RentSpree, Buildium, Zillow at $17-$49 same day); "
        "wire-fraud and seller-identity tools for title companies (CertifID, Qualia Shield, FNF ionFraud; the brokerage's role is the call-back); promo video, photo editing and floorplans (694-1,045 feedback gigs); skip-trace data vending (PropStream, BatchLeads, REISkip, Skip Genie); AppFolio bookkeeping as a human service (OJO, PM Bookkeeper, WPM at $34-$45 an hour; the automated exception layer is gap 2); cold-calling VAs and ISAs (292 OnlineJobs posts, MyOutDesk, $3-$7 an hour).",
    ])
    return out


def section_10(CH):
    out = chapter(10, SEC[10]["title"],
                  "The employed path runs through a small number of PropTech employers whose engineering pay is high and whose headcount is shrinking; the freelance path runs through marketplaces where the small firm's buying habit has pushed the public price of 'set up my CRM' to $10-$35 and the price of a person to $5-$10 an hour. "
                  "Neither path requires a real-estate licence on the evidence gathered; both reward the same stack of Python, LLM and RAG work, CRM configuration, workflow tools and property-data handling.")
    out.append(H2("Counting the employed roles"))
    out += bullets([
        "LinkedIn's public pages show '11,000+' US results for 'proptech', 'real estate ai' and 'real estate data engineer' and '8,000+' for UK proptech, but the matching is loose: the 'Follow Up Boss' page is mostly collections and billing jobs containing the words 'follow-up', and the 'AppFolio' page is AppFolio's own hiring, so these are ceilings, not role counts ([LinkedIn proptech jobs](@li_proptech); [LinkedIn follow-up-boss jobs](@li_fub)).",
        "The only clean series is IT Jobs Watch for UK permanent ads in the six months to 11 October 2026: <b>137 ads citing PropTech (17 a year earlier), top titles Sales Manager (36) and Account Executive (34); 808 citing 'Artificial Intelligence Engineer' (91); 505 citing retrieval-augmented generation (84); 2,087 citing Data Engineer (637); 92 Machine Learning Engineer; 488 HubSpot; 50 Zapier; 43 n8n (9)</b>; "
        "no tracked page at all for 'Reapit', 'estate agency' or 'property' ([IT Jobs Watch PropTech](@ijw_proptech); [AI Engineer](@ijw_ai); [RAG](@ijw_rag); [Data Engineer](@ijw_de); [n8n](@ijw_n8n)).",
        "US employers that actually post AI and data titles in the LinkedIn samples: AppFolio ('Staff Machine Learning Engineer - Leasing'), Zillow, CoStar and its Homes.com and Apartments.com brands, Realtor.com, Crexi, EliseAI, JLL, First American and Compass; Keller Williams, eXp, Lone Wolf and Inside Real Estate did not appear ([LinkedIn real estate AI jobs](@li_reai); [LinkedIn real estate data engineer jobs](@li_rede)). "
        "UK engineering ads cluster in London and Manchester at Rightmove, Houseful, Reapit, Street Group, Yardi and CoStar UK plus small start-ups ([LinkedIn UK proptech jobs](@li_uk)); Reapit's own careers page showed one live role with placeholder text and Indeed listed three Reapit UK jobs ([Reapit careers](@reapit_careers); [Indeed UK Reapit](@indeed_reapit) [snippet]).",
    ])
    out.append(fig_image(*CH["itjobswatch"]))
    out.append(H2("Pay: the employer matters more than the title"))
    out += bullets([
        "Within US PropTech a senior engineer at the stock-paying portals (Zillow, Opendoor, Redfin) reports about double a senior at CoStar or Yardi; the property-management vendors (Yardi, Entrata, RealPage, AppFolio) pay base-heavy packages of $100,000 to $212,000. In the UK the PropTech tag carries no premium: £65,000 median against £87,500 for a generic AI Engineer, so the premium is for AI and RAG skills, not for the property vertical ([IT Jobs Watch PropTech](@ijw_proptech)).",
        "The skills the ads name are generic: UK AI Engineer ads co-occur with Python (54.6%), Azure (42.7%) and LLM (36.4%); RAG ads with LLM (82.8%), Python (65.9%), generative AI (51.5%) and Azure (49.7%); data-engineer ads with SQL (38.0%), Python (33.7%) and pipelines (32.2%); PropTech ads with SaaS (67.2%), TypeScript and Node.js rather than AI ([IT Jobs Watch AI Engineer](@ijw_ai); [RAG](@ijw_rag); [Data Engineer](@ijw_de)). "
        "The vertical skills (RESO Web API, MLS and IDX feeds, Trestle, MLS Grid) show up in developer ads and freelancer directories, not in any salary index; no fetched ad mentioned ATTOM, CoreLogic, Snowflake, dbt, vector databases or the Rightmove real-time datafeed ([Hirist IDX developer](@hirist) [snippet]; [Arc.dev RESO](@arc)).",
        "Remote and visa reality is thin: none of 60 LinkedIn US PropTech cards used the word 'Remote' (one hybrid, one on-site), two of 60 Real Estate AI cards did (both First American), 21 of 137 UK PropTech ads (15.3%) were tagged work-from-home, Reapit says 'Most roles are hybrid', Rightmove's data roles are London hybrid two days a week, Opendoor's chairman 'wants employees back in the office', and sponsorship is small and shrinking (Zillow's green-card filings fell from 44 to 2; F1Jobs reports 8 new-hire H-1B approvals against 92 renewals) "
        "([LinkedIn proptech jobs](@li_proptech); [Reapit careers](@reapit_careers); [Built In London Rightmove](@builtin_rm) [snippet]; [Fortune, 16 Sep 2025](@fortune); [Ellis Zillow](@ellis_zillow); [F1Jobs](@f1jobs) [snippet]). No fetched ad contained explicit sponsorship or degree wording.",
    ])
    out.append(fig_image(*CH["salary_employed"]))
    out.append(H3("Table 10.1  Employed pay by employer or title"))
    h, r = T(10, 0)
    out.append(tbl(h, r, widths=[44, 60, 30, 42], font="cell_small"))
    out.append(H2("The 2025-26 market moves"))
    out += bullets([
        "PropTech funding recovered to <b>$16.7bn in 2025 (+67.9%)</b> but was concentrated in large debt and structured deals, then flattened at <b>$4.53bn in H1 2026 (-0.6%)</b> with 11 deals of $100m-plus taking 49.6% and the 75 sub-$5m rounds of Q1 2026 taking 2.8% of capital, so early-stage PropTech is not a large source of engineering jobs ([Multifamily Dive, 13 Jan 2026](@mfd); [Bisnow](@bisnow); [Inman, 9 Apr 2026](@inman_fund) [snippet]).",
        "The big residential players consolidated and cut while shipping AI: Rocket closed its Redfin purchase on 1 July 2025 and cut about 2% including product and engineering ([HousingWire](@hw_rocket)); Compass closed Anywhere on 9 January 2026 with 110 New Jersey cuts in a WARN notice ([Compass 10-K](@compass_10k) [snippet]; [NJBIZ](@njbiz) [snippet]); Zillow cut about 200 roles in January 2026 and 'just over 500' on 4 August 2026 while rolling Zillow Pro (Follow Up Boss plus consumer activity insights and AI alerts) nationwide "
        "([Real Estate News, 4 Aug 2026](@ren_zillow); [Real Estate News, 15 Oct 2025](@ren_zpro)); Opendoor's chairman said 'There's 1,400 employees at Opendoor... We don't need more than 200 of them' ([Fortune](@fortune)); CoStar launched Homes AI on Azure OpenAI in February 2026 ([Business Wire](@bw_costar) [snippet]); Lone Wolf shut LionDesk in September 2025 ([HousingWire](@hw_liondesk)); Alto shipped 'Alto Intelligence' in the UK ([Alto](@alto_intel) [vendor]); CertifID bought ClosingLock on 1 October 2026 ([Inman](@inman_certifid) [listing, not fetched]).",
        "The AI feature work is being done by the portals and CRMs themselves, which both creates the AI and ML roles seen on LinkedIn and removes some of the simple 'add AI to the CRM' work from the freelance market.",
    ])
    out.append(H2("The freelance path is priced in public"))
    out += bullets([
        "Upwork's own rate guide puts entry-level admin at roughly $10-$25 an hour, intermediate at $25-$75 and specialised development, AI and consulting at $75-$150-plus ([Upwork rate guide](@upwork_rates) [snippet]); live real-estate posts sit at the low end: an 'agent automation expert for real estate investment company' at $5-$50 an hour and a 'Senior python engineer who can build real estate automations' at $25-$75 an hour, each drawing 50-plus proposals ([Upwork post](@upwork_post1) [snippet]; [Upwork post](@upwork_post2) [snippet]).",
        "The 81 live posts read in October 2026 cluster at $100-$2,300 fixed for CRM, landing-page and integration builds, $500 for a voice agent, $20-$60 an hour for 'AI agent' design, $35-$60 an hour for SEO and 'GEO/AEO', $15-$20 an hour for Expert-tier transaction coordination, and $3-$12 an hour for everything done by a person ([Upwork jobs: follow up boss](@upwork_fub); [Upwork jobs: real estate ai chatbot](@upwork_ai); [Upwork jobs: transaction coordinator](@upwork_tc)).",
        "US-based AppFolio consultants list at $30-$75 an hour against offshore freelancers at about $10 ([Upwork AppFolio California](@upwork_af_ca); [Upwork AppFolio](@upwork_af) [snippet]); Fiverr sells CRM set-up from $10-$20 and Zapier, Make and n8n automation from $25-$35 ([Fiverr](@fiverr_fub) [snippet]); Upwork's catalogue prices Follow Up Boss set-up at $30-$399 (modal $50), kvCORE and Lofty at $20-$175, a transaction coordinator at $20-$450 with 15 of 24 gigs unrated, a listing description at $15-$40 and a real-estate AI chatbot at $20-$400 with 5-10 feedback on the real-estate-named gigs "
        "([Upwork services: follow up boss](@upwork_svc_fub); [Upwork services: transaction coordinator](@upwork_svc_tc); [Upwork services: real estate chatbot](@upwork_svc_bot)).",
        "Philippine directories list 1,437 real-estate VA profiles at $5-$8 an hour (median $6) and 51 AppFolio profiles at $6-$8; OnlineJobs.ph posts pay $700-$850 a month for a real-estate VA with MLS, Dotloop and PropStream experience ([HireTalent.ph real estate](@ht_re); [HireTalent.ph AppFolio](@ht_af); [OnlineJobs.ph](@oj_953418)); vetted API developers on Arc are $60-$100-plus an hour ([Arc.dev](@arc)). "
        "One Upwork AppFolio bookkeeping post states 'we are open to international talent only', and several US posts require weekend and holiday cover in US hours ([Upwork](@upwork_intl) [snippet]; [OnlineJobs.ph 1640648](@oj_1640648)).",
        "The consulting tier above the gigs is visible only in AppFolio accounting ($34-$45 an hour, $300 a month minimum, per-unit retainers), in vendor onboarding fees (Lofty $299-$1,499, AppFolio $400-$1,000-plus, Buildium $1,000-$2,000, PayProp £600-£2,000) and in a sponsored claim that BoldTrail implementation runs $1,000-$5,000; no certified-partner rate card exists for Follow Up Boss, kvCORE, Lofty, AppFolio, Buildium, Reapit or Alto, and Clutch, LinkedIn Services and vendor partner directories were not reached "
        "([OJO](@ojo); [CostBench AppFolio](@costbench_af) [secondary]; [Luxury Presence Lofty](@lp_lofty) [snippet]; [AI Tools Bakery](@aitb) [secondary]).",
    ])
    out.append(fig_image(*CH["freelance_rates"]))
    out.append(H2("How these businesses buy technology help explains the price floor"))
    out += bullets([
        "US agents mostly buy their own tools: 34% spend $50-$250 a month, 20% $251-$500 and 24% over $500; 67% say the brokerage already provides what they need; brokerages commonly spend $50 or less per agent per month (about 28%) with 18% at $201-plus; about 45% of brokerages that switched did so for functionality, 28% named third-party integration a top opportunity, 48% named AI the technology they are most interested in; no survey measures spending on outside consultants "
        "([NAR newsroom, 18 Sep 2025](@nar_newsroom); [TotalBrokerage 2024](@tb_2024); [TotalBrokerage 2025](@tb_2025) [vendor surveys]).",
        "UK agencies are later-stage buyers pulled by compliance: 52% plan to adopt AI within 12 months, 66% expect to rely on compliance and AML automation, nearly nine in ten larger agencies plan adoption while smaller independents lag and about a third are nervous ([Property Industry Eye, 16 Jan 2026](@pie_alto_ai) [vendor survey]); 59% prefer to wait until others have tested new technology and almost half use no AI ([Estate Agent Today, Apr 2026](@eat_cautious) [snippet]). "
        "Alto claims 6,000-plus agencies and a consultancy's guide puts Reapit at about 5,000 offices and 25,000 users, so the UK installed base is two vendors deep with no third-party consultant layer around either ([Alto blog](@alto_blog) [vendor, snippet]; [The Negotiator](@neg_crm) [snippet]).",
    ])
    out.append(H3("Table 10.2  Employed path against freelance path, dimension by dimension"))
    h, r = T(10, 1)
    out.append(tbl(h, r, widths=[24, 76, 76], font="cell_small", first_col_bold=True))
    out.append(source_line("Sources for the comparison table: Levels.fyi [%d]; Ellis [%d]; IT Jobs Watch [%d]; Upwork rate guide [%d] (snippet); Upwork AppFolio [%d] (snippet); OJO [%d]; HireTalent.ph [%d]; Arc.dev [%d]; Real Estate News, 4 Aug 2026 [%d]; HousingWire Rocket [%d]; Fortune Opendoor [%d]; F1Jobs [%d] (snippet); "
                           "OnlineJobs.ph [%d]; OnlineJobs.ph TC search [%d]; PeoplePerHour [%d]; IT Jobs Watch Zapier [%d]; Upwork jobs: transaction coordinator [%d]; Hirist [%d] (snippet); HousingWire NAR 2025 [%d]." % tuple(ref(u) for u in (
                               "https://www.levels.fyi/companies/zillow/salaries/software-engineer/title/machine-learning-engineer", "https://www.ellis.com/visa-sponsors/zillow-inc",
                               "https://www.itjobswatch.co.uk/jobs/uk/artificial%20intelligence%20engineer.do", "https://www.upwork.com/resources/upwork-hourly-rates",
                               "https://www.upwork.com/hire/appfolio-freelancers/california-us/", "https://ojobookkeeping.com/appfolio-bookkeeping/", "https://hiretalent.ph/industry/real-estate",
                               "https://arc.dev/hire-developers/reso-web-api", "https://www.realestatenews.com/2026/08/04/zillow-cuts-500-roles-ahead-of-q2-earnings-release",
                               "https://www.housingwire.com/articles/rocket-lays-off-2-of-workforce-after-closing-redfin-acquisition/", "https://www.fortune.com/2025/09/16/opendoor-chairman-keith-rabois-layoffs-opendoor",
                               "https://www.f1jobs.io/companies/zillow-inc", "https://www.onlinejobs.ph/jobseekers/job/Real-Estate-Virtual-Assistant-with-experience-only-953418",
                               "https://www.onlinejobs.ph/jobseekers/jobsearch?jobkeyword=transaction+coordinator", "https://www.peopleperhour.com/freelance-jobs?keyword=estate%20agent",
                               "https://www.itjobswatch.co.uk/jobs/uk/zapier.do", "https://www.upwork.com/nx/search/jobs/?q=real%20estate%20transaction%20coordinator",
                               "https://www.hirist.tech/j/idx-developer-php-nodejs-1632700?jobPos=8", "https://www.housingwire.com/articles/nar-2025-technology-survey-realtor-tech-usage-trends/"))))
    out.append(note_box("<b>The practical reading:</b> the employed path's income ceiling is set by the stock-paying portals, which are the same firms that cut 2-7% of staff in 2025-26 and where 'remote' means hybrid in Seattle, San Francisco, London or Manchester, while the base-heavy property-management vendors were not reported cutting and pay $100,000-$212,000. "
                        "The freelance path's public price floor is set by Fiverr and Philippine VAs, so a US- or UK-priced consultant's revenue depends on work that buyers already price at $25-$150 an hour (custom automation, data, AI agents, 'I'm not looking for someone who only connects apps') and on the validation and compliance work in section 9 that nobody prices, sold through private channels (referrals, vendor partner directories, LinkedIn Services) for which no data was found. "
                        "Neither path requires a licence on the evidence; both reward MLS and portal data fluency, CRM and PM-system knowledge, and the compliance vocabulary of section 2."))
    return out


def section_11(CH):
    out = chapter(11, SEC[11]["title"],
                  "The researchers were blocked by many primary hosts (" + BLOCKED_HOSTS.rstrip(".") + "), and the shared web-search budget ran out part-way through every notes file, after which research continued by direct fetch of known URLs. "
                  "The items below rest on search snippets, secondary reports, vendor claims or sponsored comparisons, or were not found at all, and should be checked before being repeated to a client.")
    out.append(H3("Table 11.1  Items that rest on snippets, secondary reports, vendor claims or sponsored comparisons"))
    h, r = T(11, 0)
    out.append(tbl(h, r, widths=[74, 102], font="cell"))
    return out


def conclusion_page(CH):
    out = chapter(None, "Conclusion", None)
    out.append(Paragraph("What the research changes", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("<b>The problem a small property business will pay to remove is not valuing, selling or letting.</b> It is the loop of chasing, re-keying and date-watching that surrounds every deal and every tenancy, and in 2025-26 that loop was put under outside pressure at the same time in both countries: "
            "by regulators (HMRC's July 2026 AML guidance, the Renters' Rights Act from 1 May 2026, the DMCC Act, the FCC's revocation rules, HUD's fair-housing-and-AI guidance), by fraudsters (seller impersonation doubling, AI-built tenant identities), by the ombudsmen (lettings complaints up 47% and 65%) and by the portals (Rightmove removing images, Zillow folding Follow Up Boss into Zillow Pro). "
            "The strongest language is therefore risk and evidence language, not productivity language, and the strongest thing a reader can carry into a conversation is a regulator's finding or a dated review about the buyer's own software."),
        inl("<b>The software these firms already pay for has drawn a clear line around what it will not do:</b> it will alert but not verify, log but not own, reconcile the bank but not the owner statement, score the applicant but not handle the exception, and migrate the data but not check it arrived. "
            "Every top-ranked gap sits on that line, and every one touches records the law says the firm must control and that staff today paste into free tools or email to a coordinator at £4.50 an hour: tenancy certificates and notices, bank statements and ID, owner ledgers, title documents, application documents and executed contracts."),
    ]]
    out.append(Paragraph("Where not to go, and what the law reserves to a person", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("Listing copy, phone answering, CRM set-up, screening reports, cold calling and title-side wire tools are where the vendors, the gigs and the venture money already sit, and their users complain about quality, contracts and price rather than absence."),
        inl("The things the law reserves to a person (the Right to Rent check with the holder present, the nominated officer's AML judgment, the conveyancer's ID1, the landlord's FCRA notice, the licensed agent's publication sign-off, the call-back on a wire instruction) are boundaries to design around, not gaps to fill."),
    ]]
    out.append(Paragraph("Two vocabularies, two markets for the same skills", S["h2"]))
    out += [Paragraph(t, S["concl"]) for t in [
        inl("The vocabulary split is not cosmetic: a UK buyer searches 'renters rights act compliance checklist', 'material information part b', 'sales progression software' and 'estate agency aml risk assessment', hires a 'lettings administrator' around 'deposits', 'certificates' and 'referencing', and finds nothing when typing those words into a freelance marketplace; "
            "a US buyer searches 'follow up boss vs lofty', 'transaction coordinator checklist pdf' and 'fair housing words to avoid pdf', hires a 'TC' or an 'ISA' around 'contract to close' and 'no lead falls through the cracks', and finds operations help only by typing a product name. The same service will need two sets of words, and the notes give them verbatim."),
        inl("The job-market notes add the last contrast: the employed path pays most at the portals that are cutting staff and hiring hybrid in a handful of cities, while the freelance path is priced down to $10 a gig and $5 an hour by marketplaces, and the only priced middle tier, AppFolio trust-accounting cleanup at $34-$45 an hour with a free health check as the door-opener, "
            "is the proof that small firms pay for validation when someone offers it in their own words."),
    ]]
    out.append(Spacer(1, 6 * mm))
    out.append(note_box("This document reports problems, workflows, numbers, vocabulary and gaps only. It contains no solutions and no recommendations. The Sources appendix lists every URL the research cited; section 11 lists what could not be verified.", warm=False))
    return out


def sources_appendix():
    out = chapter(None, "Sources", "Every URL cited in the research report, numbered in order of first appearance. Body references [n] point here. "
                                   "Hosts that blocked the researcher are listed in section 11, which follows this appendix; facts from them carry the [snippet], [secondary] or [sponsored] tag.")
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
                                 title="Small real estate firm problems UK and US (12 Oct 2026)",
                                 author="Research for Mustafa Shoukat",
                                 subject="Problems, workflows, numbers, vocabulary and service gaps in small UK and US real estate businesses")
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
