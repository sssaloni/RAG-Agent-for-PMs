# PM RAG — Product Manager Knowledge Base

Ask natural language questions across your PRDs, user research notes,
sprint retros, and competitive analysis docs.

## Setup (5 minutes)

```bash
# 1. Clone / copy this folder
cd pm_rag

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your OpenAI key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 5. Drop your documents into the docs/ folder
#    Supported: .pdf, .txt
cp ~/Desktop/my_prd.pdf docs/
cp ~/Desktop/user_research_q2.pdf docs/
```

## Run the pipeline

```bash
# Step 1 — Ingest (run once, or whenever docs change)
python ingest.py

# Step 2 — Ask questions interactively
python query.py

# Step 2 (alt) — Run the 4 built-in test questions
python app.py
```

## Example questions to ask

```
What were the top user pain points from the Q2 research?
What success metrics did we set for the onboarding redesign?
What blockers kept recurring in our retros last quarter?
How does our product compare to Competitor X on pricing?
What was the scope of the notification centre feature?
Which user segments did we decide to exclude in the personas doc?
```

## Where PM Prompt Pro helps

There are two places where prompt quality directly changes output quality:

### 1. The system prompt in `query.py`
Open `query.py` and find `PM_SYSTEM_PROMPT`.
This wraps every retrieved chunk + user question before sending to GPT.

**How to improve it with PM Prompt Pro:**
Paste this into the GPT:

> "I'm building a RAG pipeline for a PM knowledge base. The retrieved chunks
> come from PRDs, user research notes, retros, and competitive analysis docs.
> Help me write a CRISPE system prompt that tells the LLM to answer
> specifically, cite sources, avoid hallucinating, and format answers for
> a PM audience."

### 2. The questions you ask (query time)
Vague questions return vague answers even with perfect retrieval.

**Weak:** "What do users think?"
**Strong:** "What were the top 3 pain points mentioned by mid-market HR managers in our Q2 discovery interviews related to the candidate tracking workflow?"

Use PM Prompt Pro to sharpen your retrieval queries the same way
you'd sharpen a PRD problem statement.

## Folder structure

```
pm_rag/
├── docs/               ← drop your PDFs here
├── chroma_db/          ← auto-created by ingest.py (don't edit)
├── ingest.py           ← Step 1: load, chunk, embed, store
├── query.py            ← Step 2: retrieve, prompt, generate
├── app.py              ← test runner with 4 sample questions
├── requirements.txt
├── .env                ← your OPENAI_API_KEY (never commit this)
└── README.md
```

## Tuning tips

| Problem | Fix |
|---|---|
| Answers are too generic | Improve the system prompt using PM Prompt Pro |
| Wrong chunks retrieved | Make your question more specific |
| Missing context | Reduce CHUNK_SIZE in ingest.py to 300, re-run ingest |
| Answers too long | Add "Answer in 2-3 sentences max" to the system prompt |
| Hallucinating facts | Lower temperature to 0 in query.py (already default) |
| Slow responses | Switch MODEL to "gpt-4o-mini" in query.py |
