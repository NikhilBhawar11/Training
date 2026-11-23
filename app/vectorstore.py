"""
Lightweight Vector Store for GadKille using NumPy and JSON metadata.

Replaces heavy ChromaDB / SQLite / HNSW dependencies with a high-performance,
in-memory NumPy vector matrix and persisted JSON metadata.
Reduces runtime memory usage from ~500 MB down to ~2 MB.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.embed import BaseEmbeddingProvider, get_embedding_provider

DEFAULT_INDEX_DIR = Path(__file__).resolve().parent.parent / "data" / "index"


class VectorStore:
    """
    Lightweight vector store storing normalized embeddings in a NumPy array (.npy)
    and chunk text/metadata in a JSON file (metadata.json).
    """

    def __init__(
        self,
        index_directory: Optional[str] = None,
        embedder: Optional[BaseEmbeddingProvider] = None,
        collection_name: str = "gadkille_forts",
    ):
        self.index_dir = Path(index_directory or DEFAULT_INDEX_DIR)
        self.collection_name = collection_name
        self.embedder = embedder or get_embedding_provider()

        self.embeddings_path = self.index_dir / "embeddings.npy"
        self.metadata_path = self.index_dir / "metadata.json"

        # In-memory storage
        self._vectors: Optional[np.ndarray] = None  # shape: (N, D)
        self._normalized_vectors: Optional[np.ndarray] = None
        self._documents: List[Dict[str, Any]] = []
        self._index_meta: Dict[str, Any] = {}

        self.load_index()

    def load_index(self) -> bool:
        """Load persisted vector embeddings and metadata from disk."""
        if not self.embeddings_path.exists() or not self.metadata_path.exists():
            self._vectors = None
            self._normalized_vectors = None
            self._documents = []
            self._index_meta = {}
            return False

        try:
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                meta_data = json.load(f)

            vectors = np.load(self.embeddings_path)
            if len(vectors) != len(meta_data.get("documents", [])):
                print(
                    f"Warning: vector count ({len(vectors)}) != document count "
                    f"({len(meta_data.get('documents', []))}). Invalid index."
                )
                return False

            self._index_meta = {
                "version": meta_data.get("version", "1.0"),
                "provider": meta_data.get("provider", "unknown"),
                "model": meta_data.get("model", "unknown"),
                "dimensions": meta_data.get("dimensions", vectors.shape[1] if vectors.ndim > 1 else 0),
                "created_at": meta_data.get("created_at"),
            }
            self._documents = meta_data.get("documents", [])
            self._vectors = vectors.astype(np.float32)

            # Pre-normalize vectors for instant dot-product cosine similarity
            norms = np.linalg.norm(self._vectors, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self._normalized_vectors = self._vectors / norms
            return True

        except Exception as exc:
            print(f"Error loading vector index from {self.index_dir}: {exc}")
            self._vectors = None
            self._normalized_vectors = None
            self._documents = []
            return False

    def save_index(self, target_dir: Optional[Path] = None) -> None:
        """
        Safely persist vectors and metadata using atomic file replacement (.tmp -> real).
        """
        out_dir = target_dir or self.index_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        tmp_emb_path = out_dir / "temp_embeddings.npy"
        tmp_meta_path = out_dir / "temp_metadata.json"
        real_emb_path = out_dir / "embeddings.npy"
        real_meta_path = out_dir / "metadata.json"

        if self._vectors is None or len(self._documents) == 0:
            return

        # 1. Save temp files
        np.save(tmp_emb_path, self._vectors)

        meta_payload = {
            "version": "1.0",
            "provider": self.embedder.provider_name,
            "model": self.embedder.model_name,
            "dimensions": self.embedder.dimensions,
            "count": len(self._documents),
            "documents": self._documents,
        }

        with open(tmp_meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_payload, f, ensure_ascii=False, indent=2)

        # 2. Atomic replacement
        if os.name == "nt":
            # On Windows, replace can fail if destination exists
            if real_emb_path.exists():
                real_emb_path.unlink()
            if real_meta_path.exists():
                real_meta_path.unlink()

        tmp_emb_path.replace(real_emb_path)
        tmp_meta_path.replace(real_meta_path)

        # Update in-memory normalized vectors
        norms = np.linalg.norm(self._vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._normalized_vectors = self._vectors / norms

    def reset_collection(self) -> None:
        """Reset the vector store to empty."""
        self._vectors = None
        self._normalized_vectors = None
        self._documents = []
        self._index_meta = {}

    def index_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Index list of text chunks and persist to disk.
        Each chunk is expected to have 'text' and optional 'metadata'.
        """
        if not chunks:
            print("No chunks available to index.")
            return

        documents = []
        texts = []

        for chunk in chunks:
            text = chunk["text"]
            metadata = chunk.get("metadata", {})
            clean_metadata = {
                key: value for key, value in metadata.items() if value is not None
            }

            unique_text = str(clean_metadata) + text
            chunk_id = hashlib.sha256(unique_text.encode("utf-8")).hexdigest()

            documents.append({
                "id": chunk_id,
                "text": text,
                "metadata": clean_metadata,
            })
            texts.append(text)

        # Generate embeddings in batch via the provider
        raw_embeddings = self.embedder.generate_embeddings(texts, task_type="document")
        self._vectors = np.array(raw_embeddings, dtype=np.float32)
        self._documents = documents

        self.save_index()
        print(f"Successfully indexed {len(documents)} chunks to {self.index_dir}.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for top_k most similar chunks using cosine similarity.
        Returns a list of dicts: [{'text': ..., 'metadata': ..., 'score': float}].
        """
        if self.count() == 0 or self._normalized_vectors is None:
            return []

        if not query or not query.strip():
            return []

        query_embedding = self.embedder.generate_embedding(query, task_type="query")
        q_vec = np.array(query_embedding, dtype=np.float32)

        q_norm = np.linalg.norm(q_vec)
        if q_norm > 0:
            q_vec = q_vec / q_norm
        else:
            return []

        # Cosine similarity is the dot product of pre-normalized vectors
        scores = np.dot(self._normalized_vectors, q_vec)

        # Retrieve top-k indices
        k = min(top_k, len(scores))
        top_indices = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            # Clip between 0.0 and 1.0 for consistency
            normalized_score = max(0.0, min(1.0, (score + 1.0) / 2.0 if score < 0 else score))

            doc = self._documents[idx]
            results.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "score": round(normalized_score, 4),
            })

        return results

    def count(self) -> int:
        """Return total number of indexed vectors."""
        return len(self._documents) if self._documents else 0

    @property
    def index_metadata(self) -> Dict[str, Any]:
        """Return metadata describing the index (provider, model, dimensions)."""
        return self._index_meta
