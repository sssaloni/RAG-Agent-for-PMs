# PM RAG — Product Manager Knowledge Base

Ask natural language questions across your PRDs, user research notes, sprint retrospectives, and competitive analysis documents using Retrieval-Augmented Generation (RAG).

---

## 🏗️ System Architecture & Processes

The complete architecture and process flows (loading, chunking, embeddings, and vector database processes) are documented here:
*   📄 **Architecture Document**: [agent_architecture.md](../agent_architecture.md)
*   🖼️ **System Diagram**: [rag_agent_architecture.png](../rag_agent_architecture.png)

---

## What this project does

This project demonstrates a simple RAG pipeline for Product Managers.

It:

* Loads PDFs and text documents
* Splits them into chunks
* Creates embeddings using OpenAI
* Stores them in ChromaDB
* Retrieves relevant context
* Uses GPT to answer questions grounded in your documents

---

## Prerequisites

Before starting, make sure you have:

* Python 3.11.x installed
* An OpenAI API key
* Internet access

⚠️ **Important:** This project is not compatible with Python 3.14 due to dependency limitations in NumPy and LangChain.

Check your Python version:

```bash
python --version
```

You should see something like:

```text
Python 3.11.x
```

---

## Setup

### 1. Clone or copy this folder

```bash
cd pm_rag
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

You should see:

```text
(venv)
```

in your terminal.

---

### 3. Upgrade pip

```bash
python -m pip install --upgrade pip
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Create a `.env` file

Create a file named `.env` in the project root:

```env
OPENAI_API_KEY=sk-your-openai-key-here
```

Do not commit this file to Git.

---

### 6. Add your documents

Drop your documents into the `docs/` folder.

Supported formats:

* `.pdf`
* `.txt`

Example:

```text
docs/
├── PRD_AI_Workforce_Planning.pdf
├── UserResearch_Q2.pdf
├── SprintRetros_Q1.txt
└── CompetitiveAnalysis.txt
```

---

## Run the pipeline

### Step 1: Build the vector database

Run this whenever documents change.

```bash
python ingest.py
```

Expected output:

```text
Loading documents...
Chunking documents...
Embedding and storing in Chroma...
Ingestion complete!
```

---

### Step 2: Ask questions interactively

```bash
python query.py
```

Example:

```text
Ask a question:
>
```

---

### Step 3: Run sample questions

```bash
python app.py
```

---

### Step 4: Launch the web interface

```bash
python server.py
```

Open:

```text
http://localhost:5000
```

in your browser.

---

## Example questions

```text
What were the top user pain points from the Q2 research?

What success metrics did we set for the onboarding redesign?

What blockers kept recurring in our retros last quarter?

How does our product compare to Competitor X on pricing?

What was the scope of the notification centre feature?

Which user segments did we decide to exclude in the personas document?
```

---

## Folder structure

```text
pm_rag/
├── docs/               # Drop your PDFs and TXT files here
├── chroma_db/          # Auto-generated vector database
├── static/             # Frontend assets for the web UI
├── ingest.py           # Load → chunk → embed → store
├── query.py            # Retrieve → prompt → generate
├── app.py              # Built-in sample queries
├── server.py           # Flask web application
├── requirements.txt
├── .env                # OPENAI_API_KEY (never commit)
├── .gitignore
└── README.md
```

---

## Troubleshooting

### Python version errors

Problem:

```text
NumPy installation fails
```

Fix:

Use Python 3.11.

---

### ChromaDB `_type` error

Problem:

```text
KeyError: '_type'
```

Cause:

An old Chroma database exists from a different version.

Fix:

Delete the vector database and rebuild it.

Windows:

```powershell
Remove-Item -Recurse -Force .\chroma_db
```

macOS/Linux:

```bash
rm -rf chroma_db
```

Then run:

```bash
python ingest.py
```

---

### OpenAI `proxies` error

Problem:

```text
Client.__init__() got an unexpected keyword argument 'proxies'
```

Cause:

Incompatible `httpx` version.

Fix:

```bash
pip install httpx==0.27.2
```

---

### Flask not found

Problem:

```text
ModuleNotFoundError: No module named 'flask'
```

Fix:

```bash
pip install flask flask-cors
```

---

### Answers don't improve after adding documents

Cause:

The vector database was not rebuilt.

Fix:

```bash
python ingest.py
```

again.

---

## Prompt engineering tips

There are two places where prompt quality directly affects output quality.

### 1. Improve the system prompt

Open `query.py` and locate:

```python
PM_SYSTEM_PROMPT
```

This prompt wraps retrieved context before it is sent to GPT.

Good prompts should instruct the model to:

* Answer specifically
* Cite sources
* Avoid hallucinations
* Format responses for PM audiences

---

### 2. Ask better questions

Weak:

```text
What do users think?
```

Strong:

```text
What were the top three pain points mentioned by mid-market HR managers in our Q2 discovery interviews related to the candidate tracking workflow?
```

Specific questions improve retrieval quality.

---

## Tuning tips

| Problem                 | Fix                                                |
| ----------------------- | -------------------------------------------------- |
| Answers are too generic | Improve the system prompt                          |
| Wrong chunks retrieved  | Ask more specific questions                        |
| Missing context         | Reduce `CHUNK_SIZE` in `ingest.py` and rebuild     |
| Answers are too long    | Add "Answer in 2–3 sentences" to the system prompt |
| Hallucinated facts      | Set temperature to `0`                             |
| Slow responses          | Use `gpt-4o-mini`                                  |
| Documents changed       | Re-run `python ingest.py`                          |

---

## How the RAG pipeline works

```text
Documents
    ↓
Load Documents
    ↓
Chunk Documents
    ↓
Create Embeddings
    ↓
Store in ChromaDB
    ↓
User Question
    ↓
Create Query Embedding
    ↓
Similarity Search
    ↓
Retrieve Relevant Chunks
    ↓
GPT Generates Answer
    ↓
Return Response
```

In simple terms:

> This project is like an open-book exam. Instead of answering from memory, GPT first looks up relevant information from your documents and then uses that information to generate an answer.
