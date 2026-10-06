# AI Job Market Research and Action Plan
**Prepared for:** Mustafa Shoukat
**Date:** 28 August 2026
**Scope:** AI engineering, agentic AI, AI architecture, enterprise solutions, AI project management, enterprise RAG, and country-level demand

---

## 0. Research Basis

Individual job descriptions read from: Databricks, ServiceNow, Grafana Labs, Saviynt, Booz Allen, NTT Data, Deloitte, KPMG, Barclays, Ingram Micro, GE Vernova, Air India, Harvard, NVIDIA, Alvarez & Marsal, Apex Systems, plus live Upwork, Indeed, Glassdoor and Talentmate postings.

Aggregate datasets that parsed posting text directly:
- 43,480 US AI engineering postings
- 16,927 AI architecture postings
- 468 AI program management postings
- 1,135 agentic AI listings
- 542 Upwork AI agent jobs

---

## 1. The One Big Shift

The market moved from "build a chatbot with an LLM" to "run an agent in production and prove it works."

- The standalone prompt engineer title is gone, absorbed into what is now called context engineering
- Recruiters now screen for evidence, not vocabulary: a published MCP server, merged pull requests into a major agent framework, and cost and latency numbers that imply you ran something in production long enough to optimise it
- Resume language like "built cutting-edge agentic AI solutions" is now a negative signal

---

## 2. Master Keyword List

Put these in your profile, resume and proposals only where you can back them with shipped work.

### Protocols
MCP, A2A, ACP

### Orchestration
LangGraph, LangChain, LlamaIndex, CrewAI, Pydantic AI, Agno, Mastra, Google ADK, Claude Agent SDK, OpenAI Agents SDK, Microsoft Agent Framework, Semantic Kernel, DSPy, Vercel AI SDK, Temporal

### Retrieval
Hybrid search, reranking, semantic chunking, embedding versioning, recall@k, Graph RAG, Neo4j, Memgraph, ontologies, Pinecone, Weaviate, Qdrant, pgvector, Chroma, Milvus, OpenSearch, Elastic

### Memory
Mem0, Zep, checkpointing, episodic and semantic memory, state machines

### Evals
Ragas, LangSmith, Braintrust, Arize Phoenix, Langfuse, DeepEval, Promptfoo, LLM-as-judge calibration, error analysis, regression gating, GAIA, SWE-bench

### Ops and Inference
OpenTelemetry, per-call cost attribution, prompt versioning, model routing, LLM gateway, prompt caching, vLLM, SGLang, TensorRT-LLM, TGI, llama.cpp, Ollama, LiteLLM, Ray Serve, Triton, Docker, Kubernetes

### Security and Governance
Prompt injection defence, prompt firewalls, red team harnesses, OWASP LLM Top 10, agent identity, least-privilege tool access, action authorisation, rollback safety, audit APIs, NIST AI RMF, EU AI Act, model risk management

### Voice
LiveKit Agents, Pipecat, Realtime API, Deepgram Nova-3, Cartesia Sonic-3, AssemblyAI, semantic VAD, turn detection, barge-in, SIP, Twilio, Telnyx

### Cloud
Azure OpenAI, AWS Bedrock, Vertex AI, Databricks, Snowflake, Terraform

### Enterprise
Copilot Studio, Agentforce, ServiceNow, solution blueprints, reference architectures, Architecture Review Boards, C4, Structurizr, SAP S/4HANA, Ariba, OData, SOAP

---

## 3. The Three Career Tracks

### Track A: AI / Agentic Engineer
- Median salary 176,000 USD
- Python 62 percent, cloud 55 percent, foundation models 51 percent of postings
- 66 percent individual contributor roles
- Volume around 1,550 postings per week, peaked at 2,327 in late June
- Agentic AI Engineer bands run 185k to 320k base
- One JD template sets the bar as: by day 90 the hire has shipped a new agentic feature to production with full eval coverage

### Track B: AI Architect and Enterprise Solutions
- Median salary 189,000 USD
- Around 605 new US postings per week, 45 percent mid-level IC, 44 percent from companies over 10,000 employees
- Skill mention rates: cloud 60.9 percent, Python 43.9 percent, observability 38.9 percent, foundation models 37.8 percent, RAG 28.1 percent, CI/CD 26.2 percent
- Tools: Azure 42.5 percent, AWS 40.1 percent, GCP 25.4 percent, Databricks 15.5 percent, Docker 13.7 percent, Snowflake 11.7 percent
- Median experience asked: 7 years
- **Certifications barely register.** Highest is Certified ScrumMaster at 2.9 percent, AWS Solutions Architect at 1.7 percent. Do not buy certs for this track.
- 15 percent of these roles are contract, driven by IT Services and Professional Services firms staffing per engagement. This is the realistic freelance entry point.

