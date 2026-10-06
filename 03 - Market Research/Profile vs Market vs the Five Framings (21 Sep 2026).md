# Profile vs market vs the five framings

**Date:** 21 September 2026
**Question asked:** what is the difference between the five directions in the 21 Sep messages (AI product and agentic system architecture, then AI research automation, then machine intelligence evolution, then new substrates of intelligence, then the science of general intelligence) and the work already decided in this workspace.
**Method:** every strategic file in this workspace read again (`Position vs Market (Sep 2026).md`, both market research documents, the 8 Sep workspace audit and its GitHub findings, the LinkedIn specialist draft, `DECISIONS NEEDED`, the Fiverr briefs analysis, the OpenShift proposal and rate card, `Full-Profile.md`), then checked against live 2026 market data on agentic hiring, MCP adoption, evaluation and observability spend, frontier lab hiring, AI for science, and the Saudi sovereign programme. Sources at the end.

---

## 1. The finding in one paragraph

The five framings are not five rungs of one ladder. Framing 1 is a job that exists, pays, is being filled right now, and is roughly eight weeks of artefacts away from you. Framings 2 to 5 are research agendas that live inside about five organisations on earth, are credentialled by published research output rather than by delivery, and have no procurement line, no client, and no posting you could answer this year. The difference between those messages and what this workspace decided in September is not ambition. It is that the September plan names an artefact and the five messages name a person. You already have nine headline variants on file and a checklist standing at 0 of 80. The five framings are variants ten to fourteen, written in eight minutes.

---

## 2. What the market actually pays for each framing

| # | Framing | Does the job exist in 2026 | What it is credentialled by | Your distance |
|---|---|---|---|---|
| 1 | AI product and agentic systems architecture | Yes, at scale. About 90,000 agentic postings in 2026, up 280% year on year. Architect median 189,000 USD, agentic engineer bands 185k to 320k, architect bands quoted as high as 260k to 420k. 15% of architect roles are contract, staffed per engagement by IT and professional services firms | One production system you designed, with eval numbers, governance controls and a named failure you fixed | **6 to 10 weeks of artefacts.** Everything underneath is already built |
| 2 | AI research automation, autonomous machine intelligence | Barely, as employment. OpenAI reported reaching an automated research intern in September 2026 and targets an automated AI researcher by March 2028; Anthropic names self improvement the next milestone. The people doing this are Research Scientists (PhD dominant, 771k to 1.47M USD) and Research Engineers (no PhD required, but demonstrated research output required, up to 530k) | Public research output: papers, reproductions, benchmarks, environments, open models | **2 to 4 years**, starting from a first public research artefact you do not yet have. Your BS completes August 2027 |
| 3 | AI R&D automation, machine intelligence evolution, CodAgentic as a research laboratory | Not as a market. It is an internal agenda at frontier labs and a handful of funded startups (Lila Sciences and the twelve AI co-scientist systems of 2026), all compute heavy | Capital and compute, plus a research record | **Not reachable from under 10k USD a month with no owned compute.** This is an outcome of success, not a route to it |
| 4 | New substrates of intelligence, automated invention of paradigms | No | State or lab scale research programmes | Not a career step. A reading interest |
| 5 | Architect of general intelligence, the science of intelligence | No | PhD plus a decade | Not a career step. A reading interest |

Two things follow. First, only framing 1 converts into money, a visa, a contract or a title inside the next twelve months. Second, framings 2 to 5 are not forbidden to you; they are gated by a kind of evidence (public research output) you have never produced, while framing 1 is gated by a kind of evidence (a delivered, measured, governed system) you have produced four times and never published.

---

## 3. Why framing 1 is not the small ambition

The strongest argument for framing 1 is the same trend the other four point at. If research automation works, the scarce skill stops being "can you invent an architecture", because machines will propose architectures. The scarce skill becomes "can you make an autonomous system trustworthy, bounded, auditable and lawful inside an institution that will never hand a model the keys". The 2026 numbers already price this:

- Almost four in five enterprises have adopted agents in some form; about one in nine runs them in production. That gap is the entire job.
- Over 40% of early agentic projects are abandoned, and the named causes are architecture, cost overrun and missing governance, not model quality.
- Only 38% of production agents have automated evaluations running on every prompt change. Agents without eval coverage had a 47% rollback rate over the prior year; agents with full coverage, 9%.
- Evaluation and observability budgets rose at 71% of enterprises, averaging about 310k USD a year in mid market and 2.4M in the Fortune 500.
- MCP went from experiment to infrastructure: about 97 million monthly SDK downloads, 5,800+ servers, 28% of the Fortune 500 deployed, 41% of software organisations in limited or broad production. The 2026 roadmap's own priority is enterprise readiness: identity provider integration, audit trails, gateway behaviour.

That last row corrects an earlier note in this workspace. In April, MCP was called "the cheapest ahead position, almost nobody sells it". In September 2026 that is no longer true for MCP in general. What is still thin is MCP done the way a regulated buyer needs it: authorisation through the customer's identity provider, per tenant scoping, audit trail, a written security model. ByanRAG already has the Casbin layer that makes that version possible, so the opening survives, but it narrowed, and it now has to be sold as governed tool infrastructure rather than as "an MCP server".

