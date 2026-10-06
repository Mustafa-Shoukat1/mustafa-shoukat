# Roadmap PDF vs Jobs vs My Skills

**Date:** 5 October 2026
**What this is:** one page that puts three things side by side: what the roadmap PDF says to learn, how often real job ads ask for it, and where you stand.

**Where the numbers come from**
- **PDF:** `AI_Systems_Architect_Roadmap.pdf` (8 phases). The PDF itself is not saved in this folder.
- **Jobs, worldwide:** 28 job ads read in full (14 from September 2026, 14 from April to August 2026).
- **Jobs, Gulf:** 32 job ads from Saudi Arabia, the UAE and Qatar, 5 September to 2 October 2026.
- **You:** a check of your GitHub and files on 3 October 2026.

---

## Short answer

1. You already know Phases 1 and 2 of the PDF. Skip them.
2. Jobs ask most for: agents, systems that run live, safety and control, RAG, monitoring, and testing.
3. Your biggest gap is testing with scores (Phase 5). You built the test setup, but no score has ever been published.
4. Smaller gaps: a real MCP server, cost tracking, Kubernetes or OpenShift, and running the AI model on your own server.
5. Two things matter in the Gulf that the PDF does not mention: Arabic, and keeping data inside the country.

---

## Side by side

| PDF item | Worldwide jobs (out of 28) | Gulf jobs (out of 32) | You |
|---|---|---|---|
| **Phase 1.** Basics: Python, Git, databases, Docker, Linux | Python in 17 | Not counted | **Know it** |
| **Phase 2.** RAG (AI that reads your documents and answers with sources) | 14 | About 18 | **Know it.** ByanRAG does all of it |
| **Phase 3.** Agents (AI that does tasks step by step) | 24 | About 15 | **Mostly.** Missing a human approval step and a stop button |
| **Phase 3.** Agent tools such as LangChain and LangGraph | 14 | Not counted | **Know it** |
| **Phase 3.** MCP (a standard way to connect AI to other apps) | 10 | Not counted | **Small demo only** |
| **Phase 4.** Running live systems for real users | 20 | Not counted | **Know it** |
| **Phase 4.** Safety and control: logins, permissions, records of who did what | 15 | Not counted | **Know it** |
| **Phase 4.** Cloud | 16 (Azure 10, AWS 7, Google 7) | Asked about as often as own-server skills | **Partly.** Some AWS, almost no Azure |
| **Phase 4.** Cost tracking | 7 | Not counted | **Not yet** |
| **Phase 4.** Kubernetes (software that runs apps across many servers) | 1, but this is likely undercounted | OpenShift is named in the Riyadh jobs closest to your work | **Not yet** |
| **Phase 5.** Monitoring and tracing | 13 | Not counted | **Partly.** Monitoring yes, tracing no |
| **Phase 5.** Testing AI with scores | 11 | The Saudi government guideline asks for accuracy checks | **Biggest gap.** Setup built, no published score |
| **Phase 6.** Design and architecture | 21 want design and coding together; only 2 want design alone | 12 of 14 architect jobs ask for 8 or more years | **Done in practice,** never written down |
| **Phase 7.** Public proof of your work | 4 mention open source, always as "preferred" | No Gulf company was found publishing Arabic test scores | **Built, but private** |
| **Phase 8.** Research automation | Not in any ad | Not in any ad | **Later** |

### Things jobs ask for that the PDF leaves out

| Item | Worldwide jobs (out of 28) | Gulf jobs (out of 32) | You |
|---|---|---|---|
| Daily hands-on coding | 25 | Not counted | Yes |
| Arabic | 0 | Required in 4, a plus in 7 | Your systems handle Arabic. Business-level spoken Arabic is not confirmed |
| Data stays in the country, own servers | 0 | Clearly asked in 7, softly in 9 more | **Partly.** Built for it, but the AI model was not yet running on your own server on 21 September |
| Finished degree | Required in 2; 20 do not mention it | Required in 14 | In progress until 2027 |
| Open to working from Riyadh | 1 of 30 clearly yes | You are already there | |

---

## Every PDF item, one by one

**Phase 1. Foundations** (jobs: Python in 17 of 28)
- Know: Python, Git and GitHub, APIs and JSON, SQL and databases, Linux, basic networking, basic software architecture, Docker
- Partly: none
- Not yet: none

