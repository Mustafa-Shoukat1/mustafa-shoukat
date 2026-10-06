# Codagentic — Rate Card

**Mustafa Shoukat** · AI Integration & Enterprise RAG · Riyadh (UTC+3)
Effective 9 September 2026 · Valid 90 days · All figures USD, exclusive of tax

---

## Engagement models

| Model | Price | Best for |
|---|---|---|
| **Fixed-scope project** | $8,000 – $26,000 | Defined deliverable, agreed acceptance criteria |
| **Monthly retainer** | $3,000 – $6,000 / month | Ongoing delivery, iteration, support. 6-month minimum |
| **Hybrid** | $5,000 setup + $2,000 – $3,000 / month | Build then operate — the default for production systems |
| **Assessment** | $1,500 – $3,000 | Fixed-fee diagnostic. Credited in full against a follow-on build |
| **Hourly** | $65 – $85 / hour | Advisory and scoped extensions only. Not offered for full builds |

**Payment:** 30% on signature · 40% at UAT · 30% on acceptance.
Retainers are invoiced monthly in advance, 60-day notice either way.

---

## Service lines

### 1. Enterprise & regulated RAG — self-hosted, permission-aware, Arabic + English

The flagship line. Multi-tenant document Q&A with server-side RBAC, hybrid Arabic/English retrieval, source citations and answer-confidence scoring, deployed on your infrastructure.

| Package | Price | Timeline |
|---|---|---|
| Air-gap / readiness assessment | $2,500 | 1 week |
| Pilot — one department, measured baseline | $6,000 – $9,000 | 3 weeks |
| Production implementation | $18,000 – $26,000 | 6 – 8 weeks |
| Support & optimisation retainer | $3,000 – $5,000 / month | Ongoing |

*Includes:* hybrid dense + BM25 retrieval with reranking, per-tenant vector isolation, 5-level RBAC, audit logging, Prometheus/Grafana/Loki observability, REST API, bilingual RTL/LTR interface, handover documentation and training.

*Add-ons:* Arabic prompt optimisation + domain glossary $2,000 – $3,500 · LoRA fine-tuning with eval harness $4,000 – $8,000 · additional department $800 – $1,500 · DR design $2,500 – $4,000.

---

### 2. AI integration into existing systems

Connecting AI to the systems a business already runs — CRM, calendar, telephony, email, billing, internal dashboards.

| Package | Price | Timeline |
|---|---|---|
| Single integration (one system, one workflow) | $1,500 – $4,000 | 1 – 2 weeks |
| Multi-system workflow | $4,000 – $10,000 | 3 – 5 weeks |
| Ongoing integration retainer | $2,500 – $4,500 / month | Ongoing |

*Shipped integrations:* WhatsApp Cloud API, Supabase, Twilio, n8n, GoHighLevel, Google OAuth/Calendar, SMTP/IMAP, Filevine, Stripe, Gmail/Sheets/Vertex/Firestore.

---

### 3. WhatsApp & conversational commerce

Official Cloud API only. The compliance layer is the product: HMAC-verified fail-closed webhooks, atomic deduplication, 24-hour service-window handling, STOP/START opt-out, PII-redacting logs, row-level security.

| Package | Price | Timeline |
|---|---|---|
| Starter — one flow, one number | $1,200 – $2,500 | 1 week |
| Business — multi-flow, CRM write-back, dashboard | $2,500 – $6,000 | 2 – 3 weeks |
| Managed operation | $600 – $1,500 / month | Ongoing |

---

### 4. AI audit & rescue

Fixed-fee diagnostic of an existing AI system that is underperforming, expensive or unreviewed. Written findings, prioritised remediation plan, and a quoted rebuild if you want one.

| Package | Price | Timeline |
|---|---|---|
| System audit | $1,500 – $3,000 | 1 week |
| Audit + remediation sprint | $5,000 – $9,000 | 2 – 3 weeks |

*Covers:* retrieval quality and eval coverage, prompt and context design, security and access control, cost per query, observability gaps, failure modes under load.

---

### 5. Voice agents — *in build, quoted case by case*

Not offered as a standard package until a recorded production deployment exists. Indicative range for scoping conversations only: $1,500 – $8,000 build, $300 – $1,200 / month managed.

---

## What is always included

- Source code and full ownership of what is built for you
- Handover documentation and a runbook
- Named failure modes and their mitigations, written down before the build starts
- Acceptance against measured numbers, not demos

## What is never included unless quoted

Hardware and cloud spend · third-party licences and API credits · data cleanup and document digitisation · out-of-scope system integrations · 24/7 on-call.

---
---

# Internal notes — not for client distribution

**Provenance.** Bands come from `Mustafa_AI_Agency_Plan.docx` (Mar 2026): $3,000/month minimum, $8,000+ per project, $5K + $2–3K/month hybrid, $1,500–$3,000 audit entry, 10 clients × $4,500 = $45K/month. Cross-checked against `Position vs Market (Sep 2026).md`: regulated self-hosted RAG $3,000–$25,000 (your highest ticket), AI integration builds $1,000–$10,000, WhatsApp $1,200–$6,000 + retainer, voice $1,500–$8,000 + $300–$1,200/month.

**Hourly positioning.** $65–$85 is deliberately above Upwork AI P90 ($60). The market doc's line is "positioning, not geography, sets your rate," and fixed price hides geography — which is why hourly is restricted to advisory here. Toptal ($100–$200+/hr) and Gun.io ($75–$175/hr, 0% commission) are the rate ceiling worth chasing; the doc calls applying there "the single highest-return administrative task on your list."

**Struck.** "AI Trainer $30–$65/hr" — the only hourly figure you ever wrote for yourself, and it anchors you at roughly half this card. Do not reuse it.

**Ordering is deliberate.** RAG leads because it is your only "ahead of market" line. Voice is last and hedged because there is no recorded call, no answer-rate number and no CRM write-back yet — listing it as delivered is one of the live credibility risks in the DECISIONS file (row 15).

**Price increases.** Per the agency plan: after 3 clients with documented results, raise new-client pricing 30–50%. After 6, introduce a premium tier at $8,000–$12,000/month. Existing clients get 60 days' notice.

**The audit is the lead product.** $1,500–$3,000 entry converting at 60–80% into a retainer is the cheapest way into an account. The `system-audit.prompt.md` file in `.github/prompts/` is already most of the delivery method.

**Before this card goes out:**
1. Set a single figure per line for each specific client — never send a range.
2. Decide the years-of-experience number (DECISIONS row 12; the evidence supports 5+, not 6 or 8+).
3. Get written client permission before naming anyone in a case study (DECISIONS row 17).
4. Attach one numbered case study. The card is materially weaker without it, and that is currently the biggest gap — no case study, no before/after number, no published eval figures.
