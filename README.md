# The Unofficial Guide - UC Berkeley Housing RAG

This project builds a small retrieval-augmented generation system for student-generated UC Berkeley housing advice. It ingests local text documents, chunks them, embeds them with a local sentence-transformers model, stores them in ChromaDB, retrieves relevant chunks for a question, and asks a Groq-hosted LLM to answer using only those retrieved excerpts.

## Domain

The system covers student advice about UC Berkeley housing: freshman dorm choices, Clark Kerr vs Unit 1 tradeoffs, off-campus search timing, lower-cost options, co-ops, scams, rent expectations, and student-reported rental warnings. This knowledge is valuable because official housing pages explain policies, but students often want practical and subjective experiences that are scattered across Reddit threads.

## Document Sources

The raw corpus lives in `data/raw/`. The starter files contain metadata, source URLs, short summaries, and notes from a previous collection step; they intentionally do not copy full Reddit threads wholesale. For a stronger final corpus, paste selected permitted excerpts into each file's `MANUAL_COLLECTION_SPACE` and rerun the pipeline.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | A Complete Guide for UC Berkeley New Admits - Housing | Reddit starter note | `data/raw/01_new_admits_housing_guide.txt` |
| 2 | freshman housing advice | Reddit starter note | `data/raw/02_freshman_housing_advice_2024.txt` |
| 3 | Best recommended housing option for incoming UC Berkeley freshman | Reddit starter note | `data/raw/03_best_freshman_housing_options.txt` |
| 4 | Freshman Housing: Advice | Reddit starter note | `data/raw/04_freshman_housing_unit1_unit2_ck_blackwell.txt` |
| 5 | dorm advice | Reddit starter note | `data/raw/05_dorm_advice_ck_vs_unit1.txt` |
| 6 | Off-campus Housing Search Tips | Reddit starter note | `data/raw/06_offcampus_housing_search_tips.txt` |
| 7 | Off campus housing recommendations? | Reddit starter note | `data/raw/07_offcampus_housing_recommendations.txt` |
| 8 | cheap off campus housing options | Reddit starter note | `data/raw/08_cheap_offcampus_housing_options.txt` |
| 9 | Is the housing situation THAT bad? | Reddit starter note | `data/raw/09_is_housing_that_bad.txt` |
| 10 | LIST OF PLACES YOU SHOULD !NOT! RENT | Reddit starter note | `data/raw/10_places_not_to_rent.txt` |

Original source URLs are listed in `source_manifest.md` and in each raw file header.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Groq key to `.env`:

```bash
GROQ_API_KEY=your_real_key_here
```

## Run The Pipeline

Run these commands from the repo root:

```bash
python src/ingest.py
python src/chunk.py
python src/embed.py
python src/app.py --retrieval-only "What are the main tradeoffs between Clark Kerr and Unit 1?"
python src/app.py "What are the main tradeoffs between Clark Kerr and Unit 1?"
```

Use `--retrieval-only` while checking whether semantic search is working before spending LLM calls.

## Chunking Strategy

**Chunk size:** 900 characters.

**Overlap:** 150 characters for long sections that must be split.

**Why these choices fit your documents:** The corpus is made of short Reddit-thread notes and summaries. Paragraph-aware chunks keep each advice point coherent, while the 900-character target avoids mixing too many different dorm or off-campus topics into one chunk. The overlap only matters for longer manually pasted comments.

**Final chunk count:** Run `python src/chunk.py` and record the printed count here.

## Embedding Model

**Model used:** `sentence-transformers/all-MiniLM-L6-v2`.

**Production tradeoff reflection:** This model is free, fast, and local, which fits the assignment. In production I would compare it against stronger hosted embedding models with better accuracy on noisy student language, longer context support, multilingual support, and better latency at scale. I would also weigh privacy and cost against the simplicity of local embeddings.

## Grounded Generation

**System prompt grounding instruction:**

```text
You answer questions for a UC Berkeley student housing unofficial guide.
Use only the retrieved source excerpts provided in the user message.
If the excerpts do not contain enough evidence, say you do not have enough information.
Treat Reddit material as subjective student advice, not verified fact.
Include a short Sources section that lists the source numbers you used.
```

**How source attribution is surfaced in the response:** `src/generate.py` labels retrieved chunks as `[Source 1]`, `[Source 2]`, and so on, with title, URL, topic, and excerpt. The final answer is instructed to include a Sources section, and `src/app.py` prints the retrieved chunks after the answer for auditability.

## Evaluation Report

Run the five questions from `planning.md` after building the vector store. Paste concise results here.

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which UC Berkeley dorms do students recommend for freshmen who care about social life? | Unit 1, Unit 2, Unit 3, and Clark Kerr appear as social options, with tradeoffs around location, room size, and convenience. | Not run yet | Not run yet | Not run yet |
| 2 | What are the main tradeoffs between Clark Kerr and Unit 1? | Clark Kerr is more spacious/social but farther; Unit 1 is more convenient and closer to food and activities. | Not run yet | Not run yet | Not run yet |
| 3 | When do students suggest starting the off-campus housing search? | Spring semester, often late February or early March; April may still work but can be stressful. | Not run yet | Not run yet | Not run yet |
| 4 | What resources do students mention for finding off-campus housing? | Cal Rentals, Craigslist, Zillow, Trulia, Facebook groups, rental agencies, signs, lease takeovers, co-ops, and transit-accessible areas. | Not run yet | Not run yet | Not run yet |
| 5 | Which apartment has the objectively lowest crime risk near UC Berkeley? | The system should say it does not have enough information because the corpus lacks verified crime statistics. | Not run yet | Not run yet | Not run yet |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

## Failure Case Analysis

**Question that failed:** Fill in after testing. The intended stress test is: "Which apartment has the objectively lowest crime risk near UC Berkeley?"

**What the system returned:** Not run yet.

**Root cause (tied to a specific pipeline stage):** Not run yet. A likely root cause would be that the corpus contains subjective student warnings but no verified crime data.

**What you would change to fix it:** If the failure matters, add verified public safety data as a separate source type and add metadata/source-type filtering so the system can separate subjective Reddit advice from official statistics.

## Spec Reflection

**One way the spec helped you during implementation:** The spec made the chunking strategy concrete before writing code. That kept the implementation focused on paragraph-aware chunks with source metadata instead of a generic fixed-size splitter.

**One way your implementation diverged from the spec, and why:** The interface is a CLI instead of a web UI. The assignment allows a CLI, and it is the lowest-risk interface while the environment still needs to be tested on another computer.

## AI Usage

**Instance 1**

- *What I gave the AI:* The homework requirements, the prior GPT 5.5 notes, the UC Berkeley housing source manifest, and the starter repo structure.
- *What it produced:* A planning document and scripts for ingestion, chunking, embedding, retrieval, grounded generation, and a CLI.
- *What I changed or overrode:* I kept the corpus as summarized starter notes rather than copying full Reddit threads, and I kept evaluation outputs marked as not run because the environment should be tested elsewhere.

**Instance 2**

- *What I gave the AI:* The chunking and retrieval requirements from `planning.md`.
- *What it produced:* A pipeline that writes JSONL artifacts and uses ChromaDB with `all-MiniLM-L6-v2`.
- *What I changed or overrode:* I made generation optional behind the CLI path and added `--retrieval-only` so retrieval can be inspected before calling Groq.