**Phase 2. Core AI engineering** (jobs: RAG in 14 of 28 worldwide, about 18 of 32 in the Gulf)
- Know: LLMs and transformers, prompting, embeddings, vector databases, RAG, chunking and retrieval, tool calling, structured outputs, AI API integration, context management, memory
- Partly: none
- Not yet: none

**Phase 3. AI agents** (jobs: agents in 24 of 28 worldwide, about 15 of 32 in the Gulf; MCP in 10 of 28)
- Know: agent architecture, tool use, multi-step workflows, multi-agent systems, human-in-the-loop, state management, agent orchestration
- Partly: MCP (small demo only), retry and fallback, planning, agent memory
- Not yet: none

**Phase 4. Production AI systems** (jobs: live systems in 20 of 28, cloud in 16, safety in 15, cost in 7)
- Know: Docker, CI/CD, authentication and authorization, secrets management, cloud databases, logging, monitoring, caching, security, multi-tenancy
- Partly: AWS, queues and background jobs, scalability
- Not yet: cost optimization

**Phase 5. AI evaluation and AgentOps** (jobs: testing in 11 of 28, monitoring in 13)
- Know: evaluation datasets, golden datasets, regression testing, observability, monitoring, failure analysis
- Partly: accuracy (no published score), retrieval evaluation (no published score), hallucination testing, tracing
- Not yet: tool-use evaluation, agent trajectory evaluation (checking each step an agent takes)

**Phase 6. AI architecture** (jobs: 21 of 28 want design and coding together)
- Know: system architecture, RAG architecture, security architecture, AI orchestration
- Partly: microservices, data architecture, multi-agent architecture, cloud architecture, AI infrastructure, architecture trade-offs (done, never written down)
- Not yet: event-driven architecture

**Phase 7. Portfolio** (jobs: hiring managers look for proof that a system ran live)
- Project 1, Enterprise RAG: built (ByanRAG). Missing scores, and it is private
- Project 2, Agentic business system: partly (Global Holman). Missing the human approval step
- Project 3, Autonomous research agent: not started

**Phase 8. AI research automation** (jobs: not in any ad)
- Know: AI coding agents (you use them daily)
- Partly: automated evaluation, reinforcement learning concepts (arabic-rag-bench, the Yehia reward pipeline)
- Not yet: automated experimentation, scientific literature research, hypothesis generation, experiment design, self-improvement loops, evolutionary algorithms, AI-for-science

**The PDF's technology stack**
- Know: Python, FastAPI, PostgreSQL, Redis, Docker, LLM APIs, RAG and vector databases, agent orchestration, TypeScript and JavaScript
- Partly: AWS, evaluation and observability
- Demo only: MCP

**The PDF's "stop doing" list**
- Data Analyst, Project Manager, Cloud Engineer, WordPress Developer, Social Media Manager, ML Engineer, Automation Expert. This matches the choice you made on 8 September.

**Count:** of the 67 "learn" items in Phases 1 to 6, you know 46, partly know 17, and have 4 still to learn.

---

## What this means

- **The PDF is right about the target but wrong about the starting point.** It starts from zero. You are past the halfway mark.
- **Testing is where demand is higher than supply.** On Hacker News hiring threads, 12 to 19 in 100 AI job ads ask for testing skills, but only 8 in 100 job seekers offer them. For RAG it is the other way round.
- **"Architect" is a weak title for you today.** Only 3 in 100 AI ads on Hacker News use it, and Gulf architect jobs mostly want 8 or more years.

---

## Where the full research is

- Full report: `reports/AI architect market scan Oct 2026.md`
- Job ads read, worldwide: `research_notes/AI architect market scan Oct 2026/global_job_postings.md`
- Job ads read, Gulf: `research_notes/AI architect market scan Oct 2026/gulf_job_market.md`
- Reddit and Hacker News views: `research_notes/AI architect market scan Oct 2026/community_sentiment.md`
- Second report (business path): `reports/Next business beyond agency work.md`

**Limits of the numbers:** the samples are small (28 and 32 ads). LinkedIn, Indeed and Bayt blocked automatic reading, so some ads were missed. "About" means the count came from the report summary, not a full recount.
