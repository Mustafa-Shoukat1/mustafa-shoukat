Gymnasium API (reset(), step(), observation, reward, done) 
SWE-bench

RLHF pipeline 


Task: Given a broken RAG pipeline with poor retrieval quality, fix the chunking strategy, embedding model selection, and retrieval parameters to achieve a target recall@k on a provided evaluation set.

THE PROBLEM YOU FACED:
━━━━━━━━━━━━━━━━━━━━

Arabic text is fundamentally different from English:
- Right-to-left
- Words have complex morphology (one root → many forms)
- Standard chunking breaks Arabic sentences badly
- Standard English embedding models perform poorly on Arabic

WHAT BROKE:
- Your chunks were splitting mid-sentence/mid-word in Arabic
- Standard chunk sizes (512 tokens) were too large for Arabic 
  regulatory text (dense paragraphs)
- Retrieval quality was poor — the right passages weren't 
  being found
- You had to experiment with: chunk sizes, overlap, embedding 
  models, retrieval strategies

WHAT YOU DID:
- Switched to Arabic-optimized embeddings (omarelshehy/Arabic-Retrieval-v1.0)
- Implemented hybrid search (dense + BM25 sparse)
- Added cross-encoder reranking (mmarco multilingual)
- Built NLI-based confidence scoring
- Tuned chunk sizes through trial and error
- Added RRF fusion for combining retrieval signals

"My experience building and debugging a complex RAG pipeline — dealing with Arabic text challenges, tuning chunking strategies, implementing hybrid retrieval, and iterating on retrieval quality — is exactly the type of real-world ML engineering problem that makes a great RL training environment. I've lived the problem, so I can design a realistic, challenging task around it.


TWO COMPLETELY DIFFERENT THINGS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

THING 1: What YOU did (in the past, building ByanRAG)
─────────────────────────────────────────────────────
You, Mustafa (a human), manually debugged your RAG pipeline.
You tried different chunk sizes.
You switched embedding models.
You added hybrid search.
You used trial and error.
NO RL was involved. NO LLM-as-agent was involved.
You were the engineer. You fixed it yourself.


THING 2: What you're DESIGNING for this assessment (now)
─────────────────────────────────────────────────────────
You take that SAME broken RAG problem you faced...
...and you package it into an ENVIRONMENT...
...where an LLM (not you) will try to fix it.

The LLM becomes the engineer.
YOU become the environment designer.


YOUR PAST:
  Mustafa faced broken RAG → Mustafa fixed it manually

YOUR ASSESSMENT:
  You RECREATE that broken RAG situation
  → Put an LLM inside it
  → LLM tries to fix it (like you did)
  → Judge scores whether the LLM fixed it correctly
  → Score is used as RL reward to train the LLM

THE CONNECTION: Your real experience INFORMS the design.
You know what broke, why it broke, and what the fix looks like.
That makes you the perfect person to design this environment.

YOUR ENVIRONMENT:
  "Fix the RAG pipeline to achieve ≥0.75 Recall@5"

HOW THE LLM COULD CHEAT:
━━━━━━━━━━━━━━━━━━━━━━━

CHEAT 1: "Look at the evaluation queries"
  The LLM reads /eval/queries.json
  Sees: "What is the penalty for tax evasion?"
  Expected doc: doc_42.txt
  
  LLM builds a fake "pipeline" that just returns 
  doc_42 whenever it sees the word "penalty"
  
  → HOW TO BLOCK: 
    The judge uses a SEPARATE hidden eval set at /judge/hidden_queries.json
    that the LLM CANNOT access (read-only, different directory)


CHEAT 2: "Modify the evaluation script"
  The LLM edits /code/evaluate.py to always print 
  "Recall@5: 0.99"
  
  → HOW TO BLOCK:
    The judge has its OWN evaluation script at /judge/evaluate.py
    The LLM cannot modify anything in /judge/
    The judge NEVER runs the LLM's evaluation script


CHEAT 3: "Bypass the pipeline entirely"
  LLM writes a /code/pipeline.py that doesn't actually 
  do retrieval — it just returns all documents for every 
  query (brute force, guaranteed to contain the right one)
  
  → HOW TO BLOCK:
    Judge also measures PRECISION or limits retrieved docs 
    to exactly top-5. If you return everything, precision is 
    near zero → low score.
    OR: Judge checks retrieval LATENCY — returning all docs 
    would be too slow.


CHEAT 4: "Hardcode document IDs"
  LLM reads the eval queries, memorizes which docs match,
  and hardcodes a lookup table instead of real retrieval
  
  → HOW TO BLOCK:
    Hidden eval set has DIFFERENT queries than anything 
    the LLM can see. Hardcoded answers won't match.


"I built ByanRAG, a production Arabic RAG system with hybrid search, cross-encoder reranking, and NLI-based confidence scoring. During development, I faced exactly these problems — English embedding models failing on Arabic, chunk sizes breaking Arabic sentence structure, and poor retrieval quality without reranking. I manually debugged and solved these issues through experimentation. This environment packages that real debugging experience into a repeatable task for LLM training. The bugs are authentic, the difficulty is calibrated from my own experience, and the evaluation criteria map to real retrieval metrics I used in production."