### Track C: AI Project and Program Manager
- Median salary 182,650 USD, middle 80 percent between 133k and 271k
- 79 percent mid-level, 7 years minimum, only 3 percent junior
- Qualification mention rates: risk management 39 percent, stakeholder management 37 percent, communication 36 percent, technical program management 32 percent, program management 28 percent
- Only 20 percent request certifications (PMP, SAFe, PgMP, CSM, PRINCE2, ITIL, PROSCI, CIPP)
- **Only 12 percent remote, and California alone is 40 percent of the US market.** Poor fit for a Pakistan-based remote practice.
- The differentiator is not Jira. It is owning the eval threshold: data dependencies, what counts as done, what happens at the 6 percent the model gets wrong, and what rollback looks like.

---

## 4. What Enterprise Job Descriptions Actually Say

- **KPMG:** multi-agent systems on Azure and GCP, solution blueprints with reference architectures and integration patterns, model risk management, auditability and security controls, ownership of an AI Agents Roadmap with RCA and monitoring frameworks
- **Large enterprise platform role:** LLM gateway with model routing across Anthropic, OpenAI, Bedrock and Azure OpenAI, prompt and version management, evaluation harnesses, cost and usage guardrails, human-in-the-loop controls, action authorisation, least-privilege tool access, rollback safety, internal MCP services
- **NTT Data:** Graph RAG, ontologies and semantic relationships, hybrid retrieval combining vector search, graph traversal and semantic techniques, evaluation pipelines with hallucination detection and grounding validation
- **Booz Allen:** MCP and A2A protocols, knowledge graphs, memory architectures for long-running agents, agent benchmarking with GAIA or SWE-bench, fine-tuning small language models for edge devices
- **Ingram Micro:** reasoning engines, planning modules, perception interfaces, memory systems, tool and API integration layers, simulation environments for validating agent behaviour
- **Consulting architect role:** Architecture as Code using Structurizr and C4 modeling with CI/CD model pipelines

---

## 5. What Is Genuinely New (Last Two to Three Months)

1. **EU AI Act high-risk obligations took effect 2 August 2026.** NIST AI RMF alignment now appears in enterprise security reviews. Almost nobody has this on their profile yet.
2. **Guardrails moved from advisory to platform.** Prompt firewalls, content filter hooks, red team harnesses and audit APIs are now central platform components consumed by every application. Orchestration control is shifting out of the agent into a dedicated infrastructure layer handling routing, retries and circuit breakers.
3. **Agent security as its own job title.** Prompt injection defence, agent identity, gateway configuration, fine-tuning data governance.
4. **Simulation environments for testing agent behaviour** now appearing in architect JDs.
5. **Architecture as Code** with Structurizr and C4.

---

## 6. What Is Dead or Dying

- Standalone prompt engineering as a title or selling point
- AutoGen and Semantic Kernel as things to learn fresh. Microsoft folded both into Microsoft Agent Framework and put them in maintenance mode, though 74 postings still ask for AutoGen because enterprise hiring lags.
- Certifications for architecture roles
- Basic RAG with a single vector store, no reranker, no eval
- Simple no-code chatbot builds. AI chatbot development grew 71 percent on Upwork while AI integration grew 178 percent.
- Deep ML and model training for most of these roles, unless the title says ML engineer

---

## 7. Country Ranking

### By where the buyers actually are

**1. United States**
Nearly 40 percent of all freelance AI agent jobs. Inside the US: California 22 percent, New York 11 percent, Texas 10 percent. Wants back-office automation, customer support agents, sales funnels, enterprise copilots. Most volume, most competition, lowest compliance pressure.

**2. Australia**
8.7 percent of AI agent postings, second only to the US. 31 percent of Australian enterprises have an agent in production, ahead of most of APAC. Wants SMB and trades automation, booking and scheduling agents, voice receptionists, home services. Timezone works from Pakistan. Best untapped market.

**3. United Kingdom**
6.8 percent of AI agent postings. Europe's top AI market, especially London. Wants voice receptionists for trades and clinics, compliance-aware RAG, fintech back office, applied AI engineers, research-to-production. Cares about EU AI Act and GDPR.

**4. Canada**
4.4 percent of postings. Healthcare admin, insurance workflows, bilingual support agents.

