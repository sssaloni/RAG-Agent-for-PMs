from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_DIR   = "chroma_db"
TOP_K        = 4
MODEL        = "gpt-4o-mini"

# ── System prompt ─────────────────────────────────────────────────────────────
PM_SYSTEM_PROMPT = """
You are a knowledgeable product management assistant with access to this team's
internal documents: PRDs, user research notes, sprint retrospectives, and
competitive analysis.

Use ONLY the context provided below to answer the question.
If the answer is not in the context, say: "I couldn't find that in the
documents. Try rephrasing or check the source docs directly."

Rules:
- Be specific. Quote or reference the document and section when possible.
- Do not invent details not present in the context.
- If multiple documents are relevant, synthesise across them.
- Keep answers concise — 3-5 sentences unless a longer answer is clearly needed.
- End with: "Source: [document name]"

Context:
{context}

Question: {question}

Answer:
"""

# ── Load vectorstore ──────────────────────────────────────────────────────────
def load_vectorstore():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings
    )
    return vectorstore

# ── Format retrieved docs ─────────────────────────────────────────────────────
def format_docs(docs):
    return "\n\n".join(
        f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
        for doc in docs
    )

# ── Build RAG chain ───────────────────────────────────────────────────────────
def build_chain(vectorstore):
    llm = ChatOpenAI(model=MODEL, temperature=0)
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=PM_SYSTEM_PROMPT
    )

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain, retriever

# ── Ask a question ────────────────────────────────────────────────────────────
def ask(chain_and_retriever, question: str):
    chain, retriever = chain_and_retriever

    answer = chain.invoke(question)
    docs   = retriever.invoke(question)

    print("\n" + "─" * 60)
    print(f"Q: {question}")
    print("─" * 60)
    print(f"\n{answer}\n")

    print("── Retrieved chunks ──────────────────────────────────────")
    for i, doc in enumerate(docs, 1):
        source  = doc.metadata.get("source", "unknown")
        preview = doc.page_content[:120].replace("\n", " ")
        print(f"  [{i}] {source} — {preview}...")
    print()

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== PM RAG — Query Pipeline ===\n")
    print("Loading knowledge base...")
    vectorstore = load_vectorstore()
    chain_and_retriever = build_chain(vectorstore)
    print("Ready. Type your question (or 'quit' to exit).\n")

    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue
        ask(chain_and_retriever, question)
