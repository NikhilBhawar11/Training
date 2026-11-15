
import re
from pathlib import Path
from bs4 import BeautifulSoup


def extract_elevation(infobox):
    """
    Extract elevation only from an explicit Elevation field.
    Returns elevation in feet.
    """

    if not infobox:
        return None

    for row in infobox.find_all("tr"):
        heading = row.find("th")
        value = row.find("td")

        if not heading or not value:
            continue

        field_name = heading.get_text(" ", strip=True).lower()

        if field_name != "elevation":
            continue

        text = value.get_text(" ", strip=True)

        # Example: 1,523 m (4,997 ft)
        feet_match = re.search(
            r"([\d,]+(?:\.\d+)?)\s*ft\b",
            text,
            re.IGNORECASE
        )

        if feet_match:
            return float(feet_match.group(1).replace(",", ""))

        # Example: 1523 m
        meter_match = re.search(
            r"([\d,]+(?:\.\d+)?)\s*m\b",
            text,
            re.IGNORECASE
        )

        if meter_match:
            meters = float(meter_match.group(1).replace(",", ""))
            return round(meters * 3.28084, 2)

    return None


def extract_article(file_path):
    file_path = Path(file_path)

    with open(file_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    title_element = soup.find(id="firstHeading")

    if not title_element:
        return None

    article_title = title_element.get_text(" ", strip=True)

    infobox = soup.find("table", class_="infobox")

    elevation = extract_elevation(infobox)

    return {
        "article_title": article_title,
        "height_ft": elevation
    }


if __name__ == "__main__":

    folder = Path("data/raw/articles")

    for file_path in folder.glob("*.html"):
        try:
            result = extract_article(file_path)

            print("\nArticle:", file_path.name)
            print("Result:", result)

        except Exception as error:
            print("Error processing", file_path.name, ":", error)
