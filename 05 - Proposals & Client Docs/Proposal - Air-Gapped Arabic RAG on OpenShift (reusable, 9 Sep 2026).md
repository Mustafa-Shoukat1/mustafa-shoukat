# Proposal: Air-Gapped Arabic/English RAG on OpenShift

**Prepared by:** Mustafa Shoukat — Codagentic
**In response to:** Client Brief, "RAG system deployed on-premises" (received Apr 2026)
**Date:** 9 September 2026
**Status:** Reusable template. Fill the bracketed fields before sending.

| Field | Value |
|---|---|
| Client | `[CLIENT ORGANISATION]` |
| Contact | `[NAME, TITLE]` |
| Prepared for | `[DEPARTMENT / PROGRAMME]` |
| Valid until | `[DATE + 30 days]` |

---

## 1. The part that usually breaks

Most on-premise Arabic RAG deployments fail in the same place, and it is not the model. It is retrieval.

I have hit this personally while building an Arabic-first enterprise RAG platform:

- **Standard chunking cuts Arabic in the wrong places.** A 512-token window is tuned for English prose. Arabic regulatory text runs in dense paragraphs with long coordinated clauses; fixed windows split mid-sentence and, with some tokenizers, mid-word. The chunk that contains the answer stops containing it.
- **English-trained embedding models under-retrieve Arabic.** Arabic morphology derives many surface forms from one root. A general multilingual embedding treats those forms as weakly related, so the correct passage never enters the candidate set — and no amount of prompt engineering downstream recovers a passage that was never retrieved.
- **Dense-only search misses exact terms.** Regulatory queries turn on specific identifiers: article numbers, penalty clauses, dated circulars, transliterated product names. Vector similarity smooths precisely the tokens that matter.

The consequence is a system that demos well and then answers "I could not find that" on the questions the organisation actually cares about — or worse, answers confidently from the wrong department's document.

The fixes below are not theoretical. They are what is already running in the platform this proposal is built on.

---

## 2. What already exists

This proposal is not a greenfield build. It is the deployment and hardening of a system already running for Arabic-first enterprise document Q&A across multiple organisations.

Shipped and in use today:

