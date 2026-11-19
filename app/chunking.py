
from typing import Dict, List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> List[str]:
    """
    Split text into character-based chunks
    with overlapping content.
    """

    if not text or not text.strip():
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk_size or overlap")

    words = text.split()
    chunks = []

    current_chunk = []
    current_length = 0

    for word in words:

        word_length = len(word)

        if current_length + word_length + 1 > chunk_size and current_chunk:

            chunks.append(" ".join(current_chunk))

            # Preserve approximately the requested overlap
            overlap_words = []
            overlap_length = 0

            for previous_word in reversed(current_chunk):
                if overlap_length + len(previous_word) + 1 > overlap:
                    break

                overlap_words.insert(0, previous_word)
                overlap_length += len(previous_word) + 1

            current_chunk = overlap_words
            current_length = len(" ".join(current_chunk))

        current_chunk.append(word)

        current_length = len(" ".join(current_chunk))

    if current_chunk:
        chunks.append(" ".join(current_chunk))

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
