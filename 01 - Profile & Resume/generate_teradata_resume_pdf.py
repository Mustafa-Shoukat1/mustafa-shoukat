"""Rebuild of Mustafa's own Teradata resume, with two employer records corrected.

Changes applied on request (19 Sep 2026), both to match the live LinkedIn record
so a recruiter comparing resume and profile sees no discrepancy:

  1. "Generative AI Engineer, AutorecAI, United Kingdom (Remote), 2022 to 2023"
     ->  "Generative AI Consultant, Aretec, Lahore (Remote, Contract), Jul 2023 to Aug 2024"
  2. "Software Automation Engineer, COMET Estimating LLC, Austin TX (Remote), 2020 to 2022"
     ->  "Data Scientist, COMET Estimating LLC, Remote (US), Jul 2021 to Jun 2023"

Everything else is reproduced as he wrote it. The other findings raised in review
(open-source PR states, "BS Completed", MS NUST, air-gapped, Yehia R1, "6+ years")
were deliberately left alone at his direction.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

BLACK = HexColor("#000000")
BODY = HexColor("#1a1a1a")
ACCENT = HexColor("#1F4E79")
LINK = HexColor("#1155CC")
RULE = HexColor("#9DB7CE")

S = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=15, leading=17.5,
                           textColor=BLACK, alignment=TA_CENTER, spaceAfter=2),
    "tagline": ParagraphStyle("tagline", fontName="Helvetica", fontSize=9, leading=11,
                              textColor=ACCENT, alignment=TA_CENTER, spaceAfter=1.5),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.2, leading=10,
                              textColor=LINK, alignment=TA_CENTER, spaceAfter=2),
    "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=9.5, leading=11,
                              textColor=ACCENT, spaceBefore=2.5, spaceAfter=0),
    "role": ParagraphStyle("role", fontName="Helvetica-Bold", fontSize=8.3, leading=10,
                           textColor=BLACK, spaceBefore=2.5, spaceAfter=1),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=7.4, leading=8.8,
                           textColor=BODY, alignment=TA_JUSTIFY, spaceAfter=1),
    "skill": ParagraphStyle("skill", fontName="Helvetica", fontSize=7.2, leading=8.9,
                            textColor=BODY, spaceAfter=0.9),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=7.4, leading=8.8,
                             textColor=BODY, leftIndent=10, bulletIndent=1, spaceAfter=1.0,
                             bulletFontName="Helvetica", bulletFontSize=7.4),
    "edu": ParagraphStyle("edu", fontName="Helvetica", fontSize=7.5, leading=9,
                          textColor=BODY, spaceAfter=0.6),
}

DOT = "•"


def b(t):
    return f"<b>{t}</b>"


def a(url, text):
    return f'<a href="{url}" color="#{LINK.hexval()[2:]}">{text}</a>'


def section(story, title):
    story.append(Paragraph(title, S["section"]))
    story.append(HRFlowable(width="100%", thickness=0.7, color=RULE,
                            spaceBefore=0.8, spaceAfter=1.6))


def role(story, heading, bullets):
    story.append(Paragraph(heading, S["role"]))
    for line in bullets:
        story.append(Paragraph(line, S["bullet"], bulletText=DOT))


def build(path):
    doc = SimpleDocTemplate(path, pagesize=letter,
                            leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                            topMargin=0.34 * inch, bottomMargin=0.26 * inch,
                            title="Mustafa Shoukat - Senior AI Engineer",
                            author="Mustafa Shoukat")
    st = []

    st.append(Paragraph("MUSTAFA SHOUKAT", S["name"]))
    st.append(Paragraph(
        "Senior AI Engineer &#183; Enterprise AI Architecture &#183; Agentic Systems &#183; RAG Platforms",
        S["tagline"]))
    st.append(Paragraph(
        a("mailto:mustafashoukat.ai@gmail.com", "mustafashoukat.ai@gmail.com")
        + " | " + a("https://wa.me/923093609261", "+92 309 3609261")
        + " | " + a("https://linkedin.com/in/mustafashoukat", "LinkedIn")
        + " | " + a("https://github.com/Mustafa-Shoukat1", "GitHub")
        + " | Open to Remote", S["contact"]))

    # ---- SUMMARY ----
    section(st, "SUMMARY")
    st.append(Paragraph(
        "AI Engineer who owns enterprise AI platforms end to end, not just features. Architected and shipped "
        "20+ production systems for enterprise and government-grade clients across Saudi Arabia, the UAE, the US, "
        "and the UK, including a multi-tenant, distributed RAG platform with 5-level RBAC, full audit logging, and "
        "on-premises/air-gapped deployment for regulated networks, and a Claude-as-judge fine-tuning pipeline that "
        "took an Arabic LLM to #1 on the AraGen Leaderboard. 6+ years across Python, Java, FastAPI, vector databases, "
        "SQL/NoSQL data stores, cloud-native deployment (AWS, GCP, Azure, Docker), and production observability "
        "(Prometheus/Grafana/Loki), building agentic systems (LangGraph, CrewAI) with tool-calling and multi-step "
        "planning. Trained 150+ professionals and mentored engineers in AI engineering; active open-source "
        "contributor to LangChain, RAGAS, and Unstructured.", S["body"]))

    # ---- SKILLS ----
    section(st, "TECHNICAL SKILLS")
    for label, text in [
        ("Languages", "Python, Java, TypeScript, JavaScript, SQL, Rust"),
        ("AI / LLM &amp; Orchestration",
         "LangChain, LangGraph, CrewAI, LlamaIndex, AutoGen, MCP (Model Context Protocol), tool-calling &amp; "
         "multi-step planning, OpenAI, Gemini, Groq, Cohere, HuggingFace, Ollama"),
        ("RAG &amp; Vectors",
         "Qdrant, Milvus, FAISS, ChromaDB, Pinecone, pgvector; hybrid/semantic retrieval (BM25 + dense), RRF, "
         "rerankers, NLI faithfulness scoring"),
        ("Evaluation / Governance",
         "LangSmith, Helicone, MLflow; RAG evaluation &amp; groundedness scoring, guardrails, prompt-injection "
         "defense, Claude-as-judge pipelines"),
        ("Backend", "FastAPI, Django, Flask, Node.js/Express, Celery, Redis, WebSockets, SSE"),
        ("Cloud / DevOps",
         "Docker, Docker Compose, GitHub Actions CI/CD, AWS (S3, App Runner), GCP, Azure, Nginx, Prometheus, "
         "Grafana, Loki, Sentry"),
        ("Databases",
         "PostgreSQL, MongoDB (SQL &amp; NoSQL data stores), Redis, Supabase, Neon; SQLAlchemy, Drizzle, Prisma, Alembic"),
        ("Specialties",
         "Multi-tenant, distributed architecture (Celery/Redis), on-premises / air-gapped RAG, RBAC/access control, "
         "Arabic-first NLP"),
    ]:
        st.append(Paragraph(f"{b(label)}: {text}", S["skill"]))

    # ---- EXPERIENCE ----
    section(st, "EXPERIENCE")

    role(st, "AI Software Engineer, Independent / Contract &#183; Remote (KSA / UAE / UK / US) | 2024 to Present", [
        "Ship and maintain production AI systems across RAG platforms, voice AI, WhatsApp automation, and CRMs for "
        "clients in four countries: deployed systems, not prototypes.",
        "Built a government-contracting platform that scrapes SAM.gov by NAICS code and runs LangGraph agents for "
        "solicitation analysis, bid/no-bid decisions, and automated PDF proposal generation on a provider-agnostic LLM layer.",
        "Engineered WhatsApp lead-qualification systems with fail-closed HMAC webhook verification, Whisper voice-note "
        "transcription, atomic message deduplication, and CRM dashboards with human handover.",
        "Advise organizations moving AI from pilot to day-to-day operations: architecture, evaluation, scalability, "
        "and cost-optimized inference.",
    ])

    role(st, "Agentic AI Engineer, Watad (Navid) &#183; Riyadh, Saudi Arabia | 2023 to 2026", [
        b("Owned end-to-end architecture") + " for ByanRAG 2.2, a production, multi-tenant Arabic-first RAG platform, "
        "with org-isolated Qdrant collections, a 5-level Casbin RBAC hierarchy enforced on every endpoint, and a "
        "14-panel admin console (users, documents, analytics, audit logs, system health), built for on-premises "
        "deployment inside regulated networks.",
        b("Designed the hybrid semantic retrieval pipeline") + " (dense embeddings, BM25 sparse search, RRF fusion, "
        "CrossEncoder reranking) powering source-cited, bilingual (Arabic/English) streaming SSE chat.",
        b("Designed a Claude-as-judge reward pipeline") + " (3C3H metric) and NLI-based evaluation guardrails, "
        "including faithfulness/groundedness scoring, Recall@5, MRR, and prompt-injection defenses, that took "
        "Yehia R1 to " + b("#1 on the AraGen Leaderboard") + " (0.5B–25B).",
        b("Led multi-agent orchestration") + " (LangGraph, CrewAI) with tool-calling and multi-step planning to "
        "automate document analysis, bid/no-bid decisions, and proposal generation for GCC enterprise clients, "
        "replacing manual analyst workflows.",
        b("Owned the production stack end to end") + " and set engineering standards for testing and deployment: "
        "Docker Compose, nginx/TLS, LangSmith tracing, full Prometheus/Grafana/Loki observability, and a 600+ test "
        "suite with CI/CD.",
    ])

    # --- CORRECTED BLOCK 1: Aretec, matching the live LinkedIn record ---
    role(st, "Generative AI Consultant, Aretec &#183; Lahore, Pakistan (Remote, Contract) | Jul 2023 to Aug 2024", [
        "Built end-to-end AI recruitment automation (candidate sourcing, resume screening, AI-conducted interviews, "
        "and scheduling), cutting manual hiring overhead for staffing firms.",
        "Shipped AutoRec, a recruitment-automation SaaS: FastAPI + Celery/Redis scraping backend, LangChain/Gemini "
        "extraction layer, WebSocket-streamed job progress, tiered Stripe billing, and an internationalized Next.js frontend.",
    ])

    # --- CORRECTED BLOCK 2: COMET, matching the live LinkedIn record ---
    role(st, "Data Scientist, COMET Estimating LLC &#183; Remote (US) | Jul 2021 to Jun 2023", [
        "Built ML, NLP, and automation pipelines for a construction-industry data company: predictive analytics "
        "models, document-processing pipelines, and intelligent estimation tools.",
        "Hardened pipelines against messy real-world data: inconsistent formats, missing fields, and high-variance inputs.",
    ])

    # ---- ARCHITECTURE ----
    section(st, "SELECTED ARCHITECTURE WORK")
    for item in [
        b("ByanRAG 2.2 &#183; Multi-Tenant Arabic Document Management &amp; RAG Platform")
        + " (FastAPI, React, TypeScript, Qdrant, Casbin, Docker, Prometheus/Grafana/Loki): Enterprise document "
        "management system with grounded, source-cited Arabic-first Q&amp;A. Multi-tenant by design with "
        "per-organization data isolation, a 5-level Casbin RBAC hierarchy, and a 14-panel admin console; architected "
        "for on-premises deployment inside regulated and government networks. Hybrid retrieval combining dense "
        "embeddings, BM25 sparse search, RRF fusion, and CrossEncoder reranking, with NLI faithfulness scoring. "
        "Containerized with Docker Compose, deployed behind nginx with TLS and full observability, backed by a 600+ "
        "test suite and CI/CD.",
        b("Global Holman &#183; AI Government-Contracting Platform")
        + " (FastAPI, LangGraph, LlamaIndex, Next.js, Celery/Redis, async Postgres): End-to-end agentic platform that "
        "scrapes SAM.gov by NAICS code, ingests solicitation PDFs into a RAG pipeline, and runs LangGraph multi-agent "
        "workflows for requirement analysis, bid/no-bid decisions, and automated PDF proposal generation, over a "
        "provider-agnostic LLM layer, reusable platform APIs, and swappable vector stores.",
        b("Navid RAG ARC &#183; Arabic LLM RAG Service")
        + " (FastAPI, LangChain, Milvus, Celery, Arabic NLP, sentence-transformers): Modular Arabic-first RAG backend "
        "with hybrid BM25 + dense retrieval, Reciprocal Rank Fusion, multilingual reranking, and a tool-calling ReAct "
        "agent for multi-step reasoning and planning.",
    ]:
        st.append(Paragraph(item, S["bullet"], bulletText=DOT))

    # ---- MENTORSHIP & OSS ----
    section(st, "MENTORSHIP &amp; OPEN SOURCE")
    for item in [
        "Trained " + b("150+ professionals") + " and mentored engineers in Data Science, Machine Learning, AI "
        "Engineering, and system architecture across enterprise and independent settings.",
        b("LangChain") + " (92k+ stars): fixed malformed function-call parsing + added tests (merged PR).",
        b("RAGAS") + " (7k+ stars): multiple merged PRs, including bug fixes, multilingual (Arabic/CJK) support, and "
        "backward-compatible import aliases, plus tests.",
        b("Unstructured") + " (14k+ stars): PaddleOCR language-mapping fix + tests (merged PR).",
    ]:
        st.append(Paragraph(item, S["bullet"], bulletText=DOT))

    # ---- EDUCATION ----
    section(st, "EDUCATION")
    st.append(Paragraph(
        b("MS Artificial Intelligence") + " &#183; National University of Sciences and Technology (NUST), Pakistan, "
        "In Progress (2025–Present)", S["edu"]))
    st.append(Paragraph(
        b("BS Computer Science") + " &#183; Virtual University of Pakistan, Completed", S["edu"]))
    st.append(Paragraph(
        "Kaggle active contributor | Hugging Face model cards | AI / Data Science certifications | "
        "Former Student Representative", S["edu"]))

    doc.build(st)
    print(f"Wrote {path}")


if __name__ == "__main__":
    build("Mustafa_Shoukat_Resume_Teradata.pdf")
