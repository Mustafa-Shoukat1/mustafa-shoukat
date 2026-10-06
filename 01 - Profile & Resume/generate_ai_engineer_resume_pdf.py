"""Generate Mustafa Shoukat's AI Engineer resume as a clean, scannable 1-page PDF."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# Colors
BLACK = HexColor("#111111")
DARK_GRAY = HexColor("#333333")
MEDIUM_GRAY = HexColor("#555555")
ACCENT = HexColor("#1a5276")
LINK_COLOR = HexColor("#1a73e8")
LINE_COLOR = HexColor("#cccccc")

STYLES = {
    "name": ParagraphStyle(
        "name", fontName="Helvetica-Bold", fontSize=14, leading=17,
        textColor=BLACK, alignment=TA_CENTER, spaceAfter=2,
    ),
    "tagline": ParagraphStyle(
        "tagline", fontName="Helvetica", fontSize=9, leading=11,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=2,
    ),
    "contact": ParagraphStyle(
        "contact", fontName="Helvetica", fontSize=8.5, leading=11,
        textColor=MEDIUM_GRAY, alignment=TA_CENTER, spaceAfter=1,
    ),
    "section_heading": ParagraphStyle(
        "section_heading", fontName="Helvetica-Bold", fontSize=9.5, leading=11,
        textColor=ACCENT, spaceAfter=2, spaceBefore=4,
    ),
    "job_title": ParagraphStyle(
        "job_title", fontName="Helvetica-Bold", fontSize=8.5, leading=10,
        textColor=BLACK, spaceAfter=2, spaceBefore=3,
    ),
    "summary": ParagraphStyle(
        "summary", fontName="Helvetica", fontSize=8, leading=11,
        textColor=DARK_GRAY, spaceAfter=1,
    ),
    "skills": ParagraphStyle(
        "skills", fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=DARK_GRAY, spaceAfter=1,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=8, leading=10.5,
        textColor=DARK_GRAY, leftIndent=12, bulletIndent=0, spaceAfter=2,
        bulletFontName="Helvetica", bulletFontSize=8,
    ),
    "education": ParagraphStyle(
        "education", fontName="Helvetica", fontSize=8, leading=11,
        textColor=DARK_GRAY, spaceAfter=1,
    ),
    "oss_item": ParagraphStyle(
        "oss_item", fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=DARK_GRAY, leftIndent=12, bulletIndent=0, spaceAfter=1.5,
        bulletFontName="Helvetica", bulletFontSize=7.5,
    ),
    "project_item": ParagraphStyle(
        "project_item", fontName="Helvetica", fontSize=7.5, leading=10,
        textColor=DARK_GRAY, leftIndent=12, bulletIndent=0, spaceAfter=1.5,
        bulletFontName="Helvetica", bulletFontSize=7.5,
    ),
}


def link(url, text):
    return f'<a href="{url}" color="#{LINK_COLOR.hexval()[2:]}">{text}</a>'


def bold(text):
    return f"<b>{text}</b>"


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.45 * inch,
        bottomMargin=0.4 * inch,
    )

    story = []

    # ──────── HEADER ────────
    story.append(Paragraph("MUSTAFA SHOUKAT", STYLES["name"]))
    story.append(Paragraph(
        "AI Software Engineer",
        STYLES["tagline"],
    ))
    story.append(Paragraph(
        f'{link("mailto:mustafashoukat.ai@gmail.com", "mustafashoukat.ai@gmail.com")}  |  '
        f'{link("https://wa.me/923093609261", "+92 309 3609261")}  |  '
        f'{link("https://github.com/Mustafa-Shoukat1", "GitHub")}  |  '
        f'{link("https://linkedin.com/in/mustafashoukat", "LinkedIn")}  |  '
        f'{link("https://huggingface.co/Mustafa-Shoukat1", "HuggingFace")}',
        STYLES["contact"],
    ))
    story.append(HRFlowable(width="100%", thickness=0.8, color=LINE_COLOR, spaceAfter=3, spaceBefore=2))

    # ──────── SPECIALIZATIONS ────────
    story.append(Paragraph("SPECIALIZATIONS", STYLES["section_heading"]))
    specializations = [
        "AI Product Development (Web &amp; Mobile Apps)",
        "Local &amp; Agentic RAG System Development",
        "Generative AI SaaS Product Development",
        "AI System Architecture Design &amp; Implementation",
        "Cloud-Native AI Deployment (AWS &amp; Scalable Environments)",
        "Low-Code / No-Code AI Automation Solutions",
    ]
    for spec in specializations:
        story.append(Paragraph(spec, STYLES["oss_item"], bulletText="\u2022"))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=2, spaceBefore=2))

    # ──────── SUMMARY ────────
    story.append(Paragraph("SUMMARY", STYLES["section_heading"]))
    story.append(Paragraph(
        f"AI Software Engineer with 6 years of experience shipping production AI systems for clients in KSA, UK, and USA. "
        f"Active open-source contributor to LangChain, RAGAS, and Unstructured "
        f"with CI-passing PRs. Experienced with air-gapped deployments for government networks in the Gulf region.",
        STYLES["summary"],
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=2, spaceBefore=2))

    # ──────── TECHNICAL SKILLS ────────
    story.append(Paragraph("TECHNICAL SKILLS", STYLES["section_heading"]))
    skills_data = [
        ("AI/ML Frameworks",
         "LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, HuggingFace Transformers, PyTorch, scikit-learn"),
        ("RAG &amp; Retrieval",
         "Hybrid retrieval (dense + BM25 + RRF), cross-encoder reranking, semantic chunking, Arabic NLP pipelines"),
        ("Vector Databases",
         "Qdrant, FAISS, Pinecone, Milvus, ChromaDB"),
        ("RL &amp; Evaluation",
         "NLI scoring, Recall@k, MRR, NDCG, pytest (617+ tests), Gymnasium RL environments"),
        ("LLM Fine-Tuning",
         "LoRA, QLoRA, SFT"),
        ("Languages &amp; Web",
         "Python, TypeScript, SQL, FastAPI, React, Next.js, Gradio"),
        ("Infrastructure",
         "Docker, AWS, GCP, Azure, GitHub Actions CI/CD, air-gapped deployments"),
        ("Automation",
         "n8n, Twilio, Make.com, Zapier, Flowise, GoHighLevel"),
        ("Observability",
         "LangSmith, AgentOps, MLflow"),
    ]
    for label, val in skills_data:
        story.append(Paragraph(f"<b>{label}:</b> {val}", STYLES["skills"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=2, spaceBefore=2))

    # ──────── EXPERIENCE ────────
    story.append(Paragraph("EXPERIENCE", STYLES["section_heading"]))

    # -- Navid --
    story.append(Paragraph("AI Software Engineer, Navid-Wattad Digital, KSA (Remote)  |  2024 - Present", STYLES["job_title"]))
    navid_bullets = [
        f"Built {bold('ByanRAG 2.2')}, production Arabic legal RAG: 5 ML models, hybrid retrieval (dense + BM25 + RRF), "
        f"cross-encoder reranking, NLI-based confidence scoring, and {bold('617+ automated tests')} across 4-stage pipeline.",

        f"Architected {bold('reproducible, sandboxed environments')} via 7-service Docker Compose: isolated per-tenant "
        f"deployments, {bold('air-gap support for government networks')}, and 65%+ CI coverage.",

        f"Built {bold('agentic AI workflows')} and internal SaaS tools with LangChain, LangGraph, and FastAPI, "
        f"serving multiple business units with automated document processing and intelligent Q&amp;A.",
    ]
    for b in navid_bullets:
        story.append(Paragraph(b, STYLES["bullet"], bulletText="\u2022"))

    # -- AutorecAI --
    story.append(Paragraph("Generative AI Engineer, AutorecAI, UK (Remote)  |  2022 - 2024", STYLES["job_title"]))
    autorec_bullets = [
        f"Built production {bold('agentic AI systems')} with custom tool-use orchestration, "
        f"autonomous task execution, and automated output validation for enterprise clients.",

        f"Designed {bold('containerized, air-gapped RAG deployments')} for regulated environments: zero external dependencies, "
        f"reproducible Docker setup, serving legal and compliance document Q&amp;A.",

        f"Deployed on {bold('AWS and GCP')} with Docker, GitHub Actions CI/CD, and automated regression testing.",
    ]
    for b in autorec_bullets:
        story.append(Paragraph(b, STYLES["bullet"], bulletText="\u2022"))

    # -- Comet --
    story.append(Paragraph("Software Automation Engineer, Comet Estimating LLC, USA (Remote)  |  2020 - 2022", STYLES["job_title"]))
    comet_bullets = [
        f"Built Python automation pipelines with {bold('data validation and QA workflows')}, CI/CD on Google Cloud Run.",

        f"Developed {bold('lead scoring system with human-in-the-loop review')}, combining automated qualification "
        f"with manual verification. Received {bold('Best Performance Award')}.",
    ]
    for b in comet_bullets:
        story.append(Paragraph(b, STYLES["bullet"], bulletText="\u2022"))

    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=2, spaceBefore=2))

    # ──────── OPEN-SOURCE CONTRIBUTIONS ────────
    story.append(Paragraph("OPEN-SOURCE CONTRIBUTIONS", STYLES["section_heading"]))
    oss_items = [
        f"{bold('LangChain')} (92k+ stars): Fixed malformed function dicts in tool call parsers + 16 tests (PR #36680)",
        f"{bold('RAGAS')} (7k+ stars): 3 PRs \u2014 bug fixes, multilingual support (Arabic/CJK), backward-compatible import aliases + 62 tests",
        f"{bold('Unstructured')} (14k+ stars): PaddleOCR language mapping fix + 6 tests (PR #4329)",
    ]
    for item in oss_items:
        story.append(Paragraph(item, STYLES["oss_item"], bulletText="\u2022"))

    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=2, spaceBefore=2))

    # ──────── PROJECTS ────────
    story.append(Paragraph("PROJECTS", STYLES["section_heading"]))
    project_items = [
        f"{bold('arabic-rag-bench')}: Open-source Gymnasium RL environment for training LLMs to debug Arabic RAG pipelines. "
        f"Deterministic Recall@5 scoring, reward-hacking defenses, 24 tests, CI (Python 3.10/3.11/3.12).",
        f"{bold('AI Receptionist SaaS')}: WhatsApp-based AI receptionist for real estate and legal firms. "
        f"Twilio + n8n + GoHighLevel integration.",
    ]
    for item in project_items:
        story.append(Paragraph(item, STYLES["project_item"], bulletText="\u2022"))

    story.append(HRFlowable(width="100%", thickness=0.5, color=LINE_COLOR, spaceAfter=2, spaceBefore=2))

    # ──────── EDUCATION ────────
    story.append(Paragraph("EDUCATION", STYLES["section_heading"]))
    story.append(Paragraph(
        f"{bold('MS Artificial Intelligence')}, National University of Sciences and Technology (NUST), Pakistan (2025 - Present)",
        STYLES["education"],
    ))
    story.append(Paragraph(
        f"{bold('BS Computer Science')}, Virtual University (2023 - 2027)",
        STYLES["education"],
    ))

    doc.build(story)
    print(f"PDF generated: {output_path}")


if __name__ == "__main__":
    build_pdf(r"d:\Mustafa AI\Mustafa_Shoukat_AI_Engineer_Resume.pdf")
