"""
Semantic Search retrieval engine for GadKille.

Uses the lightweight NumPy vector store and embedding provider to retrieve
relevant fort article chunks without loading PyTorch or ChromaDB.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.vectorstore import VectorStore

logger = logging.getLogger(__name__)


class SemanticSearch:
    """Semantic search engine backed by a lightweight NumPy vector store."""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or VectorStore()

    def load_documents(self) -> List[Dict[str, Any]]:
        """Load extracted Wikipedia article documents."""
        file_path = Path("data/raw/extracted_articles.json")
        if not file_path.exists():
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            articles = json.load(file)

        documents = []
        for article in articles:
            documents.append({
                "text": article.get("text", ""),
                "title": article.get("title", "Unknown Fort"),
                "source": article.get("source", "unknown"),
                "page": article.get("page", 1),
            })

        return documents

    def build_index(self, force: bool = True) -> None:
        """Explicitly build or rebuild the vector index."""
        from scripts.build_index import build_index

        build_index(force_rebuild=force)
        self.vector_store.load_index()

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Search for relevant chunks using the lightweight vector store."""
        if self.vector_store.count() == 0:
            logger.warning(
                "SemanticSearch index is empty or missing at data/index. "
                "Returning empty results. Run scripts/build_index.py to build index."
            )
            return []

        return self.vector_store.search(query, top_k=top_k)


if __name__ == "__main__":
    search_engine = SemanticSearch()
    query = "Which forts are located in Ahmednagar?"
    results = search_engine.search(query, top_k=3)

    print("\nQuery:", query)
    print("Results count:", len(results))
    for result in results:
        print("\nScore:", round(result["score"], 4))
        print("Metadata:", result["metadata"])
        print("Text:", result["text"][:250])
