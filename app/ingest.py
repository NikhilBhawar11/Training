
import json
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"


def clean_text(value):
    if value:
        return " ".join(value.split())
    return None


def extract_template_records(file_path):

    records = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        content = soup.find(id="mw-content-text")

        if content is None:
            print("Wikipedia content not found.")
            return records

        table = content.find("table")

        if table is None:
            print("Fort table not found.")
            return records

        current_district = None

        for row in table.find_all("tr"):

            try:
                links = row.find_all("a", href=True)

                if not links:
                    continue

                # First link identifies the district
                first_name = clean_text(links[0].get_text())

                if first_name and first_name.lower().endswith("district"):
                    current_district = first_name.replace(
                        " district", ""
                    )

                    fort_links = links[1:]

                else:
                    continue

                for link in fort_links:

                    try:
                        fort_name = clean_text(link.get_text())
                        source_url = link.get("href")

                        if not fort_name or not source_url:
                            continue

                        # Convert relative URLs into full URLs
                        if source_url.startswith("/"):
                            source_url = (
                                "https://en.wikipedia.org" + source_url
                            )

                        # Skip red links for articles that do not exist
                        if "redlink=1" in source_url:
                            continue

                        # Only accept Wikipedia article URLs
                        if not source_url.startswith(
                            "https://en.wikipedia.org/wiki/"
                        ):
                            continue

                        records.append({
                            "fort_name": fort_name,
                            "district": current_district,
                            "height_ft": None,
                            "base_village": None,
                            "trek_notes": None,
                            "source_url": source_url
                        })

                    except Exception as error:
                        print("Skipping invalid fort:", error)

            except Exception as error:
                print("Skipping invalid row:", error)

    except FileNotFoundError:
        print("File not found:", file_path)

    except Exception as error:
        print("Ingestion error:", error)

    return records


def main():

    file_path = RAW_DIR / "forts_template.html"

    records = extract_template_records(file_path)

    # Remove duplicate name-and-district combinations
    unique_records = {}

    for record in records:
        key = (
            record["fort_name"].lower(),
            record["district"].lower()
        )

        if key not in unique_records:
            unique_records[key] = record

    cleaned_records = list(unique_records.values())

    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(
                cleaned_records,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nIngestion completed!")
        print("Total unique forts:", len(cleaned_records))
        print("Saved to:", OUTPUT_FILE)

    except Exception as error:
        print("Error saving JSON:", error)


if __name__ == "__main__":
    main()
    