# The Unofficial Guide - UC Berkeley Housing RAG

This project is a small retrieval-augmented generation system for UC Berkeley housing advice. It searches cleaned student-generated Reddit notes plus one official UC Berkeley housing resource, retrieves relevant chunks with semantic search, and uses Groq to generate grounded answers with source attribution.

Detailed run artifacts are in:

- `eval_outputs/01_retrieval_outputs.md`
- `eval_outputs/02_generation_outputs.md`
- `eval_outputs/03_evaluation_notes.md`

## Domain

My domain is student-generated and official UC Berkeley housing advice. I chose this because official pages explain policies, deadlines, and resources, but students also need practical advice about dorm social life, Clark Kerr vs Unit 1, off-campus search timing, rent expectations, scams, co-ops, and tradeoffs between price, location, and convenience.

## Document Sources

The corpus lives in `data/raw/`. Each file has metadata at the top and collected content under `MANUAL_COLLECTION_SPACE:`. The Reddit documents are cleaned notes from public student discussions; the official document is cleaned notes from UC Berkeley housing pages. Full source URLs are also listed in `source_manifest.md`.

| # | Source | Type | File |
|---|--------|------|------|
| 1 | A Complete Guide for UC Berkeley New Admits - Housing | Reddit student advice | `data/raw/01_new_admits_housing_guide.txt` |
| 2 | freshman housing advice | Reddit student advice | `data/raw/02_freshman_housing_advice_2024.txt` |
| 3 | Best recommended housing option for incoming UC Berkeley freshman | Reddit student advice | `data/raw/03_best_freshman_housing_options.txt` |
| 4 | Freshman Housing: Advice | Reddit student advice | `data/raw/04_freshman_housing_unit1_unit2_ck_blackwell.txt` |
| 5 | dorm advice | Reddit student advice | `data/raw/05_dorm_advice_ck_vs_unit1.txt` |
| 6 | Off-campus Housing Search Tips | Reddit student advice | `data/raw/06_offcampus_housing_search_tips.txt` |
| 7 | Off campus housing recommendations? | Reddit student advice | `data/raw/07_offcampus_housing_recommendations.txt` |
| 8 | cheap off campus housing options | Reddit student advice | `data/raw/08_cheap_offcampus_housing_options.txt` |
| 9 | Is the housing situation THAT bad? | Reddit student advice | `data/raw/09_is_housing_that_bad.txt` |
| 10 | LIST OF PLACES YOU SHOULD !NOT! RENT | Reddit student warnings | `data/raw/10_places_not_to_rent.txt` |
| 11 | UC Berkeley Official Housing Application and FAQ Notes | Official university notes | `data/raw/11_uc_berkeley_official_housing_application_faq.txt` |

## Ingestion And Cleaning

The raw `.txt` files use consistent metadata fields such as `TITLE`, `SOURCE`, `URL` or `URLS`, `DATE_ACCESSED`, `TOPIC`, `DOCUMENT_TYPE`, and `DOMAIN`. `src/chunk.py` reads directly from `data/raw/`, extracts that metadata, and chunks only the text after `MANUAL_COLLECTION_SPACE:`.

Helper sections such as `SUMMARY`, `SHORT_EXCERPT_OR_NOTES`, `COPYRIGHT_NOTE`, and `SOURCE_NOTES_FOR_RAG` are not used as retrievable content. The cleaner removes the literal `MANUAL_COLLECTION_SPACE:` marker and simple Reddit UI noise such as `Reply`, `Award`, `Share`, vote counts, and comment counts.

## Chunking Strategy

**Chunk size:** 1000 characters.

**Overlap:** 150 characters only when a paragraph or combined chunk is too long and must be split.

**Reasoning:** The documents are mostly cleaned forum-style notes with short paragraphs. I split on paragraph boundaries first so each chunk keeps a coherent student advice point. The 1000-character target is large enough to keep context, but small enough that a query about a specific topic, such as Clark Kerr distance or off-campus search timing, can match a focused chunk. Overlap is only used for long text so important context is not lost at split boundaries.

The chunking script writes to `data/chunks/chunks.jsonl` and overwrites the file on each run. The tested evaluation run used the chunk IDs shown in `eval_outputs/01_retrieval_outputs.md`.

### Sample Chunks

1. `05_dorm_advice_ck_vs_unit1::chunk-000` from `data/raw/05_dorm_advice_ck_vs_unit1.txt`: The chunk says Clark Kerr and Unit 1 can both be social, but Clark Kerr has more of a Greek-life feel, while Unit 1 and Unit 2 can vary by floor.

