"""
Embedding Provider Abstraction for GadKille.

Provides lightweight, external API-based embeddings (e.g. Google Gemini)
to avoid loading large PyTorch/Sentence-Transformers models in memory-constrained
environments like Render Free (512 MB RAM limit).
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'gemini', 'mock')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the embedding model."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Dimension size of the embedding vectors."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str, task_type: str = "query") -> List[float]:
        """Convert a single text string into a numerical vector."""
        pass

    @abstractmethod
    def generate_embeddings(
        self, texts: List[str], task_type: str = "document"
    ) -> List[List[float]]:
        """Convert a batch of text strings into a list of numerical vectors."""
        pass


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Lightweight embedding provider using Google Gemini API via google-genai SDK.
    Requires no local PyTorch or SentenceTransformers weights in memory.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        dimensions: Optional[int] = None,
    ):
        from dotenv import load_dotenv

        load_dotenv()

        self._api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self._api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. Required for Gemini embeddings."
            )

        self._model = model or os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
        self._dimensions = dimensions or int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
        self._client = None

    def _get_client(self):
        if self._client is None:
            from google import genai

            self._client = genai.Client(api_key=self._api_key)
        return self._client

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def _map_task_type(self, task_type: str) -> str:
        tt = task_type.upper()
        if "DOC" in tt:
            return "RETRIEVAL_DOCUMENT"
        elif "QUERY" in tt or "SEARCH" in tt:
            return "RETRIEVAL_QUERY"
        elif "SIMILAR" in tt:
            return "SEMANTIC_SIMILARITY"
        return "RETRIEVAL_QUERY"

    def generate_embedding(self, text: str, task_type: str = "query") -> List[float]:
        if not text or not text.strip():
            return [0.0] * self._dimensions

        import time

        from google.genai import types

        client = self._get_client()
        gemini_task = self._map_task_type(task_type)

        config = types.EmbedContentConfig(
            task_type=gemini_task,
            output_dimensionality=self._dimensions,
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = client.models.embed_content(
                    model=self._model,
                    contents=text,
                    config=config,
                )
                if resp.embeddings and resp.embeddings[0].values:
                    return list(resp.embeddings[0].values)
                return [0.0] * self._dimensions
            except Exception as exc:
                err_str = str(exc)
                if ("429" in err_str or "RESOURCE_EXHAUSTED" in err_str) and attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    raise exc

        return [0.0] * self._dimensions

    def generate_embeddings(
        self, texts: List[str], task_type: str = "document"
    ) -> List[List[float]]:
        if not texts:
            return []

        import time

        from google.genai import types

        client = self._get_client()
        gemini_task = self._map_task_type(task_type)
        config = types.EmbedContentConfig(
            task_type=gemini_task,
            output_dimensionality=self._dimensions,
        )

        all_embeddings: List[List[float]] = []
        batch_size = 30  # Smaller batch to respect RPM limits

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    resp = client.models.embed_content(
                        model=self._model,
                        contents=batch,
                        config=config,
                    )
                    for emb in resp.embeddings:
                        all_embeddings.append(list(emb.values))
                    break
                except Exception as exc:
                    err_str = str(exc)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        wait_sec = 21  # Wait out the 1-minute rate window
                        print(
                            f"Rate limit reached (429). Waiting {wait_sec}s before retrying "
                            f"(attempt {attempt + 1}/{max_retries})..."
                        )
                        time.sleep(wait_sec)
                    else:
                        raise exc

        return all_embeddings


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic mock embedding provider for tests and CI pipelines.
    Generates fast hash-based pseudo-embeddings with zero network or PyTorch requirements.
    """

    def __init__(self, dimensions: int = 768, model: str = "mock-embedding-v1"):
        self._dimensions = dimensions
        self._model = model

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def _hash_vector(self, text: str) -> List[float]:
        import hashlib
        import math

        if not text:
            return [0.0] * self._dimensions

        raw_hash = hashlib.sha256(text.encode("utf-8")).digest()
        vec = []
        for i in range(self._dimensions):
            byte_val = raw_hash[i % len(raw_hash)]
            val = ((byte_val / 127.5) - 1.0) * math.cos(i)
            vec.append(val)

        # Normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def generate_embedding(self, text: str, task_type: str = "query") -> List[float]:
        return self._hash_vector(text)

    def generate_embeddings(
        self, texts: List[str], task_type: str = "document"
    ) -> List[List[float]]:
        return [self._hash_vector(t) for t in texts]


class LocalSentenceTransformerProvider(BaseEmbeddingProvider):
    """
    Optional fallback provider using local SentenceTransformers.
    Only instantiated if explicitly configured via EMBEDDING_PROVIDER=local.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer

        self._model_name = model_name
        self._model = SentenceTransformer(model_name)
        self._dimensions = self._model.get_sentence_embedding_dimension()

    @property
    def provider_name(self) -> str:
        return "local"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def generate_embedding(self, text: str, task_type: str = "query") -> List[float]:
        embedding = self._model.encode(
            text, convert_to_numpy=True, normalize_embeddings=True
        )
        return embedding.tolist()

    def generate_embeddings(
        self, texts: List[str], task_type: str = "document"
    ) -> List[List[float]]:
        if not texts:
            return []
        embeddings = self._model.encode(
            texts, convert_to_numpy=True, normalize_embeddings=True
        )
        return embeddings.tolist()


def get_embedding_provider(
    provider: Optional[str] = None,
) -> BaseEmbeddingProvider:
    """
    Factory to retrieve the configured embedding provider.
    Priority:
      1. Explicit `provider` argument
      2. Environment variable EMBEDDING_PROVIDER (defaults to 'gemini')
      3. Fallback to 'mock' if no Gemini API key is configured or offline
    """
    from dotenv import load_dotenv

    load_dotenv()

    prov = (provider or os.getenv("EMBEDDING_PROVIDER", "gemini")).lower()

    if prov == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            # Fall back to mock if Gemini key is missing
            return MockEmbeddingProvider()
        return GeminiEmbeddingProvider()

    elif prov == "mock":
        return MockEmbeddingProvider()

    elif prov == "local":
        return LocalSentenceTransformerProvider()

    else:
        raise ValueError(f"Unsupported embedding provider: {prov}")


class EmbeddingModel:
    """
    Backwards-compatible wrapper matching legacy app.embed.EmbeddingModel interface.
    Delegates to the configured BaseEmbeddingProvider.
    """

    def __init__(self, model_name: Optional[str] = None):
        self._provider = get_embedding_provider()

    def generate_embedding(self, text: str) -> List[float]:
        return self._provider.generate_embedding(text, task_type="query")

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._provider.generate_embeddings(texts, task_type="document")
