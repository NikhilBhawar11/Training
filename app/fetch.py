
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests
from bs4 import BeautifulSoup

from app import records


BASE_DIR = Path(__file__).resolve().parent.parent

RECORDS_FILE = BASE_DIR / "data" / "records.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw" / "articles"

BATCH_SIZE = 10
REQUEST_DELAY = 1

# Known legitimate Wikipedia title variations
TITLE_ALIASES = {
    "Balapur": ["Balapur Fort"],
    "Bhamer": ["Bhamer Dhule"],
    "Laling": ["Laling fort"],
    "Bhairavgad": ["Bhairavgad (fort)"],
    "Panhala": ["Panhala Fort"],
    "Pargadh": ["Pargad"],
    "Udgir": ["Udgir Fort"],
    "Shivneri": ["Shivneri Fort"],
    "Torna": ["Torna Fort"],
    "Raigad": ["Raigad Fort"],
    "Alang": ["Alang Fort"]
}


def safe_filename(url):
    page_name = unquote(urlparse(url).path.split("/")[-1])
    return re.sub(r"[^a-zA-Z0-9_-]", "_", page_name) + ".html"


def normalize_title(value):
    value = value.lower()
    value = re.sub(r"\s*\([^)]*\)", "", value)
    return re.sub(r"[^a-z0-9]", "", value)


def validate_article(html, expected_name):
    soup = BeautifulSoup(html, "html.parser")

    heading = soup.find(id="firstHeading")

    if not heading:
        return False, "Wikipedia article title not found"

    actual_title = heading.get_text(" ", strip=True)

    allowed_titles = [expected_name]
    allowed_titles.extend(TITLE_ALIASES.get(expected_name, []))

    normalized_actual = normalize_title(actual_title)

    for allowed in allowed_titles:
        if normalized_actual == normalize_title(allowed):
            return True, actual_title

    return False, f"Title mismatch: {actual_title}"


def fetch_documents():

    with open(RECORDS_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    successful = 0
    skipped = 0
    failed = 0
    invalid = 0

    session = requests.Session()

    session.headers.update({
        "User-Agent": "GadKilleStudentProject/1.0 (educational project)"
    })

    # Download seven missing fort articles
    target_forts = [
    "Achala Fort",
    "Ahivant Fort",
    "Alang",
    "Anjaneri",
    "Ankai Fort"
]

    selected_records = [
        record for record in records
        if record.get("fort_name") in target_forts
    ]

    for record in selected_records:

        url = record["source_url"]
        fort_name = record["fort_name"]

        output_file = OUTPUT_DIR / safe_filename(url)

        if output_file.exists():

            try:
                existing_html = output_file.read_text(encoding="utf-8")

                is_valid, message = validate_article(
                    existing_html,
                    fort_name
                )

                if is_valid:
                    print(f"\nSkipping valid existing file: {fort_name}")
                    skipped += 1
                    continue

                print(f"\nExisting file is invalid: {fort_name}")
                print("Reason:", message)

            except Exception as error:
                print("Could not validate existing file:", error)

        try:
            print(f"\nDownloading: {fort_name}")

            response = session.get(url, timeout=20)
            response.raise_for_status()

            is_valid, message = validate_article(
                response.text,
                fort_name
            )

            if not is_valid:
                print("Article validation failed:", message)
                invalid += 1
                continue

            output_file.write_text(
                response.text,
                encoding="utf-8"
            )

            print("Downloaded and verified:", message)

            successful += 1
            time.sleep(REQUEST_DELAY)

        except requests.exceptions.Timeout:
            print("Request timed out:", fort_name)
            failed += 1

        except requests.exceptions.HTTPError as error:
            print("HTTP error:", error)
            failed += 1

        except requests.exceptions.RequestException as error:
            print("Request failed:", error)
            failed += 1

        except Exception as error:
            print("Unexpected error:", error)
            failed += 1

    print("\n========== DOWNLOAD SUMMARY ==========")
    print("Total attempted:", len(selected_records))
    print("Downloaded:", successful)
    print("Skipped:", skipped)
    print("Invalid articles:", invalid)
    print("Failed:", failed)
    print("Output folder:", OUTPUT_DIR)


if __name__ == "__main__":
    fetch_documents()