| Capability | Implementation |
|---|---|
| Arabic-optimised dense retrieval | `omarelshehy/Arabic-Retrieval-v1.0`, 768-dim |
| Keyword / sparse retrieval | `Qdrant/bm25` |
| Hybrid fusion | Reciprocal Rank Fusion over dense + sparse |
| Reranking | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` (multilingual cross-encoder) |
| Answer confidence | NLI entailment scoring (`mDeBERTa-v3-base-xnli`) between answer and cited chunks |
| Multi-tenant isolation | Dedicated vector collection per organisation; cross-org access returns 404, not 403 |
| Department-level RBAC | Casbin policy engine, 5-role hierarchy, 32 policy rules, DB-backed, enforced server-side on every endpoint |
| Document access levels | Organisation / Department / Private, enforced at query time via payload filtering |
| Source citation | Inline citations streamed with the answer over SSE |
| Document ingestion | Docling converter, 13+ formats (PDF, DOCX, XLSX, PPTX, HTML, CSV, MD, JSON, XML, images) |
| Bilingual UI | Full Arabic RTL and English LTR, no hardcoded strings |
| Audit trail | Every login, query, upload, delete and config change logged with user, IP, timestamp; CSV export |
| Observability | Prometheus (12+ custom metrics), Grafana, Loki |
| Test suite | 617 tests, 65% backend coverage gate enforced in CI |
| API | 50+ REST endpoints |

**Deployment today is Docker Compose.** Porting to OpenShift is real work and is priced as such in section 7.

---

## 3. Requirement-by-requirement response

| # | Your requirement | Status | How it is met |
|---|---|---|---|
| 1 | OpenShift cluster with GPU | **Port required** | Existing Compose topology converted to a Helm chart / OpenShift manifests. GPU node selector and resource limits for the inference service. Containers already run non-root (UID 1000), which OpenShift's restricted SCC requires. |
| 2 | Strictly air-gapped, no outbound internet | **Work item — see §4** | Four of the five ML models already load and run in-container. Generation is the one component that currently calls out. Replacing it with local vLLM is a configuration change behind an existing provider abstraction, not a rebuild. |
| 3 | 100% open source, no licensing fees, no external APIs | **Met after §4** | Every component listed above is open source: FastAPI, Qdrant, PostgreSQL, Redis, nginx, Prometheus, Grafana, Loki, vLLM, and open-weight models. No per-seat or per-token licensing. |
| 4 | 5–15 concurrent sessions | **Met** | Multi-worker deployment with an auto-sized ML thread pool; a single GPU node covers this range with headroom. See §5. |
| 5 | Complete response in 3–5 seconds | **Met, with a design constraint** | Achievable at this concurrency. Requires an answer-length cap and moving confidence scoring off the blocking path. Full budget in §5. |
| 6 | Organisational RBAC, department data isolation | **Met** | Casbin, server-side, on every endpoint — not client-side filtering. Department tag enforced as a metadata filter at query time, so an unauthorised chunk is never retrieved, not merely hidden. |
| 7 | Hybrid search, Arabic + English | **Met** | Dense (Arabic-optimised) + BM25 sparse, combined by RRF, then cross-encoder reranked. This is the direct answer to §1. |
| 8 | Saudi/Gulf business context, MSA + local terms | **Met + tuning** | Arabic-optimised embeddings and chunking tuned for Arabic regulatory text. Domain and dialect terms handled through a client-specific glossary and prompt layer during Phase 2. |
| 9 | Optional light fine-tuning / prompt engineering | **Optional line item** | Priced separately in §7. Recommendation: exhaust retrieval tuning and prompt work first — cheaper, faster, reversible. Fine-tuning is rarely the bottleneck when retrieval is the problem. |
| 10 | Full data isolation, no external training or leakage | **Met after §4** | Once generation is local, no document text leaves the cluster at any stage. Per-org vector collections and audit logging make that demonstrable, not merely asserted. |
| 11 | Optimised inference engine (vLLM) | **Work item — §4** | vLLM with continuous batching and paged attention, sized in §5. |
| 12 | REST API for internal chat integration | **Met** | 50+ documented REST endpoints, streaming and non-streaming, built for exactly this. |
| 13 | Every response cites its source document | **Met** | Citations are part of the streamed answer, tied to specific retrieved chunks, plus an NLI confidence score per answer. |
| 14 | Stable re-indexing without downtime | **Partly met — work item** | Background ingestion, SHA-256 dedup, versioning, orphan cleanup and sparse backfill all exist. Zero-downtime collection swap (build new collection, atomic alias switch) is a defined Phase 2 item. |

---

## 4. The air-gap: stated plainly

I will not claim a fully air-gapped system that has not yet run air-gapped, so here is the exact position.

**Today:** embeddings, sparse indexing, reranking, NLI confidence scoring and document conversion all run inside the container. Generation calls an external inference endpoint. The system has an air-gap configuration flag; it is a flag, not a deployment I can point to and say "this ran with the network cable pulled."

**What this engagement does:** stands up vLLM inside the cluster serving an open-weight Arabic-capable model, behind the LLM provider abstraction the platform already has (a configurable base URL, already protected against SSRF). Candidate models: Falcon-H1 7B (Arabic-focused), Qwen3-8B, or a client-approved equivalent. The deployment is then verified with egress blocked at the namespace network policy, not merely at the application config.

**Why this is low risk:** the abstraction boundary already exists and is already exercised. This swaps the implementation behind an interface, and the four other models prove the in-container inference pattern works. The genuine unknowns are Arabic generation quality of the chosen open-weight model versus the current one, and GPU sizing — both resolved in Phase 1, before the bulk of the fee is committed.

**Acceptance:** the air-gap requirement is signed off by running the full test suite with the namespace egress policy set to deny-all. Not by a configuration flag.

---

## 5. Meeting 3–5 seconds at 5–15 concurrent

Latency budget for a complete (not first-token) response:

| Stage | Budget | Note |
|---|---|---|
| Query embedding | 20–40 ms | Arabic embedding model, in-container |
| Hybrid retrieval (dense + BM25) | 30–90 ms | Qdrant, HNSW tuned (`m`, `ef_construct`, `ef` configurable) |
| RRF fusion | <5 ms | |
| Cross-encoder rerank (top ~50 → top 5) | 100–300 ms | GPU-resident |
| **Retrieval subtotal** | **~0.2–0.45 s** | |
| Generation (vLLM, 7–8B, ~200 output tokens) | 2.5–4.5 s | Dominant term. Continuous batching holds this across 15 concurrent streams |
| **Total** | **~2.7–5.0 s** | |

Two design decisions follow from this budget, and I would rather state them now than discover them at UAT:

1. **Answer length must be capped** (~200–250 tokens). Generation dominates the budget; an uncapped answer will breach 5 seconds regardless of hardware. For contact-centre use this is the right shape anyway — agents want the answer and the citation, not an essay.
2. **NLI confidence scoring moves off the blocking path.** It currently runs before the answer is finalised. At 100–200 ms batched it is affordable, but it is spent in the wrong place; it will be computed against the streamed answer and attached on completion.

**GPU sizing:** a single GPU with 40–48 GB (A100 40GB, L40S 48GB or equivalent) serves a 7–8B model in FP16 with KV-cache headroom for 15 concurrent sessions. At this concurrency the load is modest — this does not need a multi-GPU cluster, and I will not quote one.

**Verification:** a Locust load-test configuration already exists in the platform. Acceptance includes a measured run at 15 concurrent sessions with p50 and p95 published, plus recall@5 against a client-approved golden set.

---

## 6. Proposed architecture

```
                    OpenShift Cluster  (namespace: rag-prod, egress: deny-all)
 +--------------------------------------------------------------------------+
 |                                                                          |
 |   Route / Ingress (TLS, rate limit)                                      |
 |            |                                                             |
 |            v                                                             |
 |   +------------------+       REST + SSE      +----------------------+    |
 |   |  RAG API         |<----------------------| Internal chat system |    |
 |   |  (FastAPI)       |                       |      [CLIENT]        |    |
 |   |  Casbin RBAC     |                       +----------------------+    |
 |   |  JWT + audit     |                                                   |
 |   +--+---+---+---+---+                                                   |
 |      |   |   |   +------------------+                                    |
 |      |   |   |                      v                                    |
 |      |   |   |            +--------------------+   GPU node              |
 |      |   |   |            |  vLLM  (7-8B)      |   nodeSelector:         |
 |      |   |   |            |  open-weight, local|   nvidia.com/gpu        |
 |      |   |   |            +--------------------+                         |
 |      |   |   |                                                           |
 |      |   |   +--> In-container ML: Arabic embeddings . BM25 .            |
 |      |   |        cross-encoder reranker . NLI scorer . Docling          |
 |      |   |                                                               |
 |      |   +--> Qdrant      (one collection per organisation)              |
 |      |   +--> PostgreSQL  (users, orgs, departments, documents,          |
 |      |   |                 audit log, Casbin policies)                   |
 |      |   +--> Redis       (response cache, sessions)                     |
 |                                                                          |
 |   Prometheus --> Grafana        Loki <-- Promtail                        |
 +--------------------------------------------------------------------------+
            No component initiates an outbound connection.
