
import json
import re
import shutil
from pathlib import Path

from app.article_loader import load_articles
from app.chunking import create_document_chunks
from app.vectorstore import VectorStore


BASE_DIR = Path(__file__).resolve().parent.parent

EVAL_PATH = BASE_DIR / "eval" / "eval_set.json"
OUTPUT_PATH = BASE_DIR / "eval" / "results.json"


# Two configurations to compare
CONFIGS = [
    {
        "name": "Config A",
        "chunk_size": 300,
        "overlap": 50,
        "top_k": 3
    },
    {
        "name": "Config B",
        "chunk_size": 500,
        "overlap": 100,
        "top_k": 5
    }
]


def normalize_title(value):
    """Normalize fort titles for reliable matching."""

    value = value.lower().strip()

    value = re.sub(r"\bfortress\b", "", value)
    value = re.sub(r"\bfort\b", "", value)

    return re.sub(r"[^a-z0-9]", "", value)


def load_data():
    """Load Wikipedia articles and evaluation questions."""

    documents = load_articles()

    with open(EVAL_PATH, "r", encoding="utf-8") as file:
        questions = json.load(file)

    return documents, questions


def calculate_metrics(results):
    """Calculate Hit Rate and Mean Reciprocal Rank."""

    total_questions = len(results)

    if total_questions == 0:
        return {
            "hit_rate": 0,
            "mrr": 0
        }

    hits = 0
    reciprocal_ranks = []

    for result in results:

        rank = result["rank"]

        if rank is not None:
            hits += 1
            reciprocal_ranks.append(1 / rank)
        else:
            reciprocal_ranks.append(0)

    return {
        "hit_rate": round(
            hits / total_questions * 100, 2
        ),
        "mrr": round(
            sum(reciprocal_ranks) / total_questions, 4
        )
    }


def evaluate_config(config, documents, questions):

    print("\n" + "=" * 55)
    print("Evaluating:", config["name"])
    print("=" * 55)

    db_path = (
        BASE_DIR
        / "data"
        / "eval_chroma"
        / config["name"].lower().replace(" ", "_")
    )

    # Remove old index
    if db_path.exists():
        shutil.rmtree(db_path)

    # Create chunks
    chunks = create_document_chunks(
        documents,
        chunk_size=config["chunk_size"],
        overlap=config["overlap"]
    )

    print("Total chunks:", len(chunks))

    # Create independent vector database
    vector_store = VectorStore(
        persist_directory=str(db_path)
    )

    vector_store.index_chunks(chunks)

    evaluation_results = []

    for question in questions:

        retrieved = vector_store.search(
            question["question"],
            top_k=config["top_k"]
        )

        expected_forts = {
            normalize_title(name)
            for name in question["expected_forts"]
        }

        rank = None

        retrieved_forts = []

        for position, item in enumerate(retrieved, start=1):

            title = (
                item.get("metadata", {})
                .get("title", "Unknown")
            )

            retrieved_forts.append(title)

            normalized_title = normalize_title(title)

            if normalized_title in expected_forts:
                rank = position
                break

        evaluation_results.append({
            "id": question["id"],
            "question": question["question"],
            "answerable": question["answerable"],
            "rank": rank,
            "retrieved_forts": retrieved_forts
        })

        status = "HIT" if rank is not None else "MISS"

        print(
            f'{question["id"]}: {status} | Rank: {rank}'
        )

    # Calculate metrics only for answerable questions
    answerable_results = [
        result
        for result in evaluation_results
        if result["answerable"]
    ]

    metrics = calculate_metrics(answerable_results)

    return {
        "configuration": config,
        "metrics": metrics,
        "total_chunks": len(chunks),
        "total_questions": len(questions),
        "answerable_questions": len(answerable_results),
        "results": evaluation_results
    }


def main():

    documents, questions = load_data()

    print("Total articles:", len(documents))
    print("Total evaluation questions:", len(questions))

    all_results = []

    # Evaluate both configurations
    for config in CONFIGS:

        result = evaluate_config(
            config,
            documents,
            questions
        )

        all_results.append(result)

        print("\nMetrics:")
        print("Hit Rate:", result["metrics"]["hit_rate"], "%")
        print("MRR:", result["metrics"]["mrr"])

    # Select winner
    winner = max(
        all_results,
        key=lambda result: (
            result["metrics"]["hit_rate"],
            result["metrics"]["mrr"]
        )
    )

    # Save evaluation report
    final_report = {
        "configurations": all_results,
        "winner": winner["configuration"]["name"]
    }

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(
            final_report,
            file,
            indent=4,
            ensure_ascii=False
        )

    # Final comparison
    print("\n" + "=" * 55)
    print("FINAL COMPARISON")
    print("=" * 55)

    for result in all_results:

        config = result["configuration"]
        metrics = result["metrics"]

        print(
            f'{config["name"]}: '
            f'Chunk={config["chunk_size"]}, '
            f'Overlap={config["overlap"]}, '
            f'Top-K={config["top_k"]}, '
            f'Chunks={result["total_chunks"]}, '
            f'Hit Rate={metrics["hit_rate"]}%, '
            f'MRR={metrics["mrr"]}'
        )

    print("\nWinner:", winner["configuration"]["name"])
    print("Report saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()
