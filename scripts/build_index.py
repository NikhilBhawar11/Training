"""
Safe Embedding Index Builder for GadKille.

Builds a compact, high-performance NumPy vector index from extracted Wikipedia
articles without running PyTorch or SentenceTransformers.
Embeddings are generated via the configured embedding provider (e.g. Gemini).
"""

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.chunking import create_document_chunks  # noqa: E402
from app.embed import get_embedding_provider  # noqa: E402
from app.vectorstore import VectorStore  # noqa: E402

DEFAULT_ARTICLES_FILE = PROJECT_ROOT / "data" / "raw" / "extracted_articles.json"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "index"


def load_articles(file_path: Path):
    if not file_path.exists():
        raise FileNotFoundError(f"Articles file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        articles = json.load(f)

    documents = []
    for article in articles:
        documents.append({
            "text": article.get("text", ""),
            "title": article.get("title", "Unknown Fort"),
            "source": article.get("source", "unknown"),
            "page": article.get("page", 1),
        })
    return documents


def build_index(
    articles_file: Path = DEFAULT_ARTICLES_FILE,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    force_rebuild: bool = False,
    provider_name: str = None,
) -> bool:
    """
    Build and atomically persist the vector index.
    Validates temporary files before replacing any existing index.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = output_dir / "metadata.json"
    embeddings_path = output_dir / "embeddings.npy"

    embedder = get_embedding_provider(provider=provider_name)
    print(f"Using Embedding Provider: {embedder.provider_name}")
    print(f"Model: {embedder.model_name} (Dimensions: {embedder.dimensions})")

    # Check existing index compatibility
    if not force_rebuild and metadata_path.exists() and embeddings_path.exists():
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if (
                meta.get("provider") == embedder.provider_name
                and meta.get("model") == embedder.model_name
                and meta.get("dimensions") == embedder.dimensions
                and meta.get("count", 0) > 0
            ):
                print(
                    f"Compatible index already exists with {meta.get('count')} chunks. "
                    "Use --force to rebuild."
                )
                return True
        except Exception as e:
            print(f"Existing index could not be read ({e}). Rebuilding...")

    print(f"Loading articles from: {articles_file}")
    documents = load_articles(articles_file)
    print(f"Total documents loaded: {len(documents)}")

    chunks = create_document_chunks(documents)
    print(f"Generated {len(chunks)} text chunks.")

    # Build index using a temporary store to avoid destroying the existing index
    temp_dir = output_dir / "temp_build"
    temp_dir.mkdir(parents=True, exist_ok=True)

    try:
        temp_store = VectorStore(index_directory=str(temp_dir), embedder=embedder)
        print(f"Generating embeddings for {len(chunks)} chunks in batches...")
        temp_store.index_chunks(chunks)

        # Validate temporary build
        if temp_store.count() != len(chunks):
            raise ValueError(
                f"Validation failed: generated {temp_store.count()} vectors, expected {len(chunks)}"
            )

        # Atomic replacement into output_dir
        tmp_emb = temp_dir / "embeddings.npy"
        tmp_meta = temp_dir / "metadata.json"
        target_emb = output_dir / "embeddings.npy"
        target_meta = output_dir / "metadata.json"

        if os.name == "nt":
            if target_emb.exists():
                target_emb.unlink()
            if target_meta.exists():
                target_meta.unlink()

        tmp_emb.replace(target_emb)
        tmp_meta.replace(target_meta)

        # Cleanup temp directory
        try:
            temp_dir.rmdir()
        except Exception:
            pass

        print(
            f"Successfully built and persisted index ({len(chunks)} vectors, "
            f"{embedder.dimensions} dimensions) to {output_dir}."
        )
        return True

    except Exception as exc:
        print(f"Error during index generation: {exc}")
        # Clean up temp files without touching live index
        if temp_dir.exists():
            for p in temp_dir.glob("*"):
                try:
                    p.unlink()
                except Exception:
                    pass
            try:
                temp_dir.rmdir()
            except Exception:
                pass
        return False


def main():
    parser = argparse.ArgumentParser(description="Build GadKille vector index.")
    parser.add_argument(
        "--articles",
        type=Path,
        default=DEFAULT_ARTICLES_FILE,
        help="Path to extracted_articles.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Path to output directory for index",
    )
    parser.add_argument(
        "--force", action="store_true", help="Force rebuild even if index is compatible"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="Embedding provider (gemini, mock, local)",
    )

    args = parser.parse_args()
    success = build_index(
        articles_file=args.articles,
        output_dir=args.output,
        force_rebuild=args.force,
        provider_name=args.provider,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