2. `05_dorm_advice_ck_vs_unit1::chunk-001` from `data/raw/05_dorm_advice_ck_vs_unit1.txt`: The chunk says Unit 1 is better for access to food and things to do, while Clark Kerr has nicer and bigger rooms.

3. `06_offcampus_housing_search_tips::chunk-001` from `data/raw/06_offcampus_housing_search_tips.txt`: The chunk recommends starting the off-campus search around late February or early March and mentions Zillow, Trulia, Facebook groups, North Berkeley listings, and Craigslist.

4. `08_cheap_offcampus_housing_options::chunk-002` from `data/raw/08_cheap_offcampus_housing_options.txt`: The chunk mentions Facebook housing groups, bsc.coop, Apartments.com, CalRentals, and Craigslist, with a warning about scam literacy.

5. `11_uc_berkeley_official_housing_application_faq::chunk-006` from `data/raw/11_uc_berkeley_official_housing_application_faq.txt`: The chunk describes UC Berkeley Off-Campus Rental Services and says official off-campus tips recommend starting six to eight weeks before the target move-in date.

## Embeddings And Vector Store

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`.

**Vector store:** ChromaDB persistent local collection.

I chose `all-MiniLM-L6-v2` because it is free, local, and fast enough for a small homework corpus. In production I would compare it against higher-accuracy embedding models with stronger performance on noisy student language, longer context support, lower latency at scale, multilingual support, and clearer privacy/cost tradeoffs.

## Query Interface

The interface is a CLI in `src/app.py`.

Retrieval-only mode:

```bash
python src/app.py --retrieval-only "What are the main tradeoffs between Clark Kerr and Unit 1?"
```

Generation mode:

```bash
python src/app.py "What are the main tradeoffs between Clark Kerr and Unit 1?"
```

Input is a natural-language question. Retrieval-only output shows ranked chunks, source titles/URLs, chunk IDs, distances, and chunk text. Generation output shows the final answer followed by the retrieved chunks for inspection.

## Grounded Generation

`src/generate.py` sends retrieved chunks to Groq using this grounding instruction:

```text
Use only the retrieved source excerpts provided in the user message.
If the excerpts do not contain enough evidence, say you do not have enough information.
Treat Reddit material as subjective student advice, not verified fact.
Include a short Sources section that lists the source numbers you used.
```

The prompt labels retrieved excerpts as numbered sources with title, URL, topic, and text. The answer is expected to cite those source numbers or URLs. `src/app.py` also prints the retrieved chunks after the answer so the user can audit the grounding.

## Retrieval Test Results

I tested five evaluation questions. Three representative retrieval checks:

| Query | Top chunks retrieved | Result |
|---|---|---|
| Which UC Berkeley dorms do students recommend for freshmen who care about social life? | Retrieved `05_dorm_advice_ck_vs_unit1::chunk-000`, `03_best_freshman_housing_options::chunk-005`, and `03_best_freshman_housing_options::chunk-001`, plus two off-campus chunks. | Partially accurate retrieval. The main dorm chunks were relevant, but two chunks were off-topic. |
| What are the main tradeoffs between Clark Kerr and Unit 1? | Retrieved multiple Clark Kerr / Unit 1 chunks from `05_dorm_advice_ck_vs_unit1`, `04_freshman_housing_unit1_unit2_ck_blackwell`, and `03_best_freshman_housing_options`. | Accurate retrieval. The chunks directly supported the tradeoff answer. |
| When do students suggest starting the off-campus housing search? | Retrieved `06_offcampus_housing_search_tips::chunk-001`, `06_offcampus_housing_search_tips::chunk-000`, and official UC Berkeley chunks about off-campus timing. | Accurate retrieval. It found both student advice and official timing guidance. |

For Q4, retrieval was also usable: the first chunk was more about leases and financial aid, but later chunks contained the search resources. For Q5, retrieved chunks did not contain crime statistics, which supported a safe refusal.

## Example Generated Responses

**Q2: What are the main tradeoffs between Clark Kerr and Unit 1?**

System summary: Clark Kerr is often described as larger, prettier, more connected to Greek life, and farther from campus. Unit 1 is closer to campus, closer to food, and more convenient for students who prioritize location. Sources included the Clark Kerr vs Unit 1 Reddit thread and freshman housing advice threads.

Visible source attribution from the run:

```text
Sources:
[1] https://www.reddit.com/r/berkeley/comments/tvuyj6/dorm_advice/
[2] https://www.reddit.com/r/berkeley/comments/tvuyj6/dorm_advice/
[3] https://www.reddit.com/r/berkeley/comments/ugfili/freshman_housing_advice/
[4] https://www.reddit.com/r/berkeley/comments/me683s/best_recommended_housing_option_for_incoming_uc/
[5] https://www.reddit.com/r/berkeley/comments/ugfili/freshman_housing_advice/
```

**Q4: What resources do students mention for finding off-campus housing?**

System summary: The answer listed Craigslist, Zillow, Trulia, Facebook housing groups, rental agencies, Apartments.com, CalRentals, SG Real Estate Berkeley, Berkeley Student Cooperative housing, walking around for “for rent” signs, and North Berkeley listings.

Visible source attribution from the run:

```text
Sources:
[2], [3], [4], [5]
```

**Out-of-scope refusal, Q5: Which apartment has the objectively lowest crime risk near UC Berkeley?**

System response:

```text
I do not have enough information to determine which apartment has the objectively lowest crime risk near UC Berkeley. The provided sources are Reddit threads that offer subjective student advice and do not provide objective crime risk data or comparisons.

