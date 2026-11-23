"""
Traditional Smart Search for GadKille using TF-IDF and Cosine Similarity.

Provides lexical search across fort name, district, base village, and trek notes.
Precomputes and caches the TF-IDF vectorizer and document matrix to avoid
redundant matrix allocations on every user query.
"""

from typing import Any, Dict, List, Optional, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records

_CACHED_STATE: Optional[Tuple[TfidfVectorizer, Any, List[Dict[str, Any]]]] = None


def _get_tfidf_index() -> Tuple[TfidfVectorizer, Any, List[Dict[str, Any]]]:
    """Retrieve or build the cached TF-IDF index."""
    global _CACHED_STATE
    if _CACHED_STATE is not None:
        return _CACHED_STATE

    records = load_records()
    documents = []

    for fort in records:
        text = " ".join([
            str(fort.get("fort_name") or ""),
            str(fort.get("district") or ""),
            str(fort.get("base_village") or ""),
            str(fort.get("trek_notes") or ""),
        ])
        documents.append(text)

    vectorizer = TfidfVectorizer()
    if documents:
        tfidf_matrix = vectorizer.fit_transform(documents)
    else:
        tfidf_matrix = None

    _CACHED_STATE = (vectorizer, tfidf_matrix, records)
    return _CACHED_STATE


def invalidate_smart_search_cache() -> None:
    """Clear the cached TF-IDF index."""
    global _CACHED_STATE
    _CACHED_STATE = None


def smart_search(query: str) -> List[Dict[str, Any]]:
    """
    Search forts using TF-IDF cosine similarity.
    Reuses the precomputed vectorizer and document matrix for instant search.
    """
    if not query or not query.strip():
        return []

    vectorizer, tfidf_matrix, records = _get_tfidf_index()

    if tfidf_matrix is None or not records:
        return []

    query_vector = vectorizer.transform([query])
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    ranked_results = []
    for index, score in enumerate(scores):
        if score > 0:
            result = records[index].copy()
            result["relevance_score"] = round(float(score), 3)
            ranked_results.append(result)

    ranked_results.sort(key=lambda item: item["relevance_score"], reverse=True)
    return ranked_results


if __name__ == "__main__":
    query = input("Enter your search query: ")
    results = smart_search(query)

    print("\n===== SMART SEARCH RESULTS =====")
    for fort in results[:5]:
        print(
            fort["fort_name"],
            "| District:", fort["district"],
            "| Score:", fort["relevance_score"]
        )
