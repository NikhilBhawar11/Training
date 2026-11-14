
from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingModel:

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        print("Loading embedding model...")
        self.model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully!")

    def generate_embedding(self, text: str) -> List[float]:
        """Convert one text into a numerical vector."""

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def generate_embeddings(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Convert multiple texts into numerical vectors."""

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.tolist()


if __name__ == "__main__":

    embedder = EmbeddingModel()

    text = "Raigad Fort is a historic fort in Maharashtra."

    vector = embedder.generate_embedding(text)

    print("\nOriginal text:", text)
    print("Embedding dimensions:", len(vector))
    print("First 10 values:", vector[:10])
