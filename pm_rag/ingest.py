import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
DOCS_DIR    = "docs"          # folder containing your PDFs and .txt files
CHROMA_DIR  = "chroma_db"     # where the vector store is persisted on disk
CHUNK_SIZE  = 500             # tokens per chunk — sweet spot for PM docs
CHUNK_OVERLAP = 50            # overlap so context isn't cut mid-sentence

# ── Load documents ────────────────────────────────────────────────────────────
def load_documents(docs_dir: str):
    docs = []
    for filename in os.listdir(docs_dir):
        filepath = os.path.join(docs_dir, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs.extend(loader.load())
            print(f"  Loaded PDF: {filename} ({len(loader.load())} pages)")
        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding="utf-8")
            docs.extend(loader.load())
            print(f"  Loaded TXT: {filename}")
    return docs

# ── Chunk documents ───────────────────────────────────────────────────────────
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        # Split on natural PM doc boundaries first, then fall back to sentences
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"  Split into {len(chunks)} chunks")
    return chunks

# ── Embed and store ───────────────────────────────────────────────────────────
def embed_and_store(chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )
    print(f"  Stored {len(chunks)} chunks in Chroma at ./{CHROMA_DIR}")
    return vectorstore

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== PM RAG — Ingestion Pipeline ===\n")

    print("Step 1: Loading documents from ./docs ...")
    docs = load_documents(DOCS_DIR)
    print(f"  Total pages/sections loaded: {len(docs)}\n")

    print("Step 2: Chunking documents ...")
    chunks = chunk_documents(docs)
    print()

    print("Step 3: Embedding and storing in Chroma ...")
    embed_and_store(chunks)

    print("\nDone. Run query.py to start asking questions.\n")