Sources:
None (insufficient information)
```

## Evaluation Report

| # | Question | Expected answer | System response summary | Retrieval quality | Response accuracy |
|---|----------|-----------------|-------------------------|-------------------|-------------------|
| 1 | Which UC Berkeley dorms do students recommend for freshmen who care about social life? | Clark Kerr, Unit 1/2/3, and Blackwell; Clark Kerr is linked with Greek life/social life, Units vary by floor, Blackwell has mixed opinions. | Answer named Clark Kerr, Unit 1, and Blackwell, explained Greek-life feel and floor variation, and noted mixed Blackwell social opinions. | Partially relevant | Accurate |
| 2 | What are the main tradeoffs between Clark Kerr and Unit 1? | Clark Kerr is larger/prettier/more Greek-life-oriented but farther; Unit 1 is closer and more convenient. | Answer clearly framed the tradeoff as Greek/social/room size vs location/convenience. | Relevant | Accurate |
| 3 | When do students suggest starting the off-campus housing search? | Students mention late February/March; April or summer can work but is harder. Official guidance says six to eight weeks before move-in, late April through early July for fall. | Answer included both student timing and official UC Berkeley timing. | Relevant | Accurate |
| 4 | What resources do students mention for finding off-campus housing? | Craigslist, Zillow, Trulia, Facebook groups, rental agencies, Apartments.com, CalRentals, SG Real Estate Berkeley, BSC/co-ops, signs, and North Berkeley listings. | Answer listed the main resources found in the retrieved chunks. | Relevant | Accurate |
| 5 | Which apartment has the objectively lowest crime risk near UC Berkeley? | Refuse or say insufficient information because the corpus has no objective crime-risk data. | Answer refused to name an apartment and explained the sources lacked objective crime comparisons. | Relevant for refusal | Accurate |

## Failure / Limitation Case

Q1 exposed a retrieval limitation. The system retrieved the main dorm social-life chunks, but it also retrieved off-campus housing chunks because the corpus contains overlapping housing vocabulary. The generated answer was still accurate because the relevant dorm chunks were ranked highly, but the retrieval set was noisy. I would improve this by adding metadata filtering for `topic` or `document_type`, so a dorm-specific query can prioritize residence-hall documents over off-campus housing documents.

Q5 was the intended safety test. The system handled it correctly by refusing to infer objective crime risk from subjective student housing advice. If I wanted the system to answer that kind of question, I would need to add verified public safety or crime-statistics sources and clearly separate those from student opinion.

## Spec Reflection

The spec helped me decide to preserve paragraph-level advice instead of splitting blindly every fixed number of characters. That mattered because many comments contain a complete housing tradeoff in one paragraph.

The implementation diverged from the early spec because I added an official UC Berkeley housing document after the initial Reddit-only plan. I did that because official sources are better for policy questions about guarantees, deadlines, CalNet, and off-campus rental services, while Reddit is better for student opinions.

## AI Usage

**Instance 1:** I used GPT/Copilot to identify a UC Berkeley housing-advice domain and collect a starter list of Reddit source threads. I kept the source list and metadata structure, but I manually updated the raw files with cleaned notes rather than copying full Reddit pages wholesale.

**Instance 2:** I used Codex to scaffold the RAG pipeline from my homework requirements and planning document. I then redirected the chunking implementation so it used only `MANUAL_COLLECTION_SPACE:` content and ignored helper summaries, because the summaries were planning aids rather than final retrievable evidence.

**Instance 3:** I used GPT 5.5 / Codex to turn the raw retrieval and generation logs into evaluation notes and this README. I kept the documented judgments tied to the actual `eval_outputs` files and did not include runtime warning noise in the polished report.