So framing 1, stated properly, is not "I build agents". It is: **I build the control plane that lets autonomous systems be trusted inside regulated institutions.** That sentence survives all five escalations, and it is the only one you can start proving this week.

---

## 4. Profile versus market: where you actually are

### 4.1 Verified from the repositories, not the resumes

- ByanRAG and `arabic-rag`: 560 of 818 commits are yours. Per organisation Qdrant collections, 32 Casbin rules over 50+ endpoints, hybrid dense plus BM25 with reciprocal rank fusion, cross encoder reranking, NLI faithfulness scoring, cited streaming answers, full RTL, exportable audit log, Prometheus, Grafana, Loki, blue green deploy scripts, an OWASP CRS nginx image with ZAP blocking in CI, air gap install and start scripts that verify three pre cached models.
- Live products since June, built on a team rather than solo: whoza.ai (585 commits, four contributors, live), aroya.ai (live), TOTO unified WhatsApp, Instagram and TikTok inbox for a Malaysian client (deployed), the PRE WhatsApp assistant (in production and maintained), Ghar Tak, WhatsApp Translator (a licensed 360dialog product).
- Research adjacent work that already exists: `arabic-rag-bench` (an RL environment with four planted bugs and deterministic Recall@5), the Claude as judge and 3C3H reward pipeline for Yehia 7B GRPO training, Ragas Arabic and CJK PRs, `mcp-demo` with Arabic tools.
- Delivery evidence: `docs/DELIVERY_BENCHMARK_REPORT.md` of 12 May carries real numbers (RAG query 2.05 s average on the full pipeline, health 33 ms, login 288 ms, backend 2,545 of 2,545 tests, frontend 368 of 368, E2E 245 of 255).

### 4.2 Blocking, and unchanged since April

- Generation still defaults to the HuggingFace router and `MOCK_LLM=1`. The code supports local serving; no deployment with a local model is evidenced.
- The nightly Ragas job has failed every night. The cause is known and trivial: `docker-compose.yml` now requires `REDIS_PASSWORD` and `POSTGRES_PASSWORD`, and `ragas-nightly.yml` never sets them. So there is no recall or faithfulness number anywhere, for a system built precisely to produce them.
- No Kubernetes, no GPU scheduling, no PII redaction before the prompt, no permission inheriting connector, no published case study, no merged upstream PR.
- Claims a buyer can falsify in one question: "air gapped with zero external dependencies", a "65% coverage gate" against a report that says backend coverage is 29%, "617+ tests" against a report that counts 3,158, "0.87 faithfulness" written before any evaluation ran, "AI Receptionist SaaS" as delivered work, "contributor to Mulhem" with zero commits in any Mulhem repository, an MS at NUST the live profile does not show.

### 4.3 The dissonance nobody has named yet

Your inbound demand is the only market data that is about you rather than about the market. Across 267 Fiverr briefs, 15 Sep 2025 to 10 Sep 2026: automation and API integration 47 (18%), AI agent and chatbot builds 45 (17%), full app or SaaS 40 (15%), support and reception 34 (13%), lead generation and CRM 30 (11%), WhatsApp named explicitly in 105 briefs (39%), healthcare 18%. **Document AI and RAG: 14 briefs, 5%.**

That is not evidence the sovereign RAG specialisation is wrong. It is evidence you are fishing in the wrong water for it, exactly as your own 28 August note says: those buyers do not post on Fiverr, they hire through integrators, consultancies, Gulf government suppliers and forward deployed roles. You are running two economies at once:

| | Cash economy | Career economy |
|---|---|---|
| Channel | Fiverr, Upwork, referrals | Gulf integrators, sovereign programmes, platform vendors, consultancies |
| Tickets | 200 to 6,000 USD plus retainers | 3,000 to 25,000 USD per engagement, or 70k to 130k salaried with sponsorship, tax free, higher for architecture |
| Volume | 20.5 briefs a month arriving unprompted | Two live openings on disk, both unanswered until September |
| Proof it needs | Screenshots and speed | Eval numbers, governance controls, residency compliance |
| Your state | Producing, under 10k a month | Fully built, entirely unpublished |

All five framings are about the career economy. None of them pays next month. The mistake would be to let framing language pull you out of the cash economy before the career economy has produced one signed thing.

### 4.4 Constraints the five framings ignore