**5. United Arab Emirates**
AI job postings growing around 74 percent annually, fastest of any major market. Leads Middle East agent production alongside Saudi sovereign initiatives. Wants government and smart city projects, defence, real estate, Arabic and English voice agents. One hour ahead of Pakistan. Highest fit-to-effort ratio.

**6. Singapore**
Highest APAC production rate at 34 percent. Fintech, logistics, enterprise engagement systems.

**7. Germany**
Largest AI market inside the EU. Manufacturing workflow automation, compliance and audit agents, on-prem and self-hosted. Slow to buy, pays well, heavy on data residency.

**8. India**
Projected 2.3 million AI-related jobs by 2027. High volume, low rate. Watch as competition, not as a client market.

**9. Saudi Arabia**
Sovereign AI programmes, Arabic-first systems, government digital transformation. Big budgets, slow procurement, relationship driven.

**10. Netherlands, Ireland and Nordics**
Small volume, high rates, strong on privacy-first and self-hosted builds.

### What all of them buy

By industry: marketing and sales 17.6 percent, enterprise and business software 13.2 percent, healthcare 8.1 percent, finance 6.5 percent, media 5.9 percent, real estate 4.8 percent.

By use case: back-office automation 15.2 percent, customer support 14.8 percent, voice and call automation 7.6 percent, lead and outreach automation 7.4 percent, content generation 7.2 percent.

### The rate insight

Most freelance jobs sit at 20 to 40 USD per hour with a weighted average of 35.08. The top of the market, up to 600 USD per hour, goes to healthcare voice receptionists, enterprise automation copilots, and multi-agent orchestration in financial systems, because buyers pay for risk management and integration expertise, not hours.

**You already build the top-bracket work. Quoting hourly puts you in the wrong band.**

---

## 8. Enterprise RAG: The Nine Things Buyers Ask For

Market context: RAG was around 1.2 billion USD in 2024, projected to 11 billion by 2030. Organisations report 30 to 70 percent efficiency gains, but 40 to 60 percent of RAG implementations fail before production, usually from poor retrieval quality and governance gaps.

RAG engineer comp: 130k to 175k mid-level, 195k to 290k senior. "RAG engineer" is really three jobs: retrieval engineer, applied LLM engineer, and platform engineer.

1. **Governed knowledge assistants with permission-aware retrieval.** Role, department and entitlement filtering enforced server-side. Permission sync from SharePoint, Drive, Confluence, HR systems. Most common ask and most common failure point.

2. **GraphRAG and knowledge graphs.** Entity-relationship graphs enabling theme-level queries with full traceability, reaching search precision as high as 99 percent. Cost: 3 to 5 times more LLM calls than standard RAG, entity recognition accuracy 60 to 85 percent depending on domain. Delivers value with 8 or more heterogeneous sources, multi-hop queries and semantic reasoning needs. 67 percent of projects get abandoned when teams skip the readiness diagnostic.

3. **Multi-representation knowledge layers.** Vector embeddings for semantic search, knowledge graphs for relationship reasoning, hierarchical indexes for categorical navigation, all maintained at once. The old retrieve-stuff-generate framing is treated as obsolete. RAG is now a knowledge runtime, an orchestration layer. The skill is query routing.

4. **Multimodal RAG over private documents.** Roughly 80 percent of enterprise PDFs contain at least one table, chart or complex layout, so OCR-based RAG starts with structurally degraded input. Three architectures dominate: caption-and-index, unified vision embeddings (Cohere Embed 4, voyage-multimodal-3.5), and page-as-image late interaction (ColPali, ColQwen2.5, ColNomic). Production stack: Marker and Docling for parsing, VLMs for tables, ColPali and ColQwen2 for visual retrieval, Qdrant for multi-vector indexing, CLIP and SigLIP for image embeddings. For PHI and self-hosted, Nomic Embed Multimodal plus a local VLM such as PaliGemma 2 or Gemma 3 vision keeps everything in-VPC. OCR options: DeepSeek-OCR, PaddleOCR-VL, GOT-OCR 2.0, Granite-Docling.

5. **Auditability and explainable retrieval.** A 2026 Forrester study found auditability topped the priority list for financial services firms evaluating AI assistants. One bank cut compliance review time for AI-generated contract summaries from days to hours because every extracted clause traced back to the original scanned document page. GraphRAG provides the reasoning path, vector RAG does not.

6. **Sovereign and air-gapped deployment.** Full stack inside the customer network, local inference, zero outbound traffic. Buyers: defence (ITAR, CMMC), healthcare (HIPAA), public sector (FedRAMP), education (FERPA), EU-regulated workloads.

