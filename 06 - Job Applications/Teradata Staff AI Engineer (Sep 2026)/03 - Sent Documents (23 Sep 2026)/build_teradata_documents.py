"""Build the three Teradata application documents (23 Sep 2026).

Baseline: the first documents in "tera data" (Synopsis and Statement of Purpose)
and the Positioning Brief from this folder, which Mustafa approved.
Corrections applied to the baseline at his direction:
  * from Pakistan, based in Riyadh, Saudi Arabia; no phone number
  * no Text to SQL project; Yehia, not Mulhem
  * ByanRAG numbers: two organizations, 150+ users, 2 to 3 second answers on
    self hosted open source models, a team of four he leads and mentors
  * selected projects: Global Holman, VacantSeek 2.0, Whoza.ai (not PRE, not aroya)
  * a short MCP line (mcp-demo server with Arabic tools; MCP tools in his workflow)
Style rule: no separator characters (no dashes, middots, pipes, arrows, stars,
or horizontal rules) anywhere in the documents.
"""

from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).parent / "final"

INK = HexColor("#1a1a1a")
ACCENT = HexColor("#1F4E79")
MUTED = HexColor("#555555")

DATE = "23 September 2026"
ROLE = "Staff AI Engineer, Teradata"

S = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=17, leading=20,
                           textColor=INK, alignment=TA_CENTER),
    "tag": ParagraphStyle("tag", fontName="Helvetica", fontSize=9.5, leading=12,
                          textColor=ACCENT, alignment=TA_CENTER, spaceBefore=2),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.8, leading=11.5,
                              textColor=MUTED, alignment=TA_CENTER, spaceBefore=3),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=13, leading=16,
                            textColor=ACCENT, alignment=TA_LEFT, spaceBefore=14),
    "meta": ParagraphStyle("meta", fontName="Helvetica", fontSize=9, leading=12,
                           textColor=MUTED, spaceBefore=1, spaceAfter=8),
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=13,
                        textColor=ACCENT, spaceBefore=8, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9.6, leading=13.2,
                           textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6),
    "brief": ParagraphStyle("brief", fontName="Helvetica", fontSize=9.2, leading=12.4,
                            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=2.5),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9.4, leading=12.8,
                             textColor=INK, alignment=TA_JUSTIFY, leftIndent=14,
                             bulletIndent=2, spaceAfter=3.5),
}


def a(url, text):
    return f'<a href="{url}" color="#1155CC">{text}</a>'


def header(story, title):
    gap = "&nbsp;" * 4
    story.append(Paragraph("MUSTAFA SHOUKAT", S["name"]))
    story.append(Paragraph("Senior AI Engineer, Enterprise AI Architecture and Technical Leadership", S["tag"]))
    story.append(Paragraph(
        a("mailto:mustafashoukat.ai@gmail.com", "mustafashoukat.ai@gmail.com") + gap
        + a("https://linkedin.com/in/mustafashoukat", "linkedin.com/in/mustafashoukat") + gap
        + a("https://github.com/Mustafa-Shoukat1", "github.com/Mustafa-Shoukat1") + gap
        + "Riyadh, Saudi Arabia",
        S["contact"]))
    story.append(Paragraph(title, S["title"]))
    story.append(Paragraph(f"Prepared for {ROLE}, {DATE}", S["meta"]))


def doc(name, title):
    OUT.mkdir(exist_ok=True)
    return SimpleDocTemplate(str(OUT / name), pagesize=letter,
                             leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                             topMargin=0.45 * inch, bottomMargin=0.45 * inch,
                             title=f"Mustafa Shoukat, {title}", author="Mustafa Shoukat")


def bullets(story, items):
    for item in items:
        story.append(Paragraph(item, S["bullet"], bulletText="•"))


