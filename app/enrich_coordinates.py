
import json
import re
import shutil
import math

from pathlib import Path
from urllib.parse import urlparse, unquote

from app.article_extractor import extract_article


BASE_DIR = Path(__file__).resolve().parent.parent

RECORDS_FILE = BASE_DIR / "data" / "records.json"
ARTICLES_DIR = BASE_DIR / "data" / "raw" / "articles"

BACKUP_FILE = BASE_DIR / "data" / "records.before_coordinates.json"


def get_article_filename(source_url):
    """
    Generate the same filename used by fetch.py.
    """

    page_name = unquote(
        urlparse(source_url).path.split("/")[-1]
    )

    return re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        page_name
    ) + ".html"


def enrich_records():

    with open(RECORDS_FILE, encoding="utf-8") as file:
        records = json.load(file)

    # Create backup before modifying records
    if not BACKUP_FILE.exists():
        shutil.copy2(RECORDS_FILE, BACKUP_FILE)
        print("Backup created:", BACKUP_FILE)
    else:
        print("Existing backup found:", BACKUP_FILE)

    updated = 0
    missing = 0

    for record in records:

        source_url = record.get("source_url")

        if not source_url:
            missing += 1
            continue

        filename = get_article_filename(source_url)

        article_path = ARTICLES_DIR / filename

        if not article_path.exists():
            missing += 1
            continue

        extracted = extract_article(article_path)

        latitude = extracted.get("latitude")
        longitude = extracted.get("longitude")

        if latitude is None or longitude is None:
            missing += 1
            continue

        latitude = float(latitude)
        longitude = float(longitude)

        if not (
            math.isfinite(latitude)
            and math.isfinite(longitude)
            and -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            missing += 1
            continue

        record["latitude"] = latitude
        record["longitude"] = longitude

        updated += 1

        print(
            f"Updated: {record['fort_name']} "
            f"| {latitude}, {longitude}"
        )

    # Save through a temporary file
    temp_file = RECORDS_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(records, file, indent=4, ensure_ascii=False)

    temp_file.replace(RECORDS_FILE)

    print("\n========== SUMMARY ==========")
    print("Total forts:", len(records))
    print("Coordinates added:", updated)
    print("Missing/unavailable:", missing)
    print("Backup:", BACKUP_FILE)


if __name__ == "__main__":
    enrich_records()
