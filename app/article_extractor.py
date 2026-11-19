
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


def extract_coordinates(soup):
    """
    Extract coordinates from Wikipedia KartographerLiveData.
    Wikipedia stores coordinates as [longitude, latitude].
    """

    for script in soup.find_all("script"):

        script_text = script.string or script.get_text()

        if "wgKartographerLiveData" not in script_text:
            continue

        matches = re.findall(
            r'"coordinates"\s*:\s*\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]',
            script_text
        )

        if matches:

            longitude = float(matches[0][0])
            latitude = float(matches[0][1])

            if not (-90 <= latitude <= 90):
                continue

            if not (-180 <= longitude <= 180):
                continue

            return {
                "latitude": latitude,
                "longitude": longitude
            }

    return None


def extract_article(file_path):
    """
    Extract clean article content, elevation and coordinates
    from a downloaded Wikipedia fort article.
    """

    file_path = Path(file_path)

    with open(file_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    # Extract article title
    title_element = soup.find(id="firstHeading")

    if not title_element:
        return None

    article_title = title_element.get_text(" ", strip=True)

    # Extract elevation
    infobox = soup.find("table", class_="infobox")
    elevation = extract_elevation(infobox)

    # Extract coordinates
    coordinates = extract_coordinates(soup)

    # Find main Wikipedia article content
    content = soup.find(id="mw-content-text")

    article_parts = []

    if content:

        parser_output = content.select_one(".mw-parser-output")

        if parser_output:
            content = parser_output

        # Remove unwanted elements
        for element in content.select(
            "table, style, script, sup, "
            ".mw-editsection, .navbox, .metadata, "
            ".reference, .reflist, "
            ".mw-references-wrap, ol.references"
        ):
            element.decompose()

        # Sections that should not be included
        excluded_sections = {
            "references",
            "external links",
            "further reading",
            "see also",
            "notes",
            "footnotes",
            "bibliography",
            "sources"
        }

        # Extract article paragraphs and lists
        for element in content.select("h2, h3, p, li"):

            if element.name in ("h2", "h3"):

                heading = element.get_text(" ", strip=True)

                heading = re.sub(
                    r"\[edit\]",
                    "",
                    heading,
                    flags=re.IGNORECASE
                )

                heading = heading.strip().lower()

                if heading in excluded_sections:
                    break

                continue

            text = element.get_text(" ", strip=True)

            if text and len(text) > 30:
                article_parts.append(text)

    article_text = "\n".join(article_parts)

    return {
        "article_title": article_title,
        "article_text": article_text,
        "height_ft": elevation,
        "latitude": coordinates["latitude"] if coordinates else None,
        "longitude": coordinates["longitude"] if coordinates else None
    }


if __name__ == "__main__":

    folder = Path("data/raw/articles")

    for file_path in folder.glob("*.html"):

        try:
            result = extract_article(file_path)

            print("\nArticle:", file_path.name)

            if result:
                print("Title:", result["article_title"])
                print("Text length:", len(result["article_text"]))
                print("Text:", result["article_text"])
                print("Elevation:", result["height_ft"])
                print("Coordinates:", result["latitude"], result["longitude"])

        except Exception as error:
            print("Error processing", file_path.name, ":", error)