# ---------------------------------------------------------------- 1. Synopsis
def synopsis():
    st = []
    header(st, "Executive Synopsis")

    st.append(Paragraph("Profile", S["h"]))
    st.append(Paragraph(
        "Mustafa Shoukat is an AI engineer from Pakistan, based in Riyadh, Saudi Arabia, who operates at Staff level "
        "scope: he owns the architecture of distributed, fault tolerant AI platforms end to end, not just individual "
        "features. He has architected and shipped more than 20 production systems for enterprise and government "
        "grade clients across Saudi Arabia, the UAE, the United States and the United Kingdom, taking AI from "
        "prototype to hardened, observable, day to day production inside regulated environments.",
        S["body"]))

    st.append(Paragraph("Career trajectory", S["h"]))
    bullets(st, [
        "<b>Data Scientist, COMET Estimating.</b> ML, NLP and document processing pipelines hardened against messy "
        "real world construction data.",
        "<b>Generative AI Consultant, Aretec.</b> Production LLM and retrieval applications for business users, "
        "including fine tuning for accuracy and response speed.",
        "<b>Agentic AI Engineer, Watad (Navid), Riyadh.</b> Architecture owner and team lead for ByanRAG 2.2, the "
        "company's Arabic first enterprise RAG platform, and contributor to Yehia, Navid's Arabic LLM.",
        "<b>Independent AI Software Engineer.</b> Architects and ships production AI platforms for clients in four "
        "countries and advises organizations moving AI from pilot to operations.",
    ])

    st.append(Paragraph("Most relevant enterprise AI achievements", S["h"]))
    bullets(st, [
        "<b>ByanRAG 2.2.</b> Multi tenant, Arabic first RAG platform used by two organizations and more than 150 "
        "users, with isolated vector collections per organization, five levels of role based access on every "
        "endpoint, full audit logging, and on premises deployment for government networks. Cited answers in 2 to 3 "
        "seconds on self hosted open source models.",
        "<b>Yehia R1.</b> Designed the Claude as judge reward pipeline (3C3H metric) and NLI evaluation guardrails "
        "that helped take Yehia R1 to first place on the AraGen Leaderboard (0.5B to 25B).",
        "<b>Global Holman.</b> Agentic government contracting platform: LangGraph and CrewAI workflows that read "
        "SAM.gov solicitations, analyze requirements, support bid decisions and draft PDF proposals.",
        "<b>VacantSeek 2.0.</b> B2B real estate SaaS on AWS ECS; led a production hardening program of more than "
        "340 merged pull requests covering deployment, storage, security gates and monitoring.",
        "<b>Whoza.ai.</b> Live AI voice receptionist for UK tradespeople, built with a team of four on Twilio, "
        "FastAPI, React and Supabase.",
    ])

    st.append(Paragraph("Technical leadership", S["h"]))
    st.append(Paragraph(
        "He leads and mentors the ByanRAG team of four (an AI engineer, an LLM engineer, a frontend engineer and a "
        "DevOps and QA engineer), sets the standards for testing, deployment and model integration, backed by a "
        "suite of more than 600 tests, and has trained more than 150 professionals in data science, ML and AI "
        "engineering. He contributes to LangChain, RAGAS and Unstructured, released the open source tool ytkb, and "
        "builds with MCP, including his own MCP server with Arabic tools.",
        S["body"]))

    st.append(Paragraph("Core stack", S["h"]))
    st.append(Paragraph(
        "Python and Java, FastAPI, LangGraph, CrewAI and MCP, Qdrant, Milvus, FAISS and pgvector, PostgreSQL and "
        "MongoDB, Celery and Redis, Docker, AWS, GCP and Azure, Prometheus, Grafana and Loki.",
        S["body"]))
    doc("1_Mustafa_Shoukat_Executive_Synopsis.pdf", "Executive Synopsis").build(st)


