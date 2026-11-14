
from pathlib import Path
from app.semantic_search import SemanticSearch

# Copy your exact 10 questions from task-docs/how_llms_work.md

QUESTIONS = [
    "Which forts are located in Ahmednagar district?",

    "Which district is Ahmednagar Fort located in?",

    "Tell me about Bahadurgad Fort.",

    "Which district is Bhairavgad Fort located in?",

    "List the forts available in Nashik district.",

    # Q6: Intentionally unanswerable from the dataset
    "What is the current weather at Raigad Fort?",

    "Which forts are located in Pune district?",

    "List the forts available in Satara district.",

    "Is Raigad Fort included in the GadKille dataset?",

    "How many fort records are available in GadKille?"
]


def main():
    search_engine = SemanticSearch()
    search_engine.build_index()

    output = [
        "# GadKille Semantic Search Evaluation",
        "",
        "Model: all-MiniLM-L6-v2",
        "Retrieval method: Cosine similarity",
        "Top K: 3",
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
            output.extend([
                f"### Result {rank}",
                f"- Similarity score: {result['score']:.4f}",
                f"- Title: {result['metadata']['title']}",
                f"- Source: {result['metadata']['source']}",
                f"- Page: {result['metadata']['page']}",
                "",
                result["text"],
                ""
            ])

    output_path = Path("eval/search_results.md")
    output_path.write_text("\n".join(output), encoding="utf-8")

    print(f"\nEvaluation saved to: {output_path}")


if __name__ == "__main__":
    main()
