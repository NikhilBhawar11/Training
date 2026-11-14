
import json
import numpy as np

from pathlib import Path
from app.chunking import create_document_chunks
from app.embed import EmbeddingModel


class SemanticSearch:

    def __init__(self):
        self.embedder = EmbeddingModel()
        self.chunks = []
        self.embeddings = None

    def load_documents(self):
        """Load GadKille records."""

        file_path = Path("data/records.json")

        with open(file_path, "r", encoding="utf-8") as file:
            records = json.load(file)

        documents = []

        for record in records:
            text = " ".join(
                f"{key}: {value}"
                for key, value in record.items()
                if value is not None and str(value).strip()
            )

            documents.append({
                "text": text,
                "title": record.get("fort_name", "Unknown Fort"),
                "source": record.get("source_url", "records.json"),
                "page": 1
            })

        return documents

    def build_index(self):
        """Chunk documents and generate embeddings."""

        documents = self.load_documents()

        self.chunks = create_document_chunks(documents)

        texts = [chunk["text"] for chunk in self.chunks]

        self.embeddings = np.array(
            self.embedder.generate_embeddings(texts)
        )

        print("Total chunks:", len(self.chunks))
        print("Embedding shape:", self.embeddings.shape)

    def search(self, query, top_k=3):
        """Find the most relevant chunks."""

        if self.embeddings is None:
            self.build_index()

        query_embedding = np.array(
            self.embedder.generate_embedding(query)
        )

        scores = np.dot(self.embeddings, query_embedding)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []

        for index in top_indices:
            results.append({
                "score": float(scores[index]),
                "text": self.chunks[index]["text"],
                "metadata": self.chunks[index]["metadata"]
            })

        return results


if __name__ == "__main__":

    search_engine = SemanticSearch()

    search_engine.build_index()

    query = "Which forts are located in Ahmednagar?"

    results = search_engine.search(query)

    print("\nQuery:", query)

    for result in results:
        print("\nScore:", round(result["score"], 4))
        print("Metadata:", result["metadata"])
        print("Text:", result["text"][:250])
