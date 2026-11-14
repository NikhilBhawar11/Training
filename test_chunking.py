
from app.chunking import create_document_chunks

documents = [
    {
        "title": "Ahmednagar Fort",
        "source": "Ahmednagar_Fort.html",
        "page": 1,
        "text": "Ahmednagar Fort is a historic fort in Maharashtra. " * 100
    }
]

chunks = create_document_chunks(documents)

print("Total chunks:", len(chunks))

for chunk in chunks:
    print("\nMetadata:", chunk["metadata"])
    print("Text:", chunk["text"][:150])
