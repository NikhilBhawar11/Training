
import json
from pathlib import Path

from app.chunking import create_document_chunks
from app.vectorstore import VectorStore


class SemanticSearch:

    def __init__(self):
        self.vector_store = VectorStore()

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
                "page": "not_available"
            })

        return documents

    def build_index(self):
        """Chunk documents and store them in ChromaDB."""

        documents = self.load_documents()

        chunks = create_document_chunks(documents)

        self.vector_store.index_chunks(chunks)

        print("Total documents:", len(documents))
        print("Total chunks:", len(chunks))
        print("Chunks in ChromaDB:", self.vector_store.count())

    def search(self, query, top_k=3):
        """Search for relevant chunks using ChromaDB."""

        if self.vector_store.count() == 0:
            self.build_index()

        return self.vector_store.search(query, top_k)


if __name__ == "__main__":

    search_engine = SemanticSearch()

    if search_engine.vector_store.count() == 0:
        search_engine.build_index()

    query = "Which forts are located in Ahmednagar?"

    results = search_engine.search(query, top_k=3)

    print("\nQuery:", query)

    for result in results:
        print("\nScore:", round(result["score"], 4))
        print("Metadata:", result["metadata"])
        print("Text:", result["text"][:250])
