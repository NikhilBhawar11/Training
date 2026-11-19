
import json
from pathlib import Path

from app.llm import generate_response
from app.semantic_search import SemanticSearch

BASE_DIR = Path(__file__).resolve().parent

PROMPT_DIR = BASE_DIR / "app" / "prompts"
OUTPUT_DIR = BASE_DIR / "eval"

QUESTIONS = [
    "Tell me about Raigad Fort.",
    "Which district is Sinhagad Fort located in?",
    "What is the historical importance of Shivneri Fort?",
    "Where is Harishchandragad Fort located?",
    "Explain the trekking difficulty of Rajgad Fort.",
    "Which village is the base village for Torna Fort?",
    "What is the height of Pratapgad Fort?",
    "Recommend forts in Pune district.",
    "Which forts are suitable for beginner trekkers?",
    "What is the current population of Raigad Fort?"
]


def load_prompt(filename):
    return (PROMPT_DIR / filename).read_text(encoding="utf-8")


def build_context(results):
    parts = []

    for index, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})

        parts.append(
            f"""
Document {index}
Fort: {metadata.get('title', 'Unknown')}
Source: {metadata.get('source', 'Unknown')}
Information:
{result.get('text', '')}
"""
        )

    return "\n".join(parts) or "No relevant information was found."


def main():
    search_engine = SemanticSearch()

    prompt_a = load_prompt("version_a.txt")
    prompt_b = load_prompt("version_b.txt")

    evaluation_results = []

    for number, question in enumerate(QUESTIONS, start=1):
        print(f"\nTesting Q{number}: {question}")

        # Retrieve context once so both versions receive identical evidence.
        retrieved = search_engine.search(question, top_k=3)
        context = build_context(retrieved)

        user_prompt = f"""
Retrieved Context:
{context}

User Question:
{question}

Answer using the retrieved context.
Do not invent facts.
"""

        response_a = generate_response(
            prompt=user_prompt,
            system_prompt=prompt_a
        )

        response_b = generate_response(
            prompt=user_prompt,
            system_prompt=prompt_b
        )

        evaluation_results.append({
            "question": question,
            "version_a": response_a,
            "version_b": response_b
        })

        print("\nVERSION A:")
        print(response_a)

        print("\nVERSION B:")
        print(response_b)

        print("\n" + "=" * 70)

    output_file = OUTPUT_DIR / "prompt_comparison_results.json"

    output_file.write_text(
        json.dumps(evaluation_results, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nEvaluation completed.")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()