```

**Department isolation** is enforced twice: the organisation gets its own Qdrant collection (a hard boundary), and within it every query carries a department/access-level metadata filter derived server-side from the caller's JWT claims. A user cannot widen their own scope by manipulating the request.

---

## 7. Commercials

### Phased delivery

**Phase 1 — Air-Gap Readiness & Proof of Deployment · 3 weeks · `[USD 6,000 – 9,000]`**
- vLLM stood up in the cluster with the selected open-weight model, egress denied
- Arabic generation quality compared against the current baseline on client sample documents
- One department, one document set, deployed on your OpenShift
- Measured latency (p50/p95) at target concurrency, and a recall@5 baseline
- Written GPU sizing recommendation
- **Deliverable:** a running air-gapped pilot and a go/no-go report with numbers

Phase 1 exists so that neither of us commits the full budget before the two genuine unknowns — Arabic quality of the local model, and GPU sizing — are resolved with measurements.

**Phase 2 — Production Implementation · 6–8 weeks · `[USD 18,000 – 26,000]`**
- Full OpenShift manifests / Helm chart, health checks, resource limits, restricted SCC
- All departments onboarded, RBAC policy configured to your org chart
- Retrieval tuned on your corpus: chunking for your document classes, glossary for Saudi/Gulf business terms
- Zero-downtime re-indexing (build-and-alias-swap)
- Citation and confidence scoring verified against a client-approved golden set
- REST integration with your internal chat system
- Monitoring stack, dashboards, alerting, backup and restore procedures
- Admin and operator training, handover documentation, runbook
- **Deliverable:** accepted production system, source, documentation, and published performance numbers

**Phase 3 — Support & Optimisation · optional · `[USD 3,000 – 5,000] / month`**
- SLA-backed support, model and dependency updates, corpus growth tuning
- Monthly retrieval-quality report against the golden set
- Minimum 6-month term, 60-day notice

### Optional line items

| Item | Price |
|---|---|
| Arabic prompt optimisation + domain glossary (recommended before any fine-tuning) | `[USD 2,000 – 3,500]` |
| Light fine-tuning (LoRA) on client corpus, incl. eval harness | `[USD 4,000 – 8,000]` |
| Each additional department beyond agreed scope | `[USD 800 – 1,500]` |
| DR / multi-site replication design | `[USD 2,500 – 4,000]` |
| Standalone Air-Gap Readiness Assessment (credited against Phase 1 if you proceed) | `[USD 2,500]` |

### Payment schedule

30% on signature · 40% at Phase 2 UAT · 30% on acceptance. Phase 1 invoiced in full on completion and credited against Phase 2 if you proceed.

### Excluded

Hardware and GPU procurement, OpenShift licensing and cluster administration, network and firewall changes, document digitisation or OCR clean-up of poor-quality scans, and any third-party system integration beyond the one internal chat API.

---

## 8. What I need from you

1. OpenShift version, available GPU model and VRAM, and namespace admin access for deployment
2. A representative sample of the document corpus — 50–100 documents spanning the real range of formats and quality, not the clean ones
3. 100–200 real user questions in Arabic and English, with expected source documents, for the golden set. **This is the single highest-value thing you can provide**; retrieval cannot be tuned or proven without it
4. Your department structure and access matrix
5. A named technical contact for weekly review, and your security review windows

---

## 9. Why this team

- Two years building and operating Arabic-first enterprise RAG for government and enterprise organisations through a Saudi contract holder
- The retrieval problems in §1 were solved by hand on a real corpus, not read about
- Upstream pull requests submitted (open) to the multilingual RAG evaluation tooling used in this space, plus a public Arabic retrieval benchmark harness
- Riyadh working hours — full working-day overlap, on-site available
- Engineering discipline: 617 tests, a coverage gate, security scanning and audit logging are already in the product, not promised for later

---

## Appendix A — Re-engagement note

*Use when responding to a brief that has aged. Lead with the substance, not the apology.*

> Subject: Air-gapped Arabic RAG on OpenShift — architecture and costs
>
> Dear `[NAME]`,
>
> You shared a brief for an on-premise, air-gapped RAG system on OpenShift with department-level RBAC, Arabic/English hybrid search and cited answers. I have put together the architecture and costed implementation for exactly that specification — attached.
>
> Two things you may find useful whether or not we work together: a latency budget showing what 3–5 second complete responses actually require at 5–15 concurrent sessions, and the specific reason most Arabic RAG deployments under-retrieve (it is chunking and embedding choice, not the model).
>
> If the requirement is still live, I would suggest starting with a three-week air-gapped pilot on one department, so the performance numbers are measured rather than promised.
>
> If it has moved on or been solved internally, I would still value knowing which way you went.
>
> Regards,
> Mustafa Shoukat — Codagentic
> `[phone] · [email] · Riyadh`

---

## Appendix B — Reuse notes (internal, delete before sending)

- Replace every `[BRACKETED]` field. Set the final price inside each band before sending; never send a range to a client.
- §1 and §5 are the differentiators. Most competing proposals contain neither a named failure mode nor a latency budget. Do not cut them for length.
- §4 must stay honest. If the local-inference work has since shipped, rewrite §4 in the past tense and fold it into §2 — that is a materially stronger proposal.
- Client names stay out of §9 until written permission exists (see DECISIONS row 17).
- Do not add measured eval numbers until they have actually been measured. The `0.87 faithfulness / 0.91 relevance` figures in the old learning roadmap were scripted, never run.
