
from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    """
    Split text into smaller chunks with overlapping content.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk_size or overlap")

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = start + chunk_size

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def create_document_chunks(
    documents: List[Dict],
    chunk_size: int = 500,
    overlap: int = 100
) -> List[Dict]:
    """
    Create chunks while preserving document metadata.
    """

    all_chunks = []

    for document in documents:
        text = document.get("text", "")

        chunks = chunk_text(
            text,
            chunk_size,
            overlap
        )

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "text": chunk,
                "metadata": {
                    "source": document.get("source", "unknown"),
                    "page": document.get("page", 1),
                    "title": document.get("title", "Untitled"),
                    "chunk_index": index
                }
            })

    return all_chunks
