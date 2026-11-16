
import re
from pathlib import Path

from bs4 import BeautifulSoup


BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLE_DIR = BASE_DIR / "data" / "raw" / "articles"


def extract_article_text(file_path):
    """Extract clean readable text from a Wikipedia HTML article."""

    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    # Get article title
    heading = soup.find(id="firstHeading")
    title = heading.get_text(" ", strip=True) if heading else file_path.stem

    # Get main article content
    content = soup.find(id="mw-content-text")

    if content is None:
        return None

    # Remove unwanted elements
    for element in content.select(
        "table, style, script, sup, .mw-editsection, "
        ".navbox, .metadata, .reference, .ambox"
    ):
        element.decompose()

    text = content.get_text(" ", strip=True)

    # Clean whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return {
        "title": title,
        "text": text,
        "source": f"https://en.wikipedia.org/wiki/{file_path.stem}",
        "page": 1
    }


def load_articles():
    """Load all downloaded Wikipedia articles."""

    documents = []

    for file_path in ARTICLE_DIR.glob("*.html"):
        try:
            document = extract_article_text(file_path)

            if document and document["text"]:
                documents.append(document)

        except Exception as error:
            print(f"Error loading {file_path.name}: {error}")

    return documents


if __name__ == "__main__":
    documents = load_articles()

    print("Total articles loaded:", len(documents))

    for document in documents[:5]:
        print("\nTitle:", document["title"])
        print("Words:", len(document["text"].split()))
        print("Preview:", document["text"][:200])
