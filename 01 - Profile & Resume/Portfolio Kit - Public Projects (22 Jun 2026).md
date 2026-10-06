# Mustafa Shoukat — Public Work Portfolio
### Senior AI / Software Engineer · Public / Open-Source Projects

> **Scope of this file:** Your **public projects only** (6 projects). These are **open repos** anyone can view — so these are the ones to **pin on your GitHub profile** and link directly from LinkedIn / your CV.
> 👉 Your **private / client** projects live in a separate file: **`Mustafa-Shoukat-Portfolio.md`**.
>
> My recommendation rating: ⭐⭐⭐ = top showcase · ⭐⭐ = strong · ⭐ = good supporting project.

---

## 0. At-a-Glance Summary (Public Projects)

| # | Project | Category | Stars | Core Stack | Rating |
|---|---------|----------|-------|-----------|--------|
| 1 | Autonomous HybridRAG AI Agent | Agentic AI / RAG | 10★ | Python · Phidata · pgvector · Ollama | ⭐⭐ |
| 2 | Patent Search Tool | Agentic AI / RAG | — | Flask · CrewAI · GPT-4o · MongoDB · React | ⭐⭐ |
| 3 | CodAgentic CRM-OMS | Full-Stack Platform | — | Next.js 15 · FastAPI · SQLAlchemy · Twilio | ⭐⭐⭐ |
| 4 | InvestWise Desktop OS | Fintech / Desktop | — | Tauri · Rust · React 19 · SQLite/Diesel | ⭐⭐⭐ |
| 5 | Fine-Tuning QLoRA/ORPO LLaMA-3 | ML / Deep Learning | 3★ | PEFT · QLoRA · ORPO · HF Transformers | ⭐⭐ |
| 6 | Multimodal RAG (Chat-with-Video) | ML / Deep Learning | — | Whisper · LLaVA · BridgeTower · LanceDB | ⭐⭐ |