7. **Entity resolution and deduplication.** Needed when the same customer, counterparty or asset appears differently across systems. Boring and consistently the reason projects fail.

8. **Retrieval evaluation as a product feature.** Recall@k before any generation eval. Faithfulness and groundedness scoring. Embedding versioning and a re-embed plan. Recommended approach: 100 to 300 representative documents, 30 to 50 ground truth pairs, measure a text-only baseline, then add the simplest viable multimodal layer and measure the delta.

9. **Security of the knowledge layer.** Real deployments revealed poisoned documents triggering unwanted behaviour, retrieval precision failures in multi-hop reasoning, and inability to explain answers to auditors. Indirect prompt injection through ingested documents is the newest concern and almost nobody sells a defence yet.

---

## 9. Self-Hosted RAG: The Technical Reference

### Why teams self-host
Data sovereignty and compliance, lower cost at high volume, deterministic latency. Air-gapped is the strictest version: zero outbound traffic, all models and indexes on-prem. UC San Diego runs Onyx fully air-gapped on local GPUs for over 37,000 users.

### The seven layers
Most local RAG tutorials stop at a single-script demo. Enterprise self-hosted RAG ships all seven, including the parts that take real engineering: connector sync, ACL propagation, evaluation, observability, and operations.

### The landscape
- **Platforms with a finished UI:** Onyx (MIT), RAGFlow (Apache 2.0, 80k+ stars), AnythingLLM, Verba, Open WebUI, LibreChat
- **Frameworks you assemble:** LlamaIndex, LangChain, Haystack
- **Search infrastructure:** Elastic, OpenSearch, Weaviate, Qdrant, Milvus

### Models
Open-weight models including DeepSeek V4, GLM-5.2, Qwen 3.5 and Gemma 4 are competitive with proprietary models across most enterprise benchmarks.

**Licence warning:** the Llama 4 community licence excludes EU-established companies, ruling it out for most European organisations.

Most enterprise RAG and extraction work runs well on 8B to 32B models. Retrieval quality, not parameter count, decides accuracy.

### Serving
vLLM, SGLang and TensorRT-LLM for throughput. Ollama and llama.cpp for development and small teams. VRAM is the planning constraint: INT8 halves the requirement against FP16, Q4 brings it to roughly a quarter. Budget 0.5 to 1 FTE of engineering for the first year, which for most teams is the largest cost, not the GPU.

### What buyers screen for
Sovereign-first design with explicit air-gapped support, built-in evaluation tooling, and an Apache 2.0 or MIT licence rather than SSPL or GPL.

### Competitive warning
RAGFlow v0.25 shipped in April 2026 adding Arabic right-to-left UI support along with prebuilt ingestion pipelines, sandbox code execution and agent memory. Open source is moving into the Arabic differentiator. The moat is not the RTL interface. It is the tenancy, RBAC and compliance architecture around it, plus a shipped Riyadh track record.

---

## 10. Personal Assessment: Bayan / ByanRAG

### What is already built
- Multi-tenant with per-organisation data isolation via org-isolated Qdrant collections
- 5-level Casbin RBAC enforced on every endpoint, not just the UI
- Hybrid retrieval: dense embeddings plus BM25 sparse plus RRF fusion plus CrossEncoder reranking
- Source-cited bilingual Arabic and English answers over streaming SSE
- Answer-faithfulness scoring
- 14-panel admin console with audit logs and system health
- Full Docker stack, RTL Arabic interface, designed with on-prem in mind
- Surrounding product: chat workspace with notes and shared pages, HR tools, finance and invoice handling, project task board, support desk with ticketing, admin console, public API

### Honest assessment
Most people who say "I have RAG experience" mean a vector store and a prompt. Four things here are rare:

1. Row-level security enforced server-side per tenant and per role. The hardest part of enterprise RAG and what kills most pilots.
2. Hybrid retrieval with reranking, not naive top-k.
3. Faithfulness scoring, the eval layer everyone now asks for.
4. Arabic RTL at production quality.

**This is not a RAG developer profile. It is a sovereign document intelligence architect profile.**

### The blocking gap
Generation still calls an external language model over the internet. This is not a small caveat. Buyers in Saudi government, UAE, defence, EU public sector and healthcare disqualify on that single line. It is also the easiest gap to close.

---

## 11. Live Opportunity Found

**Senior Backend Engineer, Abu Dhabi, UAE. Posted 22 August 2026.**
Defence infrastructure, EDGE Group adjacent.

