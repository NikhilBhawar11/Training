
import json
from pathlib import Path

from app.article_extractor import extract_article

ARTICLE_DIR = Path("data/raw/articles")
OUTPUT_FILE = Path("data/raw/extracted_articles.json")


def main():
    documents = []

    for file_path in ARTICLE_DIR.glob("*.html"):
        try:
            article = extract_article(file_path)

            if not article or not article["article_text"].strip():
                print("Skipped:", file_path.name)
                continue

            documents.append({
                "title": article["article_title"],
                "text": article["article_text"],
                "source": file_path.name,
                "page": 1,
                "height_ft": article["height_ft"],
                "latitude": article["latitude"],
                "longitude": article["longitude"]
            })

            print(
                f"Extracted: {article['article_title']} | "
                f"{len(article['article_text'])} characters"
            )

        except Exception as error:
            print("Error:", file_path.name, error)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(documents, file, indent=4, ensure_ascii=False)

    print("\nTotal extracted articles:", len(documents))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
