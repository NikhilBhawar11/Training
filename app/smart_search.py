from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.records import load_records


def smart_search(query):
    records = load_records()

    if not query.strip() or not records:
        return []

    # Prepare searchable text for every fort
    documents = []

    for fort in records:
        text = " ".join([
            str(fort.get("fort_name") or ""),
            str(fort.get("district") or ""),
            str(fort.get("base_village") or ""),
            str(fort.get("trek_notes") or "")
        ])

        documents.append(text)

    # Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Convert user query into a vector
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity
    scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Rank results by similarity score
    ranked_results = []

    for index, score in enumerate(scores):
        if score > 0:
            result = records[index].copy()
            result["relevance_score"] = round(float(score), 3)
            ranked_results.append(result)

    ranked_results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

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