- Your BS completes August 2027. Saudi Council of Engineers registration and work permit tiers hinge on a completed degree, which makes UAE the realistic sponsored employment target before then and Saudi the target after.
- You cannot bid Saudi government tenders directly. Etimad requires a regional headquarters with at least fifteen full time staff, plus Saudization and local content scoring. The routes are subcontracting to a holder, joining a Gulf firm, or selling to private enterprises through a partner entity.
- You are already inside the exact institution framing 1 requires: employed at Navid in Riyadh, working on an Arabic enterprise platform under PDPL, NDMO residency rules and SDAIA expectations, in the one country spending at state scale on this (HUMAIN's eleven data centres and 2.2 GW programme, ALLaM under HUMAIN and SDAIA, a Saudi AI market projected from 79.9M USD in 2024 to 800.6M by 2030). That access is the scarcest input in this whole analysis and it is not permanent.

---

## 5. The difference, stated plainly

| The five messages | This workspace |
|---|---|
| Name an identity | Name an artefact |
| Escalate every two minutes | Repeat the same four blocking items since 4 April |
| Assume the gap is ambition | Show the gap is publication: zero numbers, zero merged PRs, zero case studies, 0 of 80 |
| Frame CodAgentic as a future research laboratory | Record CodAgentic at under 10k a month against a 50k goal, with no rate card attached to a live offer until 9 September |
| Point at the frontier | Point at Riyadh, where you already hold a badge |

They agree on one thing worth keeping: the durable skill is systems architecture around models, not frameworks. The workspace said it first, and said it with receipts.

---

## 6. What to do, in order

**This week, hours not days.**
1. Add `REDIS_PASSWORD` and `POSTGRES_PASSWORD` to the Boot stack and Stop stack steps of `ragas-nightly.yml`. One green run gives you the first recall and faithfulness numbers you have ever had.
2. Point `LLM_API_URL` at vLLM serving Falcon H1 Arabic 7B (about 5 GB at Q4, leads the Open Arabic LLM Leaderboard at roughly 71.5%), set `MOCK_LLM=0`, record the Arabic quality delta. That day, "sovereign" stops carrying an asterisk.
3. Correct the falsifiable claims: coverage 29% not 65%, tests 3,158 not 617, "air gap ready" not "air gapped", the Mulhem clause precise or absent, the receptionist SaaS out of Projects, the scripted 0.87 line deleted.

**Weeks 2 to 6, the framing 1 artefact.**
4. One governed agentic workflow at Navid, end to end: tool selection measured, retry and fallback paths, approval gate, kill switch, PII redaction before the prompt, audit trail, cost per query. This is what the architect job descriptions describe and the piece none of your systems currently has.
5. Port the Docker Compose stack to k3s with GPU scheduling. Single node counts.
6. One MCP server exposing ByanRAG retrieval behind the existing Casbin and API key layer, published with identity provider integration and a written security model.

**Weeks 7 to 8, the publication.**
7. The case study: tenancy model, RBAC enforcement point, retrieval pipeline with the week 1 numbers, sovereign topology, redaction and audit trail, cost and latency. Publish it. Change the title the same day, once, then leave the title alone for six months.
8. Send it to Navid leadership as an internal architecture record, to the unanswered OpenShift brief, to SDAIA's vendor database, and to the Gulf integrator and boutique list (Mozn, Ejada, Lucidya, Tezeract, aTeam, Core42, Inception, AI71).

**Continuously.** Keep WhatsApp, voice and integration work running. Twenty briefs a month arrive on their own; that runway is what buys the eight weeks.

**Where framings 2 to 5 go.** Into one line on a calendar, not into a title: upgrade `arabic-rag-bench` into a published Arabic agent benchmark, and land one merged upstream PR in Ragas. Those two are simultaneously credible research output and credible architecture proof, and they are the only honest on ramp from where you stand to where those messages point. If you ever want framing 2 seriously, that is the door: research engineer through demonstrated output, after the degree, after a public benchmark, never through a self description.

---

## 7. Sources checked

Market and hiring: agentic posting volume, growth and salary bands (jobsbyculture, aitechconnect, theaicareerlab, novelvista, gsdcouncil, 2026); pilot to production gap and abandonment rates (same set, plus the Gartner figures cited in the September market document). Evaluation and observability spend, eval coverage and rollback rates, platform landscape (guptadeepak 2026 market reality check, LangChain State of Agent Engineering, MLflow agent observability guide, AWS AgentCore Evaluations GA March 2026). MCP adoption (cdata 2026 enterprise readiness, guptadeepak MCP enterprise guide, the modelcontextprotocol 2026 roadmap, WorkOS, nevermined statistics). Frontier research automation (Help Net Security on OpenAI's automated research intern, September 2026; Anthropic on recursive self improvement; MIT Technology Review, August 2026; Turingpost RSI explainer). Frontier lab hiring and credentials (Sundeep Teki, research engineer versus research scientist; jobsbyculture AI research engineer path). AI for science employment (Turingpost twelve AI co-scientists 2026; Lila Sciences; Research.com science career outlooks). Saudi sovereign programme (vision2030.ai Year of AI, HUMAIN, SDAIA and ALLaM coverage, Gulf AI Monitor). Internal: `Position vs Market (Sep 2026).md`, `Complete Market Research 2026`, `AI Job Market Research and Action Plan`, `01 - GitHub Findings (8 Sep 2026).md`, `02 - GitHub Activity Inventory`, `Fiverr Briefs Analysis (Sep 2025 to Sep 2026).md`, `LinkedIn - Specialist Profile (draft, 8 Sep 2026).md`, `DECISIONS NEEDED`, `Proposal - Air-Gapped Arabic RAG on OpenShift`, `Rate Card (Codagentic, 9 Sep 2026)`, `Full-Profile.md`.
