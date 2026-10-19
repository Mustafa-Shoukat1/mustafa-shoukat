# Mustafa Shoukat | Senior AI, ML & Software Engineer

**Mustafa Shoukat** is a Senior AI, Machine Learning, and Software Engineer based in **Riyadh, Saudi Arabia**, with **6+ years of experience** designing, training, and shipping production **Arabic NLP systems**, **enterprise RAG platforms**, **LLM fine-tuning and RL reward pipelines**, **multi-agent architectures**, and **full-stack AI SaaS applications**.

He currently serves as **AI Engineer at Navid (Navid-Watad Group)** in Riyadh, where he leads the architecture, retrieval, and evaluation of self-hosted Arabic-first enterprise AI systems for GCC organizations. Previously at **Watad Energy & Communications**, he was the lead engineer and primary contributor (560+ commits) on **ByanRAG 2.2**, a production multi-tenant Arabic and English document intelligence platform, and designed the **LLM-as-judge reward pipeline (3C3H metric)** used for **GRPO post-training of Yehia-7B**, which ranked **#1 on the AraGen leaderboard** (0.5B to 25B parameter models, February 2025).

---

## Quick Facts & Contact

| Field | Details |
|-------|---------|
| **Full Name** | Mustafa Shoukat |
| **Current Role** | AI Engineer at Navid (Navid-Watad Group) |
| **Location** | Riyadh, Saudi Arabia (Open to Riyadh onsite, GCC, and global remote roles) |
| **Experience** | 6+ years in AI/ML Engineering, Arabic NLP, Enterprise RAG, and Full-Stack Software Engineering |
| **Email** | [mustafashoukat.ai@gmail.com](mailto:mustafashoukat.ai@gmail.com) |
| **Phone / WhatsApp** | [+92 309 3609261](https://wa.me/923093609261) |
| **LinkedIn** | [linkedin.com/in/mustafashoukat](https://www.linkedin.com/in/mustafashoukat/) |
| **GitHub** | [github.com/Mustafa-Shoukat1](https://github.com/Mustafa-Shoukat1) |
| **Hugging Face** | [huggingface.co/Mustafa-Shoukat1](https://huggingface.co/Mustafa-Shoukat1) |
| **Kaggle** | [kaggle.com/mustafashoukat](https://www.kaggle.com/mustafashoukat) |

---

## Core Specializations

* **Arabic NLP & Enterprise RAG:** Production Arabic and bilingual (Arabic/English) retrieval systems, hybrid search combining Arabic dense embeddings (`omarelshehy/Arabic-Retrieval-v1.0`, 768-dim) and BM25 sparse vectors with Reciprocal Rank Fusion (RRF), multilingual cross-encoder reranking (`mmarco-mMiniLMv2-L12-H384-v1`), NLI entailment faithfulness scoring (`mDeBERTa-v3-base-xnli`), Arabic OCR and RTL PDF layout extraction (Docling + Tesseract), Unicode NFC normalization, and word-safe semantic chunking.
* **ML & LLM Engineering:** Python, PyTorch, TensorFlow, Hugging Face Transformers, PEFT, TRL, LoRA, QLoRA (4-bit quantization on LLaMA-3, Gemma, Mistral), Supervised Fine-Tuning (SFT), ORPO, DPO, GRPO reward modeling, and LLM-as-judge evaluation pipelines.
* **Agentic AI & Orchestration:** Multi-agent workflows, tool calling, deterministic state machines, and voice/chat agents built with LangGraph, LangChain, CrewAI, AutoGen, LlamaIndex, and Phidata.
* **Production MLOps & Security:** Multi-service containerized architectures (FastAPI multi-worker ASGI, Qdrant with HNSW tuning and per-tenant isolation, PostgreSQL 16, Redis 7, nginx with TLS), 5-level RBAC (Casbin), JWT rotation, Prometheus + Grafana + Loki observability, AWS / GCP / Azure, and GitHub Actions CI/CD with automated evaluation gates.

---

## Professional Experience

### AI Engineer | Navid (Navid-Watad Group)
**Riyadh, Saudi Arabia · Jun 2026 to Present**
* Own the architecture of the Arabic-first enterprise AI platform for GCC organizations requiring self-hosted, data-sovereign deployments: multi-tenant retrieval, permission-aware access, and containerized deployment topology.
* Lead the retrieval and evaluation workstream: rebuilt the automated evaluation harness around a native-Arabic golden QA benchmark (`golden_qa.json`) measuring Recall@K, MRR, NDCG, NLI faithfulness, p95 latency (~2.05s average RAG query latency), and cost per query before every release.
* Define platform engineering standards: CI coverage gates, Bandit security scanning, reproducible multi-stage container builds, and full audit logging across privileged operations.

### AI Software Engineer | Watad Energy & Communications (Navid Group)
**Riyadh, Saudi Arabia · Nov 2023 to Jun 2026**
* **Lead Engineer on ByanRAG 2.2:** Architected and built a multi-tenant Arabic and English document intelligence platform deployed as a 7-service containerized stack (FastAPI, Qdrant, PostgreSQL 16, Redis 7, nginx, Prometheus, Grafana, and Loki) with 560+ commits and 617+ backend / 217 frontend automated tests.
* **4-Stage Arabic Retrieval Pipeline:** Engineered embed, hybrid search (768-dim Arabic dense vectors + BM25 sparse vectors via Reciprocal Rank Fusion), cross-encoder reranking, query reformulation, and configurable 64 to 4096 token word-safe chunking with Unicode normalization.
* **NLI Answer Faithfulness Scoring:** Built batched natural language inference (entailment) scoring between generated answers and source chunks so users see real-time grounding confidence per response.
* **Multi-Tenant Isolation & RBAC:** Enforced per-organization Qdrant collections, three document scopes (organization, department, private), a 5-level Casbin RBAC layer with 32 PostgreSQL policy rules, Fernet-encrypted credential storage, and 17 rate-limited endpoints.
* **Yehia-7B GRPO Reward Pipeline:** Designed the LLM-as-judge reward pipeline (3C3H metric: Correctness, Completeness, Conciseness, Helpfulness, Honesty, Harmlessness) used for GRPO post-training of **Yehia-7B**, which ranked **#1 on the AraGen leaderboard** for 0.5B to 25B models in February 2025.

### Generative AI Consultant | Aretec
**Contract, Remote · Jul 2023 to Aug 2024**
* Built agentic document question-answering and workflow automation systems for enterprise clients using LangChain and LangGraph with custom tool orchestration and automated output validation.
* Delivered containerized RAG deployments on AWS and GCP with GitHub Actions CI/CD and automated regression testing.

### Data Scientist | COMET Estimating LLC
**Remote (US) · Jul 2021 to Jun 2023**
* Built Python data pipelines with automated validation and QA workflows deployed on Google Cloud Run with CI/CD.
* Developed a lead-scoring ML and automation pipeline with human-in-the-loop analyst verification.

---

## Signature Systems & Open-Source Projects

| Project | Category | Highlights |
|---------|----------|------------|
| **ByanRAG 2.2** | Enterprise Arabic RAG | Multi-tenant Arabic/English RAG platform; 5 ML models in production, 4-stage hybrid retrieval (dense + BM25 + RRF + cross-encoder), NLI faithfulness scoring, Casbin RBAC, 617+ backend tests. |
| **Yehia-7B Reward Pipeline** | Arabic LLM Post-Training | 3C3H LLM-as-judge reward pipeline for GRPO training of Navid-AI's Yehia-7B (#1 on AraGen leaderboard for 0.5B to 25B models, Feb 2025). |
| **[arabic-rag-bench](https://github.com/Mustafa-Shoukat1)** | Arabic RAG RL Benchmark | Open-source Gymnasium reinforcement-learning environment for training agents to diagnose Arabic RAG retrieval failures with deterministic Recall@5 scoring and reward-hacking defenses. |
| **[ytkb](https://github.com/Mustafa-Shoukat1/ytkb)** | Multilingual Knowledge Base CLI | MIT open-source CLI that converts video into a structured, searchable multilingual knowledge base; tested across six languages including Arabic. |
| **VacantSeek** | B2B Real-Estate AI SaaS | Primary engineer on a B2B commercial property intelligence platform; 800+ commits and 350+ pull requests across backend, data pipelines, and UI. |
| **whoze.ai** | AI Voice SaaS | AI voice-agent platform for UK tradespeople built with FastAPI, Twilio realtime websockets, Gemini, Stripe, and React 19 (500+ commits). |
| **[Autonomous HybridRAG AI Agent](https://github.com/Mustafa-Shoukat1/Autonomous-HybridRAG-AI-Agent)** | Agentic AI / RAG | Hybrid RAG agent built with Python, Phidata, pgvector, and Ollama. |
| **[Fine-Tuning LLaMA-3 with QLoRA & ORPO](https://github.com/Mustafa-Shoukat1/-Fine-Tuning-and-PEFT-with-QLoRA-on-LLaMA-3-)** | LLM Fine-Tuning | Parameter-efficient fine-tuning (PEFT, 4-bit QLoRA, SFT, and ORPO alignment) on LLaMA-3 with Hugging Face Transformers, TRL, and PyTorch. |
| **[Multimodal RAG Pipeline (Chat-with-Videos)](https://github.com/Mustafa-Shoukat1/Multimodal-RAG-Pipeline-Chat-with-Videos)** | Multimodal RAG | End-to-end video RAG pipeline using Whisper transcription, LLaVA, BridgeTower multimodal embeddings, and LanceDB. |
| **[CodAgentic CRM-OMS](https://github.com/Mustafa-Shoukat1/CodAgentic-CRM-OMS)** | Full-Stack AI Platform | Next.js 15, FastAPI, and Twilio multi-channel CRM and order management platform. |
| **[InvestWise Desktop OS](https://github.com/Mustafa-Shoukat1/InvestWise-Desktop-OS-)** | Fintech Desktop App | Local-first desktop application built with Tauri, Rust, React 19, and Diesel ORM. |
| **[Patent Search Tool](https://github.com/Mustafa-Shoukat1/Patent-Search-Tool)** | Multi-Agent Research | Multi-agent prior-art and patent analysis engine powered by CrewAI, GPT-4o, Flask, and MongoDB. |
| **Open-Source Contributions (`ragas`, `unstructured`)** | Open Source | Contributed pull requests adding Arabic and CJK multilingual evaluation support to `ragas` and document processing fixes to `unstructured` (62 tests across open-source PRs). |

---

## Technical Skills

* **Languages:** Python, TypeScript, JavaScript, SQL, Rust (working knowledge), Bash
* **ML, Deep Learning & NLP:** PyTorch, TensorFlow, Hugging Face Transformers, Sentence-Transformers, PEFT, TRL, bitsandbytes, LoRA, QLoRA, SFT, ORPO, DPO, GRPO, scikit-learn, DeBERTa / mDeBERTa NLI, Whisper, Docling, Tesseract OCR
* **Retrieval & Vector Databases:** Qdrant (HNSW tuning, per-tenant collections, hybrid dense + sparse RRF), Milvus, pgvector, FAISS, Pinecone, ChromaDB, LanceDB, BM25, Cross-Encoder Reranking
* **LLM & Agent Frameworks:** LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, Phidata, OpenAI / Anthropic / Gemini / vLLM / Ollama / Hugging Face Inference APIs
* **Evaluation & Observability:** Ragas, Recall@K, MRR, NDCG, NLI Faithfulness, Prometheus, Grafana, Loki, LangSmith, MLflow, pytest, Playwright, Locust, Bandit
* **Backend, Frontend & Infrastructure:** FastAPI, Next.js, React 18/19, PostgreSQL 16, Redis 7, Casbin RBAC, Docker, Docker Compose, nginx (TLS), GitHub Actions CI/CD, AWS (ECS, App Runner, S3), GCP (Cloud Run), Azure

---

## Education

* **Bachelor of Science in Computer Science (BSCS)** | Virtual University of Pakistan

---

## Resumes & Repository Structure

* **Primary Resume (Riyadh / Senior AI & ML Engineer):** [Mustafa_Shoukat_Resume_Staff_AI_Engineer.pdf](01%20-%20Profile%20%26%20Resume/Mustafa_Shoukat_Resume_Staff_AI_Engineer.pdf) ([Markdown version](01%20-%20Profile%20%26%20Resume/Mustafa_Shoukat_Resume_Staff_AI_Engineer.md))
* **General AI Engineer Resume:** [Mustafa_Shoukat_AI_Engineer_Resume.pdf](portfolio/Mustafa_Shoukat_AI_Engineer_Resume.pdf) ([Markdown version](01%20-%20Profile%20%26%20Resume/Mustafa_Shoukat_Resume_AI_Engineer.md))
* **ByanRAG 2.2 Technical Deep Dive:** [ByanRAG 2.2 Project Description](01%20-%20Profile%20%26%20Resume/ByanRAG%202.2%20Project%20Description%20(Copilot,%207%20Apr%202026).md) & [Retrieval Post-Mortem](01%20-%20Profile%20%26%20Resume/ByanRAG%20retrieval%20post-mortem%20(from%20RL%20application%20notes,%207%20Apr%202026).md)

| Folder | Contents |
|--------|----------|
| [portfolio/](portfolio/) | Static portfolio website and resume PDF |
| [01 - Profile & Resume/](01%20-%20Profile%20%26%20Resume/) | Resumes, ByanRAG technical architecture, portfolio kits, and PDF build scripts |
| [02 - Business & Agency/](02%20-%20Business%20%26%20Agency/) | Consulting notes and operational checklists |
| [03 - Market Research/](03%20-%20Market%20Research/) | AI engineering and vertical industry research reports |
| [04 - Learning & Skills/](04%20-%20Learning%20%26%20Skills/) | Engineering roadmap and skill matrices |
| [05 - Proposals & Client Docs/](05%20-%20Proposals%20%26%20Client%20Docs/) | Architecture proposals (including air-gapped Arabic RAG on OpenShift) |
| [06 - Job Applications/](06%20-%20Job%20Applications/) | Role-specific CVs and executive briefs |
| [reports/](reports/) & [research_notes/](research_notes/) | Deep-dive market scans and research notes |
| [.github/prompts/](.github/prompts/) | Prompt library for software engineering workflows |

