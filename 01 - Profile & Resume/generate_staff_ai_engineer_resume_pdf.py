"""Generate Mustafa Shoukat's Staff / Principal AI Engineer resume as a two-page PDF.

Targeted at enterprise AI platform roles (RAG, retrieval architecture, agentic
orchestration). Source of truth for the wording:
    Mustafa_Shoukat_Resume_Staff_AI_Engineer.md

Every claim here is traceable to the ByanRAG 2.2 project description, the
8 Sep 2026 GitHub activity inventory, or the live LinkedIn record. Claims that
the 8 Sep audit could not verify (air-gapped deployment, Mulhem authorship,
merged upstream PRs, awards, MS NUST) are deliberately absent.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

BLACK = HexColor("#111111")
DARK_GRAY = HexColor("#2b2b2b")
MEDIUM_GRAY = HexColor("#555555")
ACCENT = HexColor("#1a5276")
LINK_COLOR = HexColor("#1a5276")
LINE_COLOR = HexColor("#c8c8c8")

S = {
    "name": ParagraphStyle(
        "name", fontName="Helvetica-Bold", fontSize=17, leading=20,
        textColor=BLACK, alignment=TA_CENTER, spaceAfter=3,
    ),
    "tagline": ParagraphStyle(
        "tagline", fontName="Helvetica", fontSize=9.5, leading=12,
        textColor=ACCENT, alignment=TA_CENTER, spaceAfter=4,
    ),
    "contact": ParagraphStyle(
        "contact", fontName="Helvetica", fontSize=8.2, leading=11,
        textColor=MEDIUM_GRAY, alignment=TA_CENTER, spaceAfter=1,
    ),
    "section": ParagraphStyle(
        "section", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
        textColor=ACCENT, spaceAfter=2.5, spaceBefore=5.5,
    ),
    "role": ParagraphStyle(
        "role", fontName="Helvetica-Bold", fontSize=9, leading=11.5,
        textColor=BLACK, spaceAfter=0, spaceBefore=4,
    ),
    "meta": ParagraphStyle(
        "meta", fontName="Helvetica-Oblique", fontSize=8, leading=10,
        textColor=MEDIUM_GRAY, spaceAfter=2.5,
    ),
    "summary": ParagraphStyle(
        "summary", fontName="Helvetica", fontSize=8.4, leading=11.4,
        textColor=DARK_GRAY, alignment=TA_JUSTIFY, spaceAfter=1,
    ),
    "skills": ParagraphStyle(
        "skills", fontName="Helvetica", fontSize=8, leading=10.8,
        textColor=DARK_GRAY, leftIndent=0, spaceAfter=2,
    ),
    "bullet": ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=8.3, leading=11,
        textColor=DARK_GRAY, leftIndent=11, bulletIndent=1, spaceAfter=2.1,
        bulletFontName="Helvetica", bulletFontSize=8.3,
    ),
    "compact": ParagraphStyle(
        "compact", fontName="Helvetica", fontSize=8.1, leading=10.6,
        textColor=DARK_GRAY, leftIndent=11, bulletIndent=1, spaceAfter=2.2,
        bulletFontName="Helvetica", bulletFontSize=8.1,
    ),
    "edu": ParagraphStyle(
        "edu", fontName="Helvetica", fontSize=8.4, leading=11,
        textColor=DARK_GRAY, spaceAfter=1,
    ),
}

BULLET = "•"


def link(url, text):
    return f'<a href="{url}" color="#{LINK_COLOR.hexval()[2:]}"><u>{text}</u></a>'


def b(text):
    return f"<b>{text}</b>"


def rule(story, thickness=0.5, before=2, after=2):
    story.append(HRFlowable(width="100%", thickness=thickness, color=LINE_COLOR,
                            spaceBefore=before, spaceAfter=after))


def job(story, title, meta, bullets, style="bullet"):
    """A role heading kept together with its first bullet, then the rest."""
    head = [Paragraph(title, S["role"]), Paragraph(meta, S["meta"]),
            Paragraph(bullets[0], S[style], bulletText=BULLET)]
    story.append(KeepTogether(head))
    for line in bullets[1:]:
        story.append(Paragraph(line, S[style], bulletText=BULLET))


def build(output_path):
    doc = SimpleDocTemplate(
        output_path, pagesize=letter,
        leftMargin=0.6 * inch, rightMargin=0.6 * inch,
        topMargin=0.45 * inch, bottomMargin=0.45 * inch,
        title="Mustafa Shoukat - AI Platform Engineer",
        author="Mustafa Shoukat",
        subject="Resume: Enterprise RAG, Retrieval Architecture and Agentic Orchestration",
    )
    story = []

    # ---------------- HEADER ----------------
    story.append(Paragraph("MUSTAFA SHOUKAT", S["name"]))
    story.append(Paragraph(
        "AI Platform Engineer  |  Enterprise RAG, Retrieval Architecture &amp; Agentic Orchestration",
        S["tagline"]))
    story.append(Paragraph(
        "Riyadh, Saudi Arabia  |  "
        + link("mailto:mustafashoukat.ai@gmail.com", "mustafashoukat.ai@gmail.com")
        + "  |  " + link("https://wa.me/923093609261", "+92 309 3609261"),
        S["contact"]))
    story.append(Paragraph(
        link("https://linkedin.com/in/mustafashoukat", "linkedin.com/in/mustafashoukat")
        + "  |  " + link("https://github.com/Mustafa-Shoukat1", "github.com/Mustafa-Shoukat1")
        + "  |  " + link("https://huggingface.co/Mustafa-Shoukat1", "huggingface.co/Mustafa-Shoukat1"),
        S["contact"]))
    rule(story, thickness=0.9, before=4, after=1)

    # ---------------- SUMMARY ----------------
    story.append(Paragraph("SUMMARY", S["section"]))
    story.append(Paragraph(
        "AI platform engineer with 5+ years building retrieval and agentic systems that run in "
        "production, not in notebooks. Lead engineer on a multi-tenant Arabic and English enterprise "
        "RAG platform used by government and enterprise organisations operating under data-residency "
        "constraints: per-tenant isolated vector stores, five-level RBAC enforced server-side on every "
        "endpoint, hybrid dense and sparse retrieval with reciprocal rank fusion and cross-encoder "
        "reranking, NLI-based answer faithfulness scoring, and a full metrics, logging and audit stack "
        "behind a CI coverage gate. Delivered production AI systems for clients in Saudi Arabia, the "
        "UAE, the UK and the US.",
        S["summary"]))
    rule(story)

    # ---------------- SKILLS ----------------
    story.append(Paragraph("TECHNICAL SKILLS", S["section"]))
    skills = [
        ("Retrieval &amp; RAG",
         "Hybrid retrieval (dense + BM25 + reciprocal rank fusion), cross-encoder reranking, semantic and "
         "word-safe chunking, query reformulation, content-hash deduplication, context assembly, citation "
         "traceability, Arabic and multilingual retrieval pipelines"),
        ("Evaluation &amp; Observability",
         "Ragas, recall@k, MRR, NDCG, NLI faithfulness scoring, golden-set construction, p95 latency and "
         "cost-per-query benchmarking, Prometheus, Grafana, Loki, LangSmith, MLflow, pytest, Playwright, "
         "Locust, Bandit"),
        ("LLM &amp; Agents",
         "LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, tool calling, streaming SSE generation, "
         "multi-step workflows, LoRA, QLoRA, SFT, GRPO reward pipelines, LLM-as-judge design"),
        ("Vector &amp; Data Stores",
         "Qdrant (per-tenant collections, HNSW tuning), FAISS, Milvus, Pinecone, ChromaDB, PostgreSQL 16, Redis 7"),
        ("Platform &amp; APIs",
         "Python, TypeScript, SQL, FastAPI (multi-worker ASGI, background tasks), React 18, Next.js, Casbin "
         "policy engine, JWT with refresh and blacklist, layered rate limiting, reusable platform services "
         "consumed by multiple product surfaces"),
        ("Infrastructure &amp; CI/CD",
         "Docker, multi-stage builds, Docker Compose service topologies, GitHub Actions, nginx with TLS "
         "termination, AWS, GCP, Azure, backup and restore automation"),
    ]
    for label, body in skills:
        story.append(Paragraph(f"{b(label)}: {body}", S["skills"]))
    rule(story)

    # ---------------- EXPERIENCE ----------------
    story.append(Paragraph("EXPERIENCE", S["section"]))

    job(story,
        "AI Engineer, Navid (Navid-Watad group)",
        "Riyadh, Saudi Arabia  |  Jun 2026 to Present",
        [
            "Own the architecture of the Arabic-first enterprise AI platform for GCC organisations that "
            "cannot let data leave their own infrastructure: multi-tenant retrieval, permission-aware "
            "access, and self-hosted deployment topology.",
            "Lead the retrieval and evaluation workstream: rebuilt the evaluation harness around a "
            "native-Arabic golden set so retrieval quality, faithfulness, latency and cost per query are "
            "measured before any release, replacing ad hoc spot checks.",
            "Set the engineering standards the platform ships against: coverage gate in CI, security "
            "scanning, reproducible container builds, and audit logging on every privileged action.",
        ])

    job(story,
        "AI Software Engineer, Watad Energy &amp; Communications",
        "Riyadh, Saudi Arabia  |  Nov 2023 to Jun 2026",
        [
            b("Lead engineer and primary contributor on ByanRAG") + ", a multi-tenant Arabic and English "
            "document intelligence platform: a 7-service containerised topology (FastAPI, Qdrant, "
            "PostgreSQL 16, Redis, nginx, Prometheus, Grafana and Loki) with health checks, per-service "
            "resource limits and non-root containers.",
            "Designed the " + b("4-stage retrieval pipeline") + " (embed, search, rerank, generate): "
            "Arabic-optimised 768-dimension dense embeddings combined with BM25 sparse vectors through "
            "reciprocal rank fusion, multilingual cross-encoder reranking, query reformulation, and "
            "configurable 64 to 4096 token chunking with Unicode normalisation.",
            "Built " + b("NLI-based answer confidence scoring") + ": batched entailment inference between "
            "each generated answer and its source chunks, surfaced per answer, so users can see when an "
            "answer is not supported by the retrieved documents.",
            "Implemented " + b("hard multi-tenant isolation") + ": a dedicated vector collection per "
            "organisation, three document scopes (organisation, department, private) enforced by payload "
            "filters, automatic query scoping on every database call, and cross-tenant reads returning 404 "
            "rather than 403 to prevent resource enumeration.",
            "Built the " + b("five-level RBAC layer") + " on Casbin with 32 policy rules in PostgreSQL, a "
            "declarative FastAPI guard dependency, privilege-escalation prevention, and TTL-based policy "
            "reload for multi-worker consistency.",
            "Hardened the platform for regulated networks: JWT with short-lived access tokens, refresh "
            "rotation and a persisted logout blacklist, database-backed account lockout, 17 rate-limited "
            "endpoints plus nginx-level limits, six input validators, a 13-type upload whitelist with "
            "path-traversal defence, TLS via private CA, Fernet-encrypted credential storage with key "
            "rotation, and an exportable audit log.",
            "Instrumented the platform with " + b("12+ custom Prometheus metrics") + " (RAG query latency, "
            "LLM request duration, active streams, connection-pool and cache behaviour) plus centralised "
            "Loki log aggregation and a live in-app log stream.",
            "Drove quality engineering across the stack: " + b("617 backend tests") + " and 217 frontend "
            "tests, a 65% coverage gate, Ruff and ESLint, Bandit security scanning, Playwright end-to-end "
            "tests and Locust load testing, all enforced in GitHub Actions.",
            "Designed the " + b("LLM-as-judge reward pipeline") + " (3C3H metric) used for GRPO training of "
            "Yehia-7B, which ranked first on the AraGen leaderboard for 0.5B to 25B models in February 2025.",
        ])

    job(story,
        "Generative AI Consultant, Aretec",
        "Contract, Remote  |  Jul 2023 to Aug 2024",
        [
            "Built agentic document question-answering and workflow automation systems for enterprise "
            "clients using LangChain and LangGraph with custom tool orchestration and automated output "
            "validation.",
            "Delivered containerised RAG deployments on AWS and GCP with GitHub Actions CI/CD and "
            "automated regression testing.",
        ], style="compact")

    job(story,
        "Data Scientist, COMET Estimating LLC",
        "Remote (US)  |  Jul 2021 to Jun 2023",
        [
            "Built Python data pipelines with validation and QA workflows, deployed on Google Cloud Run "
            "with CI/CD.",
            "Developed a lead-scoring system with human-in-the-loop review, pairing automated "
            "qualification with analyst verification.",
        ], style="compact")

    rule(story)

    # ---------------- SELECTED SYSTEMS ----------------
    story.append(Paragraph("SELECTED SYSTEMS", S["section"]))
    systems = [
        b("VacantSeek") + " (B2B real-estate intelligence SaaS, 2026): primary engineer, 800+ commits and "
        "350+ pull requests over a single delivery cycle, working directly against the client engineering account.",
        b("whoze.ai") + " (2026): AI product platform built with a four-engineer team, 500+ commits.",
        b("ytkb") + " (MIT, open source): CLI that converts video into a structured, searchable multilingual "
        "knowledge base; tested across six languages including Arabic. "
        + link("https://github.com/Mustafa-Shoukat1/ytkb", "github.com/Mustafa-Shoukat1/ytkb"),
        b("arabic-rag-bench") + " (open source): Gymnasium reinforcement-learning environment for training "
        "agents to diagnose Arabic RAG failures. Planted retrieval bugs, deterministic Recall@5 scoring, "
        "reward-hacking defences, 24 tests, CI on Python 3.10, 3.11 and 3.12.",
    ]
    for item in systems:
        story.append(Paragraph(item, S["compact"], bulletText=BULLET))
    rule(story)

    # ---------------- OPEN SOURCE ----------------
    story.append(Paragraph("OPEN SOURCE CONTRIBUTIONS", S["section"]))
    oss = [
        b("Ragas") + " (evaluation framework): three pull requests submitted covering multilingual support "
        "for Arabic and CJK scripts, backward-compatible import aliases, and bug fixes, with 62 accompanying tests.",
        b("Unstructured") + " (document ingestion): PaddleOCR language-mapping fix with 6 tests.",
        b("LangChain") + ": fix for malformed function dictionaries in tool-call parsers, with 16 tests.",
        b("OpenWA") + ": merged contribution (PR #102).",
    ]
    for item in oss:
        story.append(Paragraph(item, S["compact"], bulletText=BULLET))
    rule(story)

    # ---------------- EDUCATION ----------------
    story.append(Paragraph("EDUCATION", S["section"]))
    story.append(Paragraph(
        b("BS Computer Science") + ", Virtual University of Pakistan  |  Sep 2023 to Aug 2027 (in progress)",
        S["edu"]))

    doc.build(story)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    build("Mustafa_Shoukat_Resume_Staff_AI_Engineer.pdf")
