
import csv
import json
import math
from pathlib import Path

# Project directory
BASE_DIR = Path(__file__).resolve().parent.parent

TOWNS_FILE = BASE_DIR / "data" / "towns.csv"
RECORDS_FILE = BASE_DIR / "data" / "records.json"

EARTH_RADIUS_KM = 6371


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two geographical coordinates.
    Returns distance in kilometres.
    """

    # Convert degrees into radians
    lat1, lon1, lat2, lon2 = map(
        math.radians, [lat1, lon1, lat2, lon2]
    )

    # Difference between coordinates
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine formula
    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.asin(math.sqrt(a))

    distance = EARTH_RADIUS_KM * c

    return distance


def load_town_coordinates():
    """
    Load town coordinates from CSV.
    Returns a dictionary of town coordinates.
    """

    towns = {}

    with open(TOWNS_FILE, "r", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            town = row["town"].strip().lower()

            towns[town] = {
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"])
            }

    return towns


def forts_within_km(
    town,
    radius_km,
    min_height=None
):
    """
    Find forts within a given radius of a town.

    Optional filter:
    - min_height: Minimum fort height in feet.

    Fort records must contain latitude and longitude.
    """

    # Load town coordinates
    towns = load_town_coordinates()

    town = town.strip().lower()

    if town not in towns:
        raise ValueError(f"Town not found: {town}")

    town_lat = towns[town]["latitude"]
    town_lon = towns[town]["longitude"]

    # Load fort records
    with open(RECORDS_FILE, "r", encoding="utf-8") as file:
        forts = json.load(file)

    results = []

    for fort in forts:

        lat = fort.get("latitude")
        lon = fort.get("longitude")

        # Skip forts without coordinates
        if lat is None or lon is None:
            continue

        height = fort.get("height_ft")

        # Apply minimum height filter
        if min_height is not None:
            if height is None or height < min_height:
                continue

        # Calculate distance
        distance = haversine_distance(
            town_lat,
            town_lon,
            float(lat),
            float(lon)
        )

        # Check radius
        if distance <= radius_km:

            results.append({
                "fort_name": fort["fort_name"],
                "district": fort.get("district"),
                "height_ft": height,
                "distance_km": round(distance, 2),
                "source_url": fort.get("source_url")
            })

    # Sort nearest forts first
    results.sort(key=lambda x: x["distance_km"])

    return results