**Account:** [github.com/Mustafa-Shoukat1](https://github.com/Mustafa-Shoukat1) · 76 public repositories (8 Sep 2026).

---

## 1. Agentic AI & RAG

### `[ ]` ⭐⭐ 1. Autonomous HybridRAG AI Agent
- **Repo:** [`Autonomous-HybridRAG-AI-Agent`](https://github.com/Mustafa-Shoukat1/Autonomous-HybridRAG-AI-Agent) · 🌐 public · Python · 10★ · ~45 MB
- **One-liner:** An AI assistant that answers queries by cascading through memory, a vector knowledge base, provided context, and live web search.
- **What it is:** Built on the Phidata (phi) agent framework, it demonstrates a tiered retrieval strategy: it checks conversation memory and history first, then a pgvector knowledge base, then in-prompt context, and finally falls back to a DuckDuckGo web search. Chat history persists to PostgreSQL; documents embed into pgvector. **Your most-starred public AI repo (10★)** — a strong, accessible showcase of RAG patterns.
- **Tech stack:** Python, Phidata, OpenAI + Ollama (local LLMs), PostgreSQL + pgvector, SQLAlchemy, DuckDuckGo Search, BeautifulSoup4, pypdf.
- **Key features:** multi-source retrieval cascade (memory → KB → context → web) · persistent long-term memory · pgvector knowledge base · web-search fallback · PDF ingestion · automated RAG-evaluation notebook.
- **Senior blurb:** *I built an autonomous hybrid-RAG agent that cascades across long-term memory, a pgvector knowledge base, in-context data, and live web search to ground its answers, wired to both OpenAI and local Ollama models with PostgreSQL-backed persistent memory and an automated retrieval-evaluation harness.*

### `[ ]` ⭐⭐ 2. Patent Search Tool — AI Innovation Research Platform
- **Repo:** [`Patent-Search-Tool`](https://github.com/Mustafa-Shoukat1/Patent-Search-Tool) · 🌐 public · Python · ~28 MB
- **One-liner:** A multi-agent (CrewAI) research platform that automates patent, academic, market, and competitor research to surface innovation opportunities.
- **What it is:** A Flask web app orchestrating six role-specialized CrewAI agents (Strategist, Researcher, Writer, Insight Strategist, Opportunities Strategist, Document Analyst) that turn a challenge description into strategic insight. Auto-generates queries against Google Patents and Google Scholar (via Serper), analyzes news/customers/competitors, and synthesizes "opportunity spaces." Persists to MongoDB and serves a React frontend.
- **Tech stack:** Python 3.10+, Flask, CrewAI + crewai_tools, GPT-4o via langchain_openai, ChromaDB, MongoDB (mongoengine), Serper API, React frontend.
- **Key features:** six-role multi-agent system with YAML-driven config · automated Google Patents/Scholar search · trend/news/competitor analysis · AI synthesis into opportunity spaces · document-analyst agent · MongoDB persistence + React UI.
- **Senior blurb:** *I built an AI-powered patent and innovation research platform on a CrewAI multi-agent system, where six role-specialized agents automate patent, academic, market, and competitor research. I designed custom Serper-backed search tools and a YAML-configured task flow that synthesizes raw findings into strategic opportunity spaces, served through a Flask/MongoDB backend and React frontend.*

---

## 2. Full-Stack & Desktop Applications

### `[ ]` ⭐⭐⭐ 3. CodAgentic CRM-OMS — Field-Service CRM/Operations System
- **Repo:** [`CodAgentic-CRM-OMS`](https://github.com/Mustafa-Shoukat1/CodAgentic-CRM-OMS) · 🌐 public · TypeScript + Python · ~274 MB
- **One-liner:** A cross-platform CRM and operations-management system for property-maintenance/handyman businesses, pairing a Next.js frontend with a modular FastAPI backend.
- **What it is:** A full CRM/OMS for field-service companies managing the whole lifecycle — leads, customers, job scheduling, estimates, invoices, notifications, reporting. The backend is substantially implemented with discrete domain modules, plus an automated lead-generation pipeline that scrapes Yelp, Google Places, and Yellow Pages and runs an outreach engine. Your largest public repo.
- **Tech stack:** Next.js 15 / React 19 / TypeScript / Tailwind; Python FastAPI + SQLAlchemy 2.0 + Pydantic v2 on SQLite (Postgres-ready); APScheduler; Twilio (SMS) + fastapi-mail (email); JWT (python-jose) + passlib/bcrypt; BeautifulSoup scraping. Monorepo: `frontend/` + `backend/` + shared types package.
- **Key features:** lead pipeline (New→Contacted→Quoted→Won/Lost) · automated lead scraping (Yelp/Google Places/Yellow Pages) + outreach · customer profiles & service history · job scheduling + notifications · estimates & invoicing · reporting dashboard.
- **Senior blurb:** *I architected a cross-platform CRM/OMS for field-service businesses as a TypeScript/Python monorepo, with a domain-modularized FastAPI backend (leads, jobs, estimates, invoices, notifications, reporting) and a Next.js 15 frontend sharing a common type contract. I built an automated lead-generation pipeline that scrapes Yelp, Google Places, and Yellow Pages and drives multi-channel (Twilio SMS + email) outreach on scheduled background jobs.*

### `[ ]` ⭐⭐⭐ 4. InvestWise — Privacy-First Desktop Investment Tracker
- **Repo:** [`InvestWise-Desktop-OS-`](https://github.com/Mustafa-Shoukat1/InvestWise-Desktop-OS-) · 🌐 public · TypeScript + Rust · ~108 MB
- **One-liner:** A privacy-focused, local-first cross-platform desktop app for tracking investment portfolios, with a Rust/Tauri core and an extensible addon SDK.
- **What it is:** A desktop investment-portfolio tracker that keeps all financial data on the user's machine — no cloud, no subscriptions. Consolidates stocks, ETFs, mutual funds and other holdings into one view, with performance analytics, multi-currency support, CSV import, and goal planning. A substantial pnpm monorepo shipping the app plus a published UI library and addon SDK. *(Unique in your portfolio — a native desktop app with a Rust core.)*
- **Tech stack:** TypeScript + React 19, Tailwind v4, TanStack Query/Table/Virtual, Recharts, react-hook-form + Zod, Vite; native layer in **Rust via Tauri** (fs/dialog/updater/shell plugins), **Axum** web server, SQLite + **Diesel** ORM; Playwright + Vitest, Husky, Renovate, Docker, devcontainer.
- **Key features:** local-only portfolio tracking across accounts/asset types · performance analytics + charting · CSV trade import · goal planning + allocation · multi-currency with FX · extensible addon system with its own SDK + hot reload · cross-platform desktop (Win/macOS/Linux) + web mode.
- **Senior blurb:** *I architected InvestWise, a privacy-first cross-platform desktop investment tracker built on a Tauri + Rust core with a React 19/TypeScript frontend and an Axum web backend over SQLite/Diesel. I designed it as a pnpm monorepo with an extensible addon SDK and internal UI library, backed by Playwright/Vitest suites and full CI, so users get spreadsheet-grade portfolio control with zero cloud dependency.*

---

## 3. Machine Learning / Deep Learning Showcase

Notebooks that demonstrate ML depth — great for credibility on a public profile.

### `[ ]` ⭐⭐ 5. Fine-Tuning & PEFT with QLoRA / ORPO on LLaMA 3
- **Repo:** [`-Fine-Tuning-and-PEFT-with-QLoRA-on-LLaMA-3-`](https://github.com/Mustafa-Shoukat1/-Fine-Tuning-and-PEFT-with-QLoRA-on-LLaMA-3-) · 🌐 public · Jupyter · 3★ · ~3.5 MB
- **One-liner:** A hands-on notebook collection demonstrating parameter-efficient fine-tuning of LLaMA 2/3 and Gemma using LoRA, QLoRA, and ORPO.
- **What it is:** An educational, portfolio-style notebook series walking through modern LLM fine-tuning end to end — from the conceptual landscape (transfer learning, adapters, LoRA, PEFT trade-offs) to implementing QLoRA and ORPO (reference-free preference alignment) on LLaMA 3, plus LoRA on Gemma and a RAG/agent test.
- **Tech stack:** Python/Jupyter; HF Transformers/PEFT/TRL workflows, QLoRA (4-bit, bitsandbytes), LoRA adapters, ORPO; LLaMA 2/3, Gemma, Meltemi.
- **Key features:** QLoRA 4-bit fine-tuning of LLaMA 3 · ORPO monolithic preference alignment · LoRA on LLaMA 2 & Gemma · conceptual coverage of PEFT trade-offs · RAG/agent testing notebook.
- **Senior blurb:** *I authored a hands-on notebook series on parameter-efficient LLM fine-tuning, implementing QLoRA 4-bit tuning and ORPO reference-free preference alignment on LLaMA 3, plus LoRA on LLaMA 2 and Gemma, framed against the broader alignment landscape (RLHF, DPO, IPO, ORPO).*

### `[ ]` ⭐⭐ 6. Multimodal RAG — Chat with Videos
- **Repo:** [`Multimodal-RAG-Pipeline-Chat-with-Videos`](https://github.com/Mustafa-Shoukat1/Multimodal-RAG-Pipeline-Chat-with-Videos) · 🌐 public · Jupyter · ~4 MB
- **One-liner:** A multimodal RAG pipeline that lets you "chat" with video by combining speech transcription, vision-language captioning, and multimodal vector retrieval.
- **What it is:** A notebook proof-of-concept that builds RAG over videos: preprocesses videos into frames + transcripts, generates captions/visual Q&A with a vision-language model, embeds both modalities, stores them in a vector DB, and retrieves relevant segments to answer questions.
- **Tech stack:** Python/Jupyter; LangChain + **LanceDB** (multimodal vector store); **Whisper** (transcription), **LLaVA** (vision-language), **BridgeTower** (joint image-caption embeddings).
- **Key features:** frame extraction + Whisper transcription · LLaVA captioning/visual Q&A · BridgeTower cross-modal embeddings · LanceDB multimodal retrieval · end-to-end chat-with-video flow.
- **Senior blurb:** *I built a multimodal RAG pipeline that lets users chat with videos, fusing Whisper transcription, LLaVA vision-language understanding, and BridgeTower cross-modal embeddings into a LangChain + LanceDB retrieval flow that answers questions grounded in specific video segments.*

---

## 4. GitHub Profile — Pinned-Repo Recommendation

Pin these **6 public repos** on your profile (GitHub lets you pin up to 6):
1. `Autonomous-HybridRAG-AI-Agent` (10★) — flagship RAG agent
2. `CodAgentic-CRM-OMS` — large full-stack CRM/OMS
3. `InvestWise-Desktop-OS-` — Rust/Tauri desktop app
4. `Patent-Search-Tool` — CrewAI multi-agent platform
5. `-Fine-Tuning-and-PEFT-with-QLoRA-on-LLaMA-3-` (3★) — ML depth
6. `Multimodal-RAG-Pipeline-Chat-with-Videos` — multimodal AI

### Suggested GitHub profile README intro
> ### Hi, I'm Mustafa 👋 — Senior AI / Software Engineer (6 yrs)
> I build **production agentic-AI, RAG systems, and full-stack SaaS**. Arabic-first AI specialist.
>
> **Stack:** Python · TypeScript · FastAPI · Next.js · LangChain/LangGraph · CrewAI · Qdrant/Milvus · OpenAI/Gemini/Llama · Docker · AWS
>
> 📌 Pinned below are my public projects. *Many of my best applications are in private client repos — see my LinkedIn (https://www.linkedin.com/in/mustafashoukat) for the full portfolio.*

---
*Generated from live analysis of github.com/Mustafa-Shoukat1 · last 2 years of activity · 6 public projects. Private projects are in `Mustafa-Shoukat-Portfolio.md`.*