# ---------------------------------------------------- 2. Positioning Brief
BRIEF = [
    ("AI platform architecture",
     "Design and deliver highly scalable AI products; architect for scalability, reliability and performance.",
     "I designed ByanRAG 2.2 end to end: FastAPI services, a React admin console with 14 panels, isolated Qdrant "
     "collections per organization, a Casbin access model with five role levels checked on every endpoint, and "
     "full audit logging. The platform is packaged for on premises and air gapped deployment.",
     "Two organizations and more than 150 users share one platform with strict data isolation, inside regulated "
     "networks where cloud services are not an option."),
    ("Retrieval augmented generation",
     "Apply LLMs and retrieval to enterprise data with answers people can trust.",
     "I built hybrid retrieval that combines dense embeddings with BM25, merges them with Reciprocal Rank Fusion "
     "and reranks with a CrossEncoder. It is tuned for Arabic first, bilingual content and streams answers with "
     "source citations. Quality is measured with Recall@5, MRR and NLI faithfulness scoring.",
     "Cited answers in 2 to 3 seconds over large document collections on self hosted open source models, with "
     "retrieval quality tracked as numbers rather than judged by eye."),
    ("Orchestration and agentic AI",
     "Experiment with and deliver agentic AI and large language model systems.",
     "I lead multi agent workflows in LangGraph and CrewAI with tool calling and multi step planning. On Global "
     "Holman, agents pull solicitations from SAM.gov by NAICS code, read the PDFs through a RAG pipeline, analyze "
     "requirements, support the bid decision and draft the proposal over a provider agnostic LLM layer. On "
     "Whoza.ai, a voice agent answers calls and qualifies jobs for UK tradespeople. I also build with MCP: my own "
     "MCP server with Arabic tools, and MCP connected tools in my daily development workflow.",
     "Analyst work that took days is now automated, and the choice of LLM provider stays open."),
    ("Distributed systems",
     "Strong grasp of distributed system patterns, data consistency and scale.",
     "I use Celery and Redis for background ingestion, scraping and agent jobs; async PostgreSQL for data; "
     "WebSockets and server sent events for streaming; idempotent, signature verified webhooks; and swappable "
     "vector stores behind one interface. On VacantSeek 2.0 I moved the platform onto AWS ECS with CodeBuild "
     "pipelines and S3 storage.",
     "Work keeps running when a worker fails, retries never create duplicate records, and components can be "
     "replaced without rewriting the system."),
    ("Production readiness",
     "Resolve performance bottlenecks, investigate production issues and maintain code quality.",
     "I run services in Docker behind nginx with TLS, with CI/CD and a suite of more than 600 tests on ByanRAG. "
     "Monitoring uses Prometheus, Grafana and Loki, with LangSmith tracing and Sentry. Security covers role based "
     "access, audit logs, guardrails and prompt injection defenses. On VacantSeek 2.0 I led more than 340 merged "
     "pull requests of production hardening, including build gates on critical vulnerabilities.",
     "Problems surface on dashboards and traces before users report them. The same evaluation discipline helped "
     "take Yehia R1 to first place on the AraGen Leaderboard."),
    ("Technical leadership",
     "Mentor engineers, influence architecture decisions and work independently.",
     "I lead and mentor the ByanRAG team of four (AI, LLM, frontend, and DevOps and QA) and own its architecture "
     "decisions, setting the standards for testing, deployment, code review and model integration. I have trained "
     "more than 150 professionals in data science and AI engineering, work directly with clients in four "
     "countries, and contribute to LangChain, RAGAS and Unstructured.",
     "The team ships to a shared standard, and I can carry a system from first design to production on my own."),
]


def brief():
    st = []
    header(st, "Executive Positioning Brief")
    st.append(Paragraph(
        "This brief maps my experience to the requirements of the Staff AI Engineer role. For each area it states "
        "what the role asks for, what I have done, and the result.",
        S["body"]))
    for i, (area, req, did, result) in enumerate(BRIEF, 1):
        st.append(KeepTogether([
            Paragraph(f"{i}. {area}", S["h"]),
            Paragraph(f"<b>The requirement.</b> {req}", S["brief"]),
            Paragraph(f"<b>What I did.</b> {did}", S["brief"]),
            Paragraph(f"<b>Result.</b> {result}", S["brief"]),
        ]))
    st.append(KeepTogether([
        Paragraph("Engineering foundations", S["h"]),
        Paragraph(
            "<b>Languages.</b> Python as my primary language, with Java, TypeScript and SQL. "
            "<b>APIs and data.</b> RESTful APIs in FastAPI; data modeling in PostgreSQL, MongoDB, Redis and pgvector "
            "with SQLAlchemy and Alembic. <b>Cloud and containers.</b> AWS, GCP and Azure, with Docker in production. "
            "<b>AI productivity tools.</b> I use GitHub Copilot and MCP connected coding assistants every day.",
            S["brief"]),
        Paragraph(
            "I run containers with Docker and AWS ECS and messaging with Celery and Redis; the same patterns carry "
            "directly to Kubernetes and Kafka.",
            S["brief"]),
    ]))
    st.append(Paragraph("Summary", S["h"]))
    st.append(Paragraph(
        "I bring proven, hands on ownership of the six areas this role centers on: platform architecture, RAG, "
        "agentic orchestration, distributed systems, production readiness and technical leadership, backed by "
        "systems that run in production today.",
        S["brief"]))
    doc("2_Mustafa_Shoukat_Executive_Positioning_Brief.pdf", "Executive Positioning Brief").build(st)


