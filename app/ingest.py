
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

from bs4 import BeautifulSoup

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE = BASE_DIR / "data" / "records.json"

WIKIPEDIA_BASE = "https://en.wikipedia.org"


def clean_text(value):
    if value:
        return " ".join(value.split())
    return None


def normalize_url(url):
    """Normalize URLs to prevent duplicate records."""
    parsed = urlparse(url)

    return (
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path.rstrip("/")
    )


def is_valid_fort_link(link):
    """Check whether a link points to a valid Wikipedia article."""

    href = link.get("href", "")
    name = clean_text(link.get_text())

    if not name or not href:
        return False

    full_url = urljoin(WIKIPEDIA_BASE, href)
    parsed = urlparse(full_url)

    if parsed.netloc.lower() != "en.wikipedia.org":
        return False

    if not parsed.path.startswith("/wiki/"):
        return False

    if parsed.path.startswith((
        "/wiki/File:",
        "/wiki/Category:",
        "/wiki/Template:",
        "/wiki/Special:",
        "/wiki/Help:",
        "/wiki/Talk:",
        "/wiki/Wikipedia:"
    )):
        return False

    if "redlink=1" in parsed.query:
        return False

    if name.lower().endswith(" district"):
        return False

    if name.lower() in {"v", "t", "e", "forts in", "maharashtra"}:
        return False

    return True


def make_record(fort_name, district, source_url):

    return {
        "fort_name": fort_name,
        "district": district,
        "height_ft": None,
        "base_village": None,
        "trek_notes": None,
        "source_url": source_url
    }


def extract_template_records(file_path):

    records = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        content = soup.find(id="mw-content-text")

        if content is None:
            print("Wikipedia content not found:", file_path)
            return records

        current_district = None

        # Process all tables, not only the first one.
        for table in content.find_all("table"):

            for row in table.find_all("tr"):

                try:
                    links = row.find_all("a", href=True)

                    if not links:
                        continue

                    first_name = clean_text(
                        links[0].get_text()
                    )

                    # District headings identify the forts
                    # in the current row.
                    if first_name and first_name.lower().endswith(" district"):

                        current_district = first_name[:-len(" district")]

                        fort_links = links[1:]

                    else:
                        continue

                    for link in fort_links:

                        try:
                            if not is_valid_fort_link(link):
                                continue

                            fort_name = clean_text(
                                link.get_text()
                            )

                            source_url = urljoin(
                                WIKIPEDIA_BASE,
                                link["href"]
                            )

                            records.append(
                                make_record(
                                    fort_name,
                                    current_district,
                                    source_url
                                )
                            )

                        except Exception as error:
                            print("Skipping invalid fort:", error)

                except Exception as error:
                    print("Skipping invalid row:", error)

    except FileNotFoundError:
        print("File not found:", file_path)

    except Exception as error:
        print("Template ingestion error:", error)

    return records


def extract_list_records(file_path):

    records = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            soup = BeautifulSoup(file.read(), "html.parser")

        content = soup.find(id="mw-content-text")

        if content is None:
            print("Wikipedia content not found:", file_path)
            return records

        # Find the main fort listing table.
        tables = content.find_all("table")

        if not tables:
            print("Fort listing table not found.")
            return records

        for table in tables:

            for row in table.find_all("tr"):

                try:
                    for link in row.find_all("a", href=True):

                        try:
                            if not is_valid_fort_link(link):
                                continue

                            fort_name = clean_text(
                                link.get_text()
                            )

                            source_url = urljoin(
                                WIKIPEDIA_BASE,
                                link["href"]
                            )

                            records.append(
                                make_record(
                                    fort_name,
                                    None,
                                    source_url
                                )
                            )

                        except Exception as error:
                            print("Skipping invalid list entry:", error)

                except Exception as error:
                    print("Skipping invalid list row:", error)

    except FileNotFoundError:
        print("File not found:", file_path)

    except Exception as error:
        print("List ingestion error:", error)

    return records


def main():

    template_file = RAW_DIR / "forts_template.html"
    list_file = RAW_DIR / "list_of_forts.html"

    template_records = extract_template_records(template_file)
    list_records = extract_list_records(list_file)

    print("\nTemplate records:", len(template_records))
    print("List records:", len(list_records))

    # Combine both sources.
    all_records = template_records + list_records

    # Deduplicate by Wikipedia article URL.
    unique_records = {}

    for record in all_records:

        try:
            key = normalize_url(record["source_url"])

            if key not in unique_records:
                unique_records[key] = record

            else:
                # Prefer the template record if it contains
                # a district rather than None.
                existing = unique_records[key]

                if not existing["district"] and record["district"]:
                    unique_records[key] = record

        except Exception as error:
            print("Skipping invalid record:", error)

    cleaned_records = list(unique_records.values())

    try:
        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(
                cleaned_records,
                file,
                indent=4,
                ensure_ascii=False
            )

        print("\nIngestion completed!")
        print("Template records:", len(template_records))
        print("List records:", len(list_records))
        print("Total before deduplication:", len(all_records))
        print("Total unique forts:", len(cleaned_records))
        print("Saved to:", OUTPUT_FILE)

    except Exception as error:
        print("Error saving JSON:", error)


if __name__ == "__main__":
    main()
