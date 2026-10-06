# MUSTAFA SHOUKAT

**AI Platform Engineer | Enterprise RAG, Retrieval Architecture & Agentic Orchestration**

Riyadh, Saudi Arabia | mustafashoukat.ai@gmail.com | +92 309 3609261
LinkedIn: linkedin.com/in/mustafashoukat | GitHub: github.com/Mustafa-Shoukat1 | Hugging Face: huggingface.co/Mustafa-Shoukat1

---

## SUMMARY

AI platform engineer with 5+ years building retrieval and agentic systems that run in production, not in notebooks. Lead engineer on a multi-tenant Arabic and English enterprise RAG platform used by government and enterprise organisations operating under data-residency constraints: per-tenant isolated vector stores, five-level RBAC enforced server-side on every endpoint, hybrid dense and sparse retrieval with reciprocal rank fusion and cross-encoder reranking, NLI-based answer faithfulness scoring, and a full metrics, logging and audit stack behind a CI coverage gate. Delivered production AI systems for clients in Saudi Arabia, the UAE, the UK and the US.

---

## TECHNICAL SKILLS

**Retrieval and RAG:** Hybrid retrieval (dense + BM25 + reciprocal rank fusion), cross-encoder reranking, semantic and word-safe chunking, query reformulation, content-hash deduplication, context assembly, citation traceability, Arabic and multilingual retrieval pipelines

**Evaluation and Observability:** Ragas, recall@k, MRR, NDCG, NLI faithfulness scoring, golden-set construction, p95 latency and cost-per-query benchmarking, Prometheus, Grafana, Loki, LangSmith, MLflow, pytest, Playwright, Locust, Bandit

**LLM and Agents:** LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, tool calling, streaming SSE generation, multi-step workflows, LoRA, QLoRA, SFT, GRPO reward pipelines, LLM-as-judge design

**Vector and Data Stores:** Qdrant (per-tenant collections, HNSW tuning), FAISS, Milvus, Pinecone, ChromaDB, PostgreSQL 16, Redis 7

**Platform and APIs:** Python, TypeScript, SQL, FastAPI (multi-worker ASGI, background tasks), React 18, Next.js, Casbin policy engine, JWT with refresh and blacklist, layered rate limiting, reusable platform services consumed by multiple product surfaces

**Infrastructure and CI/CD:** Docker, multi-stage builds, Docker Compose service topologies, GitHub Actions, nginx with TLS termination, AWS, GCP, Azure, backup and restore automation

---

## EXPERIENCE

### AI Engineer, Navid (Navid-Watad group), Riyadh, Saudi Arabia | Jun 2026 to Present

- Own the architecture of the Arabic-first enterprise AI platform for GCC organisations that cannot let data leave their own infrastructure: multi-tenant retrieval, permission-aware access, and self-hosted deployment topology.
- Lead the retrieval and evaluation workstream: rebuilt the evaluation harness around a native-Arabic golden set so retrieval quality, faithfulness, latency and cost per query are measured before any release, replacing ad hoc spot checks.
- Set the engineering standards the platform ships against: coverage gate in CI, security scanning, reproducible container builds, and audit logging on every privileged action.

### AI Software Engineer, Watad Energy & Communications, Riyadh, Saudi Arabia | Nov 2023 to Jun 2026

- **Lead engineer and primary contributor on ByanRAG**, a multi-tenant Arabic and English document intelligence platform: a 7-service containerised topology (FastAPI, Qdrant, PostgreSQL 16, Redis, nginx, Prometheus, Grafana and Loki) with health checks, per-service resource limits and non-root containers.
- Designed the **4-stage retrieval pipeline** (embed, search, rerank, generate): Arabic-optimised 768-dimension dense embeddings combined with BM25 sparse vectors through reciprocal rank fusion, multilingual cross-encoder reranking, query reformulation, and configurable 64 to 4096 token chunking with Unicode normalisation.
- Built **NLI-based answer confidence scoring**: batched entailment inference between each generated answer and its source chunks, surfaced per answer, so users can see when an answer is not supported by the retrieved documents.
- Implemented **hard multi-tenant isolation**: a dedicated vector collection per organisation, three document scopes (organisation, department, private) enforced by payload filters, automatic query scoping on every database call, and cross-tenant reads returning 404 rather than 403 to prevent resource enumeration.
- Built the **five-level RBAC layer** on Casbin with 32 policy rules in PostgreSQL, a declarative FastAPI guard dependency, privilege-escalation prevention, and TTL-based policy reload for multi-worker consistency.
- Hardened the platform for regulated networks: JWT with short-lived access tokens, refresh rotation and a persisted logout blacklist, database-backed account lockout, 17 rate-limited endpoints plus nginx-level limits, six input validators, a 13-type upload whitelist with path-traversal defence, TLS via private CA, Fernet-encrypted credential storage with key rotation, and an exportable audit log.
- Instrumented the platform with **12+ custom Prometheus metrics** (RAG query latency, LLM request duration, active streams, connection-pool and cache behaviour) plus centralised Loki log aggregation and a live in-app log stream.
- Drove quality engineering across the stack: **617 backend tests** and 217 frontend tests, a 65% coverage gate, Ruff and ESLint, Bandit security scanning, Playwright end-to-end tests and Locust load testing, all enforced in GitHub Actions.
- Designed the **LLM-as-judge reward pipeline** (3C3H metric) used for GRPO training of Yehia-7B, which ranked first on the AraGen leaderboard for 0.5B to 25B models in February 2025.

### Generative AI Consultant, Aretec (Contract, Remote) | Jul 2023 to Aug 2024

- Built agentic document question-answering and workflow automation systems for enterprise clients using LangChain and LangGraph with custom tool orchestration and automated output validation.
- Delivered containerised RAG deployments on AWS and GCP with GitHub Actions CI/CD and automated regression testing.

### Data Scientist, COMET Estimating LLC (Remote, US) | Jul 2021 to Jun 2023

- Built Python data pipelines with validation and QA workflows, deployed on Google Cloud Run with CI/CD.
- Developed a lead-scoring system with human-in-the-loop review, pairing automated qualification with analyst verification.

---

## SELECTED SYSTEMS

- **VacantSeek** (B2B real-estate intelligence SaaS, 2026): primary engineer, 800+ commits and 350+ pull requests over a single delivery cycle, working directly against the client engineering account.
- **whoze.ai** (2026): AI product platform built with a four-engineer team, 500+ commits.
- **ytkb** (MIT, open source): CLI that converts video into a structured, searchable multilingual knowledge base; tested across six languages including Arabic. github.com/Mustafa-Shoukat1/ytkb
- **arabic-rag-bench** (open source): Gymnasium reinforcement-learning environment for training agents to diagnose Arabic RAG failures. Planted retrieval bugs, deterministic Recall@5 scoring, reward-hacking defences, 24 tests, CI on Python 3.10, 3.11 and 3.12.

---

## OPEN SOURCE CONTRIBUTIONS

- **Ragas** (evaluation framework): three pull requests submitted covering multilingual support for Arabic and CJK scripts, backward-compatible import aliases, and bug fixes, with 62 accompanying tests.
- **Unstructured** (document ingestion): PaddleOCR language-mapping fix with 6 tests.
- **LangChain**: fix for malformed function dictionaries in tool-call parsers, with 16 tests.
- **OpenWA**: merged contribution (PR #102).

---

## EDUCATION

**BS Computer Science**, Virtual University of Pakistan | Sep 2023 to Aug 2027 (in progress)
