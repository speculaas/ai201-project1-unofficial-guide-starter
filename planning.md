# Project 1 Planning: The Unofficial Guide

## Domain

My domain is UC Berkeley housing advice, mostly student-generated Reddit advice plus one official UC Berkeley housing reference. This knowledge is valuable because official housing pages explain policies and deadlines, but students also want practical advice about dorm social life, distance to campus, off-campus apartment searches, affordability, scams, co-ops, and places to avoid. That advice is scattered across threads and official pages, and the student advice often uses informal language.

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | A Complete Guide for UC Berkeley New Admits - Housing | New-admit housing guide covering residence halls and the first-year guarantee | `data/raw/01_new_admits_housing_guide.txt` |
| 2 | freshman housing advice | Freshman dorm ranking discussion for Unit 1, Unit 2, Unit 3, Clark Kerr, and Blackwell | `data/raw/02_freshman_housing_advice_2024.txt` |
| 3 | Best recommended housing option for incoming UC Berkeley freshman | Dorm comparison across Blackwell, Foothill, Units, Stern, and Clark Kerr | `data/raw/03_best_freshman_housing_options.txt` |
| 4 | Freshman Housing: Advice | Tradeoffs among Unit 1, Unit 2, Clark Kerr, and Blackwell | `data/raw/04_freshman_housing_unit1_unit2_ck_blackwell.txt` |
| 5 | dorm advice | Clark Kerr vs Unit 1 advice focused on social life, room size, location, and food access | `data/raw/05_dorm_advice_ck_vs_unit1.txt` |
| 6 | Off-campus Housing Search Tips | When and where students suggest looking for off-campus housing | `data/raw/06_offcampus_housing_search_tips.txt` |
| 7 | Off campus housing recommendations? | Rent expectations, amenities, scams, and CalRentals advice | `data/raw/07_offcampus_housing_recommendations.txt` |
| 8 | cheap off campus housing options | Lower-cost options such as co-ops, lease takeovers, Facebook groups, and transit-accessible housing | `data/raw/08_cheap_offcampus_housing_options.txt` |
| 9 | Is the housing situation THAT bad? | High-level discussion of Berkeley housing difficulty and affordability | `data/raw/09_is_housing_that_bad.txt` |
| 10 | LIST OF PLACES YOU SHOULD !NOT! RENT | Subjective warning thread about specific buildings and property management issues | `data/raw/10_places_not_to_rent.txt` |
| 11 | UC Berkeley Official Housing Application and FAQ Notes | Official notes on housing applications, guarantees, deadlines, broad preferences, and off-campus rental services | `data/raw/11_uc_berkeley_official_housing_application_faq.txt` |

The original URLs for each Reddit thread are listed in `source_manifest.md` and in each raw document header.

## Chunking Strategy

**Chunk size:** about 1000 characters.

**Overlap:** 150 characters, only when a paragraph or combined chunk is long enough to require splitting.

**Reasoning:** The final raw files put real collected content under `MANUAL_COLLECTION_SPACE:`. I only chunk that section and ignore helper summaries/notes so retrieval uses the actual corpus. Paragraph-aware chunks preserve coherent student advice better than a blind fixed-width split. A 1000-character target is large enough to keep context, while still small enough that retrieval can match focused questions about Clark Kerr, Unit 1, off-campus search timing, co-ops, official deadlines, or scams. The 150-character overlap protects the boundary when a long paragraph has to be split.

## Retrieval Approach

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`.

**Top-k:** 5 chunks.

**Production tradeoff reflection:** I chose `all-MiniLM-L6-v2` because it runs locally, is fast, and matches the recommended free stack for the assignment. For a production system, I would compare it against higher-accuracy embedding models with longer context windows and better performance on noisy social-media language. I would also weigh local privacy and cost against API-hosted latency, throughput, multilingual support, and whether the model can preserve fine distinctions between subjective student opinions and factual university policy.

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Which UC Berkeley dorms do students recommend for freshmen who care about social life? | Unit 1, Unit 2, Unit 3, and Clark Kerr appear as social options, with tradeoffs around location, room size, and convenience. |
| 2 | What are the main tradeoffs between Clark Kerr and Unit 1? | Clark Kerr is described as more spacious and social/Greek-life adjacent but farther from campus; Unit 1 is described as more convenient and closer to food and activities. |
| 3 | When do students suggest starting the off-campus housing search? | Students suggest starting in spring semester, often around late February or early March, while noting April or summer can still work but may be stressful. Official UC Berkeley guidance says six to eight weeks before target move-in, with late April through early July as an ideal fall window. |
| 4 | What resources do students mention for finding off-campus housing? | Students mention Cal Rentals / UC Berkeley Off-Campus Rental Services, Craigslist, Zillow, Trulia, Facebook groups, rental agencies, Apartments.com, walking around for signs, lease takeovers, co-ops/BSC, SG Real Estate Berkeley, and transit-accessible neighborhoods. |
| 5 | Which apartment has the objectively lowest crime risk near UC Berkeley? | The system should say it does not have enough information because the corpus contains subjective housing advice, not verified crime statistics. |

## Anticipated Challenges

1. The corpus is cleaned notes rather than full raw Reddit pages, so retrieval may miss details that were not selected during collection. If that happens, the fix is to add more permitted excerpts under `MANUAL_COLLECTION_SPACE` and rerun chunking and embedding.

2. Some sources are subjective warning threads. The generation prompt must avoid turning student complaints into verified facts and should phrase them as student-reported experiences.

3. Short documents can produce small chunks with overlapping topics, so top-k retrieval may return multiple dorm-comparison chunks for an off-campus query. I will inspect retrieved chunks before trusting generated answers.

## Architecture

```mermaid
flowchart LR
    A["Document Ingestion<br/>local .txt files + metadata parser"] --> B["Chunking<br/>paragraph-aware, 1000 chars, 150 overlap"]
    B --> C["Embedding + Vector Store<br/>all-MiniLM-L6-v2 + ChromaDB"]
    C --> D["Retrieval<br/>top-k semantic search"]
    D --> E["Generation<br/>Groq llama-3.3-70b-versatile with cited context"]
    E --> F["CLI Interface<br/>src/app.py"]
```

## AI Tool Plan

**Milestone 3 - Ingestion and chunking:** I will give ChatGPT/Codex my Documents and Chunking Strategy sections and ask it to implement `src/chunk.py`. I expect it to produce a metadata parser, noise cleaner, JSONL output, and paragraph-aware chunking function that chunks only `MANUAL_COLLECTION_SPACE:` content. I will verify by inspecting at least five chunks printed by `python src/chunk.py`.

**Milestone 4 - Embedding and retrieval:** I will give ChatGPT/Codex my Retrieval Approach and Architecture sections and ask it to implement `src/embed.py` and `src/retrieve.py` using `sentence-transformers` and ChromaDB. I expect scripts that store chunks in a persistent local vector database and print retrieved chunks with source metadata. I will verify by running the first three evaluation questions in retrieval-only mode and checking whether the returned chunks match the expected answers.

**Milestone 5 - Generation and interface:** I will give ChatGPT/Codex my grounding requirement, evaluation questions, and source-attribution requirement and ask it to implement `src/generate.py` and `src/app.py`. I expect a CLI that can answer one question or run interactively, always showing sources and retrieved chunks. I will verify by checking that unsupported questions say there is not enough information rather than inventing facts.