# ---------------------------------------------------- 3. Statement of Purpose
def purpose():
    st = []
    header(st, "Statement of Purpose")
    st.append(Paragraph("Dear Teradata Hiring Team,", S["body"]))
    for para in [
        "I am applying for the Staff AI Engineer role at Teradata because it sits exactly where I have chosen to build "
        "my career: at the meeting point of enterprise data and trustworthy, production grade AI. Teradata has spent "
        "decades earning the trust of enterprises with their most critical data, and its Enterprise Vector Store and "
        "Enterprise AgentStack show where that trust is heading next: agentic and generative AI on top of governed "
        "data, safely, at scale, and with answers people can rely on. That is the problem I have spent the last "
        "several years solving in production.",

        "I have owned AI platform architecture end to end, not individual features. I designed ByanRAG 2.2, a multi "
        "tenant, Arabic first RAG platform deployed on premises inside regulated government networks, with isolated "
        "data per organization, five levels of access control enforced on every endpoint, full audit logging, and a "
        "hybrid retrieval pipeline that returns source cited answers in 2 to 3 seconds on self hosted open source "
        "models. It now serves two organizations and more than 150 users. Alongside it, I built the Claude as judge "
        "evaluation pipeline, with faithfulness scoring and prompt injection defenses, that helped take Yehia R1 to "
        "first place on the AraGen Leaderboard. I care as much about proving an AI system is correct and safe as "
        "about making it work, because that is what separates a demo from something an enterprise will run.",

        "The technical leadership I bring is threefold. First, architecture ownership: I take systems from design "
        "through distributed, fault tolerant deployment, from Celery and Redis to AWS ECS, with full Prometheus, "
        "Grafana and Loki observability and more than 600 tests in CI/CD. Second, agentic systems at production "
        "quality: LangGraph, CrewAI and MCP orchestration with tool calling and multi step planning, applied to real "
        "workflows such as government contracting analysis on Global Holman and a live voice agent on Whoza.ai. "
        "Third, raising the people around me: I lead and mentor a team of four engineers on ByanRAG, set standards "
        "for testing, deployment and model integration, and have trained more than 150 professionals.",

        "What draws me to this role is the scale and seriousness of the problem. I have built enterprise AI for "
        "government and regulated clients across Saudi Arabia, the UAE, the US and the UK, where the requirements "
        "match Teradata's: reliability, security, data consistency, and answers that hold up under scrutiny. A Staff "
        "role, where I can shape architecture decisions, mentor engineers and resolve hard production problems, is "
        "where I can contribute the most. I am originally from Pakistan, based in Riyadh, and flexible on the working "
        "arrangement that suits the team.",

        "I would be glad to bring this experience to Teradata and help build the next generation of AI products on "
        "the enterprise data your customers already trust you with. Thank you for considering my application.",
    ]:
        st.append(Paragraph(para, S["body"]))
    st.append(Spacer(1, 4))
    st.append(Paragraph("Sincerely,", S["body"]))
    st.append(Paragraph("<b>Mustafa Shoukat</b>", S["body"]))
    doc("3_Mustafa_Shoukat_Statement_of_Purpose.pdf", "Statement of Purpose").build(st)


if __name__ == "__main__":
    synopsis()
    brief()
    purpose()
    print("Wrote", *sorted(p.name for p in OUT.glob("*.pdf")), sep="\n  ")
