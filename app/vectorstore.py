
import hashlib
from pathlib import Path

import chromadb

from app.embed import EmbeddingModel


class VectorStore:

    def __init__(
        self,
        persist_directory="data/chroma_db",
        collection_name="gadkille_forts"
    ):
        Path(persist_directory).mkdir(
            parents=True,
            exist_ok=True
        )

        self.client = chromadb.PersistentClient(
            path=persist_directory
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        self.embedder = EmbeddingModel()

    def reset_collection(self):
        """Delete old vectors and create a fresh collection."""

        collection_name = self.collection.name

        self.client.delete_collection(name=collection_name)

        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        print("ChromaDB collection reset successfully.")

    def index_chunks(self, chunks):

        if not chunks:
            print("No chunks available to index.")
            return

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:
            text = chunk["text"]
            metadata = chunk.get("metadata", {})

            clean_metadata = {
                key: value
                for key, value in metadata.items()
                if value is not None
            }

            unique_text = str(clean_metadata) + text

            chunk_id = hashlib.sha256(
                unique_text.encode("utf-8")
            ).hexdigest()

            documents.append(text)
            metadatas.append(clean_metadata)
            ids.append(chunk_id)

        embeddings = self.embedder.generate_embeddings(documents)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        print(f"Successfully indexed {len(documents)} chunks.")

    def search(self, query, top_k=3):

        if self.count() == 0:
            return []

        query_embedding = self.embedder.generate_embedding(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.count())
        )

        output = []

        if not results["ids"] or not results["ids"][0]:
            return output

        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]

            output.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - distance
            })

        return output

    def count(self):
        return self.collection.count()
