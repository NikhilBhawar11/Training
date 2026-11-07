
import json
import re
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests


BASE_DIR = Path(__file__).resolve().parent.parent

RECORDS_FILE = BASE_DIR / "data" / "records.json"
OUTPUT_DIR = BASE_DIR / "data" / "raw" / "articles"


def fetch_documents():

    # Load our extracted fort records
    with open(RECORDS_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    # Create output folder
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Download only the first 3 fort articles
    selected_records = records[:3]

    successful = 0

    for record in selected_records:

        url = record["source_url"]
        fort_name = record["fort_name"]

        # Create a safe filename from the URL
        page_name = unquote(urlparse(url).path.split("/")[-1])
        filename = re.sub(r"[^a-zA-Z0-9_-]", "_", page_name)

        output_file = OUTPUT_DIR / f"{filename}.html"

        try:
            print(f"\nDownloading: {fort_name}")

            response = requests.get(
                url,
                headers={
                    "User-Agent": "GadKilleStudentProject/1.0"
                },
                timeout=15
            )

            # Raise an error for HTTP failures
            response.raise_for_status()

            # Save downloaded HTML
            output_file.write_text(
                response.text,
                encoding="utf-8"
            )

            print("Downloaded successfully!")
            print("Saved:", output_file.name)

            successful += 1

        except requests.exceptions.Timeout:
            print("Request timed out:", fort_name)

        except requests.exceptions.HTTPError as error:
            print("HTTP error:", error)

        except requests.exceptions.RequestException as error:
            print("Request failed:", error)

        except Exception as error:
            print("Unexpected error:", error)

    print("\n========== DOWNLOAD SUMMARY ==========")
    print("Total attempted:", len(selected_records))
    print("Successfully downloaded:", successful)
    print("Output folder:", OUTPUT_DIR)


if __name__ == "__main__":
    fetch_documents()
