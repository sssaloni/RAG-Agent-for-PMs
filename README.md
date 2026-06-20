# PM RAG — Product Manager Knowledge Base

An interactive Retrieval-Augmented Generation (RAG) system for Product Managers to query internal documents (PRDs, user research notes, retrospectives, and competitive analysis) using natural language.

---

## 🏗️ System Architecture & Processes

Before running the application, you can review the beginner's conceptual guide, system architecture details, and process flows:
*   📄 **Beginner's Build Guide**: [build_guide.md](build_guide.md) (A conceptual handbook for starting to build your own RAG agent from scratch)
*   📄 **Architecture Document**: [agent_architecture.md](agent_architecture.md)
*   🖼️ **System Diagram**: [rag_agent_architecture.png](rag_agent_architecture.png)

---

## 🚀 Getting Started

Follow these steps to set up the environment, ingest documents, and run the query pipeline.

### Prerequisites
*   **Python 3.11.x** installed.
    > [!WARNING]
    > This project is not compatible with Python 3.14+ due to dependency limitations in older versions of NumPy and LangChain. Check your version with `python --version`.
*   **OpenAI API Key** (for embeddings and chat generation).
*   **Internet Access** (to connect to the OpenAI API).

---

### Step 0: Clone the Repository

Clone this repository to your local machine and navigate into the project root directory:

```bash
git clone https://github.com/your-username/RAG-Agent-for-PMs.git
cd RAG-Agent-for-PMs
```

---

### Step 1: Set Up Virtual Environment

Activate the virtual environment from the root directory:

**Windows PowerShell:**
```powershell
# If virtual environment is not created:
py -3.11 -m venv venv

# Activate:
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
# If virtual environment is not created:
python3.11 -m venv venv

# Activate:
source venv/bin/activate
```

You should see `(venv)` prepended to your terminal prompt.

---

### Step 2: Install Dependencies

Upgrade `pip` and install all required packages:
```bash
python -m pip install --upgrade pip
pip install -r pm_rag/requirements.txt
```

---

### Step 3: Configure Environment Variables

Create a `.env` file in the root directory and add your OpenAI API Key:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```
> [!IMPORTANT]
> Keep your API key private. Do not commit `.env` to Git.

---

### Step 4: Add Your Documents

Drop your PDFs or TXT files into the `pm_rag/docs/` directory.

Example structure:
```text
pm_rag/docs/
├── PRD_AI_Workforce_Planning.pdf
├── UserResearch_Q2.pdf
├── SprintRetros_Q1.txt
└── CompetitiveAnalysis.txt
```

---

### Step 5: Run the Ingestion Pipeline

Whenever you add or modify documents in the `docs/` folder, run the ingestion script to load, chunk, embed, and store them in Chroma DB:
```bash
python pm_rag/ingest.py
```

Expected output:
```text
=== PM RAG — Ingestion Pipeline ===

Step 1: Loading documents from ./docs ...
  Loaded PDF: PRD_AI_Workforce_Planning.pdf (4 pages)
  Loaded TXT: SprintRetros_Q1.txt
  Total pages/sections loaded: 5

Step 2: Chunking documents ...
  Split into 18 chunks

Step 3: Embedding and storing in Chroma ...
  Stored 18 chunks in Chroma at ./chroma_db

Done. Run query.py to start asking questions.
```

---

## 🔍 Running Queries & Interfaces

You can interact with the RAG pipeline in three ways:

### Option A: Launch the Web Dashboard (Recommended)
Start the Flask backend server:
```bash
python pm_rag/server.py
```
Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

This web GUI includes:
*   **Chat tab**: Interactive chat window with live citations, latency tracing, and source document previews.
*   **Documents tab**: Lists all documents currently loaded into the system categorized by type.
*   **DB Explorer tab**: Allows you to browse every raw text chunk and metadata record inside the vector database.
*   **Semantic Search tab**: Query the database directly to inspect cosine similarity scores and document matching.

---

### Option B: Interactive CLI (Command Line)
Ask questions directly from your terminal:
```bash
python pm_rag/query.py
```
Type `quit` or `exit` to exit.

---

### Option C: Run Sample Queries Script
Execute a quick pre-defined batch of test queries:
```bash
python pm_rag/app.py
```

---

## 💡 Example Questions to Try

```text
What were the top user pain points from the Q2 research?

What success metrics did we set for the onboarding redesign?

What blockers kept recurring in our retros last quarter?

How does our product compare to Competitor X on pricing?

What was the scope of the notification centre feature?
```

---

## 🛠️ Tuning & Optimization Tips

| Symptom | Cause | Solution |
| :--- | :--- | :--- |
| **Answers are too generic** | The system prompt is too broad | Update `PM_SYSTEM_PROMPT` in `pm_rag/query.py` or `pm_rag/server.py` |
| **Incorrect chunks retrieved** | The question was too vague | Ask more specific questions (e.g. naming specific features or segments) |
| **Missing context** | Chunk size is too large | Adjust `CHUNK_SIZE` in `pm_rag/ingest.py` to `300` and re-run ingestion |
| **Answers are too long** | LLM output constraints missing | Add "Answer in 2-3 sentences" to the system prompt guidelines |
| **Hallucinated details** | Temperature is too high | Ensure `temperature=0` is set when initializing `ChatOpenAI` |
| **Slow responses** | Model latency | Ensure you are using `gpt-4o-mini` instead of larger models |

---

## 🔧 Troubleshooting

### 1. NumPy/Chroma Installation Fails
*   **Cause**: Incompatibility with Python 3.12+.
*   **Fix**: Ensure you are using Python 3.11.x to build your virtual environment.

### 2. KeyError: `'_type'`
*   **Cause**: A conflict with an existing Chroma DB cache created with a different schema/package version.
*   **Fix**: Delete the `chroma_db` folder and rebuild.
    *   *Windows*: `Remove-Item -Recurse -Force .\pm_rag\chroma_db`
    *   *macOS/Linux*: `rm -rf pm_rag/chroma_db`
    *   Then run `python pm_rag/ingest.py`.

### 3. OpenAI Client got unexpected argument `'proxies'`
*   **Cause**: Incompatible `httpx` and `openai` library versions.
*   **Fix**: Pin `httpx` version:
    ```bash
    pip install httpx==0.27.2
    ```

### 4. Flask Not Found / Server Fails to Start
*   **Cause**: Dependencies not correctly loaded in the virtual environment.
*   **Fix**: Ensure your venv is activated, then run:
    ```bash
    pip install -r pm_rag/requirements.txt
    ```

---

## 📂 Project Structure

```text
RAG-Agent-for-PMs-main/
├── pm_rag/
│   ├── docs/               # Put your PDFs and TXT files here
│   ├── chroma_db/          # Persistent Chroma DB vector database
│   ├── static/             # Frontend client assets (HTML/JS/CSS)
│   ├── ingest.py           # Ingestion pipeline (loader -> splitter -> embedder -> Chroma)
│   ├── query.py            # CLI query interface (retriever -> prompt -> LLM)
│   ├── app.py              # Sample queries test script
│   ├── server.py           # Flask REST API backend
│   └── requirements.txt    # Project dependencies pins
├── agent_architecture.md   # Process flows and architecture description
├── rag_agent_architecture.png # Visual system architecture diagram
├── .env                    # Environment variables (OPENAI_API_KEY)
└── README.md               # Main documentation (this file)
```