What they ask for:
- On-premise microservices as the nervous system for AI agents, integrating LLMs with industrial ERPs and sensitive engineering data
- Backend logic interfacing with vector databases and RAG models so a Knowledge Mining Chatbot can securely query historical proposals and technical documents
- Defence-grade security services including a Gateway and Policy Guard enforcing authentication, RBAC, and redaction of PII and ITAR data before it reaches the LLM
- Optimisation for strictly air-gapped or on-premise deployment on local GPU clusters rather than cloud scaling
- Agent orchestration layer with task routing, state management and error handling
- Comprehensive logging, tracing, monitoring and observability for high availability and auditability

Required:
- 5+ years backend building distributed systems serving ML/AI in production
- Expert Python with FastAPI or Django, plus Go or Java for high-performance microservices
- Docker and Kubernetes for on-premise deployment
- RESTful APIs and gRPC, API gateways such as Kong or NGINX
- PostgreSQL plus vector databases (Weaviate, Milvus)
- Enterprise integration patterns and ERP protocols (OData, SOAP) for SAP S/4HANA and Ariba
- Experience with high availability, auditability and defence-grade security, preferably fintech, healthcare or defence

**This is Bayan's architecture written as a job description.**

### Gap analysis against it
| Requirement | Status |
|---|---|
| Python, FastAPI | Have |
| RAG, vector DB, hybrid retrieval | Have |
| RBAC before the LLM | Have |
| Docker, PostgreSQL | Have |
| Audit logging, admin console | Have |
| On-prem intent | Partial |
| Kubernetes on-premise with GPU scheduling | Gap |
| Local GPU inference | Gap, and it is the disqualifier |
| Go or Java | Gap |
| ERP integration (SAP S/4HANA, Ariba, OData, SOAP) | Gap |
| PII and ITAR redaction layer | Gap |
| ACL propagation from source systems | Gap |

---

## 12. The Four Week Plan

**Week 1: kill the footnote.**
vLLM serving Qwen 3.5 or Gemma 4 at 8B to 14B behind the existing provider-agnostic layer. Measure the Arabic answer quality delta against the current external model. Then "air-gapped" can be said with no asterisk.

**Week 2: Kubernetes.**
Port the Docker Compose stack to a k8s manifest with GPU node scheduling. A single-node k3s cluster counts as proof.

**Week 3: redaction and ACL layer.**
Policy guard middleware that strips PII before the prompt, plus one connector that inherits permissions from an external source (SharePoint or Google Drive).

**Week 4: the case study.**
One document covering: tenancy model, RBAC enforcement point, retrieval pipeline with recall@k and faithfulness numbers, air-gapped topology diagram, redaction and audit trail. Publish it.

**Then apply.** Abu Dhabi role first since it is live. In parallel, target systems integrators and consultancies in UAE and Saudi rather than end clients, since they staff this work per engagement.

---

## 13. Search Terms That Find This Work

Do not search "RAG developer". Search:

- "on-premise RAG", "self-hosted RAG", "air-gapped"
- "data sovereignty", "sovereign AI"
- "enterprise knowledge management" + LLM
- "GraphRAG", "knowledge graph" + retrieval
- "multi-tenant" + "RBAC" + AI
- "document intelligence", "intelligent document processing"
- "Arabic NLP", "Arabic LLM", "bilingual RAG"
- Onyx, RAGFlow, Haystack, LlamaIndex, vLLM, Ollama as keywords

**Where to look:** Bayt, Naukrigulf, Talentmate, LinkedIn filtered to Saudi and UAE, EU tender portals, Onyx and RAGFlow deployment partners, and systems integrators serving ministries. Not Upwork. These buyers do not post there.

---

## 14. Positioning Changes

| From | To |
|---|---|
| RAG developer | Sovereign document intelligence architect |
| Hourly rate | Project pricing based on risk and outcome |
| "Built cutting-edge agentic AI solutions" | Named tenancy model, RBAC enforcement point, recall@k, faithfulness score |
| Chasing US postings | UAE and Australia first, then UK and Singapore |
| Collecting frameworks | Shipping evals, cost numbers and controls |

---

## 15. The Short Version

- The experience is there. The proof in public is not.
- One blocking gap: local inference. Fix it first, before Go, before ERP, before anything else.
- One artifact to build: a technical case study on Bayan with real numbers.
- One title change: sovereign document intelligence architect.
- Two markets: UAE and Saudi first, UK and EU second.
- One caution: Gartner expects more than 40 percent of agentic AI projects to be cancelled by end of 2027 over cost, unclear value and weak controls. Survivors will be the ones who can show evals, cost numbers and controls, not the longest framework list.
