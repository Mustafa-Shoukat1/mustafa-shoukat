# Mustafa Shoukat — Private Work Portfolio & Profile Kit
### Senior AI / Software Engineer · 6 Years Experience · Agentic AI · RAG · Full-Stack SaaS

> **Scope of this file:** Your **private / client projects only** (14 projects). These are **private repos** — visitors *cannot* open them on GitHub, so this content is for your **LinkedIn descriptions, CV, and interview talking points**, and as the *text* of your GitHub profile README.
> 👉 Your **public, pinnable** projects live in a separate file: **`Mustafa-Shoukat-Public-Portfolio.md`**.
>
> **How to use it:**
> 1. Read each project. Tick the `[ ]` box for the ones you want to feature.
> 2. Copy the **senior blurbs** straight into LinkedIn / your CV.
> 3. My recommendation rating: ⭐⭐⭐ = top showcase · ⭐⭐ = strong · ⭐ = good supporting project.

---

## 0. At-a-Glance Summary (Private Projects)

| # | Project | Category | Core Stack | Rating |
|---|---------|----------|-----------|--------|
| 1 | ByanRAG 2.2 | Agentic AI / RAG | FastAPI · React · Qdrant · Yehia R1 [UNVERIFIED, see DECISIONS NEEDED #16] (1st open-source Arabic SLM on leaderboard) · Casbin | ⭐⭐⭐ |
| 2 | Global Holman GovCon AI | Agentic AI / RAG | FastAPI · LangGraph · CrewAI · Next.js | ⭐⭐⭐ |
| 3 | Navid RAG ARC | Agentic AI / RAG | FastAPI · LangChain · Milvus · Celery | ⭐⭐⭐ |
| 4 | RAG on-Premises | Agentic AI / RAG | FastAPI · Next.js 15 · Milvus · S3/Azure | ⭐ |
| 6 | whoze.ai (AI Voice for Trades) | AI SaaS Product | FastAPI · Twilio · Gemini · React 19 | ⭐⭐ |
| 8 | ToaWAR-X Marketing Agent | AI SaaS Product | Python · Streamlit · Tweepy · OpenAI | ⭐⭐ |
| 9 | Invoice-Agent (WhatsApp) | AI SaaS Product | FastAPI · WhatsApp API · OpenAI · Supabase | ⭐ |
| 10 | Property Management CRM | CRM / Ops Platform | React · Express · Drizzle · OpenAI · Google | ⭐⭐⭐ |
| 11 | Rental Central | CRM / Ops Platform | Next.js 15 · Prisma · NextAuth · IMAP | ⭐⭐ |
| 12 | AutoRec (AI Scraper SaaS) | CRM / Ops Platform | FastAPI · Celery · Gemini · Next.js · Stripe | ⭐⭐ |
| 13 | Watad Energy Web | Corporate Web | Django 4 · PostgreSQL · Azure Blob | ⭐ |
| 14 | CodAgenticAI.com | Corporate Web | React · Vite · GSAP · Pixi.js · Babylon.js | ⭐ |

**Account:** [github.com/Mustafa-Shoukat1](https://github.com/Mustafa-Shoukat1) · 159 repositories as of 22 Jun 2026 (74 public / 85 private; 76 public on 8 Sep 2026) · primary domains: **Agentic AI, RAG systems, AI SaaS, full-stack web**.

---

## 1. Agentic AI & RAG Platforms

These are your signature work — production RAG systems and multi-agent platforms.

### `[ ]` ⭐⭐⭐ 1. ByanRAG 2.2 — Multi-Tenant Arabic RAG Platform
- **Repo:** `ByanRAG-2.2` · 🔒 private · Python + React/TypeScript · ~29 MB
- **One-liner:** An enterprise-grade, multi-tenant Arabic-first document Q&A platform with role-based access, hybrid retrieval, and full production deployment.
- **What it is:** A production RAG system for contact-centre and regulatory operations: teams upload PDFs/Word/Excel/PowerPoint and ask grounded questions in Arabic or English with cited sources. It enforces strict multi-tenant isolation (per-organization Qdrant collections), a 5-level Casbin RBAC hierarchy on every endpoint, and full audit logging. Ships as a complete deployable product — Docker Compose, nginx, Alembic migrations, a live TLS demo, nightly Postgres/Qdrant backups, and Prometheus/Grafana/Loki monitoring — with a 600+ test suite. This is the most mature platform in the portfolio.
- **Tech stack:** Python 3.13, FastAPI (multi-worker uvicorn/uvloop), React 18 + TypeScript 5; Qdrant vector store; **Yehia R1 [UNVERIFIED, see DECISIONS NEEDED #16]** (the first open-source Arabic SLM on the leaderboard) via HuggingFace Inference; `gte-multilingual-reranker` reranker; `mDeBERTa` XNLI for answer-faithfulness scoring; Docling + semchunk + tiktoken ingestion; pytesseract OCR; SQLAlchemy/Alembic; Casbin RBAC; JWT/bcrypt/pyotp; Docker, nginx, GitHub Actions, gitleaks.
- **Key features:**
  - Multi-organization tenancy with isolated per-org vector collections
  - Hybrid retrieval: dense semantic + sparse BM25 with Reciprocal Rank Fusion + multilingual reranking
  - Casbin RBAC (Viewer → Super Admin) with privilege-escalation prevention
  - NLI-based answer-confidence scoring with color-coded faithfulness bars
  - Streaming SSE chat with inline citations and AR/EN language matching
  - Bilingual RTL/LTR UI + 14-page admin panel (users, departments, orgs, policies, API keys, audit, analytics, live logs, health, security)
- **Senior blurb:** *I architected ByanRAG, a multi-tenant Arabic-first RAG platform serving grounded, cited document answers with org-isolated Qdrant collections and Casbin-enforced access control on every endpoint. I designed the hybrid dense+BM25 retrieval with RRF and multilingual reranking, added NLI-based answer-faithfulness scoring, and shipped it as a hardened Docker/nginx deployment with CI/CD, nightly backups, and full Prometheus/Grafana/Loki observability.*

### `[ ]` ⭐⭐⭐ 2. Global Holman — AI Government-Contracting Platform
- **Repo:** `Global-Holman-Services-Inc` · 🔒 private · TypeScript + Python (~50/50) · ~14 MB
- **One-liner:** An agentic AI platform that monitors SAM.gov for government contract opportunities, analyzes solicitations with RAG, and auto-generates proposals and subcontractor outreach.
- **What it is:** Your most ambitious project — an end-to-end AI system for government-contracting (GovCon) businesses. It periodically scrapes SAM.gov (filtered by NAICS codes and notice type), ingests the PDF solicitations, and runs a RAG + multi-agent pipeline for requirement analysis, bid/no-bid decisioning, subcontractor identification, and automated proposal generation, with an email alert/scheduler layer. Populated `contract_analysis/` and `proposals/` output dirs show it produces real artifacts.
- **Tech stack:** FastAPI + SQLModel/SQLAlchemy + Alembic, async Postgres (asyncpg), Celery + Redis + APScheduler; **CrewAI** (multi-agent) + **LangGraph** (stateful agent graphs) + **LlamaIndex** (document RAG); provider-agnostic LLM layer (OpenAI, Gemini/Vertex, Groq, Cohere, HuggingFace); swappable vector stores (ChromaDB, FAISS, Qdrant, Weaviate) + BM25 hybrid; unstructured/PyMuPDF/llama-parse + WeasyPrint PDF rendering; Next.js frontend; Docker, Nginx, PM2, Supabase, CI.
- **Key features:**
  - Periodic SAM.gov scraping by NAICS code & notice type with PDF download
  - Scheduled email alerts for new matching opportunities
  - RAG-based solicitation/requirement analysis over ingested contracts
  - Multi-agent proposal writer that drafts and renders full PDF proposals
  - Conversational WebSocket AI assistant + bid/no-bid decision support
- **Senior blurb:** *I architected an end-to-end agentic AI platform for government contracting that scrapes SAM.gov by NAICS/notice type, ingests solicitation PDFs into a RAG pipeline, and runs CrewAI/LangGraph multi-agent workflows for requirement analysis, bid/no-bid decisions, and automated proposal generation. I designed a provider-agnostic LLM service (OpenAI/Gemini/Groq/Cohere) over swappable vector stores (Chroma/FAISS/Qdrant/Weaviate) with hybrid BM25 retrieval, on a FastAPI + async-Postgres + Celery/Redis backend.*

### `[ ]` ⭐⭐⭐ 3. Navid RAG ARC — Arabic LLM RAG Service
- **Repo:** `Navid-RAG-ARC` · 🔒 private · Python · ~4.5 MB · 1★
- **One-liner:** A modular, Arabic-focused RAG backend with hybrid search, a ReAct reasoning agent, and Milvus vector storage, served over FastAPI.
- **What it is:** A state-of-the-art Arabic LLM RAG service organized as a clean, modular backend. It separates concerns into domain apps (auth, chat, organizations, users, admin, rag) and a `core/` library covering chunking, language handling, LLM access, vector store management, search, and reasoning. Retrieval is hybrid (BM25 + dense) with rank fusion + reranker, plus a ReAct-style agent for multi-step reasoning. Uses Celery for async work, built to run with Milvus and Nginx.
- **Tech stack:** Python 3.12, FastAPI, LangChain ecosystem (community/core/OpenAI/Cohere/HuggingFace/Milvus/Chroma), Milvus + pymilvus (FAISS/Chroma options), sentence-transformers, rank-bm25, Celery, SQLModel, PyMuPDF/docx2txt/unstructured ingestion, Arabic NLP (arabic-reshaper, python-bidi, langdetect), JWT auth; Docker, Nginx, uv.
- **Key features:**
  - Hybrid BM25 + dense retrieval with rank fusion + reranking
  - ReAct reasoning agent for multi-step query handling
  - Modular vector-store layer (connection, indexing, singleton manager) over Milvus
  - Arabic-first text processing (reshaping, bidi, language detection)
  - Celery-based async/background task processing
- **Senior blurb:** *I designed Navid-RAG, a modular Arabic RAG backend on FastAPI with a hybrid BM25+dense retrieval pipeline, rank fusion, and reranking over a Milvus vector store. I added a ReAct reasoning agent for multi-step queries and Celery-driven async processing, structuring the core into cleanly separated chunking, search, reasoning, and vector-store subsystems.*

### `[ ]` ⭐ 4. RAG on-Premises — Resumable-Ingestion RAG App
- **Repo:** `RAG_on_Premises-` · 🔒 private · TypeScript + Python · ~1.2 MB *(active WIP)*
- **One-liner:** A self-hostable RAG application centered on resumable, chunked large-file uploads with a FastAPI backend and a Next.js 15 frontend.
- **What it is:** A self-hosted RAG platform focused on robust ingestion: asynchronous chunked uploads with real-time SSE progress, pluggable storage (local/S3/Azure Blob), and a LangChain + Milvus retrieval layer, with a polished Next.js 15 / Radix UI frontend. Roadmap/TODO files mark it as an early-stage WIP.
- **Tech stack:** Python 3.13, FastAPI (SSE), LangChain (Milvus/OpenAI), Milvus, boto3 (S3) + azure-storage-blob, PyMuPDF/pypdf/unstructured, psutil; Next.js 15, React 19, Tailwind, Radix UI/shadcn.
- **Key features:** chunked uploads for large files · SSE progress streaming · pluggable cloud/on-prem storage · LangChain + Milvus retrieval · system-resource monitoring.
- **Senior blurb:** *I built an on-premises RAG platform focused on reliable ingestion — asynchronous chunked uploads with real-time SSE progress and a pluggable storage layer across local disk, S3, and Azure Blob — pairing a modular FastAPI backend with LangChain/Milvus retrieval and a modern Next.js 15 frontend.*

---

## 2. AI SaaS Products

Consumer- and business-facing AI products with billing, auth, and real integrations.

### `[ ]` ⭐⭐ 6. whoze.ai — AI Voice Platform for UK Tradespeople
- **Repo:** `whoze.ai` · 🔒 private · TypeScript + Python · ~3 MB *(in build, not launched; whoze.ai had no DNS record on 8 Sep 2026)*
- **One-liner:** An AI voice-agent platform for UK tradespeople that answers calls, qualifies jobs, and handles bookings/quotes.
- **What it is:** A monorepo AI voice platform for plumbers, electricians, etc. A FastAPI backend integrates Twilio telephony, Stripe billing, and Google Gemini, with scheduling and PDF generation; a Vite + React 19 SPA runs Gemini conversations over a realtime websocket voice layer. Disciplined, documentation-driven build with go-live gating.
- **Tech stack:** FastAPI, Pydantic v2, Twilio, Stripe, boto3 (AWS), APScheduler, slowapi, JWT/cryptography; React 19 + Vite 6, Tailwind v4, Supabase JS, `@google/genai` (Gemini), jsPDF, an Express/`ws` realtime server; Docker, Netlify, AWS, Playwright + Vitest.
- **Key features:** AI voice agent (Twilio + websocket realtime) · JWT auth with rate limiting · Gemini conversational AI · Stripe billing + Supabase persistence · scheduling + PDF quotes/invoices · GitHub Actions CI + AWS deploy.
- **Senior blurb:** *I architected whoze.ai, an AI voice platform for UK tradespeople, with a FastAPI backend integrating Twilio telephony, Stripe billing, and AWS, and a React 19 frontend running Gemini-powered conversations over a realtime websocket layer — structured as a clean backend/frontend/infra monorepo with JWT auth, rate limiting, scheduling, and CI.*

### `[ ]` ⭐⭐ 8. ToaWAR-X — AI Marketing Agent for X (Twitter)
- **Repo:** `ToaWAR-X-Agent` · 🔒 private · Python · ~5.7 MB
- **One-liner:** A Streamlit AI marketing agent that scrapes X/Twitter, tracks influencers and keywords, and auto-generates & schedules categorized content and reports.
- **What it is:** A social-media automation platform for marketing on X. Beyond scraping, it runs an AI content pipeline that categorizes and summarizes posts and generates daily/weekly reports and persona-styled posts — backed by a robust scheduler with mutex locking, health monitoring, auto-recovery, and duplication prevention. Strong operational-reliability engineering.
- **Tech stack:** Python, Streamlit, SQLite, Tweepy (X API), OpenAI, Matplotlib, Pandas; organized into `core/`, ~18 `services/`, and `ai_pipelines/`.
- **Key features:** influencer/keyword management + scraping · AI categorize/summarize/title pipeline · automated daily/weekly reports + persona posts · mutex-protected scheduler with health checks & auto-recovery · duplication prevention · Streamlit dashboard with visualizations.
- **Senior blurb:** *I designed and built ToaWAR-X, an AI marketing agent for X that scrapes influencer/keyword activity via Tweepy and runs an OpenAI pipeline to categorize, summarize, and auto-generate daily and weekly reports and persona-styled posts. I focused heavily on operational reliability — a mutex-protected scheduler with health monitoring, auto-recovery, and duplication prevention, backed by multi-user, mutex, and scheduler-simulation test suites.*

### `[ ]` ⭐ 9. Invoice-Agent — WhatsApp Lead Assistant
- **Repo:** `Invoice-Agent` · 🔒 private · Python · ~0.65 MB *(lean prototype)*
- **One-liner:** A lightweight FastAPI WhatsApp assistant running a guided real-estate lead-qualification flow with an OpenAI fallback, Supabase persistence, and a built-in admin dashboard.
- **What it is:** A compact backend handling WhatsApp conversations for real-estate lead capture via a deterministic step-by-step flow with OpenAI-built replies, plus an HTML admin dashboard with human-handover toggling.
- **Tech stack:** Python, FastAPI, Uvicorn, httpx; OpenAI Responses API (`gpt-4.1-mini`); WhatsApp Meta Graph API (v25); Supabase/Postgres; Vercel.
- **Key features:** WhatsApp messaging + webhook verification · guided multi-intent flow · OpenAI reply building · Supabase lead/conversation persistence · embedded admin dashboard + human handover · chat-event logging.
- **Senior blurb:** *I built Invoice-Agent, a lightweight FastAPI WhatsApp assistant that qualifies real-estate leads through a guided conversational flow, layering OpenAI-generated replies over a deterministic step machine and persisting leads and chat events to Supabase, with a self-contained admin dashboard and human-handover control.*

---

## 3. CRM / Operations / Real-Estate Platforms

Full-stack business applications with multi-channel integrations.

### `[ ]` ⭐⭐⭐ 10. Property Management CRM — AI-Powered
- **Repo:** `Property-Management-CRM` · 🔒 private · TypeScript · ~18.5 MB
- **One-liner:** An AI-powered property-management CRM with a drag-and-drop lead pipeline, automated email follow-ups, calendar scheduling, and AI video/document analysis.
- **What it is:** A production-oriented CRM for property managers to capture, score, and convert leads. Combines a Kanban board with OpenAI-driven lead scoring and persona detection, two-way email automation (SMTP/IMAP with AI replies), Google-Calendar-synced scheduling with public booking links, and AI transcription/analysis of uploaded property videos. The most production-hardened CRM in the portfolio.
- **Tech stack:** React 18 + Vite + TypeScript + Tailwind + shadcn/Radix + TanStack Query; Node/Express + Drizzle ORM on PostgreSQL (Neon/Supabase) + optional Redis; OpenAI GPT; Google OAuth 2.0 / Calendar / Cloud Storage; SMTP/IMAP (nodemailer/imap) + fluent-ffmpeg; helmet, csrf-csrf, rate-limit, DOMPurify; Swagger, Vitest/Supertest, Pino.
- **Key features:** Kanban lead board with AI scoring & persona detection · automated email follow-ups + AI replies (IMAP/SMTP) · Google-Calendar-synced booking links · AI property-video transcription/analysis · document upload + AI matching · public lead-capture API + webhooks + analytics.
- **Senior blurb:** *I built an AI-powered property-management CRM end to end on a React/Vite frontend and a Node/Express + Drizzle/PostgreSQL backend, integrating OpenAI for lead scoring, automated email drafting, and property-video transcription. I designed the production layer myself — RBAC and audit middleware, CSRF/rate-limit/Helmet hardening, Redis caching with graceful fallback, Google OAuth/Calendar/Cloud Storage integrations, WebSockets, Swagger docs, and a full unit/API/smoke test suite.*

### `[ ]` ⭐⭐ 11. Rental Central — Property Management & Lead Platform
- **Repo:** `Rental-central` · 🔒 private · TypeScript · ~17.3 MB
- **One-liner:** A Next.js property-management and lead-generation platform with automated email-based lead ingestion and appointment scheduling.
- **What it is:** A unified platform for real-estate agents to import/manage listings, ingest leads automatically from email and other channels, schedule viewings, and track performance on a real-time dashboard. Integrates external property data (RapidAPI/Zillow) and self-hosted SMTP/IMAP for lead processing.
- **Tech stack:** Next.js 15 (App Router) + React 19 + TypeScript + Tailwind + shadcn; Prisma ORM (SQLite→Postgres); NextAuth.js; Zustand; TanStack Query; Zod; Recharts; node-cron; RapidAPI/Zillow + SMTP/IMAP.
- **Key features:** listing import (RapidAPI/Zillow) · automated email lead ingestion · viewing scheduling · dashboard + analytics · NextAuth security · cron background processing.
- **Senior blurb:** *I designed and built Rental Central, a Next.js 15 / TypeScript property-management and lead-generation platform with Prisma, NextAuth, Zustand, and TanStack Query — implementing automated email-based lead ingestion over self-hosted SMTP/IMAP, external property-data import from RapidAPI/Zillow, and cron-driven background processing feeding a real-time analytics dashboard.*

### `[ ]` ⭐⭐ 12. AutoRec — AI Web-Scraping SaaS
- **Repos:** `AutoRec` / `autorec-fe` (frontend) + `autorec-be` (backend) · 🔒 private · TypeScript + Python · 1★
- **One-liner:** An AI-driven web-scraping SaaS that extracts and structures contact/candidate data from sites at scale, with subscription billing and a real-time results UI.
- **What it is:** One product split across a FastAPI/Python backend and a Next.js frontend. Users submit URLs/batches; the backend scrapes target sites, normalizes addresses, and uses an LLM layer to parse/structure data, streaming progress over WebSockets. Tenant-aware SaaS with tiered subscription packages and Stripe billing.
- **Tech stack:** Backend — FastAPI + SQLModel + Alembic, **Celery + Redis** (distributed jobs), BeautifulSoup/aiohttp, `usaddress`, LangChain + langchain-google-genai (Gemini), JWT/passlib, slowapi, Gunicorn + Nginx + Docker Compose, WebSocket manager. Frontend — Next.js 14 + React 18 + TypeScript + Tailwind + Radix, Prisma/PostgreSQL, NextAuth, Zustand, next-intl, Stripe, Recharts.
- **Key features:** batch URL submission + queued scraping (Celery) · LLM extraction into structured records · real-time WebSocket progress · subscription tiers enforcing scrape/URL/page quotas · Stripe billing · internationalized Next.js UI.
- **Senior blurb:** *I architected AutoRec, an AI-powered web-scraping SaaS, as a FastAPI + Celery/Redis backend with WebSocket-streamed job progress and a LangChain/Gemini extraction layer that turns raw scraped HTML into structured contact data. I built the full subscription model — tiered quotas with Stripe billing — and an internationalized Next.js frontend, then containerized the system behind Nginx/Gunicorn for production.*

---

## 4. Corporate Web Platforms

### `[ ]` ⭐ 13. Watad Energy — Corporate Web Platform
- **Repo:** `Watad-Energy-web` · 🔒 private · Django + JS · ~65 MB
- **One-liner:** A Django-powered corporate website and lightweight CMS presenting Watad Energy's AI, automation, smart-city, and cybersecurity service lines.
- **What it is:** A server-rendered Django app and CMS organized into modular apps (clients, partners, applicants/careers, news, contact, core), with a TinyMCE admin, drag-and-drop ordering, and reCAPTCHA-protected forms.
- **Tech stack:** Python + Django 4, PostgreSQL, Gunicorn + WhiteNoise; Azure Blob Storage (django-storages), django-tinymce, django-admin-sortable, django-recaptcha, jet-reboot admin.
- **Key features:** modular corporate site · TinyMCE content management · drag-and-drop ordering · reCAPTCHA forms · Azure media storage + SEO sitemaps.
- **Senior blurb:** *I built the Watad Energy corporate web platform as a modular Django 4 application backed by PostgreSQL and Azure Blob Storage, with a TinyMCE-driven admin CMS, reCAPTCHA-secured forms, and a Gunicorn/WhiteNoise production deployment — structured so non-technical staff manage content independently.*

### `[ ]` ⭐ 14. CodAgenticAI.com — Agency Site + Admin Panel
- **Repo:** `CodAgenticAI.com` · 🔒 private · JavaScript · ~71 MB
- **One-liner:** A visually rich React/Vite marketing website with a self-service admin panel for managing site content.
- **What it is:** The public site for an AI agency/product — a React SPA with heavy interactive visuals (particles, mouse-trail, sound-wave/network animations) plus a built-in admin panel to manage blogs, services, founders, reviews, and industries without redeploying.
- **Tech stack:** React 18 + Vite 6, Tailwind 4, React Router 7, Axios; GSAP, Framer Motion, tsParticles, **Pixi.js, Babylon.js**; Jodit editor; Swiper/React Slick; Vercel.
- **Key features:** marketing pages · admin CRUD for blogs/services/founders/reviews/industries · rich interactive graphics · Jodit blog authoring · Vercel deploy.
- **Senior blurb:** *I designed and built CodAgenticAI.com, a React + Vite marketing platform with an immersive interactive UI layering GSAP, Framer Motion, tsParticles, Pixi.js, and Babylon.js, paired with a custom admin panel and Jodit editor so the team manages all content end to end.*

---

## 5. Master Skills List (for LinkedIn "Skills" + GitHub README)

**Languages:** Python · TypeScript · JavaScript · Rust · SQL · HTML/CSS

**AI / LLM:** OpenAI (GPT-4o / 4o-mini / 4.1-mini, Whisper, TTS) · Google Gemini / Vertex · Yehia R1 [UNVERIFIED, see DECISIONS NEEDED #16] (Arabic SLM) · Llama 3.1 / 3.2 · Groq · Cohere · HuggingFace · Ollama (local LLMs)

**Agentic frameworks:** LangChain · LangGraph · CrewAI · LlamaIndex · Phidata

**RAG & Vector Search:** Qdrant · Milvus · ChromaDB · FAISS · Weaviate · pgvector · LanceDB · hybrid retrieval (dense + BM25) · Reciprocal Rank Fusion · rerankers · NLI faithfulness scoring · sentence-transformers

**LLM Fine-Tuning:** QLoRA · LoRA · ORPO · PEFT · bitsandbytes (4-bit) · TRL

**Backend:** FastAPI · Flask · Django · Node/Express · Axum (Rust) · Celery · APScheduler · WebSockets · SSE

**Frontend:** React 18/19 · Next.js 14/15 · Vite · Vue · Tailwind · shadcn/Radix UI · TanStack Query · Zustand · Framer Motion · GSAP · Pixi.js · Babylon.js

**Data & Storage:** PostgreSQL · SQLite · MongoDB · Supabase · Redis · Neon · SQLAlchemy / SQLModel / Drizzle / Prisma / Diesel · Alembic

**DevOps & Cloud:** Docker / docker-compose · Nginx · Gunicorn · GitHub Actions CI/CD · Vercel · Netlify · AWS (App Runner, S3) · Azure Blob · Tauri · PM2 · Prometheus / Grafana / Loki · Sentry

**Integrations:** Twilio (voice/SMS) · WhatsApp Cloud API · Stripe · Google OAuth / Calendar / Cloud Storage · SMTP/IMAP · Serper · SAM.gov · Zillow/RapidAPI

**Security:** Casbin RBAC · JWT · OAuth2 · HMAC webhooks · Row-Level Security · rate limiting · CSRF/Helmet · secret scanning (gitleaks)

**Specialties:** Arabic-first NLP (RTL, reshaping, bidi) · multi-tenant architecture · voice AI (STT/TTS) · multimodal RAG · web scraping · production-grade agentic systems

---

## 6. Experience Framing (6 Years)

> ⚠️ **Fill in your real titles, employers, and dates** — I've written the framing based on what the code demonstrates, but I don't have your employment history. Replace the `‹...›` placeholders.

**Senior AI / Software Engineer — ‹Navid / Current Employer›** · ‹dates›
- Architect and ship **production RAG and agentic-AI platforms** (multi-tenant, Arabic-first, RBAC-secured) serving enterprise document Q&A with hybrid retrieval, reranking, and answer-faithfulness scoring.
- Lead **full-stack delivery** end to end — FastAPI/Node backends, React/Next.js frontends, Postgres/vector stores — with Docker, CI/CD, and observability (Prometheus/Grafana/Loki, Sentry).
- Build **AI SaaS products** with real-world integrations: Twilio voice/telephony, WhatsApp Cloud API, Stripe billing, Google Workspace, and multi-provider LLM orchestration (OpenAI, Gemini, Llama, Groq, Cohere).

**Earlier roles — ‹title / employer›** · ‹dates›
- ‹Add your prior 6 years: ML/data-science, web development, etc. — your repos show a clear ML/data-science foundation (fine-tuning, multimodal RAG, CV, NLP) evolving into full-stack AI engineering.›

**Education / Certifications:** ‹add here›

---

## 7. Communication & Soft Skills (LinkedIn)

> These are grounded in evidence from your repos — you can use them directly or trim them.

- **Clear technical writing & documentation** — your repos ship thorough READMEs, candid self-evaluations (`EVALUATION.md`), root-cause analyses, go-live checklists, and API docs (Swagger). You document not just *what* you built but its limits and readiness.
- **Bilingual / cross-cultural communication** — you build **Arabic-first** products with full RTL/bilingual UX, working across Arabic- and English-speaking stakeholders.
- **Stakeholder & client focus** — projects are framed around concrete business outcomes (lead qualification, proposal generation, field-service operations), showing you translate business needs into technical systems.
- **Ownership & reliability mindset** — operational hardening (auto-recovery, health monitoring, fail-closed security, audit logging) reflects accountability and a production-quality engineering culture.
- **Collaboration & handover discipline** — structured agent/session handoff docs and clean monorepo separation show you build for teams, not just yourself.
- ‹Add personal touches: mentoring, team leadership, public speaking, languages spoken, client-facing roles.›

---

## 8. Copy-Paste Profile Blurbs

### 8a. LinkedIn Headline (pick one)
- `Senior AI / Software Engineer · Agentic AI & RAG Systems · Full-Stack (Python · TypeScript) · 6 yrs`
- `AI Engineer building production RAG, multi-agent & voice-AI SaaS · FastAPI · Next.js · LangChain/LangGraph`
- `Senior Software Engineer | Generative & Agentic AI | RAG | Full-Stack | 6 Years`

### 8b. LinkedIn "About" Section
> Senior AI / Software Engineer with 6 years of experience designing and shipping production-grade **agentic AI, RAG systems, and full-stack SaaS**. I build the whole stack — from multi-tenant, RBAC-secured RAG platforms with hybrid retrieval and answer-faithfulness scoring, to AI voice and WhatsApp assistants, CRMs, and AI marketing agents.
>
> My toolkit spans **Python and TypeScript**, **FastAPI / Next.js / React**, and the modern AI stack — **LangChain, LangGraph, CrewAI, LlamaIndex**, multi-provider LLMs (**OpenAI, Gemini, Llama, Groq, Cohere**), and vector databases (**Qdrant, Milvus, Chroma, FAISS, pgvector**). I care about production quality: Docker, CI/CD, observability, security hardening, and honest engineering documentation.
>
> I specialize in **Arabic-first AI** and have delivered bilingual (Arabic/English) RAG platforms end to end. Whether it's automating government-contract proposals, qualifying real-estate leads over WhatsApp, or shipping multi-persona AI voice companions, I turn ambiguous business problems into reliable, shipped systems.
>
> 📫 ‹your email› · 🔗 github.com/Mustafa-Shoukat1

### 8c. Presenting Private Work
Most of these are **private client repos**, so visitors can't open them on GitHub. To showcase them:
- Describe them in your **GitHub profile README** as *text* (no links), e.g. *"Recent private work: a multi-tenant Arabic RAG platform, an AI GovCon proposal engine, and several AI SaaS products."*
- List them in your **LinkedIn "Projects"/"Experience"** with the senior blurbs above.
- Keep **screenshots / short demo videos** (with any client-sensitive data blurred) to share in interviews.
- Where a client allows, ask to make a **sanitized public fork** or a **case-study write-up**.

---

## 9. Your Selection Worklist (Private)

**Tick the projects you want me to feature, then tell me your picks. I can then:**
- `[ ]` Write a final **LinkedIn About + Experience + Skills** block ready to paste.
- `[ ]` Draft a **GitHub profile README.md** that describes this private work as text + links your public projects.
- `[ ]` Produce **per-project case-study blurbs** (longer, STAR-format) for interviews.
- `[ ]` Adjust tone (more technical vs. recruiter-friendly) or switch to third-person.

---
*Generated from live analysis of github.com/Mustafa-Shoukat1 · last 2 years of activity · 14 private projects. Public projects are in `Mustafa-Shoukat-Public-Portfolio.md`.*
