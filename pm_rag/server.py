"""
server.py — Flask backend that serves the RAG pipeline via a REST API.
Run with: python server.py
Then open http://localhost:5000 in your browser.
"""
import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

app = Flask(__name__, static_folder="static")
CORS(app)

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_DIR = "chroma_db"
DOCS_DIR   = "docs"
TOP_K      = 4
MODEL      = "gpt-4o-mini"

PM_SYSTEM_PROMPT = """
You are a knowledgeable product management assistant with access to this team's
internal documents: PRDs, user research notes, sprint retrospectives, and
competitive analysis for a B2B SaaS HCM product similar to Workday.

Use ONLY the context provided below to answer the question.
If the answer is not in the context, say: "I couldn't find that in the documents. Try rephrasing or check the source docs directly."

Rules:
- Be specific and reference the document when possible.
- Do not invent details not present in the context.
- If multiple documents are relevant, synthesise across them.
- Structure your answer clearly. Use bullet points for lists.
- Keep answers focused and useful for a product manager.

Context:
{context}

Question: {question}

Answer:
"""

# ── Initialise RAG pipeline ───────────────────────────────────────────────────
print("Loading knowledge base...")
embeddings   = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore  = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
retriever    = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
llm          = ChatOpenAI(model=MODEL, temperature=0)
prompt       = PromptTemplate(input_variables=["context", "question"], template=PM_SYSTEM_PROMPT)

def format_docs(docs):
    return "\n\n".join(
        f"[{os.path.basename(doc.metadata.get('source', 'unknown'))}]\n{doc.page_content}"
        for doc in docs
    )

chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)
print("Knowledge base ready.\n")

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/ask", methods=["POST"])
def ask():
    data     = request.json
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error": "No question provided"}), 400

    start  = time.time()
    answer = chain.invoke(question)
    docs   = retriever.invoke(question)
    elapsed = round(time.time() - start, 2)

    sources = []
    seen = set()
    for doc in docs:
        src     = os.path.basename(doc.metadata.get("source", "unknown"))
        preview = doc.page_content[:200].replace("\n", " ").strip()
        if src not in seen:
            sources.append({"file": src, "preview": preview})
            seen.add(src)

    return jsonify({
        "answer":   answer,
        "sources":  sources,
        "elapsed":  elapsed,
        "question": question
    })

@app.route("/api/docs", methods=["GET"])
def list_docs():
    docs = []
    if os.path.exists(DOCS_DIR):
        for f in os.listdir(DOCS_DIR):
            if f.endswith((".txt", ".pdf")):
                path = os.path.join(DOCS_DIR, f)
                size = os.path.getsize(path)
                # Categorise by filename
                name = f.lower()
                if "prd" in name:
                    category = "PRD"
                elif "research" in name or "usability" in name:
                    category = "User Research"
                elif "retro" in name or "sprint" in name:
                    category = "Retro"
                elif "competitive" in name or "winloss" in name or "win" in name:
                    category = "Competitive"
                else:
                    category = "Other"
                docs.append({
                    "name":     f,
                    "size":     round(size / 1024, 1),
                    "category": category
                })
    return jsonify({"docs": docs})

@app.route("/api/chunks", methods=["GET"])
def list_chunks():
    """Return all chunks stored in Chroma with metadata — powers the DB Explorer tab."""
    page     = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    category = request.args.get("category", "all")

    collection = vectorstore._collection
    results    = collection.get(include=["documents", "metadatas"])

    all_chunks = []
    for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
        src  = os.path.basename(meta.get("source", "unknown"))
        name = src.lower()
        if "prd" in name:
            cat = "PRD"
        elif "research" in name or "usability" in name:
            cat = "User Research"
        elif "retro" in name or "sprint" in name:
            cat = "Retro"
        elif "competitive" in name or "winloss" in name or "win" in name:
            cat = "Competitive"
        else:
            cat = "Other"

        all_chunks.append({
            "id":       i + 1,
            "source":   src,
            "category": cat,
            "page":     meta.get("page", "—"),
            "preview":  doc[:300].replace("\n", " ").strip(),
            "full":     doc,
            "chars":    len(doc)
        })

    # Filter by category
    if category != "all":
        all_chunks = [c for c in all_chunks if c["category"] == category]

    total  = len(all_chunks)
    start  = (page - 1) * per_page
    end    = start + per_page
    paged  = all_chunks[start:end]

    # Summary stats
    from collections import Counter
    all_raw = collection.get(include=["documents", "metadatas"])
    cat_counts = Counter()
    for meta in all_raw["metadatas"]:
        src  = os.path.basename(meta.get("source", "unknown")).lower()
        if "prd" in src:              cat_counts["PRD"] += 1
        elif "research" in src or "usability" in src: cat_counts["User Research"] += 1
        elif "retro" in src or "sprint" in src:       cat_counts["Retro"] += 1
        elif "competitive" in src or "win" in src:    cat_counts["Competitive"] += 1
        else:                                         cat_counts["Other"] += 1

    return jsonify({
        "chunks":     paged,
        "total":      total,
        "page":       page,
        "per_page":   per_page,
        "pages":      -(-total // per_page),
        "cat_counts": dict(cat_counts)
    })


@app.route("/api/chunks/search", methods=["POST"])
def search_chunks():
    """Semantic search directly against the vector store — shows similarity scores."""
    data  = request.json
    query = data.get("query", "").strip()
    top_k = int(data.get("top_k", 6))
    if not query:
        return jsonify({"error": "No query provided"}), 400

    results = vectorstore.similarity_search_with_score(query, k=top_k)
    hits = []
    for doc, score in results:
        src  = os.path.basename(doc.metadata.get("source", "unknown"))
        name = src.lower()
        if "prd" in name:              cat = "PRD"
        elif "research" in name or "usability" in name: cat = "User Research"
        elif "retro" in name or "sprint" in name:       cat = "Retro"
        elif "competitive" in name or "win" in name:    cat = "Competitive"
        else:                                           cat = "Other"
        hits.append({
            "source":     src,
            "category":   cat,
            "score":      round(float(score), 4),
            "similarity": round((1 - float(score)) * 100, 1),
            "preview":    doc.page_content[:300].replace("\n", " ").strip(),
            "full":       doc.page_content,
            "page":       doc.metadata.get("page", "—")
        })

    return jsonify({"hits": hits, "query": query})


@app.route("/api/suggestions", methods=["GET"])
def suggestions():
    questions = [
        {"q": "What are the success metrics for the AI workforce planning feature?",     "tag": "PRD"},
        {"q": "What did HR leaders say about Excel and workforce planning?",              "tag": "Research"},
        {"q": "What was the most recurring blocker across sprints in Q1?",               "tag": "Retro"},
        {"q": "Why are we losing deals to Anaplan?",                                     "tag": "Competitive"},
        {"q": "What did users say about AI trust and projections?",                      "tag": "Research"},
        {"q": "What evidence supports building the AI planning feature?",                "tag": "Cross-doc"},
        {"q": "How does Rippling's mobile app compare to ours?",                         "tag": "Competitive"},
        {"q": "What is out of scope for the mobile app redesign?",                       "tag": "PRD"},
        {"q": "How did the team fix the mid-sprint security review problem?",            "tag": "Retro"},
        {"q": "What do users say about mobile and what are we doing about it?",          "tag": "Cross-doc"},
    ]
    return jsonify({"suggestions": questions})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
