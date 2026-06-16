"""
app.py — Run this to test your PM RAG pipeline end to end.
Fires 4 sample questions that cover each doc type in your knowledge base.
"""
from query import load_vectorstore, build_chain, ask

TEST_QUESTIONS = [
    "What are the success metrics defined for the onboarding redesign?",
    "What were the top pain points users mentioned in the discovery interviews?",
    "What blockers came up most frequently in our sprint retrospectives?",
    "How does our product compare to competitors on pricing and key features?",
]

if __name__ == "__main__":
    print("\n=== PM RAG — Test Run ===\n")
    print("Loading knowledge base...")
    vectorstore = load_vectorstore()
    chain_and_retriever = build_chain(vectorstore)
    print(f"Running {len(TEST_QUESTIONS)} test questions...\n")

    for q in TEST_QUESTIONS:
        ask(chain_and_retriever, q)

    print("=" * 60)
    print("Test complete. If answers look off, check:")
    print("  1. Are the right .txt files in the ./docs folder?")
    print("  2. Did ingest.py run successfully?")
    print("  3. Is the system prompt in query.py specific enough?")
    print("     → Use PM Prompt Pro to improve it.")
    print("=" * 60 + "\n")
