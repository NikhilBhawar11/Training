
from data.sample_records import forts


def load_records():
    """Return all fort records."""
    return forts


def search(keyword):
    """Search forts by name or district."""
    keyword = keyword.lower()

    results = []

    for fort in forts:
        if (keyword in fort["fort_name"].lower() or
                keyword in fort["district"].lower()):
            results.append(fort)

    return results


def count_by(category):
    """Count records by a selected category."""
    counts = {}

    for fort in forts:
        value = fort.get(category)

        if value is not None:
            counts[value] = counts.get(value, 0) + 1

    return counts


def get_by_id(fort_id):
    """Get a fort using its position (1-based ID)."""
    if 1 <= fort_id <= len(forts):
        return forts[fort_id - 1]

    return None
