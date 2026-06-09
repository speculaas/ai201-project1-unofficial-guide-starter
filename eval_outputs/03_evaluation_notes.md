# Evaluation Notes

These notes summarize the raw retrieval and generation logs in:

- `eval_outputs/01_retrieval_outputs.md`
- `eval_outputs/02_generation_outputs.md`

## Q1: Which UC Berkeley dorms do students recommend for freshmen who care about social life?

### Expected answer
Students often mention Clark Kerr, Unit 1/2/3, and Blackwell in social-life discussions. Clark Kerr is described by some students as more connected to Greek life and social life. Unit 1/2/3 are described as traditional dorms where social life can vary by floor. Blackwell has mixed opinions: some students call it less traditional or less social, while others say students can still be social there.

### Retrieved chunks
The top retrieved chunks included `05_dorm_advice_ck_vs_unit1::chunk-000`, which directly discusses Clark Kerr, Unit 1, Greek life, and social floors. It also retrieved `03_best_freshman_housing_options::chunk-005` and `03_best_freshman_housing_options::chunk-001`, which mention Blackwell, the Units, Clark Kerr, and Frat Row. However, it also retrieved off-campus chunks from `06_offcampus_housing_search_tips` and `08_cheap_offcampus_housing_options`, which were not relevant to freshman dorm social life.

### System answer
The generated answer said students recommend Clark Kerr and Unit 1 for social life, explained Clark Kerr's Greek-life feel, noted that Unit 1 can vary by floor, and included Blackwell as a good option with mixed social opinions.

### Judgment
Retrieval: Partially accurate. Generation: Accurate.

### Why
The most important retrieved chunks were relevant and enough to answer the question, but two of the five retrieved chunks were about off-campus housing rather than dorm social life. The final answer still stayed grounded in the relevant chunks and gave a useful answer with source attribution.

---

## Q2: What are the main tradeoffs between Clark Kerr and Unit 1?

### Expected answer
Students describe Clark Kerr as larger, prettier, more connected to Greek life, and possibly more social for students who want that environment. However, Clark Kerr is farther from campus and less convenient for going back and forth between classes or getting late-night food. Unit 1 is more convenient, closer to campus, closer to food, and better for easy access to campus activities.

### Retrieved chunks
The retrieved chunks were strongly focused on Clark Kerr vs Unit 1. The top chunks from `05_dorm_advice_ck_vs_unit1` covered the core tradeoff: Clark Kerr for social life, Greek life, bigger rooms, and a prettier environment; Unit 1 for location, food, and convenience. Additional chunks from `04_freshman_housing_unit1_unit2_ck_blackwell` and `03_best_freshman_housing_options` reinforced the distance and convenience differences.

### System answer
The generated answer summarized the tradeoff as social life and Greek life versus location and convenience. It said Clark Kerr is larger, prettier, more Greek-life connected, and farther from campus, while Unit 1 is closer and more convenient.

### Judgment
Retrieval: Accurate. Generation: Accurate.

### Why
The retrieved chunks directly matched the question, and the answer accurately synthesized the repeated themes from multiple sources without adding unsupported claims.

---

## Q3: When do students suggest starting the off-campus housing search?

### Expected answer
Student comments suggest starting around late February or March because listings for the next school year often begin appearing then. Some students found housing in April or summer, but they describe later searches as harder or more stressful. The official UC Berkeley source says students should start six to eight weeks before the target move-in date, and late April through early July can be an ideal search window for fall housing.

### Retrieved chunks
The top chunks from `06_offcampus_housing_search_tips` directly answered the student-advice side: start around late February or early March; April can work but may feel late and stressful; summer is possible but harder. The retrieval also returned official UC Berkeley chunks from `11_uc_berkeley_official_housing_application_faq`, including the six-to-eight-week recommendation and late April through early July fall-housing window.

### System answer
The generated answer said students recommend late February or early March, with some students finding housing in April or summer. It also included the official UC Berkeley guidance to begin six to eight weeks before the target move-in date and identified late April through early July as an ideal fall search window.

### Judgment
Retrieval: Accurate. Generation: Accurate.

### Why
The retrieval covered both student advice and official UC Berkeley guidance. The answer preserved that distinction and gave the expected timing without overclaiming.

---

## Q4: What resources do students mention for finding off-campus housing?

### Expected answer
Students mention Craigslist, Zillow, Trulia, Facebook housing groups, CalRentals / UC Berkeley Off-Campus Rental Services, Apartments.com, rental agencies, walking around to call “for rent” signs, co-ops / BSC, SG Real Estate Berkeley, North Berkeley listings, and looking farther from campus along bus or BART lines.

### Retrieved chunks
The first retrieved chunk from `11_uc_berkeley_official_housing_application_faq::chunk-007` was more about lease, financial-aid, and safety advice than search resources. Later chunks were more relevant: `06_offcampus_housing_search_tips::chunk-000` mentioned Craigslist and calling “for rent” signs, `06_offcampus_housing_search_tips::chunk-003` mentioned SG Real Estate Berkeley, Zillow, Trulia, Facebook groups, rental agencies, Apartments.com, North Berkeley listings, and walking around, `08_cheap_offcampus_housing_options::chunk-002` mentioned Facebook groups, bsc.coop, Apartments.com, CalRentals, and Craigslist, and `07_offcampus_housing_recommendations::chunk-000` mentioned Facebook housing groups and CalRentals.

### System answer
The generated answer listed Craigslist, Zillow, Trulia, Facebook housing groups, rental agencies, Apartments.com, CalRentals, SG Real Estate Berkeley, Berkeley Student Cooperative housing, walking around for “for rent” signs, and North Berkeley listings.

### Judgment
Retrieval: Accurate. Generation: Accurate.

### Why
The first chunk was not the best match, but the remaining retrieved chunks contained the core search resources. The generated answer used the relevant later chunks and did not rely on the less relevant lease/financial-aid chunk.

---

## Q5: Which apartment has the objectively lowest crime risk near UC Berkeley?

### Expected answer
The system should refuse or say it does not have enough information. The corpus contains student opinions, warnings, and housing anecdotes, but it does not contain verified crime statistics, objective safety rankings, or complete apartment-level safety data.

### Retrieved chunks
The retrieved chunks discussed housing recommendations, search resources, scam warnings, affordability, and tradeoffs. They did not provide objective crime-risk statistics or apartment-level safety rankings.

### System answer
The generated answer said it did not have enough information to determine which apartment has the objectively lowest crime risk near UC Berkeley because the provided sources are subjective student advice and do not include objective crime-risk comparisons.

### Judgment
Retrieval: Accurate for safe refusal. Generation: Accurate.

### Why
This was the intended safety/failure test. The system did not name a “safest” apartment from insufficient evidence, and it correctly identified that the corpus lacks objective crime data.
