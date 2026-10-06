"""Build the three Teradata application documents (23 Sep 2026).

Follows the positioning guide: Synopsis = career in 30 seconds, Positioning
Brief = requirement by requirement proof, Statement of Purpose = why this role.
Facts mirror the resume already accepted (Mustafa-Shoukat1.pdf).
Style rule from Mustafa: no separator characters (no dashes, middots, pipes,
arrows, stars, or horizontal rules) anywhere in the documents.
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
LINK = HexColor("#1155CC")

DATE = "23 September 2026"
ROLE = "Staff AI Engineer, Teradata (Job ID 220477)"

S = {
    "name": ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=17, leading=20,
                           textColor=INK, alignment=TA_CENTER),
    "tag": ParagraphStyle("tag", fontName="Helvetica", fontSize=9.5, leading=12,
                          textColor=ACCENT, alignment=TA_CENTER, spaceBefore=2),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.8, leading=11.5,
                              textColor=LINK, alignment=TA_CENTER, spaceBefore=3),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=13, leading=16,
                            textColor=ACCENT, alignment=TA_LEFT, spaceBefore=16),
    "meta": ParagraphStyle("meta", fontName="Helvetica", fontSize=9, leading=12,
                           textColor=MUTED, spaceBefore=1, spaceAfter=10),
    "h": ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=10.5, leading=13,
                        textColor=ACCENT, spaceBefore=9, spaceAfter=3),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10, leading=14,
                           textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7),
    "brief": ParagraphStyle("brief", fontName="Helvetica", fontSize=9.2, leading=12.4,
                            textColor=INK, alignment=TA_JUSTIFY, spaceAfter=2.5),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=10, leading=14,
                             textColor=INK, alignment=TA_JUSTIFY, leftIndent=14,
                             bulletIndent=2, spaceAfter=4),
}


def a(url, text):
    return f'<a href="{url}" color="#1155CC">{text}</a>'


def header(story, title):
    gap = "&nbsp;" * 6
    story.append(Paragraph("MUSTAFA SHOUKAT", S["name"]))
    story.append(Paragraph("Senior AI Engineer, Enterprise AI Architecture and Agentic Systems", S["tag"]))
    story.append(Paragraph(
        a("mailto:mustafashoukat.ai@gmail.com", "mustafashoukat.ai@gmail.com") + gap
        + a("https://wa.me/923093609261", "+92 309 3609261") + gap
        + a("https://linkedin.com/in/mustafashoukat", "linkedin.com/in/mustafashoukat") + gap
        + a("https://github.com/Mustafa-Shoukat1", "github.com/Mustafa-Shoukat1"),
        S["contact"]))
    story.append(Paragraph(title, S["title"]))
    story.append(Paragraph(f"Prepared for {ROLE}, {DATE}", S["meta"]))


def doc(name, title):
    OUT.mkdir(exist_ok=True)
    return SimpleDocTemplate(str(OUT / name), pagesize=letter,
                             leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                             topMargin=0.6 * inch, bottomMargin=0.6 * inch,
                             title=f"Mustafa Shoukat, {title}", author="Mustafa Shoukat")


# ---------------------------------------------------------------- 1. Synopsis
def synopsis():
    st = []
    header(st, "Executive Synopsis")
    st.append(Paragraph(
        "I am a Senior AI Engineer with more than five years of experience building AI systems that run in "
        "production. At Watad (Navid) in Riyadh I own the architecture of the company's Arabic enterprise RAG "
        "platform, and alongside that role I deliver contract work for clients in Saudi Arabia, the UAE, the "
        "United States and the United Kingdom. Across that work I have shipped more than 20 production systems.",
        S["body"]))
    st.append(Paragraph(
        "My path runs from models to platforms. I started as a Data Scientist at COMET Estimating, building ML "
        "and document processing pipelines on real construction data. At Aretec I moved into generative AI, "
        "delivering a Text to SQL application that lets business users query enterprise databases in plain "
        "English. At Watad and with my clients I grew from building features to owning whole platforms: the "
        "architecture, security, evaluation, deployment and the engineering standards the team works to.",
        S["body"]))
    st.append(Paragraph("Selected achievements", S["h"]))
    for item in [
        "<b>ByanRAG 2.2.</b> Designed and led a multi tenant, Arabic first RAG platform with isolated vector "
        "collections per organization, five levels of role based access enforced on every endpoint, full audit "
        "logging and hybrid retrieval, self hosted on premises for regulated networks and backed by more than "
        "600 automated tests.",
        "<b>Mulhem.</b> Contributed to Mulhem, the first Arabic large language model trained locally in Saudi Arabia.",
        "<b>Model quality.</b> Built the Claude as judge reward and evaluation pipeline behind Yehia R1, which "
        "reached first place on the AraGen Leaderboard in the 0.5B to 25B class.",
        "<b>ytkb.</b> Released ytkb as open source under the MIT licence, a command line tool that turns video "
        "into a searchable knowledge base in six languages, including Arabic.",
    ]:
        st.append(Paragraph(item, S["bullet"], bulletText="•"))
    st.append(Spacer(1, 4))
    st.append(Paragraph(
        "What I bring to Teradata is the discipline to take AI from a promising prototype to a secure, observable, "
        "well tested platform that an enterprise can rely on every day.",
        S["body"]))
    doc("1_Mustafa_Shoukat_Executive_Synopsis.pdf", "Executive Synopsis").build(st)


# ---------------------------------------------------- 2. Positioning Brief
BRIEF = [
    ("AI platform architecture",
     "Design and deliver highly scalable AI products; architect for scalability, reliability and performance.",
     "I designed ByanRAG 2.2 end to end: FastAPI services, a React admin console with 14 panels, isolated Qdrant "
     "collections per organization, a Casbin access model with five role levels checked on every endpoint, and "
     "full audit logging. The platform is packaged for on premises and air gapped deployment.",
     "Several organizations share one platform with strict data isolation, and it runs inside regulated networks "
     "where cloud services are not an option."),
    ("Retrieval augmented generation",
     "Apply LLMs and retrieval to enterprise data with answers people can trust.",
     "I built hybrid retrieval that combines dense embeddings with BM25, merges them with Reciprocal Rank Fusion "
     "and reranks with a CrossEncoder. It is tuned for Arabic first, bilingual content and streams answers with "
     "source citations. Quality is measured with Recall@5, MRR and NLI faithfulness scoring.",
     "Every answer points to its source document, and retrieval quality is tracked as numbers rather than judged "
     "by eye."),
    ("Orchestration and agentic AI",
     "Experiment with and deliver agentic AI and large language model systems.",
     "I lead multi agent workflows in LangGraph and CrewAI with tool calling and multi step planning. One example is "
     "a government contracting platform that pulls solicitations from SAM.gov by NAICS code, reads the PDFs "
     "through a RAG pipeline, analyses requirements, recommends whether to bid and drafts the proposal, all over "
     "a provider agnostic LLM layer. I also build voice and WhatsApp automation with Whisper transcription and "
     "human handover.",
     "Analyst work that took days is now automated, and the choice of LLM provider stays open."),
    ("Distributed systems",
     "Strong grasp of distributed system patterns, data consistency and scale.",
     "I use Celery and Redis for background ingestion, scraping and agent jobs; async PostgreSQL for data; "
     "WebSockets and server sent events for streaming; atomic message deduplication and fail closed HMAC "
     "verification on webhooks; and swappable vector stores behind one interface.",
     "Work keeps running when a worker fails, retries never create duplicate records, and components can be "
     "replaced without rewriting the system."),
    ("Production readiness",
     "Resolve performance bottlenecks, investigate production issues and maintain code quality.",
     "I run services in Docker Compose behind nginx with TLS, with CI/CD and a suite of more than 600 tests. "
     "Monitoring uses Prometheus, Grafana and Loki, with LangSmith tracing and Sentry. Security covers role based "
     "access, audit logs, guardrails and prompt injection defenses. I have traced and fixed real bottlenecks such "
     "as reranker latency.",
     "Problems surface on dashboards and traces before users report them. The same evaluation discipline took "
     "Yehia R1 to first place on the AraGen Leaderboard."),
    ("Technical leadership",
     "Mentor engineers, influence architecture decisions and work independently.",
     "I own architecture decisions on my platforms and set the team's standards for testing, deployment, code "
     "review and model integration. I mentor engineers, have trained more than 150 professionals in data science "
     "and AI engineering, work directly with clients in four countries, and contribute to LangChain, RAGAS and "
     "Unstructured.",
     "Teams ship to a shared standard, and I can carry a system from first design to production on my own."),
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
            "<b>AI productivity tools.</b> I use AI coding assistants such as GitHub Copilot every day.",
            S["brief"]),
        Paragraph(
            "My container orchestration so far has been Docker Compose rather than Kubernetes, and my messaging has "
            "been Celery and Redis rather than Kafka. The distributed patterns are the same, and I am ready to work "
            "in both from the start.",
            S["brief"]),
    ]))
    st.append(Paragraph("Summary", S["h"]))
    st.append(Paragraph(
        "I bring proven, hands on ownership of the six areas this role centers on: platform architecture, RAG, "
        "agentic orchestration, distributed systems, production readiness and technical leadership, backed by "
        "systems that run in production today.",
        S["body"]))
    doc("2_Mustafa_Shoukat_Executive_Positioning_Brief.pdf", "Executive Positioning Brief").build(st)


# ---------------------------------------------------- 3. Statement of Purpose
def purpose():
    st = []
    header(st, "Statement of Purpose")
    st.append(Paragraph("Dear Teradata Hiring Team,", S["body"]))
    for para in [
        "I am applying for the Staff AI Engineer role because it sits where I have chosen to build my career: "
        "trustworthy AI on top of enterprise data. Teradata has earned the trust of large enterprises with their "
        "most important data, and its recent work on the Enterprise Vector Store and on agentic access to that "
        "data through MCP shows where the platform is heading. Bringing retrieval and agents to governed data, at "
        "scale and with answers people can rely on, is the problem I have spent the last several years solving.",

        "The work that prepared me most is ByanRAG 2.2, an Arabic first RAG platform I designed for regulated "
        "organizations in Saudi Arabia. It had to keep each organization's data isolated, enforce access on every "
        "request, record every action, and still return fast, cited answers in two languages. Alongside it I built "
        "the evaluation pipeline that took Yehia R1 to first place on the AraGen Leaderboard. Both taught me that an "
        "enterprise AI system is judged on its reliability and its evidence, not on a demo.",

        "In my first months I would focus on three things. First, learning Teradata's platform, codebase and "
        "customers in depth before proposing change. Second, contributing working code early while helping to set "
        "clear baselines for evaluation, observability and testing on the AI products. Third, supporting the "
        "engineers around me through design reviews, code reviews and mentoring, as I have done in my current team.",

        "At this stage of my career I want to grow as a Staff engineer: shaping architecture across teams, raising "
        "engineering standards, and building AI products that enterprises trust. I would welcome the chance to do "
        "that at Teradata, and thank you for considering my application.",
    ]:
        st.append(Paragraph(para, S["body"]))
    st.append(Spacer(1, 6))
    st.append(Paragraph("Sincerely,", S["body"]))
    st.append(Paragraph("<b>Mustafa Shoukat</b>", S["body"]))
    doc("3_Mustafa_Shoukat_Statement_of_Purpose.pdf", "Statement of Purpose").build(st)


if __name__ == "__main__":
    synopsis()
    brief()
    purpose()
    print("Wrote", *sorted(p.name for p in OUT.glob("*.pdf")), sep="\n  ")
