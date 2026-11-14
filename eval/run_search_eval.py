
from pathlib import Path
from app.semantic_search import SemanticSearch

QUESTIONS = [
    "Which forts are located in Ahmednagar district?",
    "Which district is Ahmednagar Fort located in?",
    "Tell me about Bahadurgad Fort.",
    "Which district is Bhairavgad Fort located in?",
    "List the forts available in Nashik district.",
    "What is the current weather at Raigad Fort?",
    "Which forts are located in Pune district?",
    "List the forts available in Satara district.",
    "Is Raigad Fort included in the GadKille dataset?",
    "How many fort records are available in GadKille?"
]


def main():
    search_engine = SemanticSearch()

    # Index only when the persistent collection is empty
    if search_engine.vector_store.count() == 0:
        search_engine.build_index()

    output = [
        "# GadKille Semantic Search Evaluation",
        "",
        "- Embedding model: all-MiniLM-L6-v2",
        "- Embedding dimensions: 384",
        "- Vector database: ChromaDB",
        "- Storage: Persistent",
        "- Retrieval method: Cosine similarity",
        "- Top K: 3",
        ""
    ]

    for number, question in enumerate(QUESTIONS, start=1):
        print(f"Evaluating question {number}/10")

        results = search_engine.search(question, top_k=3)

        output.extend([
            f"## Q{number}: {question}",
            ""
        ])

        for rank, result in enumerate(results, start=1):
            metadata = result["metadata"]

            output.extend([
                f"### Result {rank}",
                f"- Similarity score: {result['score']:.4f}",
                f"- Title: {metadata.get('title', 'Unknown')}",
                f"- Source: {metadata.get('source', 'Unknown')}",
                f"- Page: {metadata.get('page', 'Not available')}",
                "",
                result["text"],
                ""
            ])

        if number == 6:
            output.extend([
                "**Evaluation note:** This question is intentionally "
                "unanswerable because current weather information is "
                "not available in the dataset.",
                ""
            ])

    output.extend([
        "---",
        "",
        "# Evaluation Summary",
        "",
        "- Total questions: 10",
        "- Retrieved results per question: 3",
        "- Total retrieved results: 30",
        "- Vector database: Persistent ChromaDB",
        "- Embedding model: all-MiniLM-L6-v2",
        "",
        "## Observations",
        "",
        "1. Semantic search retrieves documents based on meaning.",
        "2. Similarity scores rank retrieved chunks.",
        "3. Source metadata identifies the original document.",
        "4. Q6 is intentionally unanswerable from the dataset.",
        "5. Retrieved results must be checked before generating answers.",
        "",
        "## Limitations",
        "",
        "- Semantic similarity does not guarantee factual correctness.",
        "- Missing information can still produce search results.",
        "- Top 3 retrieval does not guarantee exhaustive results.",
        "- Page numbers are unavailable for the current JSON records.",
        "- Weather and other live information are not in the dataset.",
        ""
    ])

    output_path = Path("eval/search_results.md")
    output_path.write_text("\n".join(output), encoding="utf-8")

    print("\nEvaluation completed successfully.")
    print("Questions evaluated:", len(QUESTIONS))
    print("Results per question: 3")
    print("Evaluation saved to:", output_path)


if __name__ == "__main__":
    main()